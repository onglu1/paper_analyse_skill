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

### 6. 列出源码文件并识别附录

arXiv 源码包中，附录通常以独立文件形式存在。列出所有 .tex 文件，由你自主判断哪些是附录：

```bash
echo "=== 解压目录中的所有 .tex 文件 ==="
find /tmp/arxiv_extract_$$ -name "*.tex" | sort
echo ""
echo "=== 目录结构 ==="
find /tmp/arxiv_extract_$$ -maxdepth 2 -type f | sort
```

查看文件列表后，你需要自主判断哪些文件是附录文件。判断依据：
- 文件名包含 "appendix"、"supplementary"、"supp" 等关键词 → 高度疑似附录
- 文件名不明确时，读取文件开头（前几行）内容检查：
  - 开头有 `\section{Appendix}`、`\appendix` 等 → 确认是附录
  - 开头是常规章节如 `\section{Introduction}` → 不是附录
- 如果主文件中有 `\include{appendix}` 或 `\input{appendix}` 引用，对应的文件就是附录

如果你不确定某个文件是否为附录，宁可保留（保守原则）。

### 6.5 保存原文到 source/（排除附录）

确认附录文件后，执行以下操作：

1. **不复制**附录文件到 `${PAPER_DIR}/source/`
2. 复制所有非附录的 `.tex`、`.bib`、`.sty`、`.cls`、`.bst` 文件到 source/
3. 对于主 `.tex` 文件，读取内容检查：
   - 如果存在 `\appendix` 命令，截断其后内容（保留 `.full_backup` 备份）
   - 如果存在 `\include{appendix}`、`\input{appendix}` 等引用，注释掉该行
4. 如果主文件被截断，保存截断后的版本到 source/，完整版保留为 `.full_backup`

详细的附录剥离方法论见 `${skill_dir}/references/appendix-stripping.md`。

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
