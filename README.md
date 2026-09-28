# Openjevtest

把已有视觉语言模型包装成布尔判断 API：传入文本、可选图片和评价标准，返回是／否及对应的模型分数。系统提示词内置；模型权重保持不变，不训练、不生成回答文本。

当前实现使用 **Qwen3.5-4B 的 MLX 4-bit 视觉版本**，在 Apple Silicon Mac 上通过 MLX-VLM 运行。它是独立实验项目，与 TypeSafe Jev 及其他同名 OpenJev 项目没有隶属关系，也不复现其未公开的训练方案。

## 快速开始

要求：Apple Silicon Mac、可用的 Metal GPU、Python 3.11、[uv](https://docs.astral.sh/uv/getting-started/installation/) 和 curl。本机已验证 M5 / 16GB 统一内存。建议把源码和 Python 环境放在 APFS 卷；模型可放外置盘。

```sh
git clone https://github.com/li-clement/Openjevtest.git
cd Openjevtest
sh scripts/setup.sh
.venv/bin/python scripts/download_model.py
sh scripts/serve.sh
```

模型文件约 3.06 GB，需要另外预留依赖、缓存及运行内存空间。仓库不包含权重。下载失败会停止并保存状态；不会无限重试。下载链接与手动恢复方法见 [模型说明](docs/models.md)。

在另一个终端调用：

```sh
curl --fail-with-body http://127.0.0.1:8765/v1/decide \
  -H 'Content-Type: application/json' \
  -d '{"query":"这笔订单重复扣了两次款。","criterion":"用户是否明确反映同一笔订单被重复扣款？"}'
```

响应的核心字段如下，数字仅为示例：

```json
{"answer":true,"probabilities":{"yes":0.82,"no":0.18},"calibrated":false}
```

图片调用：

```sh
.venv/bin/python scripts/client.py \
  --query '请检查这张图片。' \
  --criterion '图片中央的大方块是否为红色？' \
  --image /path/to/image.png
```

服务仅监听 `127.0.0.1:8765`，Ctrl+C 停止，没有安装后台服务。`GET /health` 查询状态，[`/docs`](http://127.0.0.1:8765/docs) 查看交互文档。设置 `JEV_PORT` 可更换端口。

## 原理与边界

输入组装 → prefill → 最后位置隐藏表示 → 原输出头的 A/B 分数 → sigmoid 分数差 → 布尔结果。

- 复用原模型和输出头；API 路径不采样、不进入自回归生成循环。
- `yes/no` 概率只是在两个答案内归一化的模型概率，**不是经过校准的现实风险概率**。
- 模型答错、规则歧义及提示注入仍可能发生；尚未完成安全护栏或版权业务评估。
- 目前适配固定 Qwen3.5 / MLX 后端。其他模型和服务器训练属于后续工作，不是现有功能。

## 文档与验证

- [布尔、单选与多选推理方案](docs/inference-design.md)：单选设计与多选共享前缀 Y/N 分支方案已记录，尚未实现；多选效率及一致性待验证，当前 API 仍仅支持布尔。
- [数学模型及扩展](docs/mathematics.md)
- [从权重到 API 的完整流程](docs/workflow.md)
- [API 字段、限制和错误](docs/api.md)
- [权重链接与固定版本](docs/models.md)
- [已确认候选底座](docs/model-candidates.md)
- [测试方法和验证记录](docs/validation.md)
- [第三方组件与许可证来源](THIRD_PARTY.md)

服务启动后运行 `.venv/bin/python tests/test_api.py`，测试图自动生成。前向分数对照运行 `PYTHONPATH=src .venv/bin/python tests/check_forward.py`。运行结果保存在忽略提交的 `results/`。
