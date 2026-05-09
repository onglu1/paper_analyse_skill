# 附录剥离方法论

本文件定义了从论文中智能剥离附录的统一方法，适用于 LaTeX 源码包和 MinerU 转换后的 Markdown 两种输入形式。

## 核心原则

附录剥离必须在 **保存 source 文件之前** 完成，确保后续所有下游 agent（精读、简要版、PPT、HTML 等）都不会读到附录内容，从而节约 token 和处理时间。

剥离过程不是简单的正则匹配，而是让 agent 阅读内容、自主判断附录边界。

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

5. **保留备份**
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

arXiv 源码包中，附录通常以独立文件形式存在，而不是嵌入主文件中。

### 步骤

1. **列出解压目录结构**
   ```bash
   find /tmp/arxiv_extract_$$ -type f -name "*.tex" | sort
   ```

2. **Agent 自主判断哪些文件是附录**
   检查每个 `.tex` 文件：
   - 文件名包含 "appendix"、"supplementary"、"supp" → 高度疑似附录
   - 文件名不明确时，读取文件开头内容判断：
     - 开头有 `\section{Appendix}` 或 `\appendix` → 确认是附录
     - 开头是常规 section 如 `\section{Introduction}` → 不是附录
   - 如果某文件被主文件通过 `\include{appendix}` 引用，确认是附录

3. **处理主 `.tex` 文件**
   即使附录是独立文件，主 `.tex` 中也可能有 `\appendix` 命令：
   - 搜索 `\appendix` 命令，截断其后内容
   - 搜索 `\include{appendix}`、`\input{appendix}` 等引用，注释掉

4. **附录文件不复制到 source/，截断后的主文件保存到 source/**

5. **保留完整备份**（`.full_backup`）

### 示例

解压目录文件列表：
```
main.tex
introduction.tex
method.tex
experiments.tex
appendix.tex        ← agent 判断：文件名含 "appendix"，确认为附录，不复制
acknowledgments.tex
```

---

## 保守原则

- 如果不确定某段内容是否为附录，保留它（宁可多消耗 token 也不错删正文）
- 如果 References 之后找不到明显附录标记，检查全文是否有 `\appendix` 或 `# Appendix` 等标记
- 总是保留 `.full_backup` 备份
