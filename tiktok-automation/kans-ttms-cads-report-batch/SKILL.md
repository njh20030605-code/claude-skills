---
name: "kans-ttms-cads-report-batch"
description: "在 TikTok Market Scope (TTMS) 投后结案页面用 Claude in Chrome 批量创建 KANS 越南「种草广告报告」结案。当用户给出一批待建报告（或给出 Campaign Report + GMV Max Creative 导出表让你自己筛）并要求\"批量建种草广告报告 / 跑 C-ads 结案 / 建投后结案报告 / 继续建报告\"时使用。核心：分析周期（起止日期）必须先跟用户确认再执行；逐个用 javascript_tool + 坐标点击操作受控 React 表单，靠\"可创建报告数\"配额循环建满→等处理释放→再建，靠\"Contains 1 个广告组\"+广告组全名校验勾中正确广告组。"
---

---
name: "kans-ttms-cads-report-batch"
description: "在 TikTok Market Scope (TTMS) 投后结案页面用 Claude in Chrome 批量创建 KANS 越南「种草广告报告」结案。当用户给出一批待建报告（或给出 Campaign Report + GMV Max Creative 导出表让你自己筛）并要求\"批量建种草广告报告 / 跑 C-ads 结案 / 建投后结案报告 / 继续建报告\"时使用。核心：分析周期（起止日期）必须先跟用户确认再执行；逐个用 javascript_tool + 坐标点击操作受控 React 表单，靠\"可创建报告数\"配额循环建满→等处理释放→再建，靠\"Contains 1 个广告组\"+广告组全名校验勾中正确广告组。"
---

# KANS 越南 TTMS 种草广告报告（C-ads 投后结案）批量创建

用 Claude in Chrome 在 TikTok Market Scope 上批量创建 KANS Vietnam 的「种草广告报告」（一次性投后结案报告）。本 SKILL 是实操蒸馏版，记录了真实跑通后才知道的坑，照做即可。

## ⛔ 第 0 条铁律：分析周期必须先跟用户确认

**在动手建任何报告之前，必须用 AskUserQuestion 跟用户确认「分析周期」和由此决定的「报告命名」，拿到明确答复后才执行。**

- 不许自己按广告组的起投日推断周期，不许沿用上一次运行的周期口径，不许用页面默认周期。
- 每次运行都要确认一次，即使用户说"继续建报告"。上次是 0720 截止，这次很可能是整月。
- 确认清单（一次问完）：
  1. **分析周期起止**：默认口径是**整月**，例：`2026-07-01 ～ 2026-07-31`。也可能是「起投日 ～ 月末」或自定义截止日。
  2. **报告命名规则**：命名要和周期口径对得上。历史用过的两种：
     - `素材ID_起投MMDD_截止MMDD_产品名` ← **当前默认**（保留达人起投日，例 `7632306303225892116_0629_0731_Red serum`）
     - `素材ID_起投MMDD_0720_产品名`（旧口径，2026-07 上半月那批）
  3. **周期外的素材怎么办**：起投日晚于截止日的（周期非法），是跳过还是单独定周期。
  4. **改口径后旧报告怎么办**：同素材已存在旧命名/旧周期的报告，是留着并存、还是让用户自己去后台删。**删除报告永远不代做，让用户自己删。**
- 确认结果要在收尾简报里复述一遍，方便对账。

## 前置
- 平台页：`https://marketscope.tiktok.com/brand/report/list?accountId=7501254948374904840#/`
- 账号：KANS Vietnam｜美妆个护（浏览器已登录）
- 工具：优先 `mcp__claude-in-chrome__javascript_tool`（受控表单最稳）+ 少量 `computer` 截图/坐标点击。用 ToolSearch 一次性加载：`tabs_context_mcp,navigate,javascript_tool,tabs_create_mcp,read_page,computer`。
- 先 `tabs_context_mcp{createIfEmpty:true}`，再 navigate 到列表页。**首次进列表页 body 常常是空的（只有导航栏）**，`location.reload()` 后再等 6 秒就有内容了。

