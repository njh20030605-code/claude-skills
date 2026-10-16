#!/usr/bin/env node
// 飞书多维表格迁移工具（通用）。凭据读 ~/.feishu/credentials.json {app_id, app_secret}
//
//   node fbase.js resolve  <wikiToken>                         wiki 节点 → obj_token/obj_type
//   node fbase.js schema   <app> [out.json]                    全部数据表 + 字段(名/类型/选项)，动手前必跑
//   node fbase.js dump     <app> <tableId> [out.json] [字段,字段]  拉全量记录（现状快照）
//   node fbase.js count    <app> <tableId>
//   node fbase.js workflows <app> [out.json]                   列自动化规则并备份状态
//   node fbase.js apply    <app> <diff.json> [--test] [--keep "规则名1,规则名2"]
//        停规则 → delete/update/create → 恢复（finally 兜底）。--test 只写每表第一条、回读、删掉
//        diff.json = { "<tableId>": { "delete":[record_id], "update":[{record_id,fields}], "create":[fields] } }
//        产出 applied_<tableId>_<时间戳>.json（含 created record_id，可回滚）
//   node fbase.js rollback <app> <tableId> <applied.json>      删掉 applied 里 created 的行（update 不可逆！）
//   node fbase.js persons  <app> <tableId> <人员字段> <ou_xxx...>  临时建一行写人员字段 → 回读姓名 → 删行
//   node fbase.js people   <app> [tableId...]                  从现有记录里收集所有出现过的人员 open_id↔姓名
const fs = require('fs');
const c = require(require('os').homedir() + '/.feishu/credentials.json');
const B = 'https://open.feishu.cn/open-apis';
const STAMP = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14);
const sleep = ms => new Promise(r => setTimeout(r, ms));
let tok, tokAt = 0;
async function token() {
  if (tok && Date.now() - tokAt < 90 * 60e3) return tok;
  const r = await (await fetch(B + '/auth/v3/tenant_access_token/internal', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ app_id: c.app_id, app_secret: c.app_secret }) })).json();
  tok = r.tenant_access_token; tokAt = Date.now(); return tok;
}
async function api(m, p, body, retry = 4) {
  for (let i = 0; i < retry; i++) {
    try {
      const r = await (await fetch(B + p, { method: m, headers: { Authorization: 'Bearer ' + await token(), 'Content-Type': 'application/json' }, body: body ? JSON.stringify(body) : undefined })).json();
      if (r.code === 0) return r;
      // 5xx / 限流 / 数据未就绪 → 退避重试
      if (i < retry - 1 && (r.code >= 500 || [99991400, 1254291, 1254607, 1255040].includes(r.code))) { await sleep(1500 * (i + 1)); continue; }
      return r;
    } catch (e) { if (i === retry - 1) throw e; await sleep(1500); }
  }
}
const must = (r, what) => { if (!r || r.code !== 0) throw new Error(`${what} 失败: ${r && r.code} ${r && r.msg} ${JSON.stringify(r).slice(0, 600)}`); return r; };

async function tables(app) {
  const out = []; let pt = null;
  do { const r = must(await api('GET', `/bitable/v1/apps/${app}/tables?page_size=100${pt ? '&page_token=' + pt : ''}`), 'list tables'); out.push(...r.data.items); pt = r.data.has_more ? r.data.page_token : null; } while (pt);
  return out;
}
async function fields(app, tid) {
  const out = []; let pt = null;
  do { const r = must(await api('GET', `/bitable/v1/apps/${app}/tables/${tid}/fields?page_size=100${pt ? '&page_token=' + pt : ''}`), 'list fields'); out.push(...r.data.items); pt = r.data.has_more ? r.data.page_token : null; } while (pt);
  return out;
}
async function dump(app, tid, fieldNames) {
  const out = []; let pt = null;
  do {
    const r = must(await api('POST', `/bitable/v1/apps/${app}/tables/${tid}/records/search?page_size=500${pt ? '&page_token=' + pt : ''}`, fieldNames ? { field_names: fieldNames } : {}), 'search');
    out.push(...(r.data.items || [])); pt = r.data.has_more ? r.data.page_token : null;
  } while (pt);
  return out;
}
async function count(app, tid) { return must(await api('POST', `/bitable/v1/apps/${app}/tables/${tid}/records/search?page_size=1`, {}), 'count').data.total; }
async function workflows(app) { return must(await api('GET', `/bitable/v1/apps/${app}/workflows`), 'workflows').data.workflows || []; }
async function setWf(app, id, status) { let r; for (let i = 0; i < 5; i++) { r = await api('PUT', `/bitable/v1/apps/${app}/workflows/${id}`, { status }); if (r.code === 0) return r; await sleep(2000); } return r; }
async function chunked(arr, n, fn) { for (let i = 0; i < arr.length; i += n) await fn(arr.slice(i, i + n), i); }

