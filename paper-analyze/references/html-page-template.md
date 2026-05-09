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

## 基础 HTML 模板

以下为完整模板骨架，子 agent 在此基础上填充正文内容和 glossary 数据。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{PAPER_TITLE}} - 论文精读</title>

  <!-- KaTeX -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>

  <!-- Highlight.js -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/github.min.css">
  <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"></script>

  <style>
    /* === CSS Variables === */
    :root {
      --primary: #2563eb;
      --bg: #fafafa;
      --text: #333;
      --sidebar-bg: #f0f0f0;
      --sidebar-width: 260px;
      --content-width: 800px;
      --code-bg: #f5f5f5;
      --border: #e0e0e0;
      --radius: 6px;
    }

    /* === Reset & Base === */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans SC", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.8;
      font-size: 16px;
    }

    /* === Progress Bar === */
    .progress-bar {
      position: fixed;
      top: 0;
      left: 0;
      height: 3px;
      background: var(--primary);
      width: 0%;
      z-index: 1000;
      transition: width 0.1s linear;
    }

    /* === Sidebar === */
    .sidebar {
      position: fixed;
      top: 0;
      left: 0;
      width: var(--sidebar-width);
      height: 100vh;
      background: var(--sidebar-bg);
      border-right: 1px solid var(--border);
      overflow-y: auto;
      padding: 2rem 1rem;
      z-index: 100;
    }
    .sidebar h2 {
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #666;
      margin-bottom: 1rem;
    }
    .sidebar ul { list-style: none; }
    .sidebar li { margin-bottom: 0.4rem; }
    .sidebar a {
      text-decoration: none;
      color: #555;
      font-size: 0.9rem;
      display: block;
      padding: 0.25rem 0.5rem;
      border-radius: var(--radius);
      transition: all 0.2s;
    }
    .sidebar a:hover { color: var(--primary); background: rgba(37, 99, 235, 0.05); }
    .sidebar a.active {
      color: var(--primary);
      background: rgba(37, 99, 235, 0.1);
      font-weight: 600;
    }
    .sidebar .sub-item { padding-left: 1.2rem; font-size: 0.85rem; }

    /* === Hamburger Menu (mobile) === */
    .hamburger {
      display: none;
      position: fixed;
      top: 1rem;
      left: 1rem;
      z-index: 200;
      background: var(--primary);
      color: #fff;
      border: none;
      border-radius: var(--radius);
      width: 40px;
      height: 40px;
      font-size: 1.2rem;
      cursor: pointer;
    }

    /* === Main Content === */
    .content-wrapper {
      margin-left: var(--sidebar-width);
      display: flex;
      justify-content: center;
      min-height: 100vh;
    }
    .content {
      max-width: var(--content-width);
      width: 100%;
      padding: 3rem 2rem;
    }
    .content h1 { font-size: 2rem; margin-bottom: 0.5rem; }
    .content h2 {
      font-size: 1.5rem;
      margin-top: 3rem;
      margin-bottom: 1rem;
      padding-bottom: 0.5rem;
      border-bottom: 2px solid var(--primary);
    }
    .content h3 { font-size: 1.2rem; margin-top: 2rem; margin-bottom: 0.8rem; }
    .content p { margin-bottom: 1rem; }
    .content ul, .content ol { margin-bottom: 1rem; padding-left: 1.5rem; }
    .content li { margin-bottom: 0.4rem; }
    .content img {
      max-width: 100%;
      border-radius: var(--radius);
      cursor: pointer;
      transition: transform 0.2s;
      margin: 1rem 0;
    }
    .content img:hover { transform: scale(1.02); }
    .content pre {
      background: var(--code-bg);
      border-radius: var(--radius);
      padding: 1rem;
      overflow-x: auto;
      margin-bottom: 1rem;
    }
    .content code {
      font-family: "JetBrains Mono", "Fira Code", monospace;
      font-size: 0.9em;
    }
    .content blockquote {
      border-left: 4px solid var(--primary);
      padding: 0.5rem 1rem;
      margin: 1rem 0;
      background: rgba(37, 99, 235, 0.03);
      border-radius: 0 var(--radius) var(--radius) 0;
    }

    /* === Glossary Term === */
    .glossary-term {
      border-bottom: 1px dashed var(--primary);
      cursor: help;
      position: relative;
    }

    /* === Tooltip === */
    .tooltip {
      position: absolute;
      background: #222;
      color: #fff;
      padding: 0.5rem 0.8rem;
      border-radius: var(--radius);
      font-size: 0.85rem;
      max-width: 300px;
      line-height: 1.5;
      z-index: 500;
      pointer-events: none;
      opacity: 0;
      transition: opacity 0.2s;
    }
    .tooltip::after {
      content: "";
      position: absolute;
      top: 100%;
      left: 1rem;
      border: 6px solid transparent;
      border-top-color: #222;
    }
    .tooltip.visible { opacity: 1; }

    /* === Lightbox === */
    .lightbox {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.85);
      z-index: 900;
      justify-content: center;
      align-items: center;
      cursor: zoom-out;
    }
    .lightbox.active { display: flex; }
    .lightbox img {
      max-width: 90vw;
      max-height: 90vh;
      border-radius: var(--radius);
    }

    /* === Back to Top === */
    .back-to-top {
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background: var(--primary);
      color: #fff;
      border: none;
      font-size: 1.2rem;
      cursor: pointer;
      opacity: 0;
      transform: translateY(10px);
      transition: opacity 0.3s, transform 0.3s;
      z-index: 100;
    }
    .back-to-top.visible { opacity: 1; transform: translateY(0); }

    /* === Width Slider Panel === */
    .width-toggle {
      position: fixed;
      right: 0;
      top: 50%;
      transform: translateY(-50%);
      width: 28px;
      height: 72px;
      background: var(--primary);
      color: #fff;
      border: none;
      border-radius: 6px 0 0 6px;
      cursor: pointer;
      z-index: 201;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.75rem;
      writing-mode: vertical-lr;
      letter-spacing: 0.1em;
      transition: right 0.3s;
      box-shadow: -1px 0 4px rgba(0,0,0,0.1);
    }
    .width-toggle.shifted { right: 260px; }
    .width-toggle:hover { background: #1d4ed8; }

    .width-panel {
      position: fixed;
      right: -280px;
      top: 0;
      width: 280px;
      height: 100vh;
      background: #fff;
      border-left: 1px solid var(--border);
      z-index: 200;
      padding: 2rem 1.5rem;
      transition: right 0.3s ease;
      box-shadow: -2px 0 12px rgba(0,0,0,0.06);
      display: flex;
      flex-direction: column;
    }
    .width-panel.open { right: 0; }

    .width-panel h3 {
      font-size: 0.95rem;
      margin-bottom: 2rem;
      color: #444;
      font-weight: 600;
    }

    .width-panel label {
      display: block;
      font-size: 0.85rem;
      margin-bottom: 0.6rem;
      color: #666;
    }

    .width-panel input[type="range"] {
      width: 100%;
      margin-bottom: 0.4rem;
      accent-color: var(--primary);
    }

    .width-panel .width-value {
      text-align: center;
      font-size: 1.1rem;
      color: var(--primary);
      font-weight: 700;
      margin-bottom: 2rem;
    }

    .width-panel .preset-btns {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1rem;
    }
    .width-panel .preset-btns button {
      flex: 1;
      padding: 0.4rem 0;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      cursor: pointer;
      font-size: 0.8rem;
      color: #555;
      transition: all 0.15s;
    }
    .width-panel .preset-btns button:hover {
      background: var(--primary);
      color: #fff;
      border-color: var(--primary);
    }

    .width-panel .reset-btn {
      width: 100%;
      padding: 0.6rem;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      cursor: pointer;
      font-size: 0.85rem;
      color: #666;
      transition: all 0.15s;
    }
    .width-panel .reset-btn:hover {
      background: #e5e5e5;
    }

    /* === Responsive === */
    @media (max-width: 768px) {
      .sidebar { transform: translateX(-100%); transition: transform 0.3s; }
      .sidebar.open { transform: translateX(0); }
      .hamburger { display: block; }
      .content-wrapper { margin-left: 0; }
      .content { padding: 2rem 1rem; padding-top: 4rem; max-width: 100%; }
      .width-toggle { display: none; }
      .width-panel { display: none; }
    }
  </style>
</head>
<body>

  <!-- Progress bar -->
  <div class="progress-bar"></div>

  <!-- Mobile hamburger -->
  <button class="hamburger" aria-label="Toggle navigation">&#9776;</button>

  <!-- Sidebar navigation -->
  <aside class="sidebar">
    <h2>目录</h2>
    <ul>
      <!-- {{NAV_ITEMS}} -->
      <!-- Example:
      <li><a href="#section-1">1. 研究背景</a></li>
      <li><a href="#section-2" class="sub-item">1.1 问题定义</a></li>
      -->
    </ul>
  </aside>

  <!-- Width slider toggle -->
  <button class="width-toggle" aria-label="Adjust content width" title="调节内容宽度">宽 度</button>

  <!-- Width slider panel -->
  <aside class="width-panel">
    <h3>内容宽度调节</h3>
    <label for="width-slider">文章区域宽度</label>
    <input type="range" id="width-slider" min="500" max="1200" value="800" step="10">
    <div class="width-value" id="width-display">800px</div>
    <div class="preset-btns">
      <button data-width="600">窄</button>
      <button data-width="800">标准</button>
      <button data-width="1000">宽</button>
      <button data-width="1200">超宽</button>
    </div>
    <button class="reset-btn" id="reset-width">恢复默认</button>
  </aside>

  <!-- Main content -->
  <div class="content-wrapper">
  <main class="content">
    <!-- {{CONTENT}} -->
    <!-- Sub-agent fills paper content here -->
  </main>
  </div>

  <!-- Lightbox overlay -->
  <div class="lightbox">
    <img src="" alt="Enlarged image">
  </div>

  <!-- Tooltip -->
  <div class="tooltip"></div>

  <!-- Back to top -->
  <button class="back-to-top" aria-label="Back to top">&#8593;</button>

  <script>
    // === Glossary Data ===
    const glossary = {
      // {{GLOSSARY_DATA}}
      // Example:
      // "GRPO": "Group Relative Policy Optimization。一种基于组内相对排序的策略优化算法。",
      // "G-Designer": "一种用图神经网络自动生成 MAS 通信拓扑的方法。"
    };

    // === DOM References ===
    const sidebar = document.querySelector('.sidebar');
    const hamburger = document.querySelector('.hamburger');
    const progressBar = document.querySelector('.progress-bar');
    const backToTop = document.querySelector('.back-to-top');
    const lightbox = document.querySelector('.lightbox');
    const lightboxImg = lightbox.querySelector('img');
    const tooltip = document.querySelector('.tooltip');
    const navLinks = document.querySelectorAll('.sidebar a');
    const sections = document.querySelectorAll('.content h2, .content h3');

    // === Intersection Observer: highlight current section in sidebar ===
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.getAttribute('id');
          navLinks.forEach(link => {
            link.classList.toggle('active', link.getAttribute('href') === '#' + id);
          });
        }
      });
    }, { rootMargin: '-20% 0px -60% 0px' });

    sections.forEach(section => observer.observe(section));

    // === Scroll: progress bar + back-to-top visibility ===
    window.addEventListener('scroll', () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      progressBar.style.width = progress + '%';
      backToTop.classList.toggle('visible', scrollTop > 300);
    });

    // === Back to top ===
    backToTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // === Lightbox: click image to enlarge ===
    document.querySelectorAll('.content img').forEach(img => {
      img.addEventListener('click', () => {
        lightboxImg.src = img.src;
        lightbox.classList.add('active');
      });
    });

    lightbox.addEventListener('click', () => {
      lightbox.classList.remove('active');
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') lightbox.classList.remove('active');
    });

    // === Glossary Tooltip ===
    document.querySelectorAll('.glossary-term').forEach(term => {
      term.addEventListener('mouseenter', (e) => {
        const key = e.target.dataset.term;
        const definition = glossary[key];
        if (!definition) return;
        tooltip.textContent = definition;
        tooltip.classList.add('visible');
        const rect = e.target.getBoundingClientRect();
        tooltip.style.left = rect.left + 'px';
        tooltip.style.top = (rect.top - tooltip.offsetHeight - 10 + window.scrollY) + 'px';
      });
      term.addEventListener('mouseleave', () => {
        tooltip.classList.remove('visible');
      });
    });

    // === Mobile hamburger toggle ===
    hamburger.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });

    // === Width Slider ===
    const widthToggle = document.querySelector('.width-toggle');
    const widthPanel = document.querySelector('.width-panel');
    const widthSlider = document.getElementById('width-slider');
    const widthDisplay = document.getElementById('width-display');
    const resetBtn = document.getElementById('reset-width');
    const presetBtns = document.querySelectorAll('.preset-btns button');
    const root = document.documentElement;

    const DEFAULT_WIDTH = 800;
    const STORAGE_KEY = 'html-page-content-width';

    function setContentWidth(w) {
      const val = parseInt(w);
      root.style.setProperty('--content-width', val + 'px');
      widthSlider.value = val;
      widthDisplay.textContent = val + 'px';
      localStorage.setItem(STORAGE_KEY, val);
    }

    // Load saved width
    (function() {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        setContentWidth(saved);
        widthSlider.value = saved;
      }
    })();

    widthToggle.addEventListener('click', () => {
      const isOpen = widthPanel.classList.toggle('open');
      widthToggle.classList.toggle('shifted', isOpen);
    });

    widthSlider.addEventListener('input', () => {
      setContentWidth(widthSlider.value);
    });

    resetBtn.addEventListener('click', () => {
      setContentWidth(DEFAULT_WIDTH);
    });

    presetBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        setContentWidth(btn.dataset.width);
      });
    });

    // Close panel on Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        widthPanel.classList.remove('open');
        widthToggle.classList.remove('shifted');
      }
    });

    // Close panel when clicking outside
    document.addEventListener('click', (e) => {
      if (!widthPanel.contains(e.target) && !widthToggle.contains(e.target) && !e.target.closest('.width-toggle')) {
        widthPanel.classList.remove('open');
        widthToggle.classList.remove('shifted');
      }
    });

    // === Initialize KaTeX auto-render ===
    document.addEventListener('DOMContentLoaded', () => {
      if (typeof renderMathInElement !== 'undefined') {
        renderMathInElement(document.body, {
          delimiters: [
            { left: '$$', right: '$$', display: true },
            { left: '$', right: '$', display: false }
          ]
        });
      }
      // Initialize highlight.js
      if (typeof hljs !== 'undefined') {
        hljs.highlightAll();
      }
    });
  </script>
</body>
</html>
```

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
