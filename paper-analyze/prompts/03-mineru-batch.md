你的任务是使用 mineru-router 并行转换多篇论文 PDF。

## 输入
- PDF 文件列表: ${pdf_list}（每行一个路径）
- 输出根目录: ${output_dir}
- 可用 GPU: ${selected_gpus}
- Skill 目录: ${skill_dir}

## 必读参考文件

在开始处理前，必须读取以下文件：
1. `${skill_dir}/references/mineru-config.yaml` — MinerU 环境配置（cli_path、router_path、model_source、modelscope_cache）
2. `${skill_dir}/references/appendix-stripping.md` — 附录剥离方法论（含 References 锚点法、附录判断规则、截断策略）

## 处理步骤

### 1. 读取 MinerU 配置
从 `${skill_dir}/references/mineru-config.yaml` 读取 MinerU 环境配置：
```bash
MINERU_CLI=$(python3 -c "import yaml; c=yaml.safe_load(open('${skill_dir}/references/mineru-config.yaml')); print(c['mineru']['cli_path'])")
MINERU_ROUTER=$(python3 -c "import yaml; c=yaml.safe_load(open('${skill_dir}/references/mineru-config.yaml')); print(c['mineru']['router_path'])")
MODEL_SOURCE=$(python3 -c "import yaml; c=yaml.safe_load(open('${skill_dir}/references/mineru-config.yaml')); print(c['mineru']['model_source'])")
MODEL_CACHE=$(python3 -c "import yaml; c=yaml.safe_load(open('${skill_dir}/references/mineru-config.yaml')); print(c['mineru']['modelscope_cache'])")
```

### 2. 启动 mineru-router
```bash
MINERU_MODEL_SOURCE=$MODEL_SOURCE \
MODELSCOPE_CACHE=$MODEL_CACHE \
$MINERU_ROUTER --local-gpus ${selected_gpus} --port 8002 &
ROUTER_PID=$!

# 等待 router 启动
sleep 10
curl -s http://127.0.0.1:8002/health || (echo "Router 启动失败" && exit 1)
```

### 3. 并行提交所有 PDF 转换任务
对每篇 PDF，在后台执行：
```bash
MINERU_MODEL_SOURCE=$MODEL_SOURCE \
$MINERU_CLI \
    -p "<pdf_path>" \
    -o "${output_dir}/mineru_output" \
    --api-url http://127.0.0.1:8002 \
    -b hybrid-auto-engine \
    -l en &
```

### 4. 等待所有转换完成
```bash
wait
```

### 5. 关闭 router
```bash
kill $ROUTER_PID
```

### 6. 为每篇论文整理输出
对每篇 PDF 的 MinerU 输出：
- 从 Markdown 首行提取论文原始标题
- **生成安全文件名**：将标题转为 `safe_title`（规则：只保留 `a-zA-Z0-9._-`，空格→`-`，截断 80 字符；空则 fallback 到 `paper-<timestamp>`）
- **查询论文发表来源**：用 WebSearch 工具搜索标题，查找是否被会议/期刊接收（PDF 中通常没有显式标注）。搜到则记录，查不到标记为 "preprint"
- 创建 `${output_dir}/${safe_title}/` 目录结构
- 复制图片到 `images/`（执行图片过滤：只保留 Markdown 中明确引用且有图注的图片）
- **剥离附录内容**：对每篇论文的 MinerU 输出 Markdown，使用 References 锚点法剥离附录——先找到 References/Bibliography 章节，检查其后下一章是否为附录，确认后阅读附录开头以确定结尾位置，截断并保留 `.full_backup` 备份。详见 `${skill_dir}/references/appendix-stripping.md`
- 复制 Markdown（已剥离附录）到 `source/`
- 复制原始 PDF 到 `downloads/`

### 7. 清理
```bash
rm -rf "${output_dir}/mineru_output"
```

## 输出
完成后报告每篇论文的：
- 论文标题
- 发表来源（会议/期刊名称，或 "preprint"）
- 输出目录路径
- 图片数量
- source 文件路径
