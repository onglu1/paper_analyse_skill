你的任务是从 arXiv 源码包中提取论文内容和图片。

## 输入
- 论文源码包路径: ${paper_path}
- 输出根目录: ${output_dir}
- Skill 目录: ${skill_dir}

## 必读参考文件

在开始处理前，必须读取以下文件：
1. `${skill_dir}/references/appendix-stripping.md` — 附录剥离方法论（含独立附录文件判断规则、主文件 `\appendix` 截断规则、保守原则）

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
# -cropbox 使用 CropBox 渲染而非 MediaBox，避免生成大片空白（LaTeX PDF 常见 MediaBox 远大于 CropBox）
for f in $(find /tmp/arxiv_extract_$$ -name "*.pdf" -path "*/fig*"); do
    pdftoppm -cropbox -png -r 150 "$f" "${PAPER_DIR}/images/$(basename "$f" .pdf)"
done
# 兜底裁边：对 CropBox 仍含白边的 PDF（如 CropBox=MediaBox 的情况），用 Pillow 裁切
python3 -c "
from PIL import Image
import glob, sys
for p in sorted(glob.glob('${PAPER_DIR}/images/*.png')):
    img = Image.open(p)
    gray = img.convert('L')
    bin = gray.point(lambda x: 0 if x < 250 else 255, '1')
    inv = bin.point(lambda x: 255 if x == 0 else 0, '1')
    bbox = inv.getbbox()
    if bbox and (bbox[0] > 3 or bbox[1] > 3 or (img.width-bbox[2]) > 3 or (img.height-bbox[3]) > 3):
        w, h = img.width, img.height
        img.crop(bbox).save(p)
        print(f'  trim: {p} ({w}x{h} -> {bbox[2]-bbox[0]}x{bbox[3]-bbox[1]})')
" 2>/dev/null || true
# PNG/JPG 直接复制
for d in figure pics figures fig images img; do
    if [ -d "/tmp/arxiv_extract_$$/$d" ]; then
        cp /tmp/arxiv_extract_$$/$d/*.png /tmp/arxiv_extract_$$/$d/*.jpg /tmp/arxiv_extract_$$/$d/*.jpeg "${PAPER_DIR}/images/" 2>/dev/null
        break
    fi
done
```

### 6. 探索目录结构并识别附录（关键步骤）

**不同论文的附录结构千差万别，绝不能仅凭文件名是否包含 "appendix" 来判断。必须先完整探索、理解文档组织方式、再决定如何剥离。**

详细的附录剥离方法论见 `${skill_dir}/references/appendix-stripping.md`，必须读取并遵循。以下是核心流程摘要：

#### 6.1 完整探索目录结构

首先了解解压后的完整文件布局，不只是 `.tex` 文件：

```bash
echo "=== 完整目录结构（所有文件） ==="
find /tmp/arxiv_extract_$$ -type f | sort
echo ""
echo "=== 子目录列表 ==="
find /tmp/arxiv_extract_$$ -type d | sort
```

观察是否有独立的 appendix/supplementary 子目录、附录专属图片目录等。

#### 6.2 找到并阅读主编排文件

找到包含 `\documentclass` 的主 `.tex` 文件（名称可能是 main.tex、paper.tex、article.tex 或任何名称）。**完整阅读它**，重点关注：

1. **`\include{...}` 和 `\input{...}` 命令**：列出所有被引入的文件——这构成了论文的完整结构
2. **`\appendix` 命令**：这是判断附录边界的**最可靠标志**。`\appendix` 之后的所有 `\section` 都会变成附录
3. **文档组织方式**：论文可能是集中编排（每 section 一个文件）、内联编排（全部在主文件）、分目录编排等

#### 6.3 追踪 include/input 链

对于主文件中引用的每个文件，确认它属于正文还是附录：

- `\appendix` 命令之后的 `\include`/`\input` → **直接排除**（100% 是附录）
- `\appendix` 命令之后的直接内容 → **需要截断**
- 被 include 的文件可能又 include 了其他文件（如 `appendix.tex` 中又 `\input{appendix-A}`）→ 追踪完整引用链

#### 6.4 识别附录文件

综合以上信息判断每个文件：

| 依据 | 处理 |
|------|------|
| 被 `\appendix` 之后的 `\include`/`\input` 引用 | 排除 |
| 在独立的 appendix/supp 子目录中 | 排除 |
| 文件内容为补充材料（完整 prompt 列表、额外数据表等）| 视情况排除 |
| 文件名含 "appendix"/"supplementary"/"supp" | 排除，但必须阅读内容确认 |

**警告：不要只看文件名。** 有些附录文件叫 `experiments_details.tex`、`full_prompts.tex`，文件名中不含 "appendix"。必须通过主文件的引用位置和文件内容来判断。

#### 6.5 常见附录结构

务必注意以下几种常见模式：

- **独立 appendix.tex + 子文件**：main.tex → `\include{appendix}`，appendix.tex → `\input{appendix-A/B/C}`
- **主文件内联 `\appendix`**：主文件中 `\appendix` 后面的所有内容都是附录
- **分目录组织**：正文和附录在不同子目录
- **扁平结构无显式标记**：所有 .tex 平铺，只能通过阅读内容判断
- **超长论文**：正文 10 页附录 50+ 页，如果附录没剥离干净，layout 分析和精读笔记会浪费大量 token

#### 6.6 保存原文到 source/（排除附录）

确认所有附录文件后：

1. **不复制**附录相关的 `.tex` 文件到 `${PAPER_DIR}/source/`
2. **不复制**附录图片子目录到 images/（如果存在）
3. 复制所有非附录文件（`.tex`、`.bib`、`.sty`、`.cls`、`.bst`、`.bbl`）到 source/
4. 对于主 `.tex` 文件：
   - 如果存在 `\appendix` 命令，截断其后内容
   - 如果存在 `\include{appendix}` 等引用，注释掉该行（加 `%` 前缀）
   - 完整版保留为 `.full_backup` 备份

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
