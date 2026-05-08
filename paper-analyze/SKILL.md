---
name: paper-analyze
description: 深度分析单篇或多篇论文，生成详细笔记和评估，图文并茂 / Deep analyze papers, generate detailed notes with images
---

# 论文深度分析

## 概述

统一论文解读入口，支持五种输出模式：
- **精读笔记**（必选）— 六节结构的深度解读，含概念双链引用
- **组会分享版** — 5 分钟快速讲解，图片为主
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

| 输入形式 | 识别方式 | 处理模式 |
|---------|---------|---------|
| arXiv 链接 (`arxiv.org/abs/`) | URL 匹配 | 先尝试下载源码包，失败则下载 PDF → 模式 B |
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

使用 AskUserQuestion（multiSelect: true）让用户选择输出模式：

```
问题：需要生成哪些输出？
选项：
  ☑ 精读笔记（默认选中，必选）
  □ 组会分享版
  □ PPT 大纲（Marp 格式）
  □ HTML 幻灯片版
  □ HTML 长页面版
```

注意：HTML 幻灯片版依赖 PPT 大纲，如果用户选了 HTML 幻灯片但没选 PPT 大纲，自动补选 PPT 大纲。

### 2.2 MinerU 环境检查（仅当有模式 B 论文时）

确认是否有论文需要 MinerU 转换。如果所有论文都是模式 A（有源码包），跳过本节和 2.3 节。

#### 2.2.1 查找配置文件

检查 `${skill_dir}/references/mineru-config.yaml` 是否存在：

如果存在，从中读取 MinerU 配置（CLI 路径、Python 路径、模型缓存等），直接进入 2.3 节。

如果不存在，执行 2.2.2。

#### 2.2.2 检查系统是否已安装 MinerU

```bash
# 尝试查找 mineru 命令
which mineru 2>/dev/null || \
ls $HOME/.pyenv/versions/mineru/bin/mineru 2>/dev/null || \
echo "NOT_FOUND"
```

如果找到 MinerU，向用户确认这些路径是否正确，然后从模板生成配置文件：

```bash
cp ${skill_dir}/references/mineru-config.yaml.template ${skill_dir}/references/mineru-config.yaml
```

并根据用户确认的实际路径更新 `mineru-config.yaml` 中的各项配置。

#### 2.2.3 未安装时引导安装

如果系统中未找到 MinerU：

1. 使用 AskUserQuestion 向用户确认是否安装 MinerU：
   - 选项：安装 / 跳过（此时模式 B 论文无法处理）

2. 如果用户选择安装，逐项确认配置：
   - pyenv virtualenv 的 Python 路径（默认：`$HOME/.pyenv/versions/3.12.9/envs/mineru/bin/python`）
   - MinerU CLI 安装路径（默认：`$HOME/.pyenv/versions/mineru/bin/mineru`）
   - 模型下载缓存目录（默认：`$HOME/.cache/mineru/models`）
   - 模型下载来源（默认：modelscope）

3. 参考 `${skill_dir}/references/mineru-setup.md` 指导用户完成安装

4. 安装完成后，从模板创建配置文件：

```bash
cp ${skill_dir}/references/mineru-config.yaml.template ${skill_dir}/references/mineru-config.yaml
```

将用户确认的路径写入 `mineru-config.yaml`。

**配置文件说明：**
- 模板文件：`references/mineru-config.yaml.template`（随仓库分发，可提交到 Git）
- 实际配置：`references/mineru-config.yaml`（由用户本地生成，不应提交到 Git）

### 2.3 选择可用 GPU（仅当有模式 B 论文时）

先检测可用 GPU：

```bash
nvidia-smi --query-gpu=index,name,memory.free --format=csv,noheader
```

然后使用 AskUserQuestion（multiSelect: true）让用户选择：