## 输入：怎么得出待建列表

两种входа：

**A. 用户直接给清单**：每条 `素材ID | 起投MMDD | 产品 | 达人`。产品只有三类，原样写进报告名：`White Essence` / `Red serum` / `素颜霜`。

**B. 用户丢平台导出表让你自己筛**（更常见）。典型是 4 个 xlsx：
- `Kans--02-Campaign Report-YYYY-MM-DD to YYYY-MM-DD.xlsx` —— **这是待建清单的唯一权威来源**。列 `广告组名称` 格式 `MMDD-达人-产品-BC-人群包-素材ID`（有的带 ` 的副本 1` 后缀，有的是 `-无组件` 老命名解析不出产品，那些一般消耗为 0）。列 `消耗` 就是 C-ads 花费。**"跑表里有消耗的" = 这张表 `消耗 > 0` 的广告组。** 注意最后一行 `总计： N 条结果` 是汇总行，要剔掉。
- 3 个 `..._Creative data ... - Product <productId>.xlsx` —— GMV Max 素材消耗数据，列 `Post ID`（=素材ID）、`Cost`。**只用来做匹配校验**（"匹配上即可"）：素材ID 在其中且 `Cost > 0` 才建。productId 映射：
  - `1731561143212017689` → White Essence
  - `1731559750857099289` → Red serum
  - `1731728613455398937` → 素颜霜
  - 读 `Post ID` 一定 `dtype=str`，否则 pandas 转成科学计数法丢精度。

筛选逻辑（顺序）：Campaign Report `消耗>0` → 解析出 `起投MMDD/达人/产品/素材ID` → 与 GMV Max `Cost>0` 素材ID 求交集 → 按 `(素材ID, 起投MMDD, 产品)` 去重（同一素材同一天可能有重复行）→ 剔掉周期非法项 → 与列表页已有报告名做幂等去重。
匹配不上 GMV Max 的、和周期非法的，都**不建**，在收尾简报里单独列出来。

## 命名与参数（每个报告）
- 报告名：**按第 0 条确认的规则**，默认 `素材ID_起投MMDD_截止MMDD_产品名`
- 分析周期：**按第 0 条确认的起止**，默认整月 `2026-07-01 ～ 2026-07-31`
- 归因期限：`7 天`
- 分析资源：自定义资源 → 进对应推广系列 → 只勾 1 个目标广告组

## ⚠️ 推广系列不是按产品三分的，是「批次日期 + 产品」
别再用"White Essence→17个广告组"这种硬编码，**每次都要现场枚举推广系列列表**。真实结构是按起投批次分的，例（2026-07 那次）：

| 推广系列 | 广告组数 |
|---|---|
| KOL-Brand Consideration-护肤人群-White Essence-新Cads-0619 | 1 |
| KOL-Brand Consideration-4千万人群包-White Essence-0625 | 15 |
| KOL-Brand Consideration-4千万人群包-Red serum-0625 | 5 |
| 0629-KOL-Brand Consideration-4千万人群包-Red serum | 6 |
| 0629-KOL-Brand Consideration-4千万人群包-White Essence | 16 |
| 0630-KOL-Brand Consideration-4千万人群包-素颜霜 | 2 |
| 0701-KOL-Brand Consideration-4千万人群包-White Essence | 1 |
| 0703-KOL-Brand Consideration-护肤人群-素颜霜 | 4 |

**定位规则：目标广告组的 `MMDD` 前缀 ≈ 推广系列名里的批次日期前缀**（广告组 `0630-kady_tran-...` 可能挂在 `0629-...` 系列里，`0702-...` 可能挂在 `0630-...` 系列里，所以要就近找、找不到就进相邻批次的系列翻）。

