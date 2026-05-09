---
name: paper-analyze
description: 深度分析单篇或多篇论文，生成详细笔记和评估，图文并茂 / Deep analyze papers, generate detailed notes with images
---

# 论文深度分析

## 概述

统一论文解读入口，支持五种输出模式：
- **精读笔记**（必选）— 六节结构的深度解读，含概念双链引用
- **简要版** — 5 分钟快速讲解，图片为主
- **PPT 大纲（Marp）** — 可直接转 PDF/PPTX 的演示文稿
- **HTML 幻灯片版** — 单页 HTML，键盘翻页，类 reveal.js
- **HTML 长页面版** — 单页滚动式 HTML，侧边导航，KaTeX 公式

精读笔记作为"中间表示"先行生成，其他模式基于精读笔记由独立子 agent 并行生成。

## 第零步：意图澄清（重要）

**核心原则：严格按照预设流程执行，不跳过任何用户交互步骤。即使用户的提示词中看似表达了某种意图，也必须通过 AskUserQuestion 确认，避免错误推断。**

在执行任何处理之前，检查用户提示词中是否有以下模糊点：

1. **输出模式模糊**：用户可能说"精读一下"、"总结一下"、"帮我整理一篇论文"。这些表达可能对应不同输出模式，不能自行推断。必须使用第二步中的 AskUserQuestion 让用户选择。

2. **输出目录模糊**：用户可能说"在这周论文阅读里面"、"放到笔记里"、"在某个目录下生成"。这类表述无法确定是在指定目录直接生成，还是在指定目录下创建论文子文件夹。必须使用 AskUserQuestion 确认：
   - 选项 1：在 `<指定的目录>/` 下创建 `<论文标题>/` 子文件夹（推荐，保持目录整洁）
   - 选项 2：直接在 `<指定的目录>/` 下生成所有文件

3. **论文输入歧义**：如果用户提供的路径/链接指向的内容不明确，先确认再继续。

4. **用户额外指令**：如果用户提示词中包含与预设流程不符的额外要求（如"只做精读"、"跳过图片提取"等），需要判断是否可以合并到流程中，还是需要单独确认。不确定时一律使用 AskUserQuestion。

**反例（禁止行为）：**
- 用户说"帮我把这篇论文精读总结到 0514 这周里" → 直接启动精读笔记生成并输出到某个推测的 0514 目录
- 用户说"放在笔记目录下" → 直接假设是哪个目录
- 用户只说了论文输入，没有任何额外指令 → 跳过模式选择，直接生成默认输出

正确做法：先解析出论文输入，然后不管用户的提示词里暗示了什么，都走下面的标准流程。

## 第一步：解析输入

用户调用 `/paper-analyze <论文输入>`，支持以下输入形式（多篇论文用空格或换行分隔）：

**重要：对于 arXiv 链接，禁止使用 WebFetch/Fetch 工具获取页面内容。** WebFetch 的域验证机制会因企业安全策略阻止 arxiv.org，直接使用 `curl` 即可：

```bash
# 获取论文元信息（标题、作者、日期）
curl -sL "https://arxiv.org/abs/<ARXIV_ID>" | grep -E '<title>|<meta name="citation_title"|<meta name="citation_author"|<meta name="citation_date"'
# 下载源码包
curl -sL "https://arxiv.org/e-print/<ARXIV_ID>" -o paper.tar.gz
# 下载 PDF
curl -sL "https://arxiv.org/pdf/<ARXIV_ID>" -o paper.pdf
```

| 输入形式 | 识别方式 | 处理模式 |
|---------|---------|---------|
| arXiv 链接 (`arxiv.org/abs/`) | URL 匹配 | 先用 curl 获取元信息，再尝试下载源码包，失败则下载 PDF → 模式 B |
| PDF 下载链接 | URL 以 `.pdf` 结尾 | 下载到 `downloads/` → 模式 B |
| tar.gz 下载链接 | URL 以 `.tar.gz` 结尾 | 下载到 `downloads/` → 模式 A |
| 本地 `.tar.gz` | 文件后缀 | 直接解压 → 模式 A |
| 本地 `.pdf` | 文件后缀 | 模式 B（MinerU 转换）|
| 本地目录（含 `.tex`） | 目录中有 `.tex` 文件 | 视为已解压源码包 → 模式 A |

**模式 A** = 有 LaTeX 源码包（从 `.tex` 读内容，从 `figure/` 等目录提取原图）
**模式 B** = 只有 PDF（用 MinerU 转 Markdown + 提取图片）

## 第二步：用户交互（必须执行，不可跳过）

以下三个交互步骤不论用户的提示词中是否暗示了意图，都必须按顺序执行。

### 2.1 选择输出模式

精读笔记是必选输出，始终生成。使用 AskUserQuestion（multiSelect: true）让用户选择是否需要其他输出模式。

