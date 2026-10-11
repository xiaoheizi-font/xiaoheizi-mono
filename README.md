# 小黑字🐓🏀

独立开源字体项目。本仓库当前产品是 **小黑字等宽**（英文字族 `Xiaoheizi Mono`）。

西文取 [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono)，汉字与地区字形取 [更纱黑体](https://github.com/be5invis/Sarasa-Gothic) / 思源黑体一系，带圈字母数字（`U+2460–24FF`）直接取 [思源黑体 SC Regular](https://github.com/adobe-fonts/source-han-sans)（规范 §2 例外表，按 1 em 覆盖半格稿）。彩色 emoji 另出两套配套字体，均收到与汉字同宽：一套取 [Noto Emoji](https://github.com/googlefonts/noto-emoji) COLRv1，一套取微软 [Fluent UI Emoji](https://github.com/microsoft/fluentui-emoji) Color 画风（Fluent 缺的国旗用 Noto 补入）。

| 名称 | 用途 |
|------|------|
| 小黑字 | 品牌 / 字厂名 |
| 小黑字等宽 | 中英等宽本体 |
| `Xiaoheizi Mono` | 等宽本体的 CSS 族名 |
| 小黑字表情 | 彩色 emoji，扁、色块（谷歌 Noto 风格） |
| `Xiaoheizi Emoji` | 扁平配套的 CSS 族名 |
| 小黑字表情立体 | 彩色 emoji，立体画风（微软 Fluent 风格） |
| `Xiaoheizi Emoji 3D` | 立体配套的 CSS 族名 |


## 捐赠

**本人强烈谴责恶劣的A股市场环境**：作者因买入股【华铁股份】现【R通达1】不完全统计**家庭总计亏损高达200万人民币以上**。目前正在起诉，进入二审阶段，执行更是不知要到什么时候了，能执行回来多少钱更不知道，这已经是第三、四年了，其余股票也亏损严重，现金流状况至今难以缓解。

故在此赛博要饭接受捐赠，谢谢。

| 微信赞赏码 | 支付宝领红包 | 支付宝 |
| --- | --- | --- |
| ![微信赞赏码](https://cdn.jsdelivr.net/gh/gaoyia/gaoyia@v0.0.2/donate.jpg) | ![支付宝领红包](https://cdn.jsdelivr.net/gh/gaoyia/gaoyia@v0.0.2/zfbhb.jpg) | ![支付宝](https://cdn.jsdelivr.net/gh/gaoyia/gaoyia@v0.0.2/zfb.jpg) |

## 文档

| 文件 | 内容 |
|------|------|
| [计划.md](./计划.md) | 阶段、出口条件、状态 |
| [docs/规范.md](./docs/规范.md) | Unicode、格子宽、覆盖统计表 |
| [site/index.html](./site/index.html) | 首页：下载与仓库入口 |
| [preview/preview.html](./preview/preview.html) | 字符测试页模板（覆盖数字不写在此文件） |

远程仓库：<https://github.com/xiaoheizi-font/xiaoheizi-mono>

## 预览构建

上游放在 `vendor/`（不入库）。本地可先拉上游再构建：

```powershell
python scripts/fetch-vendor.py
python scripts/build.py
```

用浏览器打开 `dist/index.html`（首页）或 `dist/preview.html`（字符测试，请刷新）。首页模板在 `site/index.html`，测试页模板在 `preview/preview.html`。覆盖率与字符图鉴由 `dist/coverage.js` 填入测试页。Markdown 覆盖表在 `dist/coverage-blocks.md`，只随 Pages 发布，不进 Release。网页嵌入请用 `dist/XiaoheiziMono-Regular.woff2`（400）或 `dist/XiaoheiziMono-Light.woff2`（300，笔画更细，格子宽与 Regular 相同），外加两套表情 WOFF2。TTF 仍可用于安装。

## 许可

字体和制作脚本按 [SIL OFL 1.1](./OFL.txt) 发布。本仓库没有 `LICENSE` 文件，也不以 MIT 发布整仓。

小黑字表情立体包含微软 Fluent 画作和 tetunori 的 TTF 合成。这两份 MIT 声明随字体一起提供，字体本身仍然只按 OFL 分发。