```
问题：选择可用的 GPU（用于 MinerU PDF 转换）：
选项：（根据检测结果动态生成）
  □ GPU 0 (空闲 38GB)
  □ GPU 1 (空闲 35GB)
  ...
```

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
2. **子 agent B（精读笔记）**：读原文 → 提取概念 → 写 glossary.md → 写精读笔记
3. **并行子 agent**（根据用户选择）：组会分享版 / PPT 大纲 / HTML 长页面版
4. **HTML 幻灯片版**（如选）：等 PPT 大纲完成后启动

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
├── <safe_title>-组会分享.md  # 组会版（如选）
├── <safe_title>-slides.html  # HTML 幻灯片版（如选）
├── <safe_title>-page.html    # HTML 长页面版（如选）
└── <safe_title>-ppt.md       # Marp PPT 大纲（如选）
```

---

## 子 Agent Prompt 模板

以下是各子 agent 的完整 prompt 模板。主 skill 在调度时替换占位符后传递给 Agent 工具。

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

---

### Prompt 1：论文获取 — 模式 A（arXiv 源码包）

````
你的任务是从 arXiv 源码包中提取论文内容和图片。

## 输入
- 论文源码包路径: ${paper_path}
- 输出根目录: ${output_dir}

## 处理步骤

### 1. 解压源码包
```bash
mkdir -p /tmp/arxiv_extract_$$
tar -xzf "${paper_path}" -C /tmp/arxiv_extract_$$
```

如果输入是目录（已解压的源码包），跳过解压，直接使用该目录。

### 2. 确定论文标题
从主 tex 文件中提取标题：
```bash
# 查找主 tex 文件（优先级：0_main.tex > main.tex > 第一个 .tex）
MAIN_TEX=$(ls /tmp/arxiv_extract_$$/0_main.tex 2>/dev/null || ls /tmp/arxiv_extract_$$/main.tex 2>/dev/null || ls /tmp/arxiv_extract_$$/*.tex 2>/dev/null | head -1)
```

从 `\title{}` 命令提取原始标题，保留为 `${paper_title}`。

### 2.5 生成安全文件名
将原始标题转换为安全文件名 `safe_title`，规则：
1. 删除所有非 ASCII 字符
2. 只保留 `a-zA-Z0-9._-`
3. 空格 → `-`，多个 `-` 合并为单个
4. 去首尾 `-`，截断至 80 字符
5. 如果结果为空，用 `paper-<arXiv-ID>` 或 `paper-<timestamp>`

后续所有目录和文件创建都必须使用 `safe_title`。

### 3. 查询论文发表来源
arXiv 和 PDF 中通常不会显式标注论文被哪个期刊/会议接收。需要使用 WebSearch 工具搜索该论文是否已被接收：

搜索策略：
1. 先用论文完整标题在 arxiv.org 上查看页面上是否有 "Submitted to"、"Accepted at"、"Published in" 等标注
2. 用 `"<论文标题>" accepted conference` 或 `"<论文标题>" published in` 搜索
3. 在 Google Scholar 上搜索标题，查看是否已标注会议/期刊信息

如果找到发表来源（如 AAAI 2026、ICML 2025、NeurIPS 等），记录下来供后续使用。如果确实查不到，标记为 "arXiv preprint"。

### 4. 创建输出目录
```bash
PAPER_DIR="${output_dir}/${safe_title}"
mkdir -p "${PAPER_DIR}/images"
mkdir -p "${PAPER_DIR}/source"
mkdir -p "${PAPER_DIR}/downloads"
```

### 5. 提取图片到 images/
```bash
# 查找图片目录（优先级：figure/ > pics/ > figures/ > fig/ > images/ > img/）
# PDF 图片转 PNG
for f in $(find /tmp/arxiv_extract_$$ -name "*.pdf" -path "*/fig*"); do
    pdftoppm -png -r 150 "$f" "${PAPER_DIR}/images/$(basename "$f" .pdf)"
done
# PNG/JPG 直接复制
for d in figure pics figures fig images img; do
    if [ -d "/tmp/arxiv_extract_$$/$d" ]; then
        cp /tmp/arxiv_extract_$$/$d/*.png /tmp/arxiv_extract_$$/$d/*.jpg /tmp/arxiv_extract_$$/$d/*.jpeg "${PAPER_DIR}/images/" 2>/dev/null
        break
    fi
done
```

### 6. 保存原文到 source/
```bash
find /tmp/arxiv_extract_$$ -maxdepth 1 -type f \( -name "*.tex" -o -name "*.bib" -o -name "*.sty" -o -name "*.cls" -o -name "*.bst" \) -exec cp {} "${PAPER_DIR}/source/" \;
```

### 7. 保存原始压缩包
```bash
cp "${paper_path}" "${PAPER_DIR}/downloads/"
```

### 8. 清理临时文件
```bash
rm -rf /tmp/arxiv_extract_$$
```

## 输出
完成后报告：
- 论文标题
- 发表来源（会议/期刊名称，或 "arXiv preprint"）
- 输出目录路径 (PAPER_DIR)
- 提取的图片数量和列表
- source/ 中的文件列表
````

---

### Prompt 2：论文获取 — 模式 B（PDF + MinerU 转换）

````
你的任务是使用 MinerU 将论文 PDF 转换为 Markdown 并提取图片。

## 输入
- 论文 PDF 路径: ${paper_path}
- 输出根目录: ${output_dir}
- GPU ID: ${gpu_id}

## 处理步骤

### 1. 读取 MinerU 配置
从 `${skill_dir}/references/mineru-config.yaml` 读取 MinerU 环境配置：
```bash
MINERU_CLI=$(python3 -c "import yaml; c=yaml.safe_load(open('${skill_dir}/references/mineru-config.yaml')); print(c['mineru']['cli_path'])")
MINERU_ROUTER=$(python3 -c "import yaml; c=yaml.safe_load(open('${skill_dir}/references/mineru-config.yaml')); print(c['mineru']['router_path'])")
MODEL_SOURCE=$(python3 -c "import yaml; c=yaml.safe_load(open('${skill_dir}/references/mineru-config.yaml')); print(c['mineru']['model_source'])")
MODEL_CACHE=$(python3 -c "import yaml; c=yaml.safe_load(open('${skill_dir}/references/mineru-config.yaml')); print(c['mineru']['modelscope_cache'])")
```

如果配置文件不存在，报告错误："MinerU 配置文件未找到，请先在主对话中配置 MinerU 环境。"

### 2. 确认 MinerU 可用
```bash
$MINERU_CLI --help | head -5
```

如果不可用，参考 `${skill_dir}/references/mineru-setup.md` 排查。

### 3. 用 MinerU 转换 PDF
```bash
MINERU_MODEL_SOURCE=$MODEL_SOURCE \
MODELSCOPE_CACHE=$MODEL_CACHE \
CUDA_VISIBLE_DEVICES=${gpu_id} $MINERU_CLI \
    -p "${paper_path}" \
    -o "${output_dir}/mineru_output" \
    -b hybrid-auto-engine \
    -l en \
    -d cuda
```

### 4. 确定论文标题
读取 MinerU 生成的 Markdown（位于 `${output_dir}/mineru_output/*/auto/*.md`），从开头 `# ` 行提取标题。

### 3.1 生成安全文件名
将原始标题转换为安全文件名 `safe_title`，规则：
1. 删除所有非 ASCII 字符，只保留 `a-zA-Z0-9._-`
2. 空格 → `-`，多个 `-` 合并为单个，去首尾 `-`
3. 截断至 80 字符；如果结果为空，用 `paper-<timestamp>` 作为 fallback

后续所有目录和文件创建都必须使用 `safe_title`。

### 3.5 查询论文发表来源
论文 PDF 中通常不会显式标注被哪个期刊/会议接收。需要使用 WebSearch 工具搜索该论文是否已被接收：

搜索策略：
1. 用 `"<论文标题>" accepted conference` 或 `"<论文标题>" published in` 搜索
2. 在 Google Scholar 上搜索标题，查看是否已标注会议/期刊

如果找到发表来源，记录下来。查不到则标记为 "preprint"。

### 4. 创建输出目录
```bash
PAPER_DIR="${output_dir}/${safe_title}"
mkdir -p "${PAPER_DIR}/images"
mkdir -p "${PAPER_DIR}/source"
mkdir -p "${PAPER_DIR}/downloads"
```

### 5. 收集图片到 images/（重要：过滤垃圾图片）
```bash
cp ${output_dir}/mineru_output/*/auto/images/* "${PAPER_DIR}/images/"
```

**图片过滤规则：** 只保留在 MinerU 输出的 Markdown 中被明确引用、且有明确图注或明确含义的图片。没有被原文引用的、或者没有图注的图片（公式渲染、装饰性元素等）直接从 images/ 中删除。

具体做法：读取 MinerU 的 Markdown 文件，找出所有 `![...](...)`  引用的图片文件名，只保留这些图片。然后进一步检查每张图片在 Markdown 中的上下文，如果只是行内公式或无意义的装饰图，也删除。

### 6. 保存原文到 source/
```bash
MINERU_MD=$(ls ${output_dir}/mineru_output/*/auto/*.md | head -1)
cp "$MINERU_MD" "${PAPER_DIR}/source/"
```

### 7. 保存原始 PDF
```bash
cp "${paper_path}" "${PAPER_DIR}/downloads/"
```

### 8. 清理 MinerU 临时输出
```bash
rm -rf "${output_dir}/mineru_output"
```

## 输出
完成后报告：
- 论文标题
- 发表来源（会议/期刊名称，或 "preprint"）
- 输出目录路径 (PAPER_DIR)
- 保留的图片数量和列表
- source/ 中的 Markdown 文件路径
````

---

### Prompt 3：MinerU 多文档并行转换（多篇论文时使用）

````
你的任务是使用 mineru-router 并行转换多篇论文 PDF。

## 输入
- PDF 文件列表: ${pdf_list}（每行一个路径）
- 输出根目录: ${output_dir}
- 可用 GPU: ${selected_gpus}

## 处理步骤

### 1. 读取 MinerU 配置
从 `${skill_dir}/references/mineru-config.yaml` 读取 MinerU 环境配置：
```bash
MINERU_CLI=$(python3 -c "import yaml; c=yaml.safe_load(open('${skill_dir}/references/mineru-config.yaml')); print(c['mineru']['cli_path'])")
MINERU_ROUTER=$(python3 -c "import yaml; c=yaml.safe_load(open('${skill_dir}/references/mineru-config.yaml')); print(c['mineru']['router_path'])")
MODEL_SOURCE=$(python3 -c "import yaml; c=yaml.safe_load(open('${skill_dir}/references/mineru-config.yaml')); print(c['mineru']['model_source'])")
MODEL_CACHE=$(python3 -c "import yaml; c=yaml.safe_load(open('${skill_dir}/references/mineru-config.yaml')); print(c['mineru']['modelscope_cache'])")
```

### 2. 启动 mineru-router
```bash
MINERU_MODEL_SOURCE=$MODEL_SOURCE \
MODELSCOPE_CACHE=$MODEL_CACHE \
$MINERU_ROUTER --local-gpus ${selected_gpus} --port 8002 &
ROUTER_PID=$!

# 等待 router 启动
sleep 10
curl -s http://127.0.0.1:8002/health || (echo "Router 启动失败" && exit 1)
```

### 3. 并行提交所有 PDF 转换任务
对每篇 PDF，在后台执行：
```bash
MINERU_MODEL_SOURCE=$MODEL_SOURCE \
$MINERU_CLI \
    -p "<pdf_path>" \
    -o "${output_dir}/mineru_output" \
    --api-url http://127.0.0.1:8002 \
    -b hybrid-auto-engine \
    -l en &
```

### 4. 等待所有转换完成
```bash
wait
```

### 5. 关闭 router
```bash
kill $ROUTER_PID
```

### 6. 为每篇论文整理输出
对每篇 PDF 的 MinerU 输出：
- 从 Markdown 首行提取论文原始标题
- **生成安全文件名**：将标题转为 `safe_title`（规则：只保留 `a-zA-Z0-9._-`，空格→`-`，截断 80 字符；空则 fallback 到 `paper-<timestamp>`）
- **查询论文发表来源**：用 WebSearch 工具搜索标题，查找是否被会议/期刊接收（PDF 中通常没有显式标注）。搜到则记录，查不到标记为 "preprint"
- 创建 `${output_dir}/${safe_title}/` 目录结构
- 复制图片到 `images/`（执行图片过滤：只保留 Markdown 中明确引用且有图注的图片）
- 复制 Markdown 到 `source/`
- 复制原始 PDF 到 `downloads/`

### 7. 清理
```bash
rm -rf "${output_dir}/mineru_output"
```

## 输出
完成后报告每篇论文的：
- 论文标题
- 发表来源（会议/期刊名称，或 "preprint"）
- 输出目录路径
- 图片数量
- source 文件路径
````

---

### Prompt 4：精读笔记生成

````
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
读取 `${paper_dir}/source/` 中的所有文件：
- 如果是 `.tex` 文件：按优先级阅读（method > experiments > introduction > abstract > related > conclusion）
- 如果是 `.md` 文件（MinerU 输出）：通读全文

### 2. 查看可用图片
列出 `${paper_dir}/images/` 中的所有图片，理解每张图片的内容和在论文中的位置。

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
- 在合适位置插入图片（`![描述](images/xxx.png)`）
- 每张图片下方加一行中文解释
- 图片越多越好，但不要引入 MinerU 的公式图片

Frontmatter 格式：
```yaml
---
title: ${paper_title}
year: 2026
venue: <从论文 tex 源码或获取 agent 报告中提取；如果都没有显式标注，用 WebSearch 搜索标题确认是否被接收，查不到填 "arXiv preprint">
paper_type: system / method
tags:
  - 论文笔记
  - 精读
---
```

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
````

---

### Prompt 5：组会分享版生成

````
你的任务是基于精读笔记生成适合组会分享的简化版笔记。

## 输入
- 论文输出目录: ${paper_dir}
- 论文标题: ${paper_title}
- Skill 目录: ${skill_dir}

## 必读参考文件

1. `${skill_dir}/references/simple-template.md` — 组会分享版规范

## 处理步骤

### 1. 读取精读笔记和 glossary
- 读取 `${paper_dir}/${safe_title}.md`（精读笔记）
- 读取 `${paper_dir}/glossary.md`（概念速查）

### 2. 查看可用图片
列出 `${paper_dir}/images/` 中的所有图片，选择最适合组会分享的图片：
- 框架图/架构图（必选）
- 原理示意图（如有）
- 实验结果对比图（选最关键的 1-3 张）
- case study / 可视化图（选最有说服力的 1-2 张）
- 跳过：细节表格截图、大段公式截图

### 3. 撰写组会分享版
严格按照 `simple-template.md` 中的 5 部分结构撰写，保存到 `${paper_dir}/${safe_title}-组会分享.md`。

核心原则：
- 基于精读笔记生成，不重新理解原文
- 图片是主要内容载体，文字精简
- 控制在 5 分钟能讲完的篇幅
- 术语首次出现时必须解释

Frontmatter：
```yaml
---
title: ${paper_title}
year: 2026
venue: <从精读笔记提取>
paper_type: system / method
tags:
  - 论文笔记
  - 组会分享
---
```

## 输出
完成后报告：
- 组会分享版路径
- 使用的图片数量
- 笔记总字数
````

---

### Prompt 6：PPT 大纲生成（Marp 格式）

````
你的任务是基于精读笔记生成 Marp 格式的 PPT 大纲。

## 输入
- 论文输出目录: ${paper_dir}
- 论文标题: ${paper_title}
- Skill 目录: ${skill_dir}

## 必读参考文件

1. `${skill_dir}/references/marp-template.md` — Marp PPT 大纲规范和示例

## 处理步骤

### 1. 读取精读笔记
读取 `${paper_dir}/${safe_title}.md`。

### 2. 查看可用图片
列出 `${paper_dir}/images/`，规划每页使用哪张图片。

### 3. 撰写 PPT 大纲
严格按照 `marp-template.md` 中的规范撰写，保存到 `${paper_dir}/${safe_title}-ppt.md`。

结构：
- 封面页（标题、作者、venue）
- 背景与动机（1-2 页）
- 问题定义（1 页）
- 方法总览（1 页，放架构图）
- 方法细节（每个关键模块 1 页）
- 实验设置（1 页）
- 实验结果（2-3 页，放结果图）
- 总结与启发（1 页）

格式要求：
- Marp frontmatter（`marp: true`, `theme: default`, `paginate: true`）
- 每页用 `---` 分隔
- 每页：页标题 + 要点（不超过 4 条）+ 图片引用
- 图片使用 `![bg right:40%](images/xxx.png)` 或 `![w:600](images/xxx.png)`

## 输出
完成后报告：
- PPT 大纲路径
- 总页数
- 使用的图片数量
````

---

### Prompt 7：HTML 幻灯片版生成

````
你的任务是基于 PPT 大纲（Marp 格式）生成单页 HTML 幻灯片文件。

## 输入
- 论文输出目录: ${paper_dir}
- 论文标题: ${paper_title}
- Skill 目录: ${skill_dir}

## 必读参考文件

1. `${skill_dir}/references/html-slides-template.md` — HTML 幻灯片版规范和模板骨架

## 处理步骤

### 1. 读取 PPT 大纲
读取 `${paper_dir}/${safe_title}-ppt.md`（Marp 格式）。

### 2. 读取 HTML 模板骨架
从 `html-slides-template.md` 中获取基础 HTML 模板。

### 3. 将 Marp 内容转换为 HTML sections
按照 `html-slides-template.md` 中的映射规则，将每页 Marp 内容转换为 `<section>` 标签。

转换规则：
- 每个 `---` 分隔的页面 → 一个 `<section>`
- 页标题 → `<h2>`
- 要点列表 → `<ul><li>`
- 图片引用 → `<img>` 标签（使用相对路径 `images/xxx.png`）
- 公式 → KaTeX 渲染（`$...$` → `<span class="katex">`, `$$...$$` → `<div class="katex-display">`）

### 4. 生成完整 HTML 文件
将转换后的内容填充到模板骨架中，保存到 `${paper_dir}/${safe_title}-slides.html`。

功能要求：
- 键盘左右翻页（ArrowLeft/ArrowRight）
- 进度条显示当前页/总页数
- 图片点击放大
- 深色主题
- 响应式设计

### 5. 验证
在终端中检查生成的 HTML 文件：
- 文件大小合理
- 包含所有 section
- 图片路径正确

## 输出
完成后报告：
- HTML 幻灯片路径
- 总页数
- 文件大小
````

---

### Prompt 8：HTML 长页面版生成

````
你的任务是基于精读笔记生成单页滚动式 HTML 长页面。

## 输入
- 论文输出目录: ${paper_dir}
- 论文标题: ${paper_title}
- Skill 目录: ${skill_dir}

## 必读参考文件

1. `${skill_dir}/references/html-page-template.md` — HTML 长页面版规范和模板骨架

## 处理步骤

### 1. 读取精读笔记和 glossary
- 读取 `${paper_dir}/${safe_title}.md`（精读笔记）
- 读取 `${paper_dir}/glossary.md`（概念速查）

### 2. 读取 HTML 模板骨架
从 `html-page-template.md` 中获取基础 HTML 模板。

### 3. 将 Markdown 转换为 HTML 内容
- 标题 → `<h1>` ~ `<h4>`
- 段落 → `<p>`
- 列表 → `<ul>/<ol>`
- 图片 → `<img>` + lightbox 支持
- 公式 → KaTeX 自动渲染（`$...$` 和 `$$...$$`）
- 代码块 → `<pre><code>` + highlight.js
- `[[glossary#概念名|概念名]]` → `<span class="glossary-term" data-term="概念名">概念名</span>`

### 4. 生成侧边导航
从笔记的标题结构生成侧边栏目录，支持滚动高亮。

### 5. 注入 glossary 数据
将 glossary.md 中的概念解释转换为 JSON，注入到 HTML 中供 tooltip 使用：
```javascript
const glossaryData = {
  "概念名": { fullName: "全称", explanation: "解释", role: "角色" },
  ...
};
```

### 6. 生成完整 HTML 文件
将所有内容填充到模板骨架中，保存到 `${paper_dir}/${safe_title}-page.html`。

功能要求：
- 侧边导航栏（跟随滚动高亮）
- 图片点击放大（lightbox）
- 公式渲染（KaTeX CDN）
- 代码高亮（highlight.js CDN）
- glossary 术语悬停提示（tooltip）
- 响应式设计（移动端隐藏侧边栏）
- 回到顶部按钮
- 阅读进度条

### 7. 验证
检查生成的 HTML 文件：
- 文件大小合理
- 所有图片路径正确
- glossary 数据完整

## 输出
完成后报告：
- HTML 长页面路径
- 文件大小
- glossary 术语数量
- 图片数量
````

---

## 依赖

- `pdftoppm`（`apt install poppler-utils`，模式 A 需要）
- MinerU 3.1.7（模式 B 需要，配置见 `references/mineru-setup.md`）
- 网络连接（下载 arXiv 源码包 / PDF 时需要）

## 快速参考

| 操作 | 命令 |
|------|------|
| 解压源码包 | `tar -xzf paper.tar.gz -C /tmp/paper` |
| PDF 图转 PNG | `pdftoppm -png -r 150 input.pdf output_prefix` |
| MinerU 配置 | `${skill_dir}/references/mineru-config.yaml`（从 template 复制并填入本机路径） |
| MinerU 单卡转换 | `CUDA_VISIBLE_DEVICES=0 MINERU_MODEL_SOURCE=<source> <cli_path> -p input.pdf -o output -b hybrid-auto-engine -l en` |
| MinerU 多卡 router | `<router_path> --local-gpus 0,1,2 --port 8002` |
| MinerU 提交到 router | `<cli_path> -p input.pdf -o output --api-url http://127.0.0.1:8002 -b hybrid-auto-engine -l en` |
| Marp 转 PDF | `marp --html --pdf input.md` |