## ⚠️ 同一素材ID会出现在多个广告组（不同起投日）
例：`7632306303225892116` 同时有 `0629-beebong9909-Red serum-...` 和 `0703-beebong9909-Red serum-...` 两个广告组。
**所以勾选校验绝不能只比素材ID，必须比广告组全名（含 MMDD 前缀）。** 从 Campaign Report 里把目标广告组的完整 `广告组名称` 带进流程，作为勾选校验的 target。

## 幂等
每次建前先抓列表页已有报告名。列表默认按创建时间倒序、每页 10 条。用**当前确认的命名规则**对应的正则（例 `\d{15,}_\d{4}_0731`）抓已存在项，凡已存在就跳过。
**注意：改了截止日就等于改了报告名，旧的 `_0720_` 报告不算已存在**，会导致本次待建量暴涨——这一点要在开工前明确告知用户待建条数，别默默建几十条。
翻页收集：报告是按创建时间聚簇的，一般前几页就把本批都覆盖了；连续 3 页匹配数为 0 就可以停，不用翻完 34 页。
```js
function fire(el){['pointerdown','mousedown','pointerup','mouseup','click'].forEach(t=>el.dispatchEvent(new MouseEvent(t,{bubbles:true,cancelable:true,view:window})));}
window.__fire=fire; window.__seen={};
window.__next=async function(n,re){
 for(let i=0;i<n;i++){
  const pg=(document.querySelector('.byted-pager-item-checked span')||{}).textContent;
  window.__seen[pg]=[...new Set(document.body.innerText.match(re)||[])];
  const items=[...document.querySelectorAll('.byted-pager-item')];
  const nx=items.at(-1);
  if(!nx||nx.className.includes('disabled')) return 'end@'+pg;
  fire(nx.querySelector('span')||nx);
  await new Promise(r=>setTimeout(r,1400));
 }
 return 'ok@'+(document.querySelector('.byted-pager-item-checked span')||{}).textContent;
};
await window.__next(8, /\d{15,}_\d{4}_0731[^\n]*/g)
```
取结果时**别一次 JSON.stringify 全量**（会被截断），分片取或先算 `n`。

## 单次运行要循环，最大化产出
一次运行里循环：建满当前配额 → 关弹窗等约 75 秒让报告处理释放新配额 → 再查配额继续建。直到待建全部建完，或**连续两次查配额都为 0（约 2–3 分钟没释放）**再退出。初始配额通常是 10。

---

## 关键坑（务必遵守）

1. **JS 批次别太长**：`javascript_tool` 单次 >45s 会 CDP 超时。每个报告拆成多次短调用，别把「选类型+命名+日期+选资源+提交」塞一次。即使超时，前面的操作往往已生效，`await` 后重新查状态即可。

2. **配置页别开太久 → 提交报 "No permission!"**：配置页停留过久（比如选资源反复折腾），提交会弹 `No permission!`（不是没权限，是页面 stale）。解决：回列表页重新「新建」走一遍全新流程。**尽量一气呵成**。

3. **别返回含 URL / query string 的东西**：`location.href`、`performance.getEntriesByType('resource')` 这类返回值会被安全层整条拦掉（`[BLOCKED: Cookie/query string data]`），连带你要的数据一起丢。用 `location.pathname` 代替。

4. **选广告组的勾选：别用 JS 爬 checkbox 触发点击**。从 checkbox 往上爬父节点 `querySelector('checkbox')` 会抓到**别的行**的框（血泪教训，勾错过）。正确做法：**截图 + 坐标点击**，checkbox 列 x≈793。点完**必须校验**（见下）。

5. **页内搜索框不认素材ID**：`按名称或 ID 搜索` 搜的是推广系列/广告组ID，搜素材ID 搜不到。老老实实进系列翻页找。

