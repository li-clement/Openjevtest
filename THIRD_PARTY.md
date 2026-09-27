# 第三方来源

本仓库实现独立的 prefill 布尔评分 API；不包含模型权重、Python 运行时或第三方包源码。

| 组件 | 来源 | 上游许可证 |
|---|---|---|
| Qwen3.5-4B | https://huggingface.co/Qwen/Qwen3.5-4B | Apache-2.0 |
| 使用的 MLX 量化快照 | https://huggingface.co/mlx-community/Qwen3.5-4B-4bit | 查看该模型仓库及原始底座条款 |
| MLX | https://github.com/ml-explore/mlx | MIT |
| MLX-VLM | https://github.com/Blaizzy/mlx-vlm | MIT |
| FastAPI | https://github.com/fastapi/fastapi | MIT |
| Uvicorn | https://github.com/encode/uvicorn | BSD-3-Clause |

完整运行依赖见 requirements-macos.lock，各依赖保留自身许可证。上述条款不自动构成本仓库自有代码的许可证；本次发布未另行指定项目代码许可证。

公开方法参考：[TypeSafe System One 介绍](https://docs.typesafe.ai/introduction)、[MLX-VLM 用法](https://github.com/Blaizzy/mlx-vlm/blob/main/docs/usage.md)。TypeSafe 的产品名、API 概念不代表本项目获得其背书；本仓库不实现其训练算法或校准保证。
