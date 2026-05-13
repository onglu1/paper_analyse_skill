你的任务是基于精读笔记生成 HTML 长页面的内容片段，然后调用拼接脚本组装最终 HTML。

## 输入
- 论文输出目录: ${paper_dir}
- 论文标题: ${paper_title}
- Skill 目录: ${skill_dir}

## 必读参考文件

1. `${skill_dir}/references/html-page-template.md` — HTML 长页面内容转换规范

## 处理步骤

### 1. 读取精读笔记和 glossary
- 读取 `${paper_dir}/${safe_title}.md`（精读笔记）
- 读取 `${paper_dir}/glossary.md`（概念速查）

### 2. 读取图片布局信息
- 读取 `${paper_dir}/image_layout.json`

### 3. 生成正文 HTML 片段

将 Markdown 转换为 HTML 元素，保存到 `${paper_dir}/_page_content.html`：

- 标题 → `<h2 id="section-N">` ~ `<h4>`（h2/h3 必须有 id 属性）
- 段落 → `<p>`
- 列表 → `<ul>/<ol>`
- 图片 → 按 image_layout.json 布局信息生成：
  - 单图：`<figure>` + `<img>` + `<figcaption>` + lightbox
  - 并排图：`<div style="display: flex;">` 容器 + 多个 `<figure>` + lightbox
  - 图注样式：`color: #888; font-size: 0.85em; font-style: normal; text-align: center;`
  - flex 比例按 `relative_width` 乘以 10 取整设置
- 公式 → 保持 `$...$` 和 `$$...$$` 格式（KaTeX 自动渲染）
- 代码块 → `<pre><code class="language-xxx">...</code></pre>`
- `[[glossary#概念名|概念名]]` → `<span class="glossary-term" data-term="概念名">概念名</span>`

### 3.5 公式特殊字符转义（重要）
公式中的某些符号与 HTML 语法冲突，必须转义：
- `<` → `\lt`（否则被解析为 HTML 标签开始）
- `>` → `\gt`（否则被解析为 HTML 标签结束）
- `&` → `&amp;`（否则被解析为 HTML 实体开始）
- `\left<` → `\left\langle`，`\right>` → `\right\rangle`
- `\leq`、`\geq` 等 LaTeX 命令本身安全，不需要处理

扫描所有 `$...$` 和 `$$...$$` 中的文本，执行上述替换。

### 4. 生成侧边导航片段

从正文中所有 `<h2>` 和 `<h3>` 提取标题和 id，生成导航列表，保存到 `${paper_dir}/_page_nav.html`：

```html
<li><a href="#section-1">研究背景</a></li>
<li><a href="#section-1-1" class="sub-item">问题定义</a></li>
```

### 5. 生成 glossary JSON

将 glossary.md 中的概念解释转换为 JSON 对象，保存到 `${paper_dir}/_page_glossary.json`：

```json
{
  "概念名": "全称。解释文本。",
  "GRPO": "Group Relative Policy Optimization。一种基于组内相对排序的策略优化算法。"
}
```

### 6. 调用拼接脚本组装最终 HTML

```bash
python3 ${skill_dir}/scripts/assemble_html_page.py \
  --template "${skill_dir}/templates/page.html" \
  --content "${paper_dir}/_page_content.html" \
  --nav "${paper_dir}/_page_nav.html" \
  --glossary "${paper_dir}/_page_glossary.json" \
  --title "${paper_title}" \
  --output "${paper_dir}/${safe_title}-page.html"
```

### 7. 清理临时文件

```bash
rm -f "${paper_dir}/_page_content.html" "${paper_dir}/_page_nav.html" "${paper_dir}/_page_glossary.json"
```

### 8. 验证
检查生成的 HTML 文件：
- 文件大小合理
- 所有图片路径正确
- 用 grep 确认 `justify-content: center` 存在（CSS 完整性检查）

## 输出
完成后报告：
- HTML 长页面路径
- 文件大小
- glossary 术语数量
- 图片数量