6. **水印干扰**：页面背景水印是一串假的 19 位数字（不同账号不一样，KANS VN 见到过 `7614060375009969160`、`7642277009700619784`）。解析 76 开头的 19 位ID时会混进来，用「广告组名全名正则 `^\d{4}-.*-\d{18,19}`」来筛叶子节点就能天然避开水印。

---

## 逐报告操作流程

### 1) 打开新建弹窗、读配额
```js
const nb=[...document.querySelectorAll('button,a,span,div')].find(b=>b.textContent.trim()==='新建');
if(nb) window.__fire(nb);
await new Promise(r=>setTimeout(r,2000));
JSON.stringify({q:(document.body.innerText.match(/可创建报告数[:：]\s*(\d+)/)||[])[1]});  // N<1 → 点「取消」关弹窗、进等待循环
```

### 2) 选报告类型 → 一次性报告 → 下一步
```js
const fire=window.__fire, dr=document.querySelector('[class*="drawer"],[role="dialog"]')||document;
const h=[...dr.querySelectorAll('*')].filter(e=>e.textContent.trim()==='种草广告报告'&&e.children.length===0);
if(h.length){let el=h[0];for(let i=0;i<3;i++)el=el.parentElement||el;fire(h[0]);fire(el);}
await new Promise(r=>setTimeout(r,600));
const once=[...dr.querySelectorAll('label,div,span')].find(e=>e.textContent.trim().startsWith('一次性报告')); if(once)fire(once);
await new Promise(r=>setTimeout(r,500));
const nx=[...dr.querySelectorAll('button')].filter(b=>b.textContent.trim()==='下一步'); if(nx.length)fire(nx.at(-1));
await new Promise(r=>setTimeout(r,2000));
JSON.stringify({cfg:!!document.querySelector('input[placeholder="请输入"]')});  // true = 到配置页（URL 会变成 reportType=3&generationMode=1）
```

### 3) 设报告名（React 受控，用原生 setter，设两次）
```js
const NAME='素材ID_起投MMDD_截止MMDD_产品名';
const set=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;
const inp=document.querySelector('input[placeholder="请输入"]');
const go=()=>{set.call(inp,NAME);inp.dispatchEvent(new Event('input',{bubbles:true}));inp.dispatchEvent(new Event('change',{bubbles:true}));};
go();await new Promise(r=>setTimeout(r,300));go();
inp.value;
```

### 4) 日期：**两个月面板，必须按面板选，不能"取最右"**
日历并排显示两个月（左＝较早月，右＝较晚月），共 84 个单元格，`x≈680` 是左右分界。**上一版 SKILL 里"取最右"的写法只对「起止都在右侧月」成立；起投日在左侧月（如 6/29）时会选错。** 用 panel 参数显式指定：
```js
window.__pick2=function(d,panel){ // panel 0=左侧月, 1=右侧月
 const c=[...document.querySelectorAll('.byted-date-date.byted-date-item')]
   .filter(x=>x.textContent.trim()==String(d)&&/grid-in/.test(x.className)&&!/disabled/.test(x.className));
 const hit=c.filter(x=>{const r=x.getBoundingClientRect(); return panel===0? r.x<680 : r.x>680;});
 return {el:hit[0],hits:hit.length};
};
```
先截图确认两个面板各是哪个月（表头形如 `2026年 6月` / `2026年 7月`），需要时用 `‹ / ›` 翻月。然后**拆成两次调用**：
```js
// 调用 A：开日历 + 点开始日
const fire=window.__fire, di=document.querySelector('input[placeholder="开始时间 ～ 结束时间"]');
fire(di);await new Promise(r=>setTimeout(r,1100));
const a=window.__pick2(1,1); if(a.el)fire(a.el);   // 例：7/1 在右侧月 → pick2(1,1)
await new Promise(r=>setTimeout(r,800));
// 调用 B：点截止日 + 校验
const b=window.__pick2(31,1); if(b.el)fire(b.el);
await new Promise(r=>setTimeout(r,900));
document.querySelector('input[placeholder="开始时间 ～ 结束时间"]').value; // 必须 === '2026-07-01 ～ 2026-07-31'
```
- 点完开始日时输入框**还不会更新**（等第二个点击），别以为失败。
- 校验字符串不符就重开日历重选一遍。
- 页面会显示 `已选 N 天。请在 2 到 185 天之间选择。` 可作二次确认。

