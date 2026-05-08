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

### 3.5 公式特殊字符转义（重要）
公式中的某些符号与 HTML 语法冲突，必须转义：
- `<` → `\lt`（否则被解析为 HTML 标签开始）
- `>` → `\gt`（否则被解析为 HTML 标签结束）
- `&` → `&amp;`（否则被解析为 HTML 实体开始）
- `\left<` → `\left\langle`，`\right>` → `\right\rangle`
- `\leq`、`\geq` 等 LaTeX 命令本身安全，不需要处理

扫描所有 `$...$` 和 `$$...$$` 中的文本，执行上述替换。

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
