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

## 基础 HTML 模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}}</title>
    <style>
        /* ===== CSS Variables for Theme ===== */
        :root {
            --primary-color: #4fc3f7;
            --bg-color: #1a1a2e;
            --text-color: #e0e0e0;
            --heading-color: #ffffff;
            --accent-color: #ff6b6b;
            --code-bg: #2d2d44;
            --slide-max-width: 1100px;
            --transition-duration: 0.4s;
        }

        /* ===== Reset & Base ===== */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg-color);
            color: var(--text-color);
            overflow: hidden;
            height: 100vh;
            width: 100vw;
        }

        /* ===== Slide Container ===== */
        .slide-container {
            position: relative;
            width: 100%;
            height: 100vh;
        }

        .slide {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 60px 80px;
            opacity: 0;
            pointer-events: none;
            transition: opacity var(--transition-duration) ease-in-out;
        }

        .slide.active {
            opacity: 1;
            pointer-events: auto;
        }

        .slide-content {
            max-width: var(--slide-max-width);
            width: 100%;
        }

        /* ===== Typography ===== */
        h1 {
            font-size: 2.8em;
            color: var(--heading-color);
            margin-bottom: 0.5em;
            text-align: center;
        }

        h2 {
            font-size: 2.2em;
            color: var(--primary-color);
            margin-bottom: 0.6em;
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 0.2em;
        }

        h3 {
            font-size: 1.6em;
            color: var(--heading-color);
            margin-bottom: 0.4em;
        }

        ul {
            list-style: none;
            padding-left: 0;
        }

        ul li {
            font-size: 1.3em;
            line-height: 1.8;
            padding-left: 1.2em;
            position: relative;
            margin-bottom: 0.3em;
        }

        ul li::before {
            content: "▸";
            color: var(--primary-color);
            position: absolute;
            left: 0;
        }

        p {
            font-size: 1.2em;
            line-height: 1.6;
            margin-bottom: 0.8em;
        }

        /* ===== Code Block ===== */
        pre {
            background: var(--code-bg);
            border-radius: 8px;
            padding: 1em 1.2em;
            overflow-x: auto;
            font-size: 0.95em;
            margin: 1em 0;
        }

        code {
            font-family: "Fira Code", "Consolas", monospace;
            color: #a5d6ff;
        }

        /* ===== Images ===== */
        .slide img {
            max-width: 80%;
            max-height: 60vh;
            border-radius: 8px;
            cursor: pointer;
            transition: transform 0.2s;
            display: block;
            margin: 0.5em auto;
        }

        .slide img:hover {
            transform: scale(1.02);
        }

        /* ===== Image Overlay (Lightbox) ===== */
        .img-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            cursor: pointer;
        }

        .img-overlay.visible {
            display: flex;
        }

        .img-overlay img {
            max-width: 95%;
            max-height: 95vh;
            border-radius: 4px;
        }

        /* ===== Progress Bar ===== */
        .progress-bar {
            position: fixed;
            bottom: 0;
            left: 0;
            height: 4px;
            background: var(--primary-color);
            transition: width 0.3s ease;
            z-index: 100;
        }

        .page-indicator {
            position: fixed;
            bottom: 12px;
            right: 20px;
            font-size: 0.9em;
            color: rgba(255, 255, 255, 0.5);
            z-index: 100;
        }

        /* ===== Responsive ===== */
        @media (max-width: 768px) {
            .slide {
                padding: 30px 20px;
            }
            h1 { font-size: 2em; }
            h2 { font-size: 1.6em; }
            ul li { font-size: 1.1em; }
            .slide img { max-width: 95%; }
        }

        @media (max-width: 480px) {
            h1 { font-size: 1.6em; }
            h2 { font-size: 1.3em; }
            ul li { font-size: 1em; }
        }
    </style>
</head>
<body>
    <!-- Slide Container -->
    <div class="slide-container">

        <!-- Slide 1: Title -->
        <section class="slide active">
            <div class="slide-content">
                <h1>{{TITLE}}</h1>
                <p style="text-align:center; color: var(--primary-color);">{{SUBTITLE}}</p>
            </div>
        </section>

        <!-- Slide 2: Example Content -->
        <section class="slide">
            <div class="slide-content">
                <h2>示例页面</h2>
                <ul>
                    <li>要点一</li>
                    <li>要点二</li>
                    <li>要点三</li>
                </ul>
            </div>
        </section>

        <!-- Slide 3: Image Example -->
        <section class="slide">
            <div class="slide-content">
                <h2>图片示例</h2>
                <img src="images/example.png" alt="示例图片">
            </div>
        </section>

    </div>

    <!-- Progress Bar -->
    <div class="progress-bar" id="progressBar"></div>
    <div class="page-indicator" id="pageIndicator"></div>

    <!-- Image Overlay -->
    <div class="img-overlay" id="imgOverlay">
        <img id="overlayImg" src="" alt="enlarged">
    </div>

    <script>
        // ===== State Management =====
        let currentSlide = 0;
        const slides = document.querySelectorAll('.slide');
        const totalSlides = slides.length;
        const progressBar = document.getElementById('progressBar');
        const pageIndicator = document.getElementById('pageIndicator');
        const imgOverlay = document.getElementById('imgOverlay');
        const overlayImg = document.getElementById('overlayImg');

        // ===== Navigation =====
        function goToSlide(index) {
            if (index < 0 || index >= totalSlides) return;
            slides[currentSlide].classList.remove('active');
            currentSlide = index;
            slides[currentSlide].classList.add('active');
            updateProgress();
        }

        function nextSlide() {
            goToSlide(currentSlide + 1);
        }

        function prevSlide() {
            goToSlide(currentSlide - 1);
        }

        // ===== Progress Update =====
        function updateProgress() {
            const progress = ((currentSlide + 1) / totalSlides) * 100;
            progressBar.style.width = progress + '%';
            pageIndicator.textContent = (currentSlide + 1) + ' / ' + totalSlides;
        }

        // ===== Keyboard Events =====
        document.addEventListener('keydown', function(e) {
            switch(e.key) {
                case 'ArrowRight':
                case ' ':
                    e.preventDefault();
                    nextSlide();
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    prevSlide();
                    break;
                case 'f':
                case 'F':
                    toggleFullscreen();
                    break;
                case 'Escape':
                    closeOverlay();
                    break;
            }
        });

        // ===== Fullscreen Toggle =====
        function toggleFullscreen() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        }

        // ===== Image Click to Enlarge =====
        document.querySelectorAll('.slide img').forEach(function(img) {
            img.addEventListener('click', function() {
                overlayImg.src = this.src;
                imgOverlay.classList.add('visible');
            });
        });

        imgOverlay.addEventListener('click', closeOverlay);

        function closeOverlay() {
            imgOverlay.classList.remove('visible');
        }

        // ===== Initialize =====
        updateProgress();
    </script>
</body>
</html>
```

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