### 5) 自定义资源 → 进对应推广系列
选资源是**钻取式导航**（不是树展开）：点「自定义资源」弹出「选择资源」模态 → 点行内「N 个广告组」蓝链接（className 含 `017976`）**进入**该系列的广告组列表；面包屑「推广系列列表」可返回。
先枚举系列名（列表在模态内可滚动容器里）：
```js
const sc=[...document.querySelectorAll('*')].find(e=>e.scrollHeight>e.clientHeight+50&&e.clientHeight>200&&e.textContent.includes('KANS SKINCARE VIETNAM'));
if(sc)sc.scrollTop=sc.scrollHeight; await new Promise(r=>setTimeout(r,900));
JSON.stringify([...new Set([...document.querySelectorAll('*')].filter(e=>e.children.length===0&&/KOL-Brand Consideration|KANS/.test(e.textContent)&&e.textContent.length<80).map(e=>e.textContent.trim()))]);
```
再按系列名进入（比硬编码"17 个广告组"稳）：
```js
window.__enter=async function(camp){
 const sc=[...document.querySelectorAll('*')].find(e=>e.scrollHeight>e.clientHeight+50&&e.clientHeight>200&&e.textContent.includes('KANS SKINCARE VIETNAM'));
 if(sc)sc.scrollTop=0; await new Promise(r=>setTimeout(r,400));
 const leaf=[...document.querySelectorAll('*')].find(e=>e.children.length===0&&e.textContent.trim()===camp);
 if(!leaf) return 'no-camp';
 leaf.scrollIntoView({block:'center'}); await new Promise(r=>setTimeout(r,400));
 let row=leaf, link=null;
 for(let i=0;i<6&&row;i++){row=row.parentElement; if(!row)break;
   link=[...row.querySelectorAll('div')].find(e=>/^\d+ 个广告组$/.test(e.textContent.trim())&&e.className.includes('017976')); if(link)break;}
 if(!link) return 'no-link';
 const label=link.textContent.trim(); window.__fire(link);
 await new Promise(r=>setTimeout(r,1600)); return 'entered:'+label;
};
await window.__enter('0629-KOL-Brand Consideration-4千万人群包-Red serum')
```
广告组超过 10 个会分页，目标不在第 1 页时点分页「2」：
```js
const p=[...document.querySelectorAll('li,a,button,span,div')].filter(e=>e.textContent.trim()==='2'&&e.children.length<=1&&(e.className.toLowerCase().includes('pag')||e.closest('[class*="pag"]')));
if(p.length)window.__fire(p.at(-1));
```

