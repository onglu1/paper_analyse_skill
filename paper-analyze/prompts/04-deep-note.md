你的任务是为一篇论文撰写精读笔记和概念速查文件（glossary.md）。

## 输入
- 论文输出目录: ${paper_dir}
- 安全文件名: ${safe_title}
- 论文原始标题: ${paper_title}
- Skill 目录: ${skill_dir}
- 调研目的: ${research_purpose}

注意：所有输出文件的命名使用 `${safe_title}`（已去除非法字符），而非原始标题。

## 必读参考文件

在开始撰写前，必须读取以下文件理解写作规范：
1. `${skill_dir}/references/note-structure.md` — 六节结构详细说明
2. `${skill_dir}/references/note-template.md` — 写作风格规范

## 处理步骤

### 1. 阅读论文原文
读取 `${paper_dir}/source/` 中的所有文件（跳过 `.full_backup` 备份文件）：
- 如果是 `.tex` 文件：按优先级阅读（method > experiments > introduction > abstract > related > conclusion）
- 如果是 `.md` 文件（MinerU 输出）：通读全文

### 2. 查看可用图片
列出 `${paper_dir}/images/` 中的所有图片，理解每张图片的内容和在论文中的位置。

### 2.5 读取图片布局信息

读取 `${paper_dir}/image_layout.json`（由布局分析 Agent 生成）。该文件描述了每张图片的：
- 并排分组关系（哪些图片应该并排显示）
- 相对宽度比例（`relative_width`）
- 布局类型（`single`、`side-by-side`、`grid-3` 等）
- 中文图注（`caption`）

在后续撰写笔记时，**必须按照此文件中的布局信息排版图片**，使用 `note-template.md` 中定义的 HTML 模板。不要使用 `![](images/xxx.png)` 的 Markdown 图片语法。

### 3. 提取概念，建立 glossary 大纲（只建标题，内容留空）

通读全文后，从以下 5 类概念中提取需要解释的术语：
1. Baseline 方法名（用户可能没读过的对照组论文）
2. 数据集名称及其测试什么能力
3. 技术术语和缩写
4. 相关工作中提到的方法
5. 论文自定义的新概念/新量

**此阶段只建立标题，内容留空。** 写入 `${paper_dir}/glossary.md`，格式：
```markdown
## <概念名>

<!-- TODO -->
```

每个概念名应该是精读笔记中可能引用的术语。不要在这个阶段写解释——解释在步骤 6 统一生成。

### 4. 撰写精读笔记
严格按照 `note-structure.md` 中的六节结构撰写，保存到 `${paper_dir}/${safe_title}.md`。

写作时必须遵守：
- 按 `note-template.md` 中的风格规范写作
- 术语首次出现时用 `[[glossary#概念名|概念名]]` 双链标记，引用到 glossary.md 中对应的标题节
- 概念不在主干中展开解释（解释在 glossary.md 中）
- 笔记中需要的概念如果在步骤 3 的 glossary 大纲中没有，**仍然先写上双链引用**，后续步骤会补齐
- 在合适位置插入图片，**必须使用 `note-template.md` 中定义的 HTML 模板**，根据 `image_layout.json` 中的 layout 类型选择对应模板
- 图注使用 `image_layout.json` 中的 `caption` 字段内容，格式为灰色小字非斜体
- 并排图片使用 flex 布局，按 `relative_width` 设置 flex 比例
- 图片越多越好，但不要引入 MinerU 的公式图片
- 禁止使用 `![](images/xxx.png)` 的 Markdown 图片语法

Frontmatter 格式（**重要：必须严格遵守以下规则，否则会导致 YAML 解析报错**）：

```yaml
---
title: 论文标题
year: 2026
venue: 发表来源
paper_type: system
tags:
  - 论文笔记
  - 精读
---
```

**字段值约束（必须执行）：**
- `title`：只允许中文字符、英文字母和空格。标题中的冒号 `:` 必须替换为空格，引号 `"` 必须删除，其他特殊符号（`-`、`/`、`&` 等）统一替换为空格。示例：`"LLM-based MAS: A Survey"` → `LLM based MAS  A Survey`
- `venue`：同理，只允许中英文字母和空格。示例：`AAAI 2025`、`NeurIPS 2024`、`arXiv preprint`
- `paper_type`：只允许 `system` 或 `method`。`system` = 论文主要贡献是一个系统或框架；`method` = 论文主要贡献是一个算法或方法
- `tags`：保持数组格式，添加 `- 精读` 标签

