你的任务是分析论文中图片的空间布局关系，输出结构化的布局描述文件 `image_layout.json`。

## 输入
- 论文输出目录: ${paper_dir}
- 输入模式: ${input_mode} (A = LaTeX 源码, B = PDF/MinerU)
- Skill 目录: ${skill_dir}

## 必读参考文件

本任务无额外 reference 依赖，所有布局判断规则均在本文件中定义。

## 输出
在 `${paper_dir}/image_layout.json` 中写入图片布局描述。

## 处理步骤

### 1. 确定论文栏数（仅 Mode B）

读取 `${paper_dir}/source/` 下 MinerU 输出的 `*_content_list.json` 文件。

分析同一页内 text 类型条目的 bbox 分布：
- 每个 bbox 格式为 `[x0, y0, x1, y1]`（归一化千分比坐标，即 `int(x * 1000 / page_width)`）
- 如果大部分 text 条目的 `x0` 集中在 0~500 或 500~1000 范围内（而非横跨 0~1000），判定为**双栏**
- 双栏时，栏宽约为 450-480（千分比单位）
- 否则为**单栏**，栏宽为 1000

记录 `column_width`（千分比单位）供后续计算使用。

### 2. 提取图片条目

**Mode B：** 从 `*_content_list.json` 中提取所有 `type: "image"` 的条目，每条包含：
- `img_path`: 图片文件路径
- `bbox`: `[x0, y0, x1, y1]` 归一化千分比坐标
- `page_idx`: 所在页码
- `image_caption`: 图注文本数组

**Mode A：** 读取 `${paper_dir}/source/` 下的 `.tex` 文件，解析所有 `\begin{figure}` ... `\end{figure}` 环境，提取：
- `\includegraphics` 的文件名和 `width` 参数
- `\begin{subfigure}` 或 `\begin{minipage}` 的宽度参数
- `\caption{}` 内容

### 3. 判断并排关系

**Mode B 规则：**
1. 同一页内（`page_idx` 相同），两张图片的 bbox 在 y 方向重叠超过 50%：
   - y 重叠计算：`overlap = min(y1_a, y1_b) - max(y0_a, y0_b)`
   - 重叠比例：`overlap / min(height_a, height_b) > 0.5`
2. 且 x 方向不重叠（`x0_b > x1_a` 或 `x0_a > x1_b`）
3. 满足以上条件 → 判定为并排
4. 共享同一个 caption 编号的图片（如 caption 中包含 "(a)" "(b)" 或 "Figure 3a" "Figure 3b"）→ 并排子图

**Mode A 规则：**
1. 在同一个 `\begin{figure}` 环境内：
   - 多个 `\begin{subfigure}` → 并排
   - 多个 `\begin{minipage}` → 并排
   - 连续的 `\includegraphics`（中间无 `\\` 或 `\newline`）→ 并排
2. 有显式 `width` 参数 → 直接使用
3. 无显式 `width` 但在 subfigure/minipage 中 → 按等宽分配（1/n）

### 4. 计算相对宽度和显示宽度

**Mode B：**
- 每张图的宽度 = `x1 - x0`（千分比单位）
- 相对于栏宽的比例 = `(x1 - x0) / column_width`
- 同组图片的 `relative_width` = 各自比例归一化（使组内总和 = 1.0）
- **`display_width`**（整组图片占内容区的百分比）：
  - 计算整组图片在原文中占**页面全宽**的比例：`group_page_ratio = 整组图片的总 bbox 宽度 / 1000`
  - 双栏论文中，如果图片跨双栏（宽度 > 600 千分比），`display_width` = "100%"
  - 双栏论文中，如果图片仅在单栏内（宽度 ≤ 栏宽），`display_width` = 图片宽度占页面宽度的比例，映射到 "40%"~"50%"
  - 单栏论文中，`display_width` = 图片宽度占页面宽度的比例，直接映射为百分比（如占 80% 页宽 → "80%"）

**Mode A：**
- 从 `width=0.48\textwidth` 提取数值 0.48
- 从 `\begin{subfigure}{0.48\textwidth}` 提取数值 0.48
- 同组图片的 `relative_width` = 各自 width 值归一化（使组内总和 = 1.0）
- 无显式 width 时，n 张并排图各为 `1/n`
- **`display_width`**：
  - `\begin{figure*}` 环境（双栏论文跨栏图）→ "100%"
  - `\begin{figure}` 环境中，所有子图 width 之和即为整组占栏宽的比例
  - 双栏论文单栏图：整组占栏宽比例 × 50%（因为一栏约占页面 50%），映射为 "40%"~"50%"
  - 单栏论文：整组占 textwidth 的比例直接作为 display_width

### 5. 确定布局类型

根据每组图片数量：
- 1 张 → `"single"`
- 2 张 → `"side-by-side"`
- 3 张 → `"grid-3"`
- 4 张 → `"grid-4"`
- >4 张 → `"grid"`

### 6. 翻译图注

将每个 figure 的 caption 翻译为简洁的中文。保留图片编号（如"图1："）。

### 7. 输出 image_layout.json

写入 `${paper_dir}/image_layout.json`，格式：

```json
{
  "figures": [
    {
      "id": "fig1",
      "caption": "图1：中文图注",
      "images": [
        {"file": "images/xxx.jpg", "relative_width": 1.0}
      ],
      "layout": "single",
      "display_width": "80%"
    }
  ]
}
```

字段说明：
- `id`: figure 编号标识（fig1, fig2, ...）
- `caption`: 中文图注
- `images[].file`: 图片文件相对路径（相对于 paper_dir）
- `images[].relative_width`: 组内相对宽度（总和 = 1.0）
- `layout`: `single` | `side-by-side` | `grid-3` | `grid-4` | `grid`
- `display_width`: 整组图片占内容区宽度的百分比（如 "100%"、"80%"、"45%"），反映原文中图片的实际大小比例

### 兜底规则

- 无法判断并排关系时，每张图单独作为一个 figure，`layout: "single"`
- 同一 figure 中图片 > 4 张时，`layout: "grid"`
- 如果 `_content_list.json` 不存在或解析失败，为 images/ 目录中的每张图片生成 `layout: "single"` 条目

## 输出
完成后报告：
- image_layout.json 路径
- 检测到的 figure 数量
- 并排组数量
- 论文栏数（单栏/双栏）