### 6) 勾选目标广告组（截图 + 坐标点击，按全名校验）
先把目标滚到可见：
```js
const t='0629-beebong9909-Red serum-BC-4千万人群包-7632306303225892116';
const leaf=[...document.querySelectorAll('*')].find(e=>e.children.length===0&&e.textContent.trim()===t);
leaf.scrollIntoView({block:'center'});await new Promise(r=>setTimeout(r,600));
leaf.textContent.trim();
```
然后 `computer` 截图，在目标行 checkbox（x≈793）处 `left_click`。**点完必须校验**：`Contains 1 个广告组` 且被勾的行名 === target 全名：
```js
window.__verify=function(target){
 const all=[...document.querySelectorAll('*')];
 const sum=all.find(e=>/Contains\s*\d+\s*个广告组/.test(e.textContent)&&e.children.length<=4);
 const summary=sum?sum.textContent.match(/Contains\s*\d+\s*个广告组/)[0]:null;
 let names=[];
 [...document.querySelectorAll('[class*="checkbox"][class*="checked"],[class*="checkbox"] [class*="checked"]')].forEach(w=>{
  const r=w.getBoundingClientRect(); if(r.width===0)return;
  const cy=r.top+r.height/2; let bl=null,bd=1e9;
  all.filter(e=>e.children.length===0&&/^\d{4}-.*-\d{18,19}/.test(e.textContent.trim()))
     .forEach(l=>{const lr=l.getBoundingClientRect(),d=Math.abs(lr.top+lr.height/2-cy);if(d<bd){bd=d;bl=l;}});
  if(bl&&bd<25)names.push(bl.textContent.trim());
 });
 names=[...new Set(names)];
 return {summary,names,ok:names.length===1&&names[0]===target};
};
JSON.stringify(window.__verify(t))
```
`ok:false` 就先取消勾选、微调坐标（±20px）重点。确认无误后点「确认」按钮（JS 找 `textContent==='确认' && !disabled` 即可，或右下坐标约 1498,690）。

### 7) 高级设置 7 天 → 提交
```js
const fire=window.__fire;
window.scrollTo(0,document.body.scrollHeight);await new Promise(r=>setTimeout(r,500));
const sh=[...document.querySelectorAll('*')].find(e=>e.textContent.trim()==='显示'&&e.children.length===0);if(sh)fire(sh);
await new Promise(r=>setTimeout(r,1000));
const s=[...document.querySelectorAll('label,span,div')].filter(e=>e.textContent.trim()==='7 天'&&e.children.length<=1);
if(s.length){fire(s[0]);const lb=s[0].closest('label')||s[0].parentElement;const r=lb.querySelector('input[type=radio]');if(r)r.click();}
await new Promise(r=>setTimeout(r,500));
JSON.stringify([...document.querySelectorAll('input[type=radio]')].map(r=>({t:(r.closest('label')||r.parentElement).textContent.trim(),c:r.checked})).filter(x=>/天/.test(x.t)));  // 期望 7 天:true
```
提交前**必须同时校验报告名 + 分析周期**（周期错过一次，代价是重建）：
```js
const chk={name:document.querySelector('input[placeholder="请输入"]').value,
           period:document.querySelector('input[placeholder="开始时间 ～ 结束时间"]').value};
// chk 与预期不符 → 不要提交，先修
const btn=[...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='提交');if(btn)window.__fire(btn);
await new Promise(r=>setTimeout(r,2800));
JSON.stringify({chk, path:location.pathname, toast:[...document.querySelectorAll('[class*="toast"],[class*="message"],[class*="notice"]')].map(e=>e.textContent.trim()).filter(x=>x.length>2&&x.length<60).slice(0,3)});
```
- `报告创建成功` = 成功，自动回列表页（`path==='/brand/report/list'`）。
- `No permission!` = 页面 stale，回列表页重新「新建」整条流程重来（勿反复重试同一 stale 页）。

## 配额循环
每建完一个回列表页，点「新建」读「可创建报告数」：>0 继续建下一个；=0 就点「取消」关弹窗，用 `computer` 的 `wait` 分段等约 75 秒（每次最多 10s），再刷新列表 / 重开弹窗查配额。列表页 `全部(n)/排队中(n)/正在处理(n)/已完成(n)` 计数可辅助判断处理进度（正在处理→已完成 才释放配额）。连续两次 0 就结束本次运行。

## 收尾简报
- 复述本次确认的**分析周期 + 命名规则**。
- 本次新建了哪几条、还剩几条待建。
- 跳过项分类列出：已存在（幂等跳过）／GMV Max 无消耗匹配不上／起投日晚于截止日周期非法。
- 需要用户手动处理的（如删旧口径报告）单独点出来。
- 若作为定时任务且待建已全部建完，可删除该定时任务；否则保留继续跑。

