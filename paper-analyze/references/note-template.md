# 论文精读笔记 — 写作风格规范

本文件供子 agent 在撰写精读笔记时参考，用于控制文字风格、格式和组织方式。

---

## 1. 写作风格

成段文字为主，用多级标题组织结构，不要把内容堆砌成项目符号列表。

重要内容可以**加粗**，但每段最多 1-2 处加粗，不要满屏加粗。

句子要通顺自然。不故作学术腔，也不口语得太随便。像在跟同事讲解一篇论文，而不是在写教科书。

遇到专业术语时，用常见概念做类比迁移，帮助读者快速建立直觉。

---

## 2. 禁止的写法

### 2.1 禁止转折句开头

不要用"然而""但是"作为段落或句子的开头词。

- ❌ "然而，这种方法存在……"
- ❌ "但是，上述方案无法……"
- ✅ "这种方法在 XX 场景下会遇到 YY 问题"

如果需要表达转折，把限制条件或问题场景放在句首，让读者自然感受到对比。

### 2.2 禁止 AI 味词汇

以下词汇和句式一律不得出现：

- 赋能、抓手、闭环、形成机制
- 围绕上述内容、基于以上分析
- 值得注意的是、需要指出的是
- 综上所述、总而言之
- 不难发现、显而易见

---

## 3. 推荐句式

多用这类自然、有引导感的句式：

- "更准确地说，这篇文章做的是……"
- "这里有一个很关键的点……"
- "如果把它讲得更直白一点……"
- "这一步的意义在于……"
- "这组实验真正说明的是……"
- "换个角度看……"
- "这个设计的出发点是……"

这些句式的共同特点是：把读者拉进思考过程，而不是居高临下地陈述结论。

---

## 4. 实验描述规范

不要把"实验现象"直接等同于"理论结论"。实验结果只能说明它实际测量到的东西。

推荐表述：

- "实验结果表明……"
- "作者观察到……"
- "在这组对比中可以看到……"

不要包装成比实际更大的贡献。如果论文只在特定数据集上验证了效果，就如实写明范围。

---

## 5. 公式格式

行内公式用 `$...$`，独立公式用 `$$...$$`。

MinerU 输出的公式可能没有 `$` 包裹，撰写笔记时必须补上。写完后自查所有数学符号是否正确包裹在 LaTeX 定界符内。

示例：

- 行内：模型的损失函数为 $L = L_{cls} + \lambda L_{reg}$
- 独立：

$$
\mathcal{L} = \sum_{i=1}^{N} \ell(f(x_i), y_i)
$$

**公式命令兼容性：论文源码常在 preamble 或 `math_commands.tex` 中通过 `\newcommand` 定义自定义命令（如 `\crossmark` → `\ding{55}`）。这些命令在原论文 PDF 中正常渲染，但 KaTeX / MathJax / Obsidian 不支持。将公式写入笔记时，不能直接抄原文的自定义命令——需查定义后替换为标准等价写法。对于 ✗、✓、✶ 等装饰性符号，优先用 Unicode 字符直接写在 Markdown 中。

---

## 6. 图片引用格式

**重要：必须先读取 `${paper_dir}/image_layout.json`，按其中的布局信息排版图片。**

根据 `image_layout.json` 中每个 figure 的 `layout` 字段，使用对应的 HTML 模板：

### 单图（layout: "single"）

```html
<div style="text-align: center; margin: 1rem auto; max-width: {display_width};">
  <img src="images/xxx.png" style="max-width: 100%;" />
  <div style="color: #888; font-size: 0.85em; margin-top: 4px;">图注内容</div>
</div>
```

### 并排双图（layout: "side-by-side"）

等宽时 flex 值相同，不等宽时按 relative_width 比例设置 flex 值：

```html
<div style="display: flex; gap: 8px; margin: 1rem auto; align-items: flex-start; max-width: {display_width};">
  <div style="flex: {ratio_1};">
    <img src="images/a.png" style="width: 100%;" />
  </div>
  <div style="flex: {ratio_2};">
    <img src="images/b.png" style="width: 100%;" />
  </div>
</div>
<div style="color: #888; font-size: 0.85em; text-align: center;">图注内容</div>
```

flex 值计算：将 relative_width 乘以 10 取整。如 0.6 和 0.4 → flex: 6 和 flex: 4。等宽时都用 flex: 1。

### 三图并排（layout: "grid-3"）

```html
<div style="display: flex; gap: 8px; margin: 1rem auto; align-items: flex-start; max-width: {display_width};">
  <div style="flex: {ratio_1};"><img src="images/a.png" style="width: 100%;" /></div>
  <div style="flex: {ratio_2};"><img src="images/b.png" style="width: 100%;" /></div>
  <div style="flex: {ratio_3};"><img src="images/c.png" style="width: 100%;" /></div>
</div>
<div style="color: #888; font-size: 0.85em; text-align: center;">图注内容</div>
```

### 四图及以上网格（layout: "grid-4" 或 "grid"）

```html
<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin: 1rem auto; max-width: {display_width};">
  <img src="images/a.png" style="width: 100%;" />
  <img src="images/b.png" style="width: 100%;" />
  <img src="images/c.png" style="width: 100%;" />
  <img src="images/d.png" style="width: 100%;" />
</div>
<div style="color: #888; font-size: 0.85em; text-align: center;">图注内容</div>
```

### 图注格式规范

- 灰色小字：`color: #888; font-size: 0.85em;`
- 非斜体（不使用 `<em>` 或 `font-style: italic`）
- 紧贴图片下方：`margin-top: 4px;`
- 内容为中文，保留图片编号（如"图1："）
- 图注内容来自 `image_layout.json` 中的 `caption` 字段

### 图片放置位置

- 框架图 → 方法总览部分
- 实验结果对比图 → 评测部分
- 消融分析图 → 评测部分
- Case study 图 → 评测部分

### 兜底

如果 `image_layout.json` 不存在或某张图片不在其中，使用单图模板：

```html
<div style="text-align: center; margin: 1rem auto; max-width: 80%;">
  <img src="images/xxx.png" style="max-width: 100%;" />
  <div style="color: #888; font-size: 0.85em; margin-top: 4px;">图片描述</div>
</div>
```

---

## 7. 双链引用规则

术语首次出现时用 `[[glossary#概念名|概念名]]` 标记，引用到 glossary.md 中对应的标题节。`|` 后面的部分是阅读模式下显示的文本。

不在主干正文中展开解释概念，解释统一放在 glossary.md 里。同一术语只在首次出现时标记双链，后续出现直接使用原文即可。

示例：本文提出了一种基于 [[Transformer]] 的检测框架，使用 [[匈牙利匹配]] 进行标签分配。

---

## 8. 段落组织

每段聚焦一个要点。段落之间保持逻辑递进关系，避免一段话讲太多事情。

标题层级不超过 4 级：

```
## 大章节
### 小节
#### 细分主题
正文中用**加粗**标记更细的要点
```

超过 4 级说明结构需要重新梳理，而不是继续加标题。
