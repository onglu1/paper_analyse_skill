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
      max-width: 800px;
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

    /* === Responsive === */
    @media (max-width: 768px) {
      .sidebar { transform: translateX(-100%); transition: transform 0.3s; }
      .sidebar.open { transform: translateX(0); }
      .hamburger { display: block; }
      .content-wrapper { margin-left: 0; }
      .content { padding: 2rem 1rem; padding-top: 4rem; }
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

### 步骤 7：填充并输出

- 替换 `{{PAPER_TITLE}}` 为论文标题
- 替换 `{{CONTENT}}` 为转换后的 HTML 正文
- 替换 `{{NAV_ITEMS}}` 为导航列表
- 替换 `{{GLOSSARY_DATA}}` 为术语 JSON
- 输出为单个 `.html` 文件，保存在论文对应目录下
