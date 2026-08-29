# 小黑字等宽 · 字符覆盖（预览构建）

- Unicode 15.0.0（Python unicodedata）
- 全平面已映射 51049 / 已分配 288735 = 17.6802%
- 宽度违规 0（发布时必须为 0）

## 总览

| 项目 | 已覆盖 | 集合大小 | 覆盖率 | 验收 | 说明 |
|------|--------|----------|--------|------|------|
| 总字符数（BMP） | 46130 | 65535 | 70.39% |  | 已映射且码位 ≤ U+FFFF / 65535 |
| 增补平面 | 4919 | 224685 | 2.19% |  | 已映射且码位 ≥ U+10000 / 该版本已分配 |
| 全平面已分配 | 51049 | 288735 | 17.68% |  | mapped / 该 Unicode 版本已分配标量值 |

## CJK

| 集合 | 已覆盖 | 集合大小 | 覆盖率 | 验收 | 说明 |
|------|--------|----------|--------|------|------|
| GB/T 2312 | 6763 | 6763 | 100.00% | ✅ | 简体中文基本集 |
| Big5 L1 | 5401 | 5401 | 100.00% | ✅ | 繁体中文高频用字基本集 |
| 日文假名 | 182 | 182 | 100.00% | ✅ | 平假名与片假名 |
| 谚文音节 | 11172 | 11172 | 100.00% | ✅ | 朝鲜文 / 韩文 |

## Unicode 区段

| 区段 | 已覆盖 | 集合大小 | 覆盖率 | 验收 | 口径 |
|------|--------|----------|--------|------|------|
| 中日韩统一表意文字 | 20992 | 20992 | 100.00% | ✅ | U+4E00–9FFF |
| 中日韩符号和标点 | 64 | 64 | 100.00% | ✅ | U+3000–303F |
| 基本拉丁字母 | 95 | 95 | 100.00% | ✅ | U+0020–007E 可视 ASCII |
| 标准阿拉伯数字 | 10 | 10 | 100.00% | ✅ | U+0030–0039 |
| 通用可视标点 | 24 | 24 | 100.00% | ✅ | U+2010–2027 |
| 货币符号 | 27 | 33 | 81.82% |  | U+20A0–20CF |
| 类字符号 | 61 | 80 | 76.25% |  | U+2100–214F |
| 西里尔字母 | 256 | 256 | 100.00% | ✅ | U+0400–04FF |
| 中日韩统一表意文字扩展 A 区 | 6592 | 6592 | 100.00% | ✅ | U+3400–4DBF |
| 中日韩统一表意文字扩展 B 区 | 2109 | 42720 | 4.94% |  | U+20000–2A6DF |
| 中日韩统一表意文字扩展 C 区 | 48 | 4154 | 1.16% |  | U+2A700–2B73F |
| 中日韩统一表意文字扩展 D 区 | 34 | 222 | 15.32% |  | U+2B740–2B81F |
| 中日韩统一表意文字扩展 E 区 | 113 | 5762 | 1.96% |  | U+2B820–2CEAF |
| 中日韩统一表意文字扩展 F 区 | 6 | 7473 | 0.08% |  | U+2CEB0–2EBEF |
| 中日韩统一表意文字扩展 G 区 | 4 | 4939 | 0.08% |  | U+30000–3134F |
| 中日韩统一表意文字扩展 H 区 | 0 | 4192 | 0.00% |  | U+31350–323AF Unicode 15.0 |
| 希腊和科普特字母 | 121 | 135 | 89.63% |  | U+0370–03FF |
| 泰文 | 1 | 87 | 1.15% |  | U+0E00–0E7F |
| 拉丁文补充-1 | 96 | 128 | 75.00% |  | U+0080–00FF |
| 通用标点 | 94 | 111 | 84.68% |  | U+2000–206F |
| 箭头 | 112 | 112 | 100.00% | ✅ | U+2190–21FF |
| 杂项技术用字符 | 217 | 256 | 84.77% |  | U+2300–23FF |
| 带圈字母数字 | 160 | 160 | 100.00% | ✅ | U+2460–24FF |
| 制表符 | 128 | 128 | 100.00% | ✅ | U+2500–257F |
| 方块元素 | 32 | 32 | 100.00% | ✅ | U+2580–259F |
| 几何图形 | 96 | 96 | 100.00% | ✅ | U+25A0–25FF |
| 杂项符号 | 108 | 256 | 42.19% |  | U+2600–26FF |
| 印刷符号 | 103 | 192 | 53.65% |  | U+2700–27BF |
| 杂项符号和箭头 | 166 | 253 | 65.61% |  | U+2B00–2BFF |
| 注音符号 | 43 | 43 | 100.00% | ✅ | U+3100–312F |
| 带圈 CJK 字母和月份 | 255 | 255 | 100.00% | ✅ | U+3200–32FF |
| CJK 兼容字符 | 255 | 256 | 99.61% |  | U+3300–33FF |
| CJK 兼容表意文字 | 366 | 472 | 77.54% |  | U+F900–FAFF |
| 半角及全角形式 | 225 | 225 | 100.00% | ✅ | U+FF00–FFEF |

## Unicode 区块

