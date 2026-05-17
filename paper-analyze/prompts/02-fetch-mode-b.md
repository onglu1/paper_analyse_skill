你的任务是使用 MinerU 将论文 PDF 转换为 Markdown 并提取图片。

## 输入
- 论文 PDF 路径: ${paper_path}
- 输出根目录: ${output_dir}
- GPU ID: ${gpu_id}
- Skill 目录: ${skill_dir}

## 必读参考文件

在开始处理前，必须读取以下文件：
1. `${skill_dir}/references/mineru-config.yaml` — MinerU 环境配置（cli_path、router_path、model_source、modelscope_cache）
2. `${skill_dir}/references/mineru-setup.md` — MinerU 安装与故障排查指南
3. `${skill_dir}/references/appendix-stripping.md` — 附录剥离方法论（含 References 锚点法、附录判断规则、截断策略）

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

### 5.5 剥离附录内容（关键步骤）

附录内容会严重消耗后续所有 agent 的 token 和时间。**尤其是 layout 分析 agent，如果 content_list.json 包含附录页的图片条目，会在大量无关图片上浪费时间（如 66 页论文中正文仅 10 页）。** 必须在保存到 source/ 前完整剥离。

详细的附录剥离方法论见 `${skill_dir}/references/appendix-stripping.md`，必须读取并遵循。核心流程：

**剥离策略（References 锚点法）：**

1. 读取 MinerU 输出的 Markdown 文件
2. 找到 **References / Bibliography** 章节（搜索 `# References`、`# Bibliography`、`## References` 等标题）——这是论文结构中最稳定的锚点
3. 查看 References 之后的下一章标题，判断是否为附录：
   - 标题包含 "Appendix"、"Appendices"
   - 标题形式为 `# A.`、`## A.` 且内容为补充材料
   - 标题包含 "Supplementary"、"Supplemental Material"
4. 如果确认是附录：
   a. 阅读附录开头部分（前 20-30 行），了解附录的章节结构
   b. 确定附录的结尾位置：大多数情况下附录延续到文件末尾；少数情况附录后有 Acknowledgments、Author Contributions 等短章节
   c. 从附录标题行开始截断 Markdown
5. 如果 References 之后找不到明显附录标记，检查全文是否有 `# Appendix` 或 `\appendix` 等标记
6. 截断后的 Markdown 保存到 source/，完整原文保留 `.full_backup` 备份

**同步过滤 content_list.json：**

Markdown 截断后，**必须**同步过滤 MinerU 输出的 `*_content_list.json` 文件，否则 layout 分析 agent 仍会处理附录页的图片：

1. 找到附录在 Markdown 中的起始位置，对应到正文的结束页码
2. 读取 `*_content_list.json`（与 Markdown 在同一 auto/ 目录下）
3. 删除其中 `page_idx` >= 附录起始页的所有条目
4. 过滤后的 content_list.json 随 Markdown 一起保存到 source/

### 6. 保存原文到 source/
```bash
MINERU_DIR=$(dirname $(ls ${output_dir}/mineru_output/*/auto/*.md | head -1))
# 保存截断后的 Markdown（已在步骤 5.5 中完成截断）
cp "$MINERU_DIR"/*.md "${PAPER_DIR}/source/"
# 保存过滤后的 content_list.json（已在步骤 5.5 中过滤掉附录页码的条目）
cp "$MINERU_DIR"/*_content_list.json "${PAPER_DIR}/source/" 2>/dev/null || true
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