**严禁在选项中包含"精读笔记"。** 精读笔记是必选项，不在 AskUserQuestion 的可选范围内。Claude Code 的 AskUserQuestion 最多 4 个选项，必须全部用于可选输出模式。

```
问题：除了精读笔记（默认必选）外，还需要生成哪些输出？
选项（最多 4 个，不包含精读笔记）：
  □ 简要版（5 分钟快速讲解）
  □ PPT 大纲（Marp 格式，可转 PDF）
  □ HTML 幻灯片版（键盘翻页，类 reveal.js）
  □ HTML 长页面版（单页滚动，侧边导航）
```

注意：HTML 幻灯片版依赖 PPT 大纲，如果用户选了 HTML 幻灯片但没选 PPT 大纲，自动补选 PPT 大纲。如果用户一个都不选，则只生成精读笔记。

### 2.2 MinerU 环境检查 + 2.3 GPU 选择（仅模式 B）

如果有论文需要 MinerU 转换（模式 B），读取 `${skill_dir}/prompts/00-mineru-setup.md` 并执行其中的环境检查和 GPU 选择流程。

如果所有论文都是模式 A（有源码包），跳过本节。

### 2.4 确认输出目录

使用 AskUserQuestion 确认输出目录。默认使用用户输入中能推断的路径，或当前工作目录。

如果用户提供了目录路径，进一步确认生成方式：
- **在目录下创建 `<论文标题>/` 子文件夹**（推荐）：文件组织清晰，多篇论文不混乱
- **直接在该目录下生成文件**：不创建子文件夹

如果用户未提供目录，直接询问期望的输出根目录。

## 第三步：论文获取与处理

### 单篇论文

根据模式启动对应的子 agent：
1. **子 agent A（论文获取）**：下载/解压/转换/提取图片
2. **子 agent A2（图片布局分析）**：分析图片空间关系 → 输出 image_layout.json（依赖 A 完成）
3. **子 agent B（精读笔记）**：读原文 → 读 image_layout.json → 提取概念 → 写 glossary.md → 写精读笔记（依赖 A2 完成）
4. **并行子 agent**（根据用户选择）：简要版 / PPT 大纲 / HTML 长页面版
5. **HTML 幻灯片版**（如选）：等 PPT 大纲完成后启动

### 多篇论文

1. 解析所有论文输入，分为模式 A 组和模式 B 组
2. 模式 A 的论文：直接并行启动各自的获取 + 处理 agent
3. 模式 B 的论文：启动统一 MinerU 转换 agent（使用 mineru-router 多 GPU 并行）
4. 所有论文获取完成后：为每篇启动独立的笔记生成 agent

**MinerU 多 GPU 并行（多篇论文时）：**

从 `${skill_dir}/references/mineru-config.yaml` 读取 MinerU 路径配置，然后：

```bash
# 读取配置（子 agent 内部执行）
MINERU_CLI=$(yq -r '.mineru.cli_path' ${skill_dir}/references/mineru-config.yaml)
MINERU_ROUTER=$(yq -r '.mineru.router_path' ${skill_dir}/references/mineru-config.yaml)
MODEL_SOURCE=$(yq -r '.mineru.model_source' ${skill_dir}/references/mineru-config.yaml)
MODEL_CACHE=$(yq -r '.mineru.modelscope_cache' ${skill_dir}/references/mineru-config.yaml)

# 启动 router（用户选了 GPU 0,1,2）
MINERU_MODEL_SOURCE=$MODEL_SOURCE \
MODELSCOPE_CACHE=$MODEL_CACHE \
$MINERU_ROUTER \
  --local-gpus 0,1,2 --port 8002 &

# 为每篇 PDF 提交转换任务
MINERU_MODEL_SOURCE=$MODEL_SOURCE \
$MINERU_CLI \
  -p paper.pdf -o output_dir \
  --api-url http://127.0.0.1:8002 \
  -b hybrid-auto-engine -l en
```

**单篇论文时：** 不启动 router，直接用 `CUDA_VISIBLE_DEVICES=<GPU>` + 配置文件中的 `cli_path` 本地执行。

## 第四步：文件名安全化（重要）

论文标题中可能包含中文、特殊符号、空格等，直接用于目录和文件名会导致 Windows 兼容性问题。**所有目录名和文件名**必须经过 sanitization 处理：

**规则：**
1. 移除所有非 ASCII 字符（中文字符、Unicode 符号等）— 论文标题通常是英文，保留英文部分即可
2. 只允许：`a-z`、`A-Z`、`0-9`、`-`（连字符）、`_`（下划线）、`.`（点）
3. 空格替换为 `-`（连字符）
4. 多个连续的 `-` 压缩为单个 `-`
5. 去除首尾的 `-`
6. 如果标题过长，截取前 80 个字符作为目录名
7. 如果 sanitization 后标题为空（标题全是中文等非 ASCII 字符），使用 `paper-<arXiv-ID>` 或 `paper-<当前时间戳>` 作为 fallback

