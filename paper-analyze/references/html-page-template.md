# HTML 长页面模板规范

## 核心定位

基于精读笔记生成单页滚动式 HTML，带侧边导航栏、图片点击放大、公式渲染（KaTeX）、代码高亮等交互效果。适合在浏览器中阅读完整的论文解读。

## 功能清单

| 功能 | 实现方式 |
|------|----------|
| 侧边导航栏 | 固定定位，IntersectionObserver 跟随滚动高亮 |
| 图片点击放大 | Lightbox overlay，ESC/点击关闭 |
| 公式渲染 | KaTeX CDN，auto-render 扩展 |
| 代码高亮 | highlight.js CDN |
| 响应式设计 | 768px 断点，汉堡菜单切换侧边栏 |
| 术语悬停提示 | Tooltip，从 glossary JSON 查找 |
| 回到顶部按钮 | 滚动超过 300px 显示 |
| 阅读进度条 | 顶部固定，宽度随滚动比例变化 |
| 内容宽度调节 | 右侧按钮展开面板，拖动滑块/预设按钮调节宽度，localStorage 持久化 |

## 配色方案

```
--bg: #fafafa          /* 页面背景 */
--text: #333           /* 正文颜色 */
--sidebar-bg: #f0f0f0  /* 侧边栏背景 */
--primary: #2563eb     /* 主题色 */
--code-bg: #f5f5f5     /* 代码块背景 */
```

## 模板文件位置

> **注意：** 完整 HTML 模板已提取到 `${skill_dir}/templates/page.html`，子 Agent 不需要复制模板。
> 子 Agent 只需生成内容片段文件，然后调用 `scripts/assemble_html_page.py` 组装。


## Glossary Tooltip 实现说明

### 数据来源

从 `glossary.md` 中提取术语及其解释，转换为 JavaScript 对象嵌入 HTML：

```javascript
const glossary = {
  "GRPO": "Group Relative Policy Optimization。一种基于组内相对排序的策略优化算法。",
  "G-Designer": "一种用图神经网络自动生成 MAS 通信拓扑的方法。"
};
```

### 标记转换

精读笔记中的 `[[glossary#概念名|概念名]]` 在 HTML 中转换为：

```html
<span class="glossary-term" data-term="概念名">概念名</span>
```

## 子 Agent 使用指南

子 agent 基于此模板生成最终 HTML 文件时，按以下步骤操作：

### 步骤 1：读取精读笔记

读取对应论文的精读笔记 Markdown 文件，获取全部正文内容。

### 步骤 2：Markdown 转 HTML

将 Markdown 结构转换为 HTML 元素：

| Markdown | HTML |
|----------|------|
| `## 标题` | `<h2 id="section-x">标题</h2>` |
| `### 子标题` | `<h3 id="section-x-y">子标题</h3>` |
| `#### 小标题` | `<h4>小标题</h4>` |
| 段落文本 | `<p>文本</p>` |
| `- 列表项` | `<ul><li>列表项</li></ul>` |
| `1. 有序列表` | `<ol><li>有序列表</li></ol>` |
| `> 引用` | `<blockquote>引用</blockquote>` |
| `` `代码` `` | `<code>代码</code>` |
| 代码块 | `<pre><code class="language-xxx">...</code></pre>` |

### 步骤 3：提取 Glossary 数据

从 `glossary.md` 中读取术语定义，生成 JavaScript 对象，替换模板中的 `{{GLOSSARY_DATA}}` 占位符。

### 步骤 4：转换术语标记

将正文中所有 `[[glossary#概念名|概念名]]` 替换为：
```html
<span class="glossary-term" data-term="概念名">概念名</span>
```

### 步骤 5：处理图片引用

将 Markdown 图片语法转换为 HTML：
```
![描述](images/fig1.png)  →  <img src="images/fig1.png" alt="描述">
```

### 步骤 6：生成侧边栏导航

从所有 `<h2>` 和 `<h3>` 标签提取标题文本和 id，生成导航列表：
```html
<li><a href="#section-1">研究背景</a></li>
<li><a href="#section-1-1" class="sub-item">问题定义</a></li>
```

替换模板中的 `{{NAV_ITEMS}}` 占位符。

### 步骤 7：公式中的 HTML 特殊字符转义（重要）

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

### 步骤 8：填充并输出

- 替换 `{{PAPER_TITLE}}` 为论文标题
- 替换 `{{CONTENT}}` 为转换后的 HTML 正文
- 替换 `{{NAV_ITEMS}}` 为导航列表
- 替换 `{{GLOSSARY_DATA}}` 为术语 JSON
- 输出为单个 `.html` 文件，保存在论文对应目录下
