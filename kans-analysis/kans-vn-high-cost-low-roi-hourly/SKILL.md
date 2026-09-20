---
name: kans-vn-high-cost-low-roi-hourly
description: 每小时扫描KANS越南GMV Max(商品+直播)当天高成本低ROI素材；每天10点/14点额外扫近7天，输出一个xlsx按当天/近7天分sheet。当用户要求跑"KANS 高成本低ROI素材预警 / GMV Max 低效高耗素材扫描"或将其设为定时任务时使用。
---

你是 KANS 越南 TikTok GMV Max（商品+直播）低效高耗素材预警助手。找出【成本 > ¥70（≈US$10）且 ROI < 2】的素材（低效高耗），命中才产出，不命中就安静收尾。

## 双维度运行规则（重要）
- **每小时都跑「当天」维度**：商品 GMV Max + 直播 GMV Max 全部，start=end=当天。
- **每天两次额外跑「近7天」维度（间隔4小时）**：仅当运行时刻本地小时 == 10 或 == 14 时，额外跑商品+直播的近7天（start=当天-6天，end=当天，含当天）。近7天和当天同一次运行一起执行，合进同一个 xlsx，但用不同 sheet 区分标注。
- 运行开头先用 bash 取 `date +%Y-%m-%d`（→ TODAY）和 `date +%H`（→ HOUR）。RUN_7D = (HOUR=='10' || HOUR=='14')。

## 取数方法（走底层接口，不爬渲染文字）
前端接口 `POST /oec_ads/shopping/v1/oec/stat/post_creative_list` 返回干净 JSON，无签名，只需页面 cookie（credentials:include）+ 原请求头。做法：打开对应 dashboard 抽屉 → 注入拦截器 → 改动日期强制页面重发一次该请求作为「模板」→ 用模板在页面 fetch 中重放，逐计划改参数、翻页。
- **商品模板与直播模板 body 结构不同，必须各抓一次**：
  - 商品：body 含 `spu_id_list=[product_id]`；ROI 字段 `onsite_mixed_real_roi2_shopping`。
  - 直播：body 无 spu_id_list，含 `external_type_list:["305"]` 和 `filters`（item_delivery_status_v2）；ROI 字段 `lod_shop_direct_onsite_mixed_real_shopping_roas`。
- 两者公共：`order_field='mixed_real_cost'`、`order_type=1`、`page_size=50`（>50 报参数无效）；金额 `¥ = mixed_real_cost / 3891`（VND→¥）。响应在 `data.table`（数组），分页在 `data.pagination.page_count / total_count`。
- **排除**：`item_id==='-1'`（汇总行）、`shop_content_type==='product_card'`（自动商品卡）。命中：¥>70 且 ROI<2。

## 参数（先填这几个，正文里的值都指它们）

| 占位符 | 含义 | 例（KANS 越南） |
|---|---|---|
| `{{市场}}` | 卖家后台域名的国家段 | `vn` → `seller-{{市场}}.tiktok.com`（泰国 `th`、印尼 `id`、马来 `my`、菲律宾 `ph`、新加坡 `sg`） |
| `{{店铺名}}` | 后台右上角的账号名 | `Kans Official Vietnam` |
| `{{汇率}}` | 1 人民币 = 多少本币，成本阈值按它折算 | `3891`（VND）；泰铢 4.5、印尼盾 2250、林吉特 0.6、比索 8.0、新币 0.18 |
| `{{成本阈值}}` / `{{ROI阈值}}` | 命中标准 | `¥70` / `2` |
| 计划清单 | 下面那张表，换成你自己的 | — |

## 前置
使用 Claude in Chrome（已登录 `seller-{{市场}}.tiktok.com`，账号 `{{店铺名}}`）。工具延迟加载时先用

## 计划清单

⚠️ 下面是**示例数据，换成你自己的**。ID 怎么拿：进 GMV Max 列表，点开任一计划的抽屉，
地址栏 `campaign_id=` 后面那串就是；商品 ID 在抽屉里的商品卡片上。

商品 GMV Max（campaign_id / product_id）：
1. 计划A-主推品 : 1800000000000001 / 1000000000000000001
2. 计划B : 1800000000000002 / 1000000000000000002
3. 计划C : 1800000000000003 / 1000000000000000003
4. 计划D-单品 : 1800000000000004 / 1000000000000000004
5. 计划E : 1800000000000005 / 1000000000000000005
6. 计划G-单品 : 1800000000000006 / 1000000000000000007
直播 GMV Max（campaign_id）：
7. 直播计划1 : 1800000000000007
（要加第二个直播计划，去直播 GMV Max 列表读它的 campaign_id 后补一行。）

## 执行步骤
### A. 抓商品模板并扫描
1. navigate 到任一商品计划抽屉，等 6 秒：
   https://seller-{{市场}}.tiktok.com/ads-creation/dashboard?origin=SC_ads_tab_button_PC&type=product&mpa=1&campaign_id=<你的商品计划ID>&product_id=<对应商品ID>&activated_tab_id=1&shop_region={{市场大写}}
2. 注入拦截器（下方），再把日期输入框改成「当天-当天」强制重发（因页面默认可能已是7天窗口、值不变不会触发；务必改成和当前不同的值），等 3 秒确认 `window.__caps` 捕获到含 spu_id_list 的模板。
3. 用商品模板对 6 个商品计划跑「当天」；若 RUN_7D 再跑一次「近7天」。