| 中文名称 | 区块 | 范围 | 该版本已分配 | 已覆盖 | 覆盖率 | 验收 | 格子 | 来源 |
|----------|------|------|--------------|--------|--------|------|------|------|
| 基本拉丁字母 | Basic Latin | U+0000–007F | 128 | 96 | 75.00% |  | 混 | jetbrains-mono |
| 拉丁字母补充-1 | Latin-1 Supplement | U+0080–00FF | 128 | 96 | 75.00% |  | 混 | jetbrains-mono |
| 拉丁扩充甲 | Latin Extended-A | U+0100–017F | 128 | 128 | 100.00% | ✅ | 1 | jetbrains-mono+sarasa |
| 拉丁扩充乙 | Latin Extended-B | U+0180–024F | 208 | 208 | 100.00% | ✅ | 1 | jetbrains-mono+sarasa |
| 国际音标扩充 | IPA Extensions | U+0250–02AF | 96 | 96 | 100.00% | ✅ | 1 | sarasa |
| 有距修饰字 | Spacing Modifier Letters | U+02B0–02FF | 80 | 80 | 100.00% | ✅ | 1 | sarasa |
| 结合变音标记 | Combining Diacritical Marks | U+0300–036F | 112 | 112 | 100.00% | ✅ | 混 | sarasa |
| 希腊及科普特 | Greek and Coptic | U+0370–03FF | 135 | 121 | 89.63% |  | 1 | jetbrains-mono+sarasa |
| 西里尔 | Cyrillic | U+0400–04FF | 256 | 256 | 100.00% | ✅ | 混 | jetbrains-mono+sarasa |
| 西里尔补充 | Cyrillic Supplement | U+0500–052F | 48 | 48 | 100.00% | ✅ | 1 | sarasa |
| 亚美尼亚 | Armenian | U+0530–058F | 91 | 91 | 100.00% | ✅ | 1 | sarasa |
| 希伯来 | Hebrew | U+0590–05FF | 88 | 0 | 0.00% |  | — | — |
| 阿拉伯 | Arabic | U+0600–06FF | 256 | 0 | 0.00% |  | — | — |
| 叙利亚 | Syriac | U+0700–074F | 77 | 0 | 0.00% |  | — | — |
| 阿拉伯补充 | Arabic Supplement | U+0750–077F | 48 | 0 | 0.00% |  | — | — |
| 塔纳 | Thaana | U+0780–07BF | 50 | 0 | 0.00% |  | — | — |
| 西非书面文字 | NKo | U+07C0–07FF | 62 | 0 | 0.00% |  | — | — |
| 撒马利亚 | Samaritan | U+0800–083F | 61 | 0 | 0.00% |  | — | — |
| 曼德恩 | Mandaic | U+0840–085F | 29 | 0 | 0.00% |  | — | — |
| 叙利亚补充 | Syriac Supplement | U+0860–086F | 11 | 0 | 0.00% |  | — | — |
| 阿拉伯扩充乙 | Arabic Extended-B | U+0870–089F | 41 | 0 | 0.00% |  | — | — |
| 阿拉伯扩充甲 | Arabic Extended-A | U+08A0–08FF | 96 | 0 | 0.00% |  | — | — |
| 天城体 | Devanagari | U+0900–097F | 128 | 0 | 0.00% |  | — | — |
| 孟加拉 | Bengali | U+0980–09FF | 96 | 0 | 0.00% |  | — | — |
| 果鲁穆奇 | Gurmukhi | U+0A00–0A7F | 80 | 0 | 0.00% |  | — | — |
| 古吉拉特 | Gujarati | U+0A80–0AFF | 91 | 0 | 0.00% |  | — | — |
| 奥里亚 | Oriya | U+0B00–0B7F | 91 | 0 | 0.00% |  | — | — |
| 泰米尔 | Tamil | U+0B80–0BFF | 72 | 0 | 0.00% |  | — | — |
| 泰卢固 | Telugu | U+0C00–0C7F | 100 | 0 | 0.00% |  | — | — |
| 卡纳达 | Kannada | U+0C80–0CFF | 91 | 0 | 0.00% |  | — | — |
| 马拉雅拉姆 | Malayalam | U+0D00–0D7F | 118 | 0 | 0.00% |  | — | — |
| 僧伽罗 | Sinhala | U+0D80–0DFF | 91 | 0 | 0.00% |  | — | — |
| 泰文 | Thai | U+0E00–0E7F | 87 | 1 | 1.15% |  | 1 | sarasa |
| 老挝 | Lao | U+0E80–0EFF | 83 | 0 | 0.00% |  | — | — |
| 藏文 | Tibetan | U+0F00–0FFF | 211 | 0 | 0.00% |  | — | — |
| 缅文 | Myanmar | U+1000–109F | 160 | 0 | 0.00% |  | — | — |
| 格鲁吉亚 | Georgian | U+10A0–10FF | 88 | 1 | 1.14% |  | 1 | sarasa |
| 谚文字母 | Hangul Jamo | U+1100–11FF | 256 | 256 | 100.00% | ✅ | 混 | sarasa |
| 埃塞 | Ethiopic | U+1200–137F | 358 | 0 | 0.00% |  | — | — |
| 埃塞补充 | Ethiopic Supplement | U+1380–139F | 26 | 0 | 0.00% |  | — | — |
| 切罗基 | Cherokee | U+13A0–13FF | 92 | 0 | 0.00% |  | — | — |
| 统一加拿大土著音节 | Unified Canadian Aboriginal Syllabics | U+1400–167F | 640 | 0 | 0.00% |  | — | — |
| 欧甘 | Ogham | U+1680–169F | 29 | 0 | 0.00% |  | — | — |
| 卢恩 | Runic | U+16A0–16FF | 89 | 0 | 0.00% |  | — | — |
| 他加禄 | Tagalog | U+1700–171F | 23 | 0 | 0.00% |  | — | — |
| 哈努努奥 | Hanunoo | U+1720–173F | 23 | 0 | 0.00% |  | — | — |
| 布希德 | Buhid | U+1740–175F | 20 | 0 | 0.00% |  | — | — |
| 蒂亚格班瓦 | Tagbanwa | U+1760–177F | 18 | 0 | 0.00% |  | — | — |
| 高棉 | Khmer | U+1780–17FF | 114 | 0 | 0.00% |  | — | — |
| 蒙文 | Mongolian | U+1800–18AF | 158 | 0 | 0.00% |  | — | — |
| 统一加拿大土著音节扩充 | Unified Canadian Aboriginal Syllabics Extended | U+18B0–18FF | 70 | 0 | 0.00% |  | — | — |
| 林布 | Limbu | U+1900–194F | 68 | 0 | 0.00% |  | — | — |
| 傣㐻 | Tai Le | U+1950–197F | 35 | 0 | 0.00% |  | — | — |
| 新傣仂 | New Tai Lue | U+1980–19DF | 83 | 0 | 0.00% |  | — | — |
| 高棉符号 | Khmer Symbols | U+19E0–19FF | 32 | 0 | 0.00% |  | — | — |
| 布吉 | Buginese | U+1A00–1A1F | 30 | 0 | 0.00% |  | — | — |
| 傣昙 | Tai Tham | U+1A20–1AAF | 127 | 0 | 0.00% |  | — | — |
| 结合变音标记扩充 | Combining Diacritical Marks Extended | U+1AB0–1AFF | 31 | 27 | 87.10% |  | 混 | sarasa |
| 巴厘 | Balinese | U+1B00–1B7F | 124 | 0 | 0.00% |  | — | — |
| 巽他 | Sundanese | U+1B80–1BBF | 64 | 0 | 0.00% |  | — | — |
| 巴塔克 | Batak | U+1BC0–1BFF | 56 | 0 | 0.00% |  | — | — |
| 雷布查 | Lepcha | U+1C00–1C4F | 74 | 0 | 0.00% |  | — | — |
| 奥尔奇基 | Ol Chiki | U+1C50–1C7F | 48 | 0 | 0.00% |  | — | — |
| 西里尔扩充丙 | Cyrillic Extended-C | U+1C80–1C8F | 9 | 9 | 100.00% | ✅ | 1 | sarasa |
| 格鲁吉亚扩充 | Georgian Extended | U+1C90–1CBF | 46 | 0 | 0.00% |  | — | — |
| 巽他补充 | Sundanese Supplement | U+1CC0–1CCF | 8 | 0 | 0.00% |  | — | — |
| 吠陀扩充 | Vedic Extensions | U+1CD0–1CFF | 43 | 0 | 0.00% |  | — | — |
| 音标扩充 | Phonetic Extensions | U+1D00–1D7F | 128 | 128 | 100.00% | ✅ | 1 | sarasa |
| 音标扩充增补 | Phonetic Extensions Supplement | U+1D80–1DBF | 64 | 64 | 100.00% | ✅ | 1 | sarasa |
| 结合变音标记补充 | Combining Diacritical Marks Supplement | U+1DC0–1DFF | 64 | 55 | 85.94% |  | 混 | sarasa |
| 拉丁扩充追加 | Latin Extended Additional | U+1E00–1EFF | 256 | 256 | 100.00% | ✅ | 1 | sarasa |
| 希腊扩充 | Greek Extended | U+1F00–1FFF | 233 | 233 | 100.00% | ✅ | 1 | sarasa |
| 通用标点 | General Punctuation | U+2000–206F | 111 | 94 | 84.68% |  | 混 | jetbrains-mono+sarasa |
| 上标及下标 | Superscripts and Subscripts | U+2070–209F | 42 | 42 | 100.00% | ✅ | 1 | sarasa |
| 货币符号 | Currency Symbols | U+20A0–20CF | 33 | 27 | 81.82% |  | 1 | sarasa |
| 结合变音记号 | Combining Diacritical Marks for Symbols | U+20D0–20FF | 33 | 21 | 63.64% |  | 混 | sarasa |
| 类字符号 | Letterlike Symbols | U+2100–214F | 80 | 61 | 76.25% |  | 1 | sarasa |
| 数字形式 | Number Forms | U+2150–218F | 60 | 60 | 100.00% | ✅ | 1 | sarasa |
| 箭头 | Arrows | U+2190–21FF | 112 | 112 | 100.00% | ✅ | 1 | jetbrains-mono+sarasa |
| 数学运算符 | Mathematical Operators | U+2200–22FF | 256 | 256 | 100.00% | ✅ | 1 | sarasa |
| 杂项技术用字符 | Miscellaneous Technical | U+2300–23FF | 256 | 217 | 84.77% |  | 混 | sarasa+source-han-sans |
| 控制图符 | Control Pictures | U+2400–243F | 39 | 39 | 100.00% | ✅ | 1 | sarasa |
| 光学字符识别 | Optical Character Recognition | U+2440–245F | 11 | 6 | 54.55% |  | 1 | sarasa |
| 带圈字母数字 | Enclosed Alphanumerics | U+2460–24FF | 160 | 160 | 100.00% | ✅ | 2 | source-han-sans |
| 制表符 | Box Drawing | U+2500–257F | 128 | 128 | 100.00% | ✅ | 1 | jetbrains-mono |
| 方块元素 | Block Elements | U+2580–259F | 32 | 32 | 100.00% | ✅ | 1 | jetbrains-mono |
| 几何图形 | Geometric Shapes | U+25A0–25FF | 96 | 96 | 100.00% | ✅ | 混 | sarasa+source-han-sans |
| 杂项符号 | Miscellaneous Symbols | U+2600–26FF | 256 | 108 | 42.19% |  | 混 | sarasa+source-han-sans |
| 印刷符号 | Dingbats | U+2700–27BF | 192 | 103 | 53.65% |  | 混 | sarasa+source-han-sans |
| 各式数学符号甲 | Miscellaneous Mathematical Symbols-A | U+27C0–27EF | 48 | 26 | 54.17% |  | 1 | sarasa |
| 增补箭头甲 | Supplemental Arrows-A | U+27F0–27FF | 16 | 5 | 31.25% |  | 1 | sarasa |
| 布莱叶盲文点字 | Braille Patterns | U+2800–28FF | 256 | 256 | 100.00% | ✅ | 1 | sarasa |
| 增补箭头乙 | Supplemental Arrows-B | U+2900–297F | 128 | 76 | 59.38% |  | 1 | sarasa |
| 各式数学符号乙 | Miscellaneous Mathematical Symbols-B | U+2980–29FF | 128 | 68 | 53.12% |  | 1 | sarasa |
| 增补数学运算符 | Supplemental Mathematical Operators | U+2A00–2AFF | 256 | 151 | 58.98% |  | 1 | sarasa |
| 杂项符号和箭头 | Miscellaneous Symbols and Arrows | U+2B00–2BFF | 253 | 166 | 65.61% |  | 1 | sarasa |
| 格拉哥里 | Glagolitic | U+2C00–2C5F | 96 | 0 | 0.00% |  | — | — |
| 拉丁扩充丙 | Latin Extended-C | U+2C60–2C7F | 32 | 32 | 100.00% | ✅ | 1 | sarasa |
| 科普特 | Coptic | U+2C80–2CFF | 123 | 0 | 0.00% |  | — | — |
| 格鲁吉亚补充 | Georgian Supplement | U+2D00–2D2F | 40 | 0 | 0.00% |  | — | — |
| 提非纳 | Tifinagh | U+2D30–2D7F | 59 | 0 | 0.00% |  | — | — |
| 埃塞扩充 | Ethiopic Extended | U+2D80–2DDF | 79 | 0 | 0.00% |  | — | — |
| 西里尔扩充甲 | Cyrillic Extended-A | U+2DE0–2DFF | 32 | 32 | 100.00% | ✅ | 混 | sarasa |
| 增补标点 | Supplemental Punctuation | U+2E00–2E7F | 94 | 58 | 61.70% |  | 混 | sarasa |
| 中日韩部首补充 | CJK Radicals Supplement | U+2E80–2EFF | 115 | 115 | 100.00% | ✅ | 2 | sarasa |
| 康熙部首 | Kangxi Radicals | U+2F00–2FDF | 214 | 214 | 100.00% | ✅ | 2 | sarasa |
| 表意描述字符 | Ideographic Description Characters | U+2FF0–2FFF | 12 | 12 | 100.00% | ✅ | 2 | sarasa |
| 中日韩符号和标点 | CJK Symbols and Punctuation | U+3000–303F | 64 | 64 | 100.00% | ✅ | 混 | sarasa |
| 平假名 | Hiragana | U+3040–309F | 93 | 93 | 100.00% | ✅ | 混 | sarasa |
| 片假名 | Katakana | U+30A0–30FF | 96 | 96 | 100.00% | ✅ | 2 | sarasa |
| 注音符号 | Bopomofo | U+3100–312F | 43 | 43 | 100.00% | ✅ | 2 | sarasa |
| 谚文兼容字母 | Hangul Compatibility Jamo | U+3130–318F | 94 | 94 | 100.00% | ✅ | 2 | sarasa |
| 汉文训读 | Kanbun | U+3190–319F | 16 | 16 | 100.00% | ✅ | 2 | sarasa |
| 注音扩充 | Bopomofo Extended | U+31A0–31BF | 32 | 32 | 100.00% | ✅ | 2 | sarasa |
| 中日韩笔画 | CJK Strokes | U+31C0–31EF | 36 | 36 | 100.00% | ✅ | 2 | sarasa |
| 片假名音标扩充 | Katakana Phonetic Extensions | U+31F0–31FF | 16 | 16 | 100.00% | ✅ | 2 | sarasa |
| 带圈中日韩字母和月份 | Enclosed CJK Letters and Months | U+3200–32FF | 255 | 255 | 100.00% | ✅ | 混 | sarasa |
| 中日韩兼容字符 | CJK Compatibility | U+3300–33FF | 256 | 255 | 99.61% |  | 2 | sarasa |
| 中日韩统一表意文字扩展区A | CJK Unified Ideographs Extension A | U+3400–4DBF | 6592 | 6592 | 100.00% | ✅ | 2 | sarasa |
| 易经六十四卦 | Yijing Hexagram Symbols | U+4DC0–4DFF | 64 | 64 | 100.00% | ✅ | 1 | sarasa |
| 中日韩统一表意文字 | CJK Unified Ideographs | U+4E00–9FFF | 20992 | 20992 | 100.00% | ✅ | 2 | sarasa |
| 彝文音节 | Yi Syllables | U+A000–A48F | 1165 | 0 | 0.00% |  | — | — |
| 彝文部首 | Yi Radicals | U+A490–A4CF | 55 | 0 | 0.00% |  | — | — |
| 傈僳(老) | Lisu | U+A4D0–A4FF | 48 | 0 | 0.00% |  | — | — |
| 瓦伊 | Vai | U+A500–A63F | 300 | 0 | 0.00% |  | — | — |
| 西里尔扩充乙 | Cyrillic Extended-B | U+A640–A69F | 96 | 96 | 100.00% | ✅ | 混 | sarasa |
| 巴默姆 | Bamum | U+A6A0–A6FF | 88 | 0 | 0.00% |  | — | — |
| 声调修饰字 | Modifier Tone Letters | U+A700–A71F | 32 | 32 | 100.00% | ✅ | 1 | sarasa |
| 拉丁扩充丁 | Latin Extended-D | U+A720–A7FF | 193 | 138 | 71.50% |  | 1 | sarasa |
| 西洛蒂城体 | Syloti Nagri | U+A800–A82F | 45 | 0 | 0.00% |  | — | — |
| 通用印度数字形式 | Common Indic Number Forms | U+A830–A83F | 10 | 0 | 0.00% |  | — | — |
| 八思巴 | Phags-pa | U+A840–A87F | 56 | 0 | 0.00% |  | — | — |
| 索拉什特拉 | Saurashtra | U+A880–A8DF | 82 | 0 | 0.00% |  | — | — |
| 天城体扩充 | Devanagari Extended | U+A8E0–A8FF | 32 | 0 | 0.00% |  | — | — |
| 克耶利 | Kayah Li | U+A900–A92F | 48 | 1 | 2.08% |  | 1 | sarasa |
| 雷姜 | Rejang | U+A930–A95F | 37 | 0 | 0.00% |  | — | — |
| 谚文字母扩充甲 | Hangul Jamo Extended-A | U+A960–A97F | 29 | 29 | 100.00% | ✅ | 2 | sarasa |
| 爪哇 | Javanese | U+A980–A9DF | 91 | 0 | 0.00% |  | — | — |
| 缅文扩充乙 | Myanmar Extended-B | U+A9E0–A9FF | 31 | 0 | 0.00% |  | — | — |
| 占文 | Cham | U+AA00–AA5F | 83 | 0 | 0.00% |  | — | — |
| 缅文扩充甲 | Myanmar Extended-A | U+AA60–AA7F | 32 | 0 | 0.00% |  | — | — |
| 傣越 | Tai Viet | U+AA80–AADF | 72 | 0 | 0.00% |  | — | — |
| 米代文扩充 | Meetei Mayek Extensions | U+AAE0–AAFF | 23 | 0 | 0.00% |  | — | — |
| 埃塞扩充甲 | Ethiopic Extended-A | U+AB00–AB2F | 32 | 0 | 0.00% |  | — | — |
| 拉丁扩充戊 | Latin Extended-E | U+AB30–AB6F | 60 | 48 | 80.00% |  | 1 | sarasa |
| 切罗基补充 | Cherokee Supplement | U+AB70–ABBF | 80 | 0 | 0.00% |  | — | — |
| 米代文 | Meetei Mayek | U+ABC0–ABFF | 56 | 0 | 0.00% |  | — | — |
| 谚文音节 | Hangul Syllables | U+AC00–D7AF | 11172 | 11172 | 100.00% | ✅ | 2 | sarasa |
| 谚文字母扩充乙 | Hangul Jamo Extended-B | U+D7B0–D7FF | 72 | 72 | 100.00% | ✅ | 1 | sarasa |
| 中日韩兼容表意文字 | CJK Compatibility Ideographs | U+F900–FAFF | 472 | 366 | 77.54% |  | 2 | sarasa |
| 字母表现形式 | Alphabetic Presentation Forms | U+FB00–FB4F | 58 | 8 | 13.79% |  | 1 | sarasa |
| 阿拉伯表现形式甲 | Arabic Presentation Forms-A | U+FB50–FDFF | 631 | 0 | 0.00% |  | — | — |
| 变体选择符 | Variation Selectors | U+FE00–FE0F | 16 | 0 | 0.00% |  | — | — |
| 竖排形式 | Vertical Forms | U+FE10–FE1F | 10 | 10 | 100.00% | ✅ | 2 | sarasa |
| 结合半边标记 | Combining Half Marks | U+FE20–FE2F | 16 | 0 | 0.00% |  | — | — |
| 中日韩兼容形式 | CJK Compatibility Forms | U+FE30–FE4F | 32 | 32 | 100.00% | ✅ | 2 | sarasa |
| 小型形式变体 | Small Form Variants | U+FE50–FE6F | 26 | 26 | 100.00% | ✅ | 2 | sarasa |
| 阿拉伯表现形式乙 | Arabic Presentation Forms-B | U+FE70–FEFF | 141 | 1 | 0.71% |  | 混 | sarasa |
| 半角及全角形式 | Halfwidth and Fullwidth Forms | U+FF00–FFEF | 225 | 225 | 100.00% | ✅ | 混 | sarasa |
| 特殊 | Specials | U+FFF0–FFFF | 5 | 2 | 40.00% |  | 1 | sarasa |
| 线形乙音节 | Linear B Syllabary | U+10000–1007F | 88 | 0 | 0.00% |  | — | — |
| 线形乙表意 | Linear B Ideograms | U+10080–100FF | 123 | 0 | 0.00% |  | — | — |
| 爱琴数字 | Aegean Numbers | U+10100–1013F | 57 | 0 | 0.00% |  | — | — |
| 古希腊数字 | Ancient Greek Numbers | U+10140–1018F | 79 | 0 | 0.00% |  | — | — |
| 古代符号 | Ancient Symbols | U+10190–101CF | 14 | 0 | 0.00% |  | — | — |
| 费斯托斯圆盘 | Phaistos Disc | U+101D0–101FF | 46 | 0 | 0.00% |  | — | — |
| 吕基亚 | Lycian | U+10280–1029F | 29 | 0 | 0.00% |  | — | — |
| 加里亚 | Carian | U+102A0–102DF | 49 | 0 | 0.00% |  | — | — |
| 科普特闰余数字 | Coptic Epact Numbers | U+102E0–102FF | 28 | 0 | 0.00% |  | — | — |
| 古意大利 | Old Italic | U+10300–1032F | 39 | 0 | 0.00% |  | — | — |
| 哥特 | Gothic | U+10330–1034F | 27 | 0 | 0.00% |  | — | — |
| 古彼尔姆 | Old Permic | U+10350–1037F | 43 | 0 | 0.00% |  | — | — |
| 乌加里特 | Ugaritic | U+10380–1039F | 31 | 0 | 0.00% |  | — | — |
| 古波斯 | Old Persian | U+103A0–103DF | 50 | 0 | 0.00% |  | — | — |
| 德撒律 | Deseret | U+10400–1044F | 80 | 0 | 0.00% |  | — | — |
| 萧伯纳 | Shavian | U+10450–1047F | 48 | 0 | 0.00% |  | — | — |
| 伊斯马尼亚 | Osmanya | U+10480–104AF | 40 | 0 | 0.00% |  | — | — |
| 奥色治 | Osage | U+104B0–104FF | 72 | 0 | 0.00% |  | — | — |
| 爱尔巴桑 | Elbasan | U+10500–1052F | 40 | 0 | 0.00% |  | — | — |
| 高加索阿尔巴尼亚 | Caucasian Albanian | U+10530–1056F | 53 | 0 | 0.00% |  | — | — |
| 维斯库奇 | Vithkuqi | U+10570–105BF | 70 | 0 | 0.00% |  | — | — |
| 线形文字甲 | Linear A | U+10600–1077F | 341 | 0 | 0.00% |  | — | — |
| 拉丁扩充己 | Latin Extended-F | U+10780–107BF | 57 | 57 | 100.00% | ✅ | 1 | sarasa |
| 塞浦路斯音节 | Cypriot Syllabary | U+10800–1083F | 55 | 0 | 0.00% |  | — | — |
| 帝国阿拉姆 | Imperial Aramaic | U+10840–1085F | 31 | 0 | 0.00% |  | — | — |
| 巴尔米拉 | Palmyrene | U+10860–1087F | 32 | 0 | 0.00% |  | — | — |
| 奈伯特 | Nabataean | U+10880–108AF | 40 | 0 | 0.00% |  | — | — |
| 哈特拉 | Hatran | U+108E0–108FF | 26 | 0 | 0.00% |  | — | — |
| 腓尼基 | Phoenician | U+10900–1091F | 29 | 0 | 0.00% |  | — | — |
| 吕底亚 | Lydian | U+10920–1093F | 27 | 0 | 0.00% |  | — | — |
| 麦罗埃圣书体 | Meroitic Hieroglyphs | U+10980–1099F | 32 | 0 | 0.00% |  | — | — |
| 麦罗埃草书体 | Meroitic Cursive | U+109A0–109FF | 90 | 0 | 0.00% |  | — | — |
| 佉卢 | Kharoshthi | U+10A00–10A5F | 68 | 0 | 0.00% |  | — | — |
| 古南阿拉比亚 | Old South Arabian | U+10A60–10A7F | 32 | 0 | 0.00% |  | — | — |
| 古北阿拉比亚 | Old North Arabian | U+10A80–10A9F | 32 | 0 | 0.00% |  | — | — |
| 摩尼 | Manichaean | U+10AC0–10AFF | 51 | 0 | 0.00% |  | — | — |
| 阿维斯塔 | Avestan | U+10B00–10B3F | 61 | 0 | 0.00% |  | — | — |
| 碑铭体帕提亚 | Inscriptional Parthian | U+10B40–10B5F | 30 | 0 | 0.00% |  | — | — |
| 碑铭体巴列维 | Inscriptional Pahlavi | U+10B60–10B7F | 27 | 0 | 0.00% |  | — | — |
| 诗篇体巴列维 | Psalter Pahlavi | U+10B80–10BAF | 29 | 0 | 0.00% |  | — | — |
| 突厥 | Old Turkic | U+10C00–10C4F | 73 | 0 | 0.00% |  | — | — |
| 古匈牙利 | Old Hungarian | U+10C80–10CFF | 108 | 0 | 0.00% |  | — | — |
| 哈尼菲罗兴亚 | Hanifi Rohingya | U+10D00–10D3F | 50 | 0 | 0.00% |  | — | — |
| 鲁米数字符号 | Rumi Numeral Symbols | U+10E60–10E7F | 31 | 0 | 0.00% |  | — | — |
| 耶西迪 | Yezidi | U+10E80–10EBF | 47 | 0 | 0.00% |  | — | — |
| 阿拉伯扩充丙 | Arabic Extended-C | U+10EC0–10EFF | 3 | 0 | 0.00% |  | — | — |
| 古粟特 | Old Sogdian | U+10F00–10F2F | 40 | 0 | 0.00% |  | — | — |
| 粟特 | Sogdian | U+10F30–10F6F | 42 | 0 | 0.00% |  | — | — |
| 回鹘 | Old Uyghur | U+10F70–10FAF | 26 | 0 | 0.00% |  | — | — |
| 花剌子模 | Chorasmian | U+10FB0–10FDF | 28 | 0 | 0.00% |  | — | — |
| 以利买 | Elymaic | U+10FE0–10FFF | 23 | 0 | 0.00% |  | — | — |
| 婆罗米 | Brahmi | U+11000–1107F | 115 | 0 | 0.00% |  | — | — |
| 开梯 | Kaithi | U+11080–110CF | 68 | 0 | 0.00% |  | — | — |
| 索拉索姆彭 | Sora Sompeng | U+110D0–110FF | 35 | 0 | 0.00% |  | — | — |
| 查克马 | Chakma | U+11100–1114F | 71 | 0 | 0.00% |  | — | — |
| 默哈杰内 | Mahajani | U+11150–1117F | 39 | 0 | 0.00% |  | — | — |
| 沙勒德 | Sharada | U+11180–111DF | 96 | 0 | 0.00% |  | — | — |
| 僧伽罗古数字 | Sinhala Archaic Numbers | U+111E0–111FF | 20 | 0 | 0.00% |  | — | — |
| 科杰基 | Khojki | U+11200–1124F | 65 | 0 | 0.00% |  | — | — |
| 木尔坦 | Multani | U+11280–112AF | 38 | 0 | 0.00% |  | — | — |
| 库达本德 | Khudawadi | U+112B0–112FF | 69 | 0 | 0.00% |  | — | — |
| 格兰他 | Grantha | U+11300–1137F | 86 | 0 | 0.00% |  | — | — |
| 内瓦 | Newa | U+11400–1147F | 97 | 0 | 0.00% |  | — | — |
| 蒂勒胡塔 | Tirhuta | U+11480–114DF | 82 | 0 | 0.00% |  | — | — |
| 悉昙 | Siddham | U+11580–115FF | 92 | 0 | 0.00% |  | — | — |
| 莫迪 | Modi | U+11600–1165F | 79 | 0 | 0.00% |  | — | — |
| 蒙文补充 | Mongolian Supplement | U+11660–1167F | 13 | 0 | 0.00% |  | — | — |
| 塔克里 | Takri | U+11680–116CF | 68 | 0 | 0.00% |  | — | — |
| 阿含 | Ahom | U+11700–1174F | 65 | 0 | 0.00% |  | — | — |
| 道格拉 | Dogra | U+11800–1184F | 60 | 0 | 0.00% |  | — | — |
| 瓦朗奇蒂 | Warang Citi | U+118A0–118FF | 84 | 0 | 0.00% |  | — | — |
| 迪维希阿库鲁 | Dives Akuru | U+11900–1195F | 72 | 0 | 0.00% |  | — | — |
| 嫩迪城体 | Nandinagari | U+119A0–119FF | 65 | 0 | 0.00% |  | — | — |
| 札那巴札尔方字 | Zanabazar Square | U+11A00–11A4F | 72 | 0 | 0.00% |  | — | — |
| 索永布 | Soyombo | U+11A50–11AAF | 83 | 0 | 0.00% |  | — | — |
| 统一加拿大土著音节扩充甲 | Unified Canadian Aboriginal Syllabics Extended-A | U+11AB0–11ABF | 16 | 0 | 0.00% |  | — | — |
| 包钦豪 | Pau Cin Hau | U+11AC0–11AFF | 57 | 0 | 0.00% |  | — | — |
| 天城体扩充甲 | Devanagari Extended-A | U+11B00–11B5F | 10 | 0 | 0.00% |  | — | — |
| 比克舒基 | Bhaiksuki | U+11C00–11C6F | 97 | 0 | 0.00% |  | — | — |
| 玛尔钦体 | Marchen | U+11C70–11CBF | 68 | 0 | 0.00% |  | — | — |
| 马萨拉姆贡德 | Masaram Gondi | U+11D00–11D5F | 75 | 0 | 0.00% |  | — | — |
| 贡贾尔贡德 | Gunjala Gondi | U+11D60–11DAF | 63 | 0 | 0.00% |  | — | — |
| 望加锡 | Makasar | U+11EE0–11EFF | 25 | 0 | 0.00% |  | — | — |
| 克维 | Kawi | U+11F00–11F5F | 86 | 0 | 0.00% |  | — | — |
| 傈僳补充 | Lisu Supplement | U+11FB0–11FBF | 1 | 0 | 0.00% |  | — | — |
| 泰米尔补充 | Tamil Supplement | U+11FC0–11FFF | 51 | 0 | 0.00% |  | — | — |
| 楔形文字 | Cuneiform | U+12000–123FF | 922 | 0 | 0.00% |  | — | — |
| 楔形数字及标点 | Cuneiform Numbers and Punctuation | U+12400–1247F | 116 | 0 | 0.00% |  | — | — |
| 早王朝楔形文字 | Early Dynastic Cuneiform | U+12480–1254F | 196 | 0 | 0.00% |  | — | — |
| 塞浦路斯-米诺斯 | Cypro-Minoan | U+12F90–12FFF | 99 | 0 | 0.00% |  | — | — |
| 埃及圣书体 | Egyptian Hieroglyphs | U+13000–1342F | 1072 | 0 | 0.00% |  | — | — |
| 埃及圣书体格式控制符 | Egyptian Hieroglyph Format Controls | U+13430–1345F | 38 | 0 | 0.00% |  | — | — |
| 安纳托利亚意音文字 | Anatolian Hieroglyphs | U+14400–1467F | 583 | 0 | 0.00% |  | — | — |
| 巴默姆补充 | Bamum Supplement | U+16800–16A3F | 569 | 0 | 0.00% |  | — | — |
| 姆鲁 | Mro | U+16A40–16A6F | 43 | 0 | 0.00% |  | — | — |
| 通萨 | Tangsa | U+16A70–16ACF | 89 | 0 | 0.00% |  | — | — |
| 巴索奥瓦 | Bassa Vah | U+16AD0–16AFF | 36 | 0 | 0.00% |  | — | — |
| 帕皓苗 | Pahawh Hmong | U+16B00–16B8F | 127 | 0 | 0.00% |  | — | — |
| 梅代法伊德林 | Medefaidrin | U+16E40–16E9F | 91 | 0 | 0.00% |  | — | — |
| 苗(老) | Miao | U+16F00–16F9F | 149 | 0 | 0.00% |  | — | — |
| 表意符号及标点 | Ideographic Symbols and Punctuation | U+16FE0–16FFF | 7 | 0 | 0.00% |  | — | — |
| 西夏 | Tangut | U+17000–187FF | 6136 | 0 | 0.00% |  | — | — |
| 西夏偏旁 | Tangut Components | U+18800–18AFF | 768 | 0 | 0.00% |  | — | — |
| 契丹小字 | Khitan Small Script | U+18B00–18CFF | 470 | 0 | 0.00% |  | — | — |
| 西夏补充 | Tangut Supplement | U+18D00–18D7F | 9 | 0 | 0.00% |  | — | — |
| 假名扩充乙 | Kana Extended-B | U+1AFF0–1AFFF | 13 | 0 | 0.00% |  | — | — |
| 假名补充 | Kana Supplement | U+1B000–1B0FF | 256 | 0 | 0.00% |  | — | — |
| 假名扩充甲 | Kana Extended-A | U+1B100–1B12F | 35 | 0 | 0.00% |  | — | — |
| 小型假名扩充 | Small Kana Extension | U+1B130–1B16F | 9 | 0 | 0.00% |  | — | — |
| 女书 | Nushu | U+1B170–1B2FF | 396 | 0 | 0.00% |  | — | — |
| 杜普雷速记 | Duployan | U+1BC00–1BC9F | 143 | 0 | 0.00% |  | — | — |
| 速记格式控制符 | Shorthand Format Controls | U+1BCA0–1BCAF | 4 | 0 | 0.00% |  | — | — |
| 兹纳缅内音符 | Znamenny Musical Notation | U+1CF00–1CFCF | 185 | 0 | 0.00% |  | — | — |
| 拜占庭乐符 | Byzantine Musical Symbols | U+1D000–1D0FF | 246 | 0 | 0.00% |  | — | — |
| 乐符 | Musical Symbols | U+1D100–1D1FF | 233 | 19 | 8.15% |  | 1 | sarasa |
| 古希腊音符 | Ancient Greek Musical Notation | U+1D200–1D24F | 70 | 0 | 0.00% |  | — | — |
| 卡克托维克数字 | Kaktovik Numerals | U+1D2C0–1D2DF | 20 | 0 | 0.00% |  | — | — |
| 玛雅数字 | Mayan Numerals | U+1D2E0–1D2FF | 20 | 0 | 0.00% |  | — | — |
| 太玄经卦爻 | Tai Xuan Jing Symbols | U+1D300–1D35F | 87 | 87 | 100.00% | ✅ | 1 | sarasa |
| 算筹 | Counting Rod Numerals | U+1D360–1D37F | 25 | 20 | 80.00% |  | 1 | sarasa |
| 数学字母数字符号 | Mathematical Alphanumeric Symbols | U+1D400–1D7FF | 996 | 903 | 90.66% |  | 1 | sarasa |
| 萨顿手语 | Sutton SignWriting | U+1D800–1DAAF | 672 | 0 | 0.00% |  | — | — |
| 拉丁扩充庚 | Latin Extended-G | U+1DF00–1DFFF | 37 | 29 | 78.38% |  | 1 | sarasa |
| 格拉哥里补充 | Glagolitic Supplement | U+1E000–1E02F | 38 | 0 | 0.00% |  | — | — |
| 西里尔扩充丁 | Cyrillic Extended-D | U+1E030–1E08F | 63 | 63 | 100.00% | ✅ | 混 | sarasa |
| 苗(创世) | Nyiakeng Puachue Hmong | U+1E100–1E14F | 71 | 0 | 0.00% |  | — | — |
| 托托 | Toto | U+1E290–1E2BF | 31 | 0 | 0.00% |  | — | — |
| 万乔 | Wancho | U+1E2C0–1E2FF | 59 | 0 | 0.00% |  | — | — |
| 纳格蒙达里 | Nag Mundari | U+1E4D0–1E4FF | 42 | 0 | 0.00% |  | — | — |
| 埃塞扩充乙 | Ethiopic Extended-B | U+1E7E0–1E7FF | 28 | 0 | 0.00% |  | — | — |
| 门迪基卡奎 | Mende Kikakui | U+1E800–1E8DF | 213 | 0 | 0.00% |  | — | — |
| 阿德拉姆 | Adlam | U+1E900–1E95F | 88 | 0 | 0.00% |  | — | — |
| 印度帐目数字 | Indic Siyaq Numbers | U+1EC70–1ECBF | 68 | 0 | 0.00% |  | — | — |
| 奥斯曼帐目数字 | Ottoman Siyaq Numbers | U+1ED00–1ED4F | 61 | 0 | 0.00% |  | — | — |
| 阿拉伯数学字母符号 | Arabic Mathematical Alphabetic Symbols | U+1EE00–1EEFF | 143 | 0 | 0.00% |  | — | — |
| 麻将牌 | Mahjong Tiles | U+1F000–1F02F | 44 | 0 | 0.00% |  | — | — |
| 多米诺牌 | Domino Tiles | U+1F030–1F09F | 100 | 0 | 0.00% |  | — | — |
| 扑克 | Playing Cards | U+1F0A0–1F0FF | 82 | 82 | 100.00% | ✅ | 1 | sarasa |
| 带圈字母数字补充 | Enclosed Alphanumeric Supplement | U+1F100–1F1FF | 200 | 174 | 87.00% |  | 2 | sarasa |
| 带圈表意文字补充 | Enclosed Ideographic Supplement | U+1F200–1F2FF | 64 | 58 | 90.62% |  | 2 | sarasa |
| 各式符号及象形 | Miscellaneous Symbols and Pictographs | U+1F300–1F5FF | 768 | 0 | 0.00% |  | — | — |
| 表情 | Emoticons | U+1F600–1F64F | 80 | 0 | 0.00% |  | — | — |
| 装饰什锦 | Ornamental Dingbats | U+1F650–1F67F | 48 | 0 | 0.00% |  | — | — |
| 交通及地图符号 | Transport and Map Symbols | U+1F680–1F6FF | 118 | 0 | 0.00% |  | — | — |
| 炼金术符 | Alchemical Symbols | U+1F700–1F77F | 124 | 0 | 0.00% |  | — | — |
| 几何形状扩充 | Geometric Shapes Extended | U+1F780–1F7FF | 103 | 64 | 62.14% |  | 1 | sarasa |
| 增补箭头丙 | Supplemental Arrows-C | U+1F800–1F8FF | 150 | 120 | 80.00% |  | 1 | sarasa |
| 增补符号及象形 | Supplemental Symbols and Pictographs | U+1F900–1F9FF | 256 | 0 | 0.00% |  | — | — |
| 棋符 | Chess Symbols | U+1FA00–1FA6F | 98 | 0 | 0.00% |  | — | — |
| 符号及象形扩充甲 | Symbols and Pictographs Extended-A | U+1FA70–1FAFF | 107 | 0 | 0.00% |  | — | — |
| 遗留电脑符号 | Symbols for Legacy Computing | U+1FB00–1FBFF | 212 | 212 | 100.00% | ✅ | 1 | sarasa |
| 中日韩统一表意文字扩展区B | CJK Unified Ideographs Extension B | U+20000–2A6DF | 42720 | 2109 | 4.94% |  | 2 | sarasa |
| 中日韩统一表意文字扩展区C | CJK Unified Ideographs Extension C | U+2A700–2B73F | 4154 | 48 | 1.16% |  | 2 | sarasa |
| 中日韩统一表意文字扩展区D | CJK Unified Ideographs Extension D | U+2B740–2B81F | 222 | 34 | 15.32% |  | 2 | sarasa |
| 中日韩统一表意文字扩展区E | CJK Unified Ideographs Extension E | U+2B820–2CEAF | 5762 | 113 | 1.96% |  | 2 | sarasa |
| 中日韩统一表意文字扩展区F | CJK Unified Ideographs Extension F | U+2CEB0–2EBEF | 7473 | 6 | 0.08% |  | 2 | sarasa |
| 中日韩兼容表意文字补充 | CJK Compatibility Ideographs Supplement | U+2F800–2FA1F | 542 | 55 | 10.15% |  | 2 | sarasa |
| 中日韩统一表意文字扩展区G | CJK Unified Ideographs Extension G | U+30000–3134F | 4939 | 4 | 0.08% |  | 2 | sarasa |
| 中日韩统一表意文字扩展区H | CJK Unified Ideographs Extension H | U+31350–323AF | 4192 | 0 | 0.00% |  | — | — |
| 标签 | Tags | U+E0000–E007F | 97 | 0 | 0.00% |  | — | — |
| 变体选择符补充 | Variation Selectors Supplement | U+E0100–E01EF | 240 | 0 | 0.00% |  | — | — |

