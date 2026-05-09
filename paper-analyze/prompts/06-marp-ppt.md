你的任务是基于精读笔记生成 Marp 格式的 PPT 大纲。

## 输入
- 论文输出目录: ${paper_dir}
- 论文标题: ${paper_title}
- Skill 目录: ${skill_dir}

## 必读参考文件

1. `${skill_dir}/references/marp-template.md` — Marp PPT 大纲规范和示例

## 处理步骤

### 1. 读取精读笔记
读取 `${paper_dir}/${safe_title}.md`。

### 2. 查看可用图片
列出 `${paper_dir}/images/`，规划每页使用哪张图片。

同时读取 `${paper_dir}/image_layout.json`，在规划图片使用时参考布局信息：
- 并排图片（`side-by-side`）：使用 Marp 的 `![bg right:50%]` 语法或多背景图语法
- 单图：根据 `relative_width` 选择合适的宽度参数（`![w:400]` ~ `![w:700]`）
- 图注：在图片下方用小字标注，格式为 `<span style="color: #888; font-size: 0.7em;">图注内容</span>`

### 3. 撰写 PPT 大纲
严格按照 `marp-template.md` 中的规范撰写，保存到 `${paper_dir}/${safe_title}-ppt.md`。

结构：
- 封面页（标题、作者、venue）
- 背景与动机（1-2 页）
- 问题定义（1 页）
- 方法总览（1 页，放架构图）
- 方法细节（每个关键模块 1 页）
- 实验设置（1 页）
- 实验结果（2-3 页，放结果图）
- 总结与启发（1 页）

格式要求：
- Marp frontmatter（`marp: true`, `theme: default`, `paginate: true`）
- 每页用 `---` 分隔
- 每页：页标题 + 要点（不超过 4 条）+ 图片引用
- 图片使用 `![bg right:40%](images/xxx.png)` 或 `![w:600](images/xxx.png)`

## 输出
完成后报告：
- PPT 大纲路径
- 总页数
- 使用的图片数量