### B. 抓直播模板并扫描
4. navigate 到直播计划抽屉，等 6 秒：
   https://seller-{{市场}}.tiktok.com/ads-creation/dashboard?origin=SC_ads_tab_button_PC&type=live&mpa=1&campaign_id=<你的直播计划ID>&activated_tab_id=1&shop_region={{市场大写}}
5. 重新注入拦截器（导航后拦截器会丢失），改日期强制重发，捕获直播模板（含 external_type_list）。
6. 用直播模板对直播计划跑「当天」；若 RUN_7D 再跑一次「近7天」。

拦截器（每次导航后都要重注一次）：
```
window.__caps=[];
(function(){const of=window.fetch;window.fetch=function(...a){const u=(a[0]&&a[0].url)||a[0];const o=a[1]||{};if(/post_creative_list/.test(''+u)&&o.body)window.__caps.push({url:''+u,headers:o.headers,body:o.body});return of.apply(this,a);};
 const oo=XMLHttpRequest.prototype.open,os=XMLHttpRequest.prototype.send;XMLHttpRequest.prototype.open=function(m,u){this.__u=u;this.__h={};const s=this.setRequestHeader;this.setRequestHeader=function(k,v){this.__h[k]=v;return s.apply(this,arguments);};return oo.apply(this,arguments);};XMLHttpRequest.prototype.send=function(b){if(/post_creative_list/.test(''+this.__u)&&b)window.__caps.push({url:''+this.__u,headers:this.__h,body:b});return os.apply(this,arguments);};})();'on';
```
改日期强制重发（把 START/END 换成对应窗口，同一维度抓模板即可，重放时会再覆盖）：
```
(function(){const sv=(el,v)=>{const st=Object.getOwnPropertyDescriptor(Object.getPrototypeOf(el),'value').set;st.call(el,v);el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));};
 const ins=[...document.querySelectorAll('input')].filter(i=>/\d{4}-\d{2}-\d{2}/.test(i.value||''));
 ins.forEach(i=>{sv(i,i.placeholder==='开始日期'?'START':'END');i.dispatchEvent(new KeyboardEvent('keydown',{bubbles:true,key:'Enter',keyCode:13}));i.dispatchEvent(new Event('blur',{bubbles:true}));});})();'set';
```
重放+扫描（PROD 版用 spu_id_list + onsite_mixed_real_roi2_shopping；LIVE 版去掉 spu_id_list、ROI 用 lod_shop_direct_onsite_mixed_real_shopping_roas）。核心 scan 逻辑：逐 campaign 翻页，`b.start_time`/`b.end_time` 按维度设，`page_size=50`、`order_field='mixed_real_cost'`、`order_type=1`；过滤 item_id!=='-1' 且 shop_content_type!=='product_card'；¥=mixed_real_cost/3891；按 item_id 去重；命中 ¥>70 && ROI<2。结果存 window.__OUT。因异步 fetch 无法直接返回，async 跑完写 window.__OUT，之后每隔约5秒轮询 `JSON.stringify(window.__OUT)` 直到非 'run'。
- **翻页停止条件（分商品/直播）**：
  - 商品接口按成本**降序返回**，可用「本页末行 ¥≤70 或已到 page_count」提前停，通常 page1（50行）即够。
  - 直播接口**不保证按成本排序**（实测乱序），**不能用末行≤70 提前停**；必须翻完该 campaign 的全部 page_count 页（直播单计划总量约数百行，可控），再筛命中。

## 汇总与产出
- 汇总字段：广告类型(商品/直播) / 广告计划 / 达人账号 / 素材ID(item_id) / 成本(¥) / ROI。
- 用 openpyxl 生成 1 个 xlsx 到 outputs：`KANS_高成本低ROI素材预警_<YYYYMMDD_HHMM>.xlsx`。
  - Sheet「当天_<YYYYMMDD>」：当天维度全部命中（商品+直播），按成本降序，ROI<1 行浅红底。
  - 若 RUN_7D，再加 Sheet「近7天_<YYYYMMDD>」：近7天维度全部命中，同格式。
  - sheet 名务必标注清楚是「当天」还是「近7天」。
- 产出条件：
  - 【当天有命中 或 近7天有命中】→ 生成 xlsx，用 present_files 展示，结束语按维度列出命中条数+最烧钱的几条，提示可去 TikTok 商家中心暂停或降预算。
  - 【全部无命中】→ 不产出文件，结束语一行：「✅ 本次(<时间>)无高成本低ROI素材（当天<，近7天视情况>）」。

## 排障
- 模板抓不到（__caps 为空）：多为日期值没变没触发；把日期改成明显不同的值再试，或刷新页面重来。
- 某计划 code:2「参数无效」：page_size>50 或商品缺 spu_id_list、直播缺 external_type_list；照模板结构补齐。
- 直播命中恒为空但明知有高耗素材：几乎一定是错用了「末行≤70 提前停」——直播乱序，务必翻完全部页。
- 金额一律用 JSON 原始 `mixed_real_cost`/3891，不读页面显示文字（会被货币插件影响）。
- 阈值 ¥70≈US$10；近7天累计口径下命中偏多属正常。

## 注意
- 只读取、只产出预警，绝不对广告做暂停/改预算等写操作。
- 全程 1 个标签页，用完关闭。
- 计划清单/汇率(3891)如有变动，改本文件即可，全组同步生效。
