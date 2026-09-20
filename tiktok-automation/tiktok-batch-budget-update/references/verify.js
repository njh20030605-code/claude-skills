// 回读校验 —— 必须作为【独立的一次】 javascript_tool 调用运行，
// 和写入放同一次调用会读到 Vue 重渲染前的旧计数。

(() => {
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

  const table = document.querySelector('.bulk-adjust-form-table');
  const rows = [...table.querySelectorAll('.vi-table__body-wrapper tbody tr')];

  return JSON.stringify({
    rows: rows.map((r, i) => {
      const c = [...r.querySelectorAll('td')].map(td => td.innerText.trim());
      const id = (c[0].match(/(\d{15,})\s*$/) || [])[1];
      const inp = deepInput(r.querySelector('[x-name="x-input-number"]'));
      return { i, id, 当前: c[2], 新填: inp ? inp.value : null };
    }),
    计数: (document.body.innerText.match(/已修改\s*\d+\s*个广告组/) || [null])[0]
  });
})()
