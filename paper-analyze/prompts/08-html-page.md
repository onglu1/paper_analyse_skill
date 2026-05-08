你的任务是基于精读笔记生成单页滚动式 HTML 长页面。

## 输入
- 论文输出目录: ${paper_dir}
- 论文标题: ${paper_title}
- Skill 目录: ${skill_dir}

## 必读参考文件

1. `${skill_dir}/references/html-page-template.md` — HTML 长页面版规范和模板骨架

## 处理步骤

### 1. 读取精读笔记和 glossary
- 读取 `${paper_dir}/${safe_title}.md`（精读笔记）
- 读取 `${paper_dir}/glossary.md`（概念速查）

### 2. 读取 HTML 模板骨架
从 `html-page-template.md` 中获取基础 HTML 模板。

### 3. 将 Markdown 转换为 HTML 内容
- 标题 → `<h1>` ~ `<h4>`
- 段落 → `<p>`
- 列表 → `<ul>/<ol>`
- 图片 → `<img>` + lightbox 支持
- 公式 → KaTeX 自动渲染（`$...$` 和 `$$...$$`）
- 代码块 → `<pre><code>` + highlight.js
- `[[glossary#概念名|概念名]]` → `<span class="glossary-term" data-term="概念名">概念名</span>`

### 3.5 公式特殊字符转义（重要）
公式中的某些符号与 HTML 语法冲突，必须转义：
- `<` → `\lt`（否则被解析为 HTML 标签开始）
- `>` → `\gt`（否则被解析为 HTML 标签结束）
- `&` → `&amp;`（否则被解析为 HTML 实体开始）
- `\left<` → `\left\langle`，`\right>` → `\right\rangle`
- `\leq`、`\geq` 等 LaTeX 命令本身安全，不需要处理

扫描所有 `$...$` 和 `$$...$$` 中的文本，执行上述替换。

### 4. 生成侧边导航
从笔记的标题结构生成侧边栏目录，支持滚动高亮。

### 5. 注入 glossary 数据
将 glossary.md 中的概念解释转换为 JSON，注入到 HTML 中供 tooltip 使用：
```javascript
const glossaryData = {
  "概念名": { fullName: "全称", explanation: "解释", role: "角色" },
  ...
};
```

### 6. 生成完整 HTML 文件
将所有内容填充到模板骨架中，保存到 `${paper_dir}/${safe_title}-page.html`。

功能要求：
- 侧边导航栏（跟随滚动高亮）
- 图片点击放大（lightbox）
- 公式渲染（KaTeX CDN）
- 代码高亮（highlight.js CDN）
- glossary 术语悬停提示（tooltip）
- 响应式设计（移动端隐藏侧边栏）
- 回到顶部按钮
- 阅读进度条

### 7. 验证
检查生成的 HTML 文件：
- 文件大小合理
- 所有图片路径正确
- glossary 数据完整

## 输出
完成后报告：
- HTML 长页面路径
- 文件大小
- glossary 术语数量
- 图片数量
