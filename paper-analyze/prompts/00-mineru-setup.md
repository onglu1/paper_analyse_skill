# MinerU 环境检查与 GPU 选择

仅当有模式 B 论文（需要 PDF 转 Markdown）时执行本流程。

## 2.2 MinerU 环境检查

### 2.2.1 查找配置文件

检查 `${skill_dir}/references/mineru-config.yaml` 是否存在：

如果存在，从中读取 MinerU 配置（CLI 路径、Python 路径、模型缓存等），直接进入 2.3 节。

如果不存在，执行 2.2.2。

### 2.2.2 检查系统是否已安装 MinerU

```bash
# 尝试查找 mineru 命令
which mineru 2>/dev/null || \
ls $HOME/.pyenv/versions/mineru/bin/mineru 2>/dev/null || \
echo "NOT_FOUND"
```

如果找到 MinerU，向用户确认这些路径是否正确，然后从模板生成配置文件：

```bash
cp ${skill_dir}/references/mineru-config.yaml.template ${skill_dir}/references/mineru-config.yaml
```

并根据用户确认的实际路径更新 `mineru-config.yaml` 中的各项配置。

### 2.2.3 未安装时引导安装

如果系统中未找到 MinerU：

1. 使用 AskUserQuestion 向用户确认是否安装 MinerU：
   - 选项：安装 / 跳过（此时模式 B 论文无法处理）

2. 如果用户选择安装，逐项确认配置：
   - pyenv virtualenv 的 Python 路径（默认：`$HOME/.pyenv/versions/3.12.9/envs/mineru/bin/python`）
   - MinerU CLI 安装路径（默认：`$HOME/.pyenv/versions/mineru/bin/mineru`）
   - 模型下载缓存目录（默认：`$HOME/.cache/mineru/models`）
   - 模型下载来源（默认：modelscope）

3. 参考 `${skill_dir}/references/mineru-setup.md` 指导用户完成安装

4. 安装完成后，从模板创建配置文件：

```bash
cp ${skill_dir}/references/mineru-config.yaml.template ${skill_dir}/references/mineru-config.yaml
```

将用户确认的路径写入 `mineru-config.yaml`。

**配置文件说明：**
- 模板文件：`references/mineru-config.yaml.template`（随仓库分发，可提交到 Git）
- 实际配置：`references/mineru-config.yaml`（由用户本地生成，不应提交到 Git）

## 2.3 选择可用 GPU

先检测可用 GPU：

```bash
nvidia-smi --query-gpu=index,name,memory.free --format=csv,noheader
```

然后使用 AskUserQuestion（multiSelect: true）让用户选择：

```
问题：选择可用的 GPU（用于 MinerU PDF 转换）：
选项：（根据检测结果动态生成）
  □ GPU 0 (空闲 38GB)
  □ GPU 1 (空闲 35GB)
  ...
```
