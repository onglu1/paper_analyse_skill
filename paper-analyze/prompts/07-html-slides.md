你的任务是基于 PPT 大纲（Marp 格式）生成 HTML 幻灯片的内容片段，然后调用拼接脚本组装最终 HTML。

## 输入
- 论文输出目录: ${paper_dir}
- 论文标题: ${paper_title}
- Skill 目录: ${skill_dir}

## 必读参考文件

1. `${skill_dir}/references/html-slides-template.md` — HTML 幻灯片内容转换规范

## 处理步骤

### 1. 读取 PPT 大纲
读取 `${paper_dir}/${safe_title}-ppt.md`（Marp 格式）。

### 1.5 读取图片布局信息

读取 `${paper_dir}/image_layout.json`，在将图片转换为 HTML 时按布局信息排版：
- 并排图片使用 flex 容器，按 `relative_width` 比例分配宽度
- 单图居中显示
- 图注格式：`<figcaption style="color: #888; font-size: 0.75em; text-align: center; font-style: normal;">图注内容</figcaption>`

图片 HTML 模板：

单图：
```html
<figure style="text-align: center; margin: 0.5rem 0;">
  <img src="images/xxx.png" style="max-width: 80%; max-height: 60vh;" />
  <figcaption style="color: #888; font-size: 0.75em; font-style: normal;">图注</figcaption>
</figure>
```

并排图：
```html
<div style="display: flex; gap: 8px; justify-content: center; align-items: flex-start;">
  <img src="images/a.png" style="flex: {ratio}; max-height: 50vh; object-fit: contain;" />
  <img src="images/b.png" style="flex: {ratio}; max-height: 50vh; object-fit: contain;" />
</div>
<div style="color: #888; font-size: 0.75em; text-align: center;">图注</div>
```

### 2. 生成 sections HTML 片段

将 Marp 内容转换为 `<section>` 标签，保存到 `${paper_dir}/_slides_sections.html`：

转换规则：
- 每个 `---` 分隔的页面 → 一个 `<section class="slide">`（第一个加 `active` 类）
- 每个 section 内部用 `<div class="slide-content">` 包裹
- 页标题 → `<h2>`
- 要点列表 → `<ul><li>`
- 图片引用 → `<img>` 标签（使用相对路径 `images/xxx.png`）
- 公式 → 保持 `$...$` 和 `$$...$$` 格式

示例输出：
```html
<section class="slide active">
  <div class="slide-content">
    <h1>论文标题</h1>
    <p style="text-align:center; color: var(--primary-color);">作者信息</p>
  </div>
</section>

<section class="slide">
  <div class="slide-content">
    <h2>研究背景</h2>
    <ul>
      <li>要点一</li>
      <li>要点二</li>
    </ul>
  </div>
</section>
```

### 2.5 公式特殊字符转义（重要）
公式中的某些符号与 HTML 语法冲突，必须转义：
- `<` → `\lt`（否则被解析为 HTML 标签开始）
- `>` → `\gt`（否则被解析为 HTML 标签结束）
- `&` → `&amp;`（否则被解析为 HTML 实体开始）
- `\left<` → `\left\langle`，`\right>` → `\right\rangle`
- `\leq`、`\geq` 等 LaTeX 命令本身安全，不需要处理

扫描所有 `$...$` 和 `$$...$$` 中的文本，执行上述替换。

### 3. 调用拼接脚本组装最终 HTML

```bash
python3 ${skill_dir}/scripts/assemble_html_slides.py \
  --template "${skill_dir}/templates/slides.html" \
  --sections "${paper_dir}/_slides_sections.html" \
  --title "${paper_title}" \
  --output "${paper_dir}/${safe_title}-slides.html"
```

### 4. 清理临时文件

```bash
rm -f "${paper_dir}/_slides_sections.html"
```

### 5. 验证
在终端中检查生成的 HTML 文件：
- 文件大小合理
- 用 grep 统计 `<section` 数量确认所有页面都在
- 图片路径正确
- 用 grep 确认 `var(--bg-color)` 存在（CSS 完整性检查）

## 输出
完成后报告：
- HTML 幻灯片路径
- 总页数
- 文件大小
