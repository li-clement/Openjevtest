# 验证记录

日期：2026-09-27。Apple M5 MacBook Air，16GB 统一内存，8 核 GPU；Python 3.11.15。模型为固定 revision 的 Qwen3.5-4B-4bit，精确依赖见 requirements-macos.lock。

## 本次仓库版本验证

- 从新建 .venv 执行 scripts/setup.sh，54 个锁定依赖安装成功。
- 下载脚本复用既有固定快照，全部 11 个文件大小及 SHA-256 校验通过。未重复下载约3GB权重；此前本机首次下载成功。
- 使用仓库 scripts/serve.sh 启动真实 HTTP 服务，未使用原外置盘专用 Python 启动器。
- tests/test_api.py：16 项检查通过，测试图由脚本自动生成；覆盖纯文本、图文对照、字段/图片错误、大小/token上限、并发503及之后恢复。
- tests/check_forward.py：文本和红图 logits 完全一致；蓝图两个 logits 同时偏移0.125，A/B分数差和判断一致。该容差反映执行路径的浮点差异，不是对任意输入数值等价的证明。

精简原始记录：[HTTP验收](validation/api_tests.json)、[前向对照](validation/forward_equivalence.json)。记录没有用户图片或业务材料。

## 本次请求耗时

单位为 ms；包含线程开始处理后的预处理和 GPU 同步，不含加载、HTTP传输和序列化。样本很少，不是性能基准。部分运行期间存在其他模型进程，不能用于吞吐或独占GPU延迟承诺。

| 样例 | 耗时 ms |
|---|---:|
| text_yes | 1021.36 |
| text_no | 128.49 |
| red_square | 1010.63 |
| blue_square | 215.07 |
| red_square | 212.18 |
| recovery_after_errors_and_concurrency | 131.8 |

## 复跑

终端一：`sh scripts/serve.sh`。

终端二：

```sh
.venv/bin/python tests/test_api.py
PYTHONPATH=src HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python tests/check_forward.py
```

使用外置权重时，两条启动/对照命令都要设置相同 JEV_MODEL_DIR；HTTP验收只需访问服务。非默认端口通过 JEV_URL 指定。

## 未验证项

安全/版权领域的准确率、提示注入鲁棒性、真实概率校准、长时间运行稳定性、其他模型和服务器后端、训练收益。布尔结果及格式正确不等于业务判断正确。