const TYPE = { 1: '文本', 2: '数字', 3: '单选', 4: '多选', 5: '日期', 7: '复选框', 11: '人员', 13: '电话', 15: '超链接', 17: '附件', 18: '单向关联', 19: '查找引用', 20: '公式', 21: '双向关联', 22: '地理位置', 23: '群组', 1001: '创建时间', 1002: '修改时间', 1003: '创建人', 1004: '修改人', 1005: '自动编号' };

const [cmd, ...a] = process.argv.slice(2);
(async () => {
  if (cmd === 'resolve') {
    const r = must(await api('GET', `/wiki/v2/spaces/get_node?token=${a[0]}&obj_type=wiki`), 'get_node');
    console.log(JSON.stringify({ obj_token: r.data.node.obj_token, obj_type: r.data.node.obj_type, title: r.data.node.title }, null, 1));
  } else if (cmd === 'schema') {
    const out = {};
    for (const t of await tables(a[0])) {
      const fs_ = await fields(a[0], t.table_id);
      out[t.table_id] = { name: t.name, rows: await count(a[0], t.table_id), fields: fs_.map(f => ({ id: f.field_id, name: f.field_name, type: TYPE[f.type] || f.type, ui: f.ui_type, options: f.property && f.property.options ? f.property.options.map(o => ({ id: o.id, name: o.name })) : undefined })) };
      console.log(`\n## ${t.name}  ${t.table_id}  (${out[t.table_id].rows} 行)`);
      for (const f of out[t.table_id].fields) console.log(`  - ${f.name}  [${f.type}]${f.options ? '  选项: ' + f.options.map(o => o.name).join(' / ') : ''}`);
    }
    fs.writeFileSync(a[1] || `schema_${a[0]}.json`, JSON.stringify(out, null, 1));
  } else if (cmd === 'dump') {
    const recs = await dump(a[0], a[1], a[3] ? a[3].split(',') : undefined);
    fs.writeFileSync(a[2] || `dump_${a[1]}.json`, JSON.stringify(recs));
    console.log('records', recs.length, '→', a[2] || `dump_${a[1]}.json`);
  } else if (cmd === 'count') {
    console.log(await count(a[0], a[1]));
  } else if (cmd === 'workflows') {
    const wf = await workflows(a[0]); fs.writeFileSync(a[1] || `wf_backup_${a[0]}.json`, JSON.stringify(wf, null, 1));
    for (const w of wf) console.log(w.status.padEnd(8), w.workflow_id, w.title);
  } else if (cmd === 'apply') {
    const app = a[0], D = JSON.parse(fs.readFileSync(a[1]));
    const test = a.includes('--test');
    const ki = a.indexOf('--keep'); const keep = ki >= 0 ? a[ki + 1].split(',').map(s => s.trim()) : [];
    const wf = await workflows(app); fs.writeFileSync(`wf_backup_${Date.now()}.json`, JSON.stringify(wf, null, 1));
    const toStop = wf.filter(w => w.status === 'Enable' && !keep.includes(w.title));
    for (const t of Object.keys(D)) console.log('before', t, await count(app, t));
    console.log(`停规则 ${toStop.length} 条（保留: ${keep.join(', ') || '无'}）`);
    for (const w of toStop) { const r = await setWf(app, w.workflow_id, 'Disable'); if (r.code !== 0) throw new Error('停规则失败，未写入任何数据: ' + w.title + ' ' + r.msg); }
    try {
      for (const [t, d] of Object.entries(D)) {
        if (test) {
          const f = (d.create || [])[0];
          if (!f) { console.log(t, '无 create 样本，跳过测试'); continue; }
          const r = must(await api('POST', `/bitable/v1/apps/${app}/tables/${t}/records/batch_create`, { records: [{ fields: f }] }), 'test create');
          const id = r.data.records[0].record_id;
          const g = await api('GET', `/bitable/v1/apps/${app}/tables/${t}/records/${id}`);
          console.log(`\n[${t}] 写入:`, JSON.stringify(f).slice(0, 1200), `\n[${t}] 回读:`, JSON.stringify(g.data.record.fields).slice(0, 1500));
          must(await api('POST', `/bitable/v1/apps/${app}/tables/${t}/records/batch_delete`, { records: [id] }), 'test delete');
          console.log(`[${t}] 测试行已删`);
          continue;
        }
        const log = { deleted: [], updated: [], created: [] };
        const save = () => fs.writeFileSync(`applied_${t}_${STAMP}.json`, JSON.stringify(log));
        await chunked(d.delete || [], 500, async (ch, i) => { must(await api('POST', `/bitable/v1/apps/${app}/tables/${t}/records/batch_delete`, { records: ch }), 'delete'); log.deleted.push(...ch); save(); console.log(t, 'delete', i + ch.length, '/', d.delete.length); });
        await chunked(d.update || [], 500, async (ch, i) => { must(await api('POST', `/bitable/v1/apps/${app}/tables/${t}/records/batch_update`, { records: ch }), 'update'); log.updated.push(...ch.map(u => u.record_id)); save(); console.log(t, 'update', i + ch.length, '/', d.update.length); });
        await chunked(d.create || [], 500, async (ch, i) => { const r = must(await api('POST', `/bitable/v1/apps/${app}/tables/${t}/records/batch_create`, { records: ch.map(f => ({ fields: f })) }), 'create'); log.created.push(...r.data.records.map(x => x.record_id)); save(); console.log(t, 'create', i + ch.length, '/', d.create.length); });
        console.log(t, 'after', await count(app, t), `→ applied_${t}_${STAMP}.json`);
      }
    } finally {
      console.log('恢复规则…');
      for (const w of toStop) { const r = await setWf(app, w.workflow_id, 'Enable'); if (r.code !== 0) console.log('  !! 恢复失败，需手动开启:', w.title, r.msg); }
      const now = await workflows(app);
      const bad = toStop.filter(w => (now.find(x => x.workflow_id === w.workflow_id) || {}).status !== 'Enable');
      console.log(bad.length ? '  !! 仍未恢复: ' + bad.map(w => w.title).join(', ') : '  规则已全部恢复');
    }
  } else if (cmd === 'rollback') {
    const L = JSON.parse(fs.readFileSync(a[2])); const ids = L.created || L;
    await chunked(ids, 500, async (ch, i) => { must(await api('POST', `/bitable/v1/apps/${a[0]}/tables/${a[1]}/records/batch_delete`, { records: ch }), 'rollback'); console.log('deleted', i + ch.length, '/', ids.length); });
    if (L.updated && L.updated.length) console.log(`注意：${L.updated.length} 条 update 无法自动回滚，需用写入前的 dump 还原`);
  } else if (cmd === 'persons') {
    const [app, tid, field, ...ids] = a;
    const r = must(await api('POST', `/bitable/v1/apps/${app}/tables/${tid}/records`, { fields: { [field]: ids.map(id => ({ id })) } }), 'probe create');
    const rid = r.data.record.record_id;
    try { const g = await api('GET', `/bitable/v1/apps/${app}/tables/${tid}/records/${rid}`); for (const p of g.data.record.fields[field] || []) console.log(p.id, p.name, p.en_name || '', p.email || ''); }
    finally { await api('DELETE', `/bitable/v1/apps/${app}/tables/${tid}/records/${rid}`); console.log('临时行已删'); }
  } else if (cmd === 'people') {
    const app = a[0]; const tids = a.slice(1).length ? a.slice(1) : (await tables(app)).map(t => t.table_id);
    const P = {};
    for (const t of tids) for (const it of await dump(app, t)) for (const v of Object.values(it.fields)) if (Array.isArray(v)) for (const p of v) if (p && p.id && String(p.id).startsWith('ou_')) P[p.id] = p.name;
    console.log(JSON.stringify(P, null, 1));
  } else {
    console.log(fs.readFileSync(__filename, 'utf8').split('\n').filter(l => l.startsWith('//')).join('\n'));
  }
})().catch(e => { console.error('FATAL', e.message || e); process.exit(1); });
