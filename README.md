# 小黑字

独立开源字体项目。本仓库当前产品是 **小黑字等宽**（英文字族 `Xiaoheizi Mono`）。

西文取 [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono)，汉字与地区字形取 [更纱黑体](https://github.com/be5invis/Sarasa-Gothic) / 思源黑体一系，带圈字母数字（`U+2460–24FF`）直接取 [思源黑体 SC Regular](https://github.com/adobe-fonts/source-han-sans)（规范 §2 例外表，按 1 em 覆盖半格稿）。彩色 emoji 另出两套配套字体，均收到与汉字同宽：一套取 [Noto Emoji](https://github.com/googlefonts/noto-emoji) COLRv1，一套取微软 [Fluent UI Emoji](https://github.com/microsoft/fluentui-emoji) Color 画风（Fluent 缺的国旗用 Noto 补入）。制作脚本开源。等宽本体与 Noto 衍生为 SIL OFL 1.1；Fluent 画作为 MIT。

| 名称 | 用途 |
|------|------|
| 小黑字 | 品牌 / 字厂名 |
| 小黑字等宽 | 中英等宽本体 |
| `Xiaoheizi Mono` | 等宽本体的 CSS 族名 |
| 小黑字表情 | 彩色 emoji，扁、色块（上游 Noto；族名不写厂商） |
| `Xiaoheizi Emoji` | 扁平配套的 CSS 族名 |
| 小黑字表情立体 | 彩色 emoji，立体画风（上游 Fluent；族名不写厂商） |
| `Xiaoheizi Emoji 3D` | 立体配套的 CSS 族名 |

衍生字体不使用上游保留名或商标：`Source`、`JetBrains`、`Sarasa`、`更纱`、`Iosevka`、`Noto`、`Fluent`、`Microsoft`、`微软`、`MS`、`Google`、`谷歌`。

## 文档

| 文件 | 内容 |
|------|------|
| [计划.md](./计划.md) | 阶段、出口条件、状态 |
| [docs/规范.md](./docs/规范.md) | Unicode、格子宽、覆盖统计表 |
| [preview/preview.html](./preview/preview.html) | 预览页模板（覆盖数字不写在此文件） |

远程仓库：<https://github.com/xiaoheizi-font/xiaoheizi-mono>

## 预览构建

上游放在 `vendor/`（不入库）。本地可先拉上游再构建：

```powershell
python scripts/fetch-vendor.py
python scripts/build.py
```

用浏览器打开 `dist/preview.html`（请刷新）。页面模板在 `preview/preview.html`，覆盖率与字符图鉴由同目录的 `coverage.js` 填入。Markdown 覆盖表在 `dist/coverage-blocks.md`。网页嵌入请用 `dist/Xiaoheizi*-Regular.woff2`（TTF 仍可用于安装）。

## GitHub 自动发布

推送到 `main` 后，[`.github/workflows/publish.yml`](.github/workflows/publish.yml) 会：

1. 拉取 `vendor/` 上游并构建字体。
2. 把预览子集发到 GitHub Pages（不含完整产品字体）。
3. 在该提交上打 tag `v0.1.0-preview.<序号>`，并创建 GitHub Release（完整 TTF + WOFF2 + 许可证 + 覆盖表）。

首次使用前，在远程仓打开 **Settings → Pages → Source → GitHub Actions**。提交说明含 `[skip release]` 时不打 tag。也可在 Actions 里手动跑「发布」。预览地址形如 `https://xiaoheizi-font.github.io/xiaoheizi-mono/`。

