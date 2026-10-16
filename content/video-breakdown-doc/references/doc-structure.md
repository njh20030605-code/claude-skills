# 文档结构与 XML 写法（只写拆解部分）

默认只产出下面这两大节。官方标准、四段拆解框架、数据诊断、爆款复制闭环、拆解卡模板这类「大方向」
**不写**，除非用户明确要。往已有文档里加时，用 `block_insert_after` 接在用户指定位置之后。

```
N. <品牌>爆款拆解（k 条）
   callout：一句话（必须由核对文件统计得出，比如「11 条里 9 条以价格和赠品为主线」）
   N.1 数据 Benchmark（Top 20）        ← 有投放数据才写
   N.2 结构母版                         ← 画板
   N.3 前三秒钩子                       ← 画板 + 开头切片 + 金句公式表 + 中段金句
   N.4 完整样片                         ← 2～4 条代表样片 + 一句说明
   N.5 可以直接复用的做法               ← 列表
   N.6 逐条拆解                         ← 说明 + 5 列大表（build_table.py 生成）
N+1. 案例库
   N+1.k 案例 k：<素材名>               ← 重点案例（用户点名的，或数据最典型的）
```

## 通用约定

- 引号：「」只放原话或屏幕文字；“”放概括和观众心理。逐条拆解表上方放一句灰字说明。
- 人名、AI 标注、产品名都以核对文件为准；素材名里不写画面没标注的人名。
- 灰色说明文字：`<p><span text-color="gray">……</span></p>`
- 不写评论类文字：低质规则冲突、「慎用」、「⚠ 易判演戏炒作」、面试提示、「我会改」（改写成「优化方向」）。

## 各节 XML

**一句话 callout**
```xml
<h1 seq="auto">韩束爆款拆解（11 条）</h1>
<callout emoji="🔑" background-color="light-yellow" border-color="yellow"><p><b>一句话：</b>……</p></callout>
```

**画板**（SVG 文件放在执行 lark-cli 的目录下）
```xml
<whiteboard type="svg" path="@./structure.svg"></whiteboard>
```
结构母版和钩子地图参考 `assets/structure_example.svg`、`assets/hooks_example.svg`：复制后按本批核对结果改文字。
结构母版每格约 8 个字、钩子地图每格约 14 个字一行，放不下的长原话改成不带引号的描述，或换一句短原话；
中段才出现的句子标秒数（「第 8 秒：「……」」）。改完用 Chrome 无头模式出 PNG 自查：
`"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --window-size=1110,620 --screenshot=out.png "file://$PWD/x.svg"`

**开头切片**（两列一排，每段截到第一句话说完，3～10 秒）
```bash
ffmpeg -v error -y -ss 0 -t <秒> -i 原片.mp4 -vf scale=540:-2 -c:v libx264 -crf 30 -c:a aac -b:a 64k -movflags +faststart clips/开头01-反常识断言.mp4
```
```xml
<p><b>开头切片：</b>每段截到第一句话说完（3～10 秒），对照上图看画面和台词怎么同时出现。</p>
<grid>
  <column width-ratio="0.5"><p><b>反常识断言</b>：「如果你的水乳用完了，那 26 年就不要再买了」</p><figure view-type="Preview"><source path="@./clips/开头01-反常识断言.mp4" name="开头01-反常识断言.mp4"/></figure></column>
  <column width-ratio="0.5">……</column>
</grid>
```

**金句公式表**
```xml
<p><b>金句公式：</b>把原句里的产品和场景换掉，就能直接写新开头。</p>
<table><colgroup><col width="130"/><col width="320"/><col width="250"/></colgroup>
<thead><tr><th background-color="light-gray"><p>类型</p></th><th background-color="light-gray"><p>原句</p></th><th background-color="light-gray"><p>套用公式</p></th></tr></thead>
<tbody><tr><td><p><b>价格漏洞</b></p></td><td><p>「老公你现在赶紧打开抖音，我们运营直播间挂错链接了」</p></td><td><p>[谁] 你赶紧打开抖音，[直播间] 把 X 挂成 Y 了</p></td></tr></tbody></table>
<p><b>中段金句，也能挪到开头用：</b>「……」「……」。</p>
```

