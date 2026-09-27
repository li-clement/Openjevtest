# 模型下载与版本

- 原始底座：[Qwen/Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B)
- 本机量化产物：[mlx-community/Qwen3.5-4B-4bit](https://huggingface.co/mlx-community/Qwen3.5-4B-4bit)
- 固定 revision：`0e7ffd5c629ef7719d4cbc04069232580bfa9d9c`
- 总文件内容大小：3061130647 字节。

仓库不分发权重及第三方处理器文件。下载者应查看上游模型条款。当前运行依赖完整快照，只有 safetensors 文件不足以处理图文输入。

## 自动下载

```sh
.venv/bin/python scripts/download_model.py
```

外置盘路径：

```sh
export JEV_MODEL_DIR=/path/to/model-snapshot
.venv/bin/python scripts/download_model.py
sh scripts/serve.sh
```

所有文件按清单核对大小和 SHA-256。curl 内部重试为零；可恢复连接错误最多再续传一次，单次连接超时15秒，大文件总时限1800秒、小文件120秒，低速60秒停止。失败保存 results/download_status.json 和 .part，返回非零；不自动切换镜像。确认持续网络阻塞时应停止重跑，采用手动下载。

## 手动下载

把下表文件按原名放到 model/Qwen3.5-4B-4bit/（或 JEV_MODEL_DIR 指定目录），然后重新运行下载脚本：完整且校验通过的文件会直接跳过。SHA-256 与大小的完整清单在 [模型清单](../models/qwen3.5-4b-4bit.json)。若最终文件校验失败，脚本保留文件并报错，用户确认后自行替换；它不会覆盖可疑文件。

| 文件 | 字节数 | 固定版本下载 |
|---|---:|---|
| `.gitattributes` | 1570 | [下载](https://huggingface.co/mlx-community/Qwen3.5-4B-4bit/resolve/0e7ffd5c629ef7719d4cbc04069232580bfa9d9c/.gitattributes?download=true) |
| `chat_template.jinja` | 7756 | [下载](https://huggingface.co/mlx-community/Qwen3.5-4B-4bit/resolve/0e7ffd5c629ef7719d4cbc04069232580bfa9d9c/chat_template.jinja?download=true) |
| `config.json` | 3366 | [下载](https://huggingface.co/mlx-community/Qwen3.5-4B-4bit/resolve/0e7ffd5c629ef7719d4cbc04069232580bfa9d9c/config.json?download=true) |
| `model.safetensors` | 3034300695 | [下载](https://huggingface.co/mlx-community/Qwen3.5-4B-4bit/resolve/0e7ffd5c629ef7719d4cbc04069232580bfa9d9c/model.safetensors?download=true) |
| `model.safetensors.index.json` | 101944 | [下载](https://huggingface.co/mlx-community/Qwen3.5-4B-4bit/resolve/0e7ffd5c629ef7719d4cbc04069232580bfa9d9c/model.safetensors.index.json?download=true) |
| `preprocessor_config.json` | 390 | [下载](https://huggingface.co/mlx-community/Qwen3.5-4B-4bit/resolve/0e7ffd5c629ef7719d4cbc04069232580bfa9d9c/preprocessor_config.json?download=true) |
| `processor_config.json` | 1300 | [下载](https://huggingface.co/mlx-community/Qwen3.5-4B-4bit/resolve/0e7ffd5c629ef7719d4cbc04069232580bfa9d9c/processor_config.json?download=true) |
| `tokenizer.json` | 19989343 | [下载](https://huggingface.co/mlx-community/Qwen3.5-4B-4bit/resolve/0e7ffd5c629ef7719d4cbc04069232580bfa9d9c/tokenizer.json?download=true) |
| `tokenizer_config.json` | 1139 | [下载](https://huggingface.co/mlx-community/Qwen3.5-4B-4bit/resolve/0e7ffd5c629ef7719d4cbc04069232580bfa9d9c/tokenizer_config.json?download=true) |
| `video_preprocessor_config.json` | 385 | [下载](https://huggingface.co/mlx-community/Qwen3.5-4B-4bit/resolve/0e7ffd5c629ef7719d4cbc04069232580bfa9d9c/video_preprocessor_config.json?download=true) |
| `vocab.json` | 6722759 | [下载](https://huggingface.co/mlx-community/Qwen3.5-4B-4bit/resolve/0e7ffd5c629ef7719d4cbc04069232580bfa9d9c/vocab.json?download=true) |
