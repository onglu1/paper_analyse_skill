# 附录剥离方法论

本文件定义了从论文中智能剥离附录的统一方法，适用于 LaTeX 源码包和 MinerU 转换后的 Markdown 两种输入形式。

## 核心原则

附录剥离必须在 **保存 source 文件之前** 完成，确保后续所有下游 agent（精读、简要版、PPT、HTML 等）都不会读到附录内容，从而节约 token 和处理时间。**尤其重要的是，layout 分析 agent 也只应处理正文的图片，不应在附录图片上浪费时间和 token。**

剥离过程不是简单的正则匹配或文件名关键词匹配，而是让 agent **先理解论文的完整组织结构，再判断附录的边界和剥离方式**。

不同论文的附录结构千差万别，绝不能仅凭文件名是否包含 "appendix" 来判断。必须先探索、再理解、最后再剥离。

---

## 方法一：Markdown/文本形式的论文（MinerU 输出）

### 步骤

1. **定位 References 章节**
   - 搜索 `# References`、`# Bibliography`、`## References`、`## Bibliography` 等标题
   - References 是学术论文结构中最稳定的锚点，附录几乎总是在 References 之后

2. **检查 References 之后的下一章**
   - 查看 References 之后的下一个一级或二级标题
   - 判断该章节是否为附录。典型标志：
     - 标题包含 "Appendix"、"Appendices"
     - 标题形式为 `# A.`、`## A.` 且内容为补充材料
     - 标题包含 "Supplementary"、"Supplemental Material"
   - 如果标题不是附录（如 "Acknowledgments" 等），继续检查下一个标题

3. **确认附录开头后，阅读开头部分确定结尾**
   - 阅读附录的前 20-30 行，了解附录的章节结构和包含的子章节
   - 确定附录的结束位置：
     - 绝大多数情况下，附录延续到文件末尾
     - 少数情况附录后有 Acknowledgments、Author Contributions 等
   - 检查附录最后是否有一些 closing 章节（如致谢）

4. **截断**
   - 将附录从开头标题行到结尾之间的内容全部移除
   - 如果附录后还有非附录内容（如致谢），保留后续内容

5. **同步过滤 image 和 layout 相关文件**
   - 如果 MinerU 输出中包含 `_content_list.json`，将其复制到 source/ 时也要过滤掉附录页码的条目
   - 识别附录的起始页码（从 Markdown 中断位置的上下文或 page_idx 判断），删除 content_list 中 page_idx >= 附录起始页的所有条目

6. **保留备份**
   - 完整原文保存为 `.full_backup`，以防需要查阅

### 示例

```
# Results
...（实验结果）

# References
[1] ...

# Appendix A. Experimental Details    ← 从这里开始是附录
...（大量实验细节）
# Appendix B. Full Prompts
...（完整 prompt 列表）
                                        ← 文件末尾，全部截断
```

---

## 方法二：LaTeX 源码包（arXiv 下载）

**这是最容易出问题的场景。** arXiv 源码包中的附录结构多种多样，绝不能仅凭文件名判断，必须执行完整的探索流程。

### 核心流程（必须严格按顺序执行）

#### 第 1 步：完整探索目录结构

首先需要了解解压后的完整目录结构，而不仅仅是 `.tex` 文件列表：

```bash
echo "=== 完整目录结构 ==="
find /tmp/arxiv_extract_$$ -type f | sort
echo ""
echo "=== 目录树 ==="
find /tmp/arxiv_extract_$$ -type d | sort
```

注意观察：
- 是否有独立的 appendix/supplementary 子目录
- 图片目录中是否有 appendix 专属的图片子目录（如 `figures/appendix/`、`figures/supp/`）
- 是否有多个子目录（如 `main/`、`appendix/`、`supplement/`）
- 根目录下文件是否很多（可能是扁平结构，所有 section 平铺在根目录）

#### 第 2 步：找到主编排文件

不同源码包的主文件命名各不相同，需要逐一检查：

```bash
# 常见主文件命名（按优先级）
ls /tmp/arxiv_extract_$$/main.tex 2>/dev/null
ls /tmp/arxiv_extract_$$/0_main.tex 2>/dev/null
ls /tmp/arxiv_extract_$$/paper.tex 2>/dev/null
ls /tmp/arxiv_extract_$$/article.tex 2>/dev/null
ls /tmp/arxiv_extract_$$/root.tex 2>/dev/null
ls /tmp/arxiv_extract_$$/*.tex 2>/dev/null | head -5
```

如果没有明显的主文件名，查看每个候选 `.tex` 文件中是否包含 `\documentclass`——包含它的就是主文件。

#### 第 3 步：阅读主文件，理解文档编排结构

**这是最关键的一步。** 必须完整阅读主 `.tex` 文件，理解论文是如何组织各个部分的。

在主文件中重点查找：

1. **`\include{...}` 和 `\input{...}` 命令**：这些命令将其他 `.tex` 文件引入主文档。列出所有被引入的文件，它们构成了论文的完整结构。

2. **`\appendix` 命令**：这个 LaTeX 命令标记正文结束、附录开始。它之后的所有 `\section` 都会变成附录章节（如 "Appendix A"）。这是判断附录边界的最可靠标志。

3. **文档结构组织方式**：不同论文的组织方式差异极大：
   - **模式 a（集中编排）**：主文件中使用 `\include{intro}`、`\include{method}`、...、`\include{appendix}`，每个 section 一个文件
   - **模式 b（内联编排）**：所有内容都在主文件中，`\appendix` 命令后面的所有内容都是附录
   - **模式 c（分目录编排）**：正文在 `main/` 子目录，附录在 `appendix/` 子目录
   - **模式 d（扁平编排）**：所有 `.tex` 文件都在根目录，文件名可能按数字前缀或描述性命名
   - **模式 e（无显式附录）**：某些论文可能没有 `\appendix` 命令，但有些文件内容明显是补充材料

