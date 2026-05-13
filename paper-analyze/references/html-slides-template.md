# HTML 幻灯片模板规范

## 核心定位

基于 PPT 大纲（Marp 格式）生成单页 HTML 文件，内嵌 CSS/JS，实现类似 reveal.js 的翻页效果。完全自包含，不依赖任何外部 CDN。

## 功能清单

1. 键盘翻页（ArrowLeft / ArrowRight / Space）
2. 进度条显示当前页/总页数
3. 图片展示（点击放大查看）
4. 响应式设计（适配不同屏幕尺寸）
5. 过渡动画（淡入淡出）
6. 全屏模式（F 键切换）

## 设计规范

- 配色方案：深色背景 + 浅色文字（适合投影环境）
- 图片使用相对路径：`images/xxx.png`（images/ 文件夹与 HTML 文件同级）
- 完全自包含：所有 CSS 和 JS 内嵌在 HTML 中

## 模板文件位置

> **注意：** 完整 HTML 模板已提取到 `${skill_dir}/templates/slides.html`，子 Agent 不需要复制模板。
> 子 Agent 只需生成 sections 片段文件，然后调用 `scripts/assemble_html_slides.py` 组装。


## 子 agent 使用说明

### 转换流程

1. **读取 PPT 大纲**：解析 Marp 格式的 markdown 文件
2. **分割页面**：以 `---` 为分隔符，将内容拆分为多个页面
3. **逐页转换**：将每个页面转换为一个 `<section class="slide">` 元素
4. **处理图片**：将 Marp 的 `![](xxx.png)` 转换为 `<img src="images/xxx.png">`
5. **输出文件**：生成单个 `.html` 文件

### 转换规则

| Marp 格式 | HTML 输出 |
|-----------|-----------|
| `# 标题` | `<h1>标题</h1>` |
| `## 标题` | `<h2>标题</h2>` |
| `### 标题` | `<h3>标题</h3>` |
| `- 要点` | `<ul><li>要点</li></ul>` |
| `![](fig.png)` | `<img src="images/fig.png" alt="fig">` |
| `---` | 新的 `<section class="slide">` |
| `` `code` `` | `<pre><code>code</code></pre>` |

### 注意事项

1. 第一个 `<section>` 默认添加 `class="active"`，其余不加
2. 每个 `<section>` 内部用 `<div class="slide-content">` 包裹内容
3. 图片路径统一使用 `images/` 前缀（相对路径）
4. 如果 Marp 中有 `bg` 类图片指令，转换为该页的背景样式
5. 保持模板中的所有 CSS 和 JS 不变，只替换 `<div class="slide-container">` 内的 `<section>` 元素
6. `{{TITLE}}` 替换为论文标题

### 公式中的 HTML 特殊字符转义（重要）

数学公式中的某些符号与 HTML 语法冲突，如果直接写入 HTML 会导致浏览器将其解析为标签或实体，造成公式渲染失败或页面结构破坏。**在将公式写入 HTML 时，必须对以下符号进行转义：**

| LaTeX 原始写法 | HTML 中必须替换为 | 说明 |
|---------------|-----------------|------|
| `<` | `\lt` | 小于号，会被解析为 HTML 标签开始 |
| `>` | `\gt` | 大于号，会被解析为 HTML 标签结束 |
| `\left<` | `\left\langle` | 左尖括号定界符 |
| `\right>` | `\right\rangle` | 右尖括号定界符 |
| `&` | `&amp;` | 与号，会被解析为 HTML 实体开始 |
| `"` 在属性值中 | `&quot;` | 引号，在 HTML 属性中需要转义 |
| `\leq` | `\leq`（保持不变） | 小于等于，本身安全 |
| `\geq` | `\geq`（保持不变） | 大于等于，本身安全 |

**示例：**
- 错误：`$x < y$` → 浏览器可能将 `< y$` 解析为未知标签
- 正确：`$x \lt y$`
- 错误：`$P(A|B) > 0.5$`
- 正确：`$P(A|B) \gt 0.5$`
- 错误：`$a & b$`
- 正确：`$a &amp; b$`（或在 KaTeX 中直接避免裸 `&`）

**规则：在生成 HTML 文件时，扫描所有公式内容（`$...$` 和 `$$...$$` 中的文本），将裸 `<` 替换为 `\lt`，裸 `>` 替换为 `\gt`，裸 `&` 替换为 `&amp;`，`\left<` 替换为 `\left\langle`，`\right>` 替换为 `\right\rangle`。注意不要误替换已经是 LaTeX 命令的部分（如 `\leq`、`\geq` 不需要处理）。**
