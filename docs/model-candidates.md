# 候选底座

记录日期：2026-09-27。选择标准是视觉、通用知识、规则理解及直接判断能力。以下是候选档位，不是业务实测排名；目前只有 Qwen3.5-4B 的指定 MLX 量化产物经过本仓库运行验证。

| 模型 | 参数口径 | 研究定位 |
|---|---|---|
| [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B) | 27B 档 | 质量基准 |
| [Gemma 4 12B-it](https://huggingface.co/google/gemma-4-12B-it) | 12B 档 | 中型跨系列对照 |
| [Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B) | 9B 档 | 质量与成本折中 |
| [Gemma 4 E4B-it](https://huggingface.co/google/gemma-4-E4B-it) | 约 4.5B 有效参数，含 embeddings 约 8B | 轻量跨系列对照 |
| [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) | 4B 档 | 当前本机实现 |
| [Qwen3.5-2B](https://huggingface.co/Qwen/Qwen3.5-2B) | 2B 档 | 规模下限候选 |

参数口径、视觉处理开销、量化格式及推理后端会影响实际内存与速度，不能仅凭型号排序。需要比较关闭思考、直接答案评分时的质量，不能用长链推理成绩代替。
