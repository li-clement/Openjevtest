# 本机布尔判断 API

版本：0.1.0；验证日期：2026-09-27。

## 启动和停止

```sh
sh scripts/serve.sh
```

前台常驻，Ctrl+C 停止；没有安装后台守护进程。默认仅监听 `127.0.0.1:8765`，无远程访问认证功能，适用于本机验证。通过 `JEV_PORT=8766 sh scripts/serve.sh` 更换端口。保持一个 worker；模型在启动时加载一次。启动完成后：

- `GET /health`：模型就绪状态、忙碌状态、模型 revision、提示词版本和系统提示词哈希。
- `POST /v1/decide`：布尔判断。
- `GET /docs`：交互接口文档。

先按 README 安装 Python 环境并下载权重；完成后推理离线运行。模型 revision 为 `0e7ffd5c629ef7719d4cbc04069232580bfa9d9c`。精确依赖见 `requirements-macos.lock`。

## 请求与响应

请求 JSON 只有以下字段，拒绝未知字段：

| 字段 | 类型 | 要求 |
|---|---|---|
| query | string | 必填，非空，最多 12000 字符；待评价材料 |
| criterion | string | 必填，非空，最多 4000 字符；由调用方提供的可信评价标准，满足时回答 true |
| image | string 或 null | 可选，单张 PNG/JPEG 文件的原始 base64，不带 data URL 前缀 |

system prompt 内置，不接收调用方覆盖。criterion 应由应用控制；query 和 image 是待审材料。角色分离不保证抵抗提示注入，需要另行验证。若要审查其它模型的回答，可由调用方明确标注后放入 query。

```sh
curl --fail-with-body http://127.0.0.1:8765/v1/decide \
  -H 'Content-Type: application/json' \
  -d '{"query":"My account was charged twice.","criterion":"Does the material explicitly report a duplicate charge?"}'
```

带图调用，客户端仅用 Python 标准库：

```sh
.venv/bin/python \
  scripts/client.py \
  --query 'Evaluate the attached image.' \
  --criterion 'Is the large central square red?' \
  --image /path/to/image.png
```

响应包含：

```json
{
  "answer": true,
  "probabilities": {"yes": 0.7057850278370112, "no": 0.29421497216298875},
  "calibrated": false,
  "threshold": 0.5,
  "logit_margin": 0.875,
  "model": "Qwen3.5-4B-4bit",
  "model_revision": "0e7ffd5c629ef7719d4cbc04069232580bfa9d9c",
  "prompt_version": "boolean-v1",
  "usage": {"input_tokens": 179, "generated_tokens": 0},
  "image_size": [256, 256],
  "latency_ms": 227.5
}
```

此例为本机早期红色方块验收记录；当前仓库复跑记录见 validation.md。概率是限定在 A=是、B=否之间的归一化值，未校准，不是现实违规概率。true 表示满足评价标准，false 表示模型判定不满足，不代表内容已证明安全。相等分数返回 false；第一版阈值固定为 0.5。不会把运行错误转换成 false。

## 推理路径

内置系统提示词及 criterion → query/图片 → 非思考聊天模板 → prefill → 最后位置隐藏状态 → 原模型输出头 → A/B logits → sigmoid(logit_A - logit_B) → 布尔值。

实现直接调用固定版本的 Qwen3.5 模型前向接口，不调用生成循环，不采样 token，不训练或更换输出头。只对最后一个位置应用原输出头，仍计算该位置的完整词表分数，再取 A/B。每个请求重新计算输入，不跨请求复用 KV 或图片缓存。

模型加载及全部推理由一个专用线程执行。同时只能接受一个推理请求；忙碌时返回 503 和 `Retry-After: 1`，不积累无界队列。请求取消时，后台尚未完成的计算仍占用该槽位。

## 首版输入限制和错误

- JSON 请求体最多 6 MiB；图片解码前文件最多 4 MiB，最多 400 万像素，单帧 PNG/JPEG。
- 图片按 EXIF 方向处理并转 RGB，等比例缩小到最长边不超过 1024 像素，实际尺寸在 image_size 返回。小字可能受缩放影响；没有静默截断文本。
- 图片与文本处理后的合计输入最多 4096 tokens；只接受一张图片，不拉取 URL 或读取客户端指定的服务器文件。
- 422：字段/图片格式无效；413：输入超限；503：模型忙；500：推理失败。
- latency_ms 包含请求在线程中开始处理后的图片解码、提示词处理、GPU 同步和评分；不包含模型加载、网络传输与 HTTP 序列化，不等于客户端端到端延迟。

## 验证与边界

启动服务后执行：

```sh
PYTHONDONTWRITEBYTECODE=1 \
.venv/bin/python \
tests/test_api.py
```

真实 HTTP 验收结果：`results/api_tests.json`。覆盖文本正反例、红蓝图像对照、图文交替后结果稳定、非法输入、输入上限、并发忙碌和错误后的恢复。前向分数与原生成路径第一个答案位置的比较结果：`results/forward_equivalence.json`，脚本为 `tests/check_forward.py`。

当前只验证本机链路和小样例，没有完成安全、版权、提示注入的业务评估或概率校准。本地量化结果不能代表服务器高精度模型效果。具体环境与服务器迁移说明见 workflow.md。