详细规范见 `note-structure.md` 第五节"Frontmatter 格式"。

### 5. 正则匹配引用，补齐 glossary 大纲

精读笔记写完后，执行以下操作：

1. 用正则表达式匹配笔记中所有 `[[glossary#...|...]]` 或 `[[glossary#...]]` 形式的引用，提取出概念名列表
2. 去重后与 glossary.md 中已有的 `## 概念名` 标题逐一对比
3. **将笔记中引用到但 glossary 中缺失的概念，补到 glossary.md 中**，同样只加标题，内容留 `<!-- TODO -->`

这一步确保精读笔记中引用的每个概念在 glossary 中都有对应条目，不会出现引用找不到目标的情况。

### 6. 逐条生成 glossary 概念解释

对 glossary.md 中的每一条 `<!-- TODO -->`，逐个生成概念解释。**每条解释必须结合文章语境**，不能写成脱离文章的通用词典定义。

生成每条解释时遵循以下规则：

- **思维链**：先思考这个概念在本文中出现的上下文（作者为什么提到它？它在论文逻辑链中的位置是什么？），再组织解释语言
- **语境优先**：解释要反映这个概念在**本文**中的含义和角色，而非泛泛的定义。如果同一术语在其他文献中有不同用法，以本文用法为准
- **详略得当**：核心概念、论文自定义的新概念可以写得详细些（多段落、必要时举本文中的具体例子）；辅助性概念（如数据集名、简单工具名）可以简洁些
- **禁止空洞**：不要写"是一种常用的机器学习方法"这类放在哪里都能用的话。每个解释必须包含本文的具体信息

生成完毕后，将 `<!-- TODO -->` 替换为实际内容，格式：
```markdown
## <概念名>

**全称：** <如有缩写，写全称>

<结合文章语境的概念解释，长度视概念重要性而定>
```

### 7. 公式格式检查
笔记写完后，检查所有数学公式：
- 行内公式用 `$...$` 包裹
- 独立公式用 `$$...$$` 包裹
- 确保在 Obsidian 中能正确渲染

**公式命令兼容性检查（重要）：**

论文原文常通过 `\newcommand`、`\renewcommand`、`\def` 定义自定义 LaTeX 命令（查阅主 .tex 文件的 preamble 和 `math_commands.tex` 等文件）。这些命令在原论文 PDF 编译时正常渲染，但 **KaTeX / MathJax / Obsidian 不支持这些自定义命令**，直接抄入笔记会导致公式无法显示。

**处理规则：**
1. 在阅读论文源码时（Mode A），注意 preamble 中的 `\newcommand`/`\renewcommand`/`\def` 定义
2. 将公式写入笔记时，**不能直接抄原文中的自定义命令**，必须替换为标准等价的写法
3. 对于装饰性符号（✗、✓、✶ 等），优先直接用 **Unicode 字符**写在 Markdown 中（不在 `$...$` 内）
4. 对于数学运算类自定义命令，查找其定义并替换为标准 LaTeX 写法

**常见自定义命令替换对照：**

| 原文自定义命令 | 问题 | 替换为 |
|--------------|------|--------|
| `\crossmark`（通常定义为 `\ding{55}` 或类似） | pifont 包不可用 | Unicode ✗，或直接写中文「错误」「未通过」 |
| `\checkmark` 被 `\renewcommand` 重定义 | 覆盖了标准行为 | Unicode ✓ |
| `\newcommand{\xxx}{\text{\ding{XX}}}` | pifont 包不可用 | 找到对应的 Unicode 符号直接写 |
| 其他 `\xxxmark` 类自定义命令 | 非标准命令 | 根据上下文理解含义，用 Unicode 或中文替代 |

**一般原则：写入笔记的公式只能使用 KaTeX 支持的标准命令**（完整列表见 https://katex.org/docs/supported.html）。不确定的命令就去查定义，查不到就用中文或 Unicode 表述。

### 8. 最终自查
- 从头到尾扫一遍，对每个专业术语确认：如果读者只看这篇笔记，能理解这个词吗？
- 确认所有 `[[glossary#概念名|概念名]]` 在 glossary.md 中都有对应的 `## 概念名` 标题
- 确认 glossary.md 中没有任何 `<!-- TODO -->` 残留
- 确认图片路径正确（相对路径 `images/xxx.png`）

## 输出
完成后报告：
- 精读笔记路径
- glossary.md 路径和条目数量
- 插入的图片数量
- 笔记总字数
