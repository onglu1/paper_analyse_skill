# MinerU 环境配置

## 配置文件

MinerU 的实际路径配置存放在 `mineru-config.yaml` 中（与本文档同目录）。该文件不随仓库分发，需要从 `mineru-config.yaml.template` 复制并填入本机实际路径。

主 skill（SKILL.md）会在首次需要 MinerU 时引导用户完成配置。所有子 agent prompt 中的 MinerU 命令均从 `mineru-config.yaml` 读取路径，不硬编码。

## 典型安装环境

MinerU 通常安装于 pyenv virtualenv，路径类似：

```bash
Python:  $HOME/.pyenv/versions/3.12.9/envs/mineru/bin/python
CLI:     $HOME/.pyenv/versions/mineru/bin/mineru
Router:  $HOME/.pyenv/versions/mineru/bin/mineru-router
版本:    mineru 3.1.7
```

使用前须设置环境变量（指定从 ModelScope 下载模型）：

```bash
export MINERU_MODEL_SOURCE=modelscope
export MODELSCOPE_CACHE=$HOME/.cache/mineru/models
```

## 模型目录

模型缓存：`$HOME/.cache/mineru/models/`（约 14 GB）

已预下载 `OpenDataLab/PDF-Extract-Kit-1.0`，包含：
- MFR (公式识别)：`unimernet_hf_small_2503`, `UniMERNet` 等
- OCR：`paddleocr_torch`
- 布局分析：`doclayout_yolo`, `layout_reader`
- 表格识别等

## 安装指引（新环境）

### 1. 系统依赖

```bash
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0 poppler-utils
```

### 2. Python 环境

```bash
pyenv virtualenv 3.12.9 mineru
pyenv shell mineru
pip install -U "mineru[core]"
```

### 3. 模型下载

```bash
export MINERU_MODEL_SOURCE=modelscope
export MODELSCOPE_CACHE=$HOME/.cache/mineru/models

python -c "
from modelscope import snapshot_download
snapshot_download('OpenDataLab/PDF-Extract-Kit-1.0', cache_dir=os.path.expanduser('~/.cache/mineru/models'))
"
```

首次使用 MinerU 时会自动补下缺失的模型文件。

### 4. 验证

```bash
export MINERU_MODEL_SOURCE=modelscope
mineru --help
```

## 使用方法

```bash
# 必须的环境变量
export MINERU_MODEL_SOURCE=modelscope
export MODELSCOPE_CACHE=$HOME/.cache/mineru/models

MINERU=$HOME/.pyenv/versions/mineru/bin/mineru

# 英文论文，pipeline 后端（兼容性最好）
$MINERU -p paper.pdf -o output -b pipeline -l en -d cuda

# 中文论文，hybrid 后端（高精度）
$MINERU -p paper.pdf -o output -b hybrid-auto-engine -l ch -d cuda

# 扫描版 PDF，启用 OCR
$MINERU -p scanned.pdf -o output -b pipeline -m ocr -l en

# 只处理指定页码范围
$MINERU -p paper.pdf -o output -s 0 -e 10
```

## 后端选择

| 后端 | 命令参数 | 显存 | 精度 | 适用场景 |
|------|---------|------|------|---------|
| pipeline | `-b pipeline` | 6 GB | 82+ | 通用，CPU 可用 |
| hybrid-auto-engine | `-b hybrid-auto-engine` | 10 GB | 90+ | 高精度，需要较好 GPU |
| vlm-auto-engine | `-b vlm-auto-engine` | 8 GB | 90+ | VLM 模型 |
| hybrid-http-client | `-b hybrid-http-client -u URL` | 3 GB | 90+ | 远程服务 |

有 NVIDIA GPU（显存 >= 10GB 时），推荐使用 `hybrid-auto-engine` 以获得最高精度。

## 输出结构

```bash
output/
└── paper_name/
    └── auto/                       # 解析方法（auto/txt/ocr）
        ├── paper_name.md           # 全文 Markdown（含图片引用、表格、公式）
        ├── images/                 # 提取的图片（JPG/PNG 格式，hash 命名）
        │   ├── xxxx.jpg
        │   └── ...
        ├── paper_name_layout.pdf   # 布局分析可视化
        └── paper_name_origin.pdf   # 原始 PDF 副本
```

**笔记撰写时**：读取 `auto/paper_name.md` 获取论文全文，从 `auto/images/` 获取图片。

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| CUDA driver too old | 降级 PyTorch 或用 `-d cpu` |
| HuggingFace 超时 | 设置 `MINERU_MODEL_SOURCE=modelscope` |
| 显存不足 (OOM) | 换 `-b pipeline` 或 `-d cpu` |
| 公式/表格识别差 | 升级到 `hybrid-auto-engine` 后端 |
| ModelScope 下载慢 | 设置 `http_proxy`/`https_proxy` 代理 |