**完整样片**
```xml
<p><b>样片 1：闪充棒 99「一支回春」</b>：先说「网上说它是一支回春」，用三位女生……</p>
<figure view-type="Preview"><source path="@./v/11-闪充棒99一支回春.mp4" name="11-闪充棒99一支回春.mp4"/></figure>
```

**可以直接复用的做法**：`<ul><li><b>表达方式：</b>……</li>…</ul>`，每条要能在视频里找到例子，
「全部素材都……」这种全称判断要对照所有核对文件确认，不成立就改成「多数」或举具体素材。

**逐条拆解**：
```bash
python3 scripts/build_table.py scripts.json rows.json t66.xml
```
上方加说明：`<p><span text-color="gray">说明：「」里是视频原话，以屏幕字幕为准，没有字幕的段落据口播转写；“”里是概括或观众心理。人物只写画面上标注了名字的，或口播里点了名的。</span></p>`

**案例**（每个案例四块）
```xml
<h2 seq="auto">案例 1：闪充棒 99「一支回春」</h2>
<p><b>一句话：</b>……</p>
<figure view-type="Preview"><source path="@./v/11-闪充棒99一支回春.mp4" name="11-闪充棒99一支回春.mp4"/></figure>
<p><b>数据</b>（2026-01-01 至 2026-10-14，口径同 N.1）</p>
<table>指标 | 本条 | Top 20 中位数（P25～P75）</table>          ← 对外版改成「指标 | 在 Top 20 中的位置」
<p><b>拆解卡</b></p>
<table>模块 | 拆解：产品与机制 / 停下来（0～x 秒）/ 看下去 / 相信它 / 现在买 / 可复制的做法 / 优化方向 [/ 迁移到别的品类]</table>
<p><b>逐段拆解</b>（画面和原话逐秒核对过；「」里是原话，“”里是概括或观众心理）</p>
<table>时间 | 画面 | 原话（字幕） | 这一段对用户在做什么</table>   ← 直接用核对文件的「逐段时间轴」
```

## 飞书命令与坑

- 个人飞书：`lark-cli --profile personal docs ... --as user`；公司飞书默认 profile，新文档放团队约定的产出文件夹（传它的 folderToken）。
- 新建：`lark-cli docs +create --as user --doc-format xml --content "@./doc.xml"`（XML 开头写 `<title>…</title>`）。
- 插入：`docs +update --command block_insert_after --block-id <锚点> --doc-format xml --content "@./x.xml"`。
- 先校验：`docs +script --command parse --content "@./x.xml" --format json`，看 `assessment.status == passed`。
- 改单块：`block_replace --block-id`；改一段：`--start-block-id/--end-block-id`，区间里有不带 ID 的 `ul/ol` 会报 1002，改成逐块操作（列表项 `li` 有 ID）。
- 多个写操作**按顺序一条一条跑**，并发会互相覆盖、偶发失败；失败的重试一次再看报错。
- 视频：本地文件用 `<source path="@./…"/>`；文档里已有的附件可以用 `<source token="…" name="…"/>` 直接复用，不用重传。
- 表格单元格里可以放视频：`block_insert_after` 锚在格内段落 ID 上，或整表重建。
- 整篇复制：`lark-cli --profile personal api POST /open-apis/drive/v1/files/<docToken>/copy --as user --data '{"name":"…","type":"docx","folder_token":"<根目录 token>"}'`；根目录 token 用 `GET /open-apis/drive/explorer/v2/root_folder/meta` 拿。
- 公开：`api PATCH /open-apis/drive/v2/permissions/<token>/public --params '{"type":"docx"}' --data '{"external_access_entity":"open","link_share_entity":"anyone_readable"}'`，再 GET 一次确认。
- 检查显示：画板 `whiteboard +export --whiteboard-token <t> --output-type preview --output ./x.jpg`；
  公开文档可以用内置浏览器（未登录）打开看；用户的 Chrome 可能登录的是公司飞书，打不开个人版文档，**不要点「切换账号」**。
