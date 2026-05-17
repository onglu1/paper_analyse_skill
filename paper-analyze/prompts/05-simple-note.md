你的任务是基于精读笔记生成简要版笔记。

## 输入
- 论文输出目录: ${paper_dir}
- 论文标题: ${paper_title}
- Skill 目录: ${skill_dir}

## 必读参考文件

在开始撰写前，必须读取以下文件理解写作规范：
1. `${skill_dir}/references/simple-template.md` — 简要版规范和 5 部分结构
2. `${skill_dir}/references/note-template.md`（第6节：图片 HTML 模板）— 图片排版 HTML 模板（单图、并排图、多图网格）
3. `${skill_dir}/references/note-structure.md`（第5节：Frontmatter 格式）— frontmatter 字段值约束规则

## 处理步骤

### 1. 读取精读笔记和 glossary
- 读取 `${paper_dir}/${safe_title}.md`（精读笔记）
- 读取 `${paper_dir}/glossary.md`（概念速查）

### 2. 查看可用图片
列出 `${paper_dir}/images/` 中的所有图片，选择最适合简要版的图片：
- 框架图/架构图（必选）
- 原理示意图（如有）
- 实验结果对比图（选最关键的 1-3 张）
- case study / 可视化图（选最有说服力的 1-2 张）
- 跳过：细节表格截图、大段公式截图

同时读取 `${paper_dir}/image_layout.json`，在插入图片时按其中的布局信息排版：
- 使用 HTML 内嵌方式（与精读笔记相同的 flex 布局模板）
- 并排图片保持并排，按 `relative_width` 设置 flex 比例
- 图注格式：灰色小字（`color: #888; font-size: 0.85em;`）、非斜体、紧贴图片下方
- 禁止使用 `![](images/xxx.png)` 的 Markdown 图片语法
- 具体 HTML 模板参见 `${skill_dir}/references/note-template.md` 的"图片引用格式"章节

### 3. 撰写简要版
严格按照 `simple-template.md` 中的 5 部分结构撰写，保存到 `${paper_dir}/${safe_title}-简要版.md`。

核心原则：
- 基于精读笔记生成，不重新理解原文
- 图片是主要内容载体，文字精简
- 控制在 5 分钟能讲完的篇幅
- 术语首次出现时必须解释

Frontmatter（从精读笔记提取，遵守 `note-structure.md` 第五节约束）：

```yaml
---
title: 论文标题（已去除冒号、引号等特殊字符，只保留中英文字母和空格）
year: 2026
venue: 发表来源（只允许中英文字母和空格）
paper_type: system
tags:
  - 论文笔记
  - 简要版
---
```

**字段值约束：** `title` 和 `venue` 的值只允许中文字符、英文字母和空格。冒号 `:` 替换为空格，引号删除，其他特殊符号替换为空格。`paper_type` 只允许 `system` 或 `method`。

## 输出
完成后报告：
- 简要版路径
- 使用的图片数量
- 笔记总字数