**示例：**
- `Multi-Agent Design: Optimizing Agents with Better Prompts and Topologies` → `Multi-Agent-Design-Optimizing-Agents-with-Better-Prompts-and-Topologies`
- `LLM-based Multi-Agent Systems: A Survey` → `LLM-based-Multi-Agent-Systems-A-Survey`

**所有子 agent 在创建目录和文件时，必须使用 sanitization 后的标题（以下称为 `safe_title`），而不是原始论文标题。**

## 第五步：输出目录结构

```
${output_dir}/<safe_title>/
├── downloads/              # 下载的原始文件
├── images/                 # 论文原图（PNG）
├── source/                 # 原文（.tex/.bib 或 MinerU .md）
├── <safe_title>.md         # 精读笔记
├── glossary.md             # 概念速查（Obsidian 双链引用）
├── <safe_title>-简要版.md  # 简要版（如选）
├── <safe_title>-slides.html  # HTML 幻灯片版（如选）
├── <safe_title>-page.html    # HTML 长页面版（如选）
└── <safe_title>-ppt.md       # Marp PPT 大纲（如选）
```

---

## 子 Agent Prompt 索引

启动子 Agent 前，读取对应的 Prompt 文件（位于 `${skill_dir}/prompts/`），替换占位符后传递给 Agent 工具。

| Prompt | 文件路径 | 用途 | 触发条件 |
|--------|----------|------|----------|
| 0 | `${skill_dir}/prompts/00-mineru-setup.md` | MinerU 环境检查 + GPU 选择 | 有模式 B 论文时 |
| 1 | `${skill_dir}/prompts/01-fetch-mode-a.md` | 论文获取（LaTeX 源码包） | 模式 A 论文 |
| 2 | `${skill_dir}/prompts/02-fetch-mode-b.md` | 论文获取（PDF + MinerU） | 模式 B 单篇论文 |
| 2a | `${skill_dir}/prompts/02a-image-layout.md` | 图片布局分析 | 论文获取完成后，精读笔记前 |
| 3 | `${skill_dir}/prompts/03-mineru-batch.md` | MinerU 多 GPU 并行转换 | 模式 B 多篇论文 |
| 4 | `${skill_dir}/prompts/04-deep-note.md` | 精读笔记 + glossary 生成 | 必选，最先执行 |
| 5 | `${skill_dir}/prompts/05-simple-note.md` | 简要版笔记 | 用户选择"简要版" |
| 6 | `${skill_dir}/prompts/06-marp-ppt.md` | Marp PPT 大纲 | 用户选择"PPT 大纲" |
| 7 | `${skill_dir}/prompts/07-html-slides.md` | HTML 幻灯片 | 用户选择"HTML 幻灯片版" |
| 8 | `${skill_dir}/prompts/08-html-page.md` | HTML 长页面 | 用户选择"HTML 长页面版" |

占位符说明：
- `${paper_path}` — 论文文件路径（.tar.gz / .pdf / 目录）
- `${output_dir}` — 用户指定的输出根目录
- `${paper_title}` — 论文原始标题
- `${safe_title}` — 安全化后的文件名（ASCII 字符、连字符、下划线、点）
- `${paper_dir}` — 论文输出目录（`${output_dir}/${safe_title}`）
- `${gpu_id}` — 用户选择的 GPU ID
- `${selected_gpus}` — 用户选择的所有 GPU（逗号分隔）
- `${skill_dir}` — 本 skill 目录的绝对路径
- `${research_purpose}` — 用户的调研目的（如有）
- `${input_mode}` — 输入模式（A = LaTeX 源码, B = PDF/MinerU）

---

## 依赖

- `pdftoppm`（`apt install poppler-utils`，模式 A 需要）
- `Pillow`（Python 库，兜底裁切白边，`pip install Pillow`）
- MinerU 3.1.7（模式 B 需要，配置见 `references/mineru-setup.md`）
- 网络连接（下载 arXiv 源码包 / PDF 时需要）

## 快速参考

| 操作 | 命令 |
|------|------|
| 解压源码包 | `tar -xzf paper.tar.gz -C /tmp/paper` |
| PDF 图转 PNG | `pdftoppm -cropbox -png -r 150 input.pdf output_prefix` |
| MinerU 配置 | `${skill_dir}/references/mineru-config.yaml`（从 template 复制并填入本机路径） |
| MinerU 单卡转换 | `CUDA_VISIBLE_DEVICES=0 MINERU_MODEL_SOURCE=<source> <cli_path> -p input.pdf -o output -b hybrid-auto-engine -l en` |
| MinerU 多卡 router | `<router_path> --local-gpus 0,1,2 --port 8002` |
| MinerU 提交到 router | `<cli_path> -p input.pdf -o output --api-url http://127.0.0.1:8002 -b hybrid-auto-engine -l en` |
| Marp 转 PDF | `marp --html --pdf input.md` |
