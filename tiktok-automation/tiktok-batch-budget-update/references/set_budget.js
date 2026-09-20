// TikTok 广告管理平台「修改预算」弹窗 —— 批量写入新预算
// 用法：把 MAP 换成 {广告组ID: 新预算} 后，整段传给 mcp__claude-in-chrome__javascript_tool
// 返回逐行日志。注意：返回里的「已修改 N 个广告组」是旧值，必须另起一次调用回读。

(() => {
  const MAP = {
    // "7664548737817054485": 60,
    // "7642356927774739733": 20,
  };

  // 两层 shadow DOM 穿透，找到真正的 <input>
  function deepInput(node) {
    const stack = [node];
    while (stack.length) {
      const n = stack.pop();
      if (n.tagName === 'INPUT') return n;
      if (n.shadowRoot) stack.push(...n.shadowRoot.children);
      if (n.children) stack.push(...n.children);
    }
    return null;
  }

  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  const table = document.querySelector('.bulk-adjust-form-table');
  if (!table) return '找不到 .bulk-adjust-form-table —— 弹窗没开？';
  const rows = [...table.querySelectorAll('.vi-table__body-wrapper tbody tr')];

  const log = [];
  const seen = new Set();

  rows.forEach((r, i) => {
    const cells = [...r.querySelectorAll('td')].map(td => td.innerText.trim());
    const id = (cells[0].match(/(\d{15,})\s*$/) || [])[1];
    const cur = parseFloat(cells[2]);
    if (!id || !(id in MAP)) { log.push([i, id, '不在清单，留空']); return; }
    seen.add(id);
    const target = MAP[id];
    if (cur === target) { log.push([i, id, '已是 ' + target + '，跳过']); return; }
    const inp = deepInput(r.querySelector('[x-name="x-input-number"]'));
    if (!inp) { log.push([i, id, '找不到输入框']); return; }
    inp.focus();
    setter.call(inp, String(target));
    inp.dispatchEvent(new Event('input',  { bubbles: true, composed: true }));
    inp.dispatchEvent(new Event('change', { bubbles: true, composed: true }));
    inp.blur();
    log.push([i, id, cur + '→' + target]);
  });

  const missing = Object.keys(MAP).filter(id => !seen.has(id));
  return JSON.stringify({ log, 清单里未在弹窗找到的ID: missing });
})()
