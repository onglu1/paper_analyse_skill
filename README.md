# paper-analyze-skill  
这是一个Claude Code skill，论文深度分析统一入口。输入一篇或多篇论文，自动生成多种格式，图文并茂的解读输出。

英文原文阅读太累？论文编写方式不符合人类学习习惯？这个skill可以帮助你理解论文。



## 功能

支持 5 种输出模式：

| 模式 | 说明 | 输出文件 |
|------|------|----------|
| 精读笔记 | obsidian笔记，六节结构的深度解读，含概念双链引用 | `.md` + `glossary.md` |
| 组会分享版 | 5 分钟快速讲解，图片为主 | `-组会分享.md` |
| PPT 大纲 | Marp 格式，可直接转 PDF/PPTX | `-ppt.md` |
| HTML 幻灯片 | 单页 HTML，键盘翻页，类 reveal.js | `-slides.html` |
| HTML 长页面 | 单页滚动 HTML，侧边导航，KaTeX 公式 | `-page.html` |

精读笔记作为中间表示先行生成，其他模式基于精读笔记并行生成。

## 论文输入支持

- arXiv 链接（`arxiv.org/abs/`）
- PDF 下载链接 / 本地 PDF（需要使用MinerU解析）
- tar.gz 下载链接 / 本地 tar.gz
- 本地 LaTeX 源码目录
- 多篇论文空格或换行分隔

## 处理流程

1. **意图澄清** — 解析用户输入，必要时用 AskUserQuestion 确认模糊意图
2. **模式选择** — 多选输出格式（精读笔记必选）
3. **论文获取** — 模式 A（LaTeX 源码包）或模式 B（PDF + MinerU 转换），多 PDF 支持 mineru-router 多 GPU 并行
4. **笔记生成** — 精读笔记先行，其他模式并行
5. **文件安全化** — 所有文件名转 ASCII，兼容 Windows

## 目录结构

```
paper-analyze/
├── SKILL.md                          # 主 skill 定义
├── .gitignore                        # 排除本地配置文件
├── references/
│   ├── note-structure.md             # 精读笔记六节结构规范
│   ├── note-template.md              # 写作风格规范
│   ├── simple-template.md            # 组会分享版规范
│   ├── marp-template.md              # Marp PPT 大纲规范
│   ├── html-slides-template.md       # HTML 幻灯片版规范 + 模板
│   ├── html-page-template.md         # HTML 长页面版规范 + 模板
│   ├── mineru-setup.md               # MinerU 安装与环境说明
│   ├── mineru-config.yaml.template   # MinerU 配置模板（可提交）
│   └── mineru-config.yaml            # 本机 MinerU 配置（本地生成，不提交）
└── README.md
```

## 依赖

- **MinerU 3.1.7** — PDF 转 Markdown（仅模式 B / 有 PDF 输入时需要）
- `pdftoppm`（`poppler-utils`）— 模式 A 下 PDF 矢量图转 PNG
- `yq` 或 Python `pyyaml` — 读取 MinerU 配置文件
- 多 GPU 环境（多 PDF 并行处理时可利用 mineru-router）

## MinerU 配置

MinerU需要下载较大模型，暂不支持API模式，如果有需要使用API进行论文解析的，十分欢迎使用者来贡献。

当论文输入包含 PDF 时，skill 需要 MinerU 将 PDF 转为结构化 Markdown。MinerU 的路径（CLI、Python 环境、模型缓存目录等）各不相同，因此不硬编码，而是通过 YAML 配置文件管理。

### 首次使用

1. 调用 `/paper-analyze` 并传入 PDF 文件时，skill 会自动检测系统是否已安装 MinerU
2. 如果未安装，skill 会引导你完成安装（参考 `references/mineru-setup.md`），并逐项确认安装路径、模型缓存目录等
3. 如果已安装但未找到配置文件，skill 会根据你确认的路径从模板生成

### 配置文件

- **模板文件**：`references/mineru-config.yaml.template` — 定义配置结构，随仓库分发
- **本地配置**：`references/mineru-config.yaml` — 由 skill 根据用户输入自动生成，包含本机实际路径。已在 `.gitignore` 中排除

配置内容示例：

```yaml
mineru:
  cli_path: "/home/user/.pyenv/versions/mineru/bin/mineru"
  router_path: "/home/user/.pyenv/versions/mineru/bin/mineru-router"
  python_path: "/home/user/.pyenv/versions/3.12.9/envs/mineru/bin/python"
  model_source: "modelscope"
  modelscope_cache: "/home/user/.cache/mineru/models"
```

所有子 agent 在执行 MinerU 命令时均从此文件读取路径，不硬编码。

## 安装

skill 目录通过符号链接或复制到 `~/.claude/skills/paper-analyze/` 即可被 Claude Code 发现。