## 表情

| 集合 | 已覆盖 | 集合大小 | 覆盖率 | 验收 | 说明 |
|------|--------|----------|--------|------|------|
| Emoji_Presentation · Regular | 49 | 1205 | 4.07% |  | 等宽本体黑白稿，半宽，不剔除 |
| Emoji_Presentation · 小黑字表情 | 1205 | 1205 | 100.00% | ✅ | 配套表情字体 |
| Emoji_Presentation · 小黑字表情微软 | 1205 | 1205 | 100.00% | ✅ | 配套表情字体 |
| 区域指示符 · 小黑字表情 | 26 | 26 | 100.00% | ✅ | U+1F1E6–1F1FF 共 26 个字母，不是旗面 |
| 国旗连字 · 小黑字表情 | 259 | 259 | 100.00% | ✅ | GSUB 两枚区域指示符连成一图 |
| 区域指示符 · 小黑字表情微软 | 26 | 26 | 100.00% | ✅ | U+1F1E6–1F1FF 共 26 个字母，不是旗面 |
| 国旗连字 · 小黑字表情微软 | 259 | 259 | 100.00% | ✅ | GSUB 两枚区域指示符连成一图 |
| 杂项符号及象形文字 · 微软 | 637 | 768 | 82.94% |  | U+1F300–1F5FF |
| 表情符号 · 微软 | 80 | 80 | 100.00% | ✅ | U+1F600–1F64F Emoticons |
| 交通和地图符号 · 微软 | 105 | 118 | 88.98% |  | U+1F680–1F6FF |
| 补充符号和象形文字 · 微软 | 242 | 256 | 94.53% |  | U+1F900–1F9FF |
| 符号和象形文字扩展 A · 微软 | 107 | 107 | 100.00% | ✅ | U+1FA70–1FAFF |