#### 第 4 步：追踪 include/input 链，确定每个文件的归属

对于主文件中 `\include{...}` 或 `\input{...}` 引用的每个文件，确认它属于正文还是附录：

1. **对于 `\appendix` 命令之后的 `\include`/`\input`**：
   - 这些文件 100% 是附录内容，直接排除

2. **对于 `\appendix` 命令之后的直接内容**（非 include/input）：
   - `\appendix` 之后到 `\end{document}` 之间的所有直接内容都是附录，需要截断

3. **检查被 include 的文件内容**：
   - 如果主文件中没有 `\appendix` 命令，但某个被 include 的文件开头就定义了附录章节（如 `\section{Appendix}`），则它或其所在位置之后的文件可能是附录
   - 打开每个被 include 的文件，查看其章节标题，判断属于论文的哪个部分

4. **检查是否有多级 include**：
   - 被 include 的文件可能又 include 了其他文件（如 appendix.tex 中又 `\input{appendix-A}`、`\input{appendix-B}`）
   - 需要追踪完整的引用链

#### 第 5 步：处理 `\appendix` 命令

如果主文件中存在 `\appendix` 命令：

1. **截断主文件**：`\appendix` 及其后的所有内容都不保留到 source/
2. **注释掉 include 引用**：如果主文件中有 `\include{appendix}` 或 `\input{appendix}` 等引用，注释掉这些行（加 `%` 前缀）
3. **保留 `.full_backup`**：完整的主文件保存为备份

#### 第 6 步：识别并排除附录文件

综合以上信息，确定哪些文件是附录：

| 判断依据 | 置信度 | 处理方式 |
|---------|--------|---------|
| 被主文件 `\appendix` 之后的 `\include`/`\input` 引用 | 确定 | 排除 |
| 文件名含 "appendix"、"supplementary"、"supp" | 高 | 排除（但仍需阅读内容确认） |
| 文件内容以 `\section{Appendix}` 或 `\appendix` 开头 | 确定 | 排除 |
| 文件在独立的 appendix/supp 子目录中 | 高 | 排除 |
| 文件内容为补充材料性质（如完整的 prompt 列表、额外实验表格等） | 高 | 排除 |
| 文件在 References 之后被引用，且内容为补充性质 | 中高 | 视情况排除 |

**重要：不要只看文件名。** 有些论文的附录文件可能叫 `experiments_details.tex`、`full_prompts.tex`、`extra_results.tex` 等，文件名中没有 "appendix" 关键词。必须通过阅读主文件中的引用位置和文件内容来判断。

#### 第 7 步：检查是否有需要保留的"后附录"内容

少数论文在附录之后还有 Acknowledgements、Author Contributions 等内容。如果这些内容在主文件的 `\appendix` 之后但在另一个独立文件中，需要保留它们。

#### 第 8 步：执行剥离并复制到 source/

确认所有附录文件后：

1. **不复制**附录相关的 `.tex` 文件到 source/
2. **不复制**附录图片目录到 images/（如果图片提取还未执行，在提取图片时跳过附录图片目录）
3. 复制所有非附录文件（`.tex`、`.bib`、`.sty`、`.cls`、`.bst`、`.bbl`）到 source/
4. 如果主文件被截断，保存截断后的版本到 source/，完整版保留为 `.full_backup`

---

## 附录结构常见变体

Agent 在探索过程中要注意以下常见模式：

### 变体 1：独立的 appendix.tex + 子文件
```
main.tex        → \include{intro}, \include{method}, ..., \include{appendix}
appendix.tex    → \input{appendix-A}, \input{appendix-B}, \input{appendix-C}
appendix-A.tex
appendix-B.tex
appendix-C.tex
```
处理：排除 appendix.tex 及所有 appendix-*.tex

### 变体 2：主文件中内联 \appendix
```
main.tex
  ... 正文内容 ...
  \appendix
  \section{Experimental Details}
  ... 大量附录内容 ...
  \end{document}
```
处理：截断 `\appendix` 之后的所有内容

### 变体 3：分目录组织
```
main/
  main.tex, intro.tex, method.tex, ...
appendix/
  appendix.tex, extra_experiments.tex, ...
```
处理：排除整个 appendix/ 目录

### 变体 4：扁平结构，无显式附录标记
```
main.tex
intro.tex
method.tex
results.tex
discussion.tex
supplementary.tex    ← 内容全是补充实验，但文件名不含 "appendix"
extra_tables.tex     ← 独立文件，内容为额外数据表
```
处理：必须阅读每个文件的章节标题和内容来判断。主文件中可能有 `\include{supplementary}` 在参考文献之后，结合上下文判断。

### 变体 5：超长论文（如 66 页正文 + 附录）
这是最容易出问题的场景。正文可能只有 10 页，但附录有 50+ 页和大量图片。如果附录没有被正确剥离，layout 分析、精读笔记等所有下游 agent 都会处理大量无意义内容。

处理：对于长论文尤其需要仔细探索。先找到主文件，确认 `\appendix` 的位置或附录文件的引用位置，确保正文和附录的边界被准确识别。

---

## 保守原则

- 如果不确定某段内容或某个文件是否为附录，**保留它**（宁可多消耗 token 也不错删正文）
- 如果 References 之后找不到明显附录标记，检查全文是否有 `\appendix` 或 `# Appendix` 等标记
- 总是保留 `.full_backup` 备份
- **但也不要因为保守就不去探索。** 探索目录结构、阅读主文件的 include 关系，是判断附录的必要步骤，不能跳过
