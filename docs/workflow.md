# 从开源权重到判断 API

1. **准备环境**：执行 scripts/setup.sh，用 uv 建立 Python 3.11 的 .venv，安装 requirements-macos.lock。requirements.txt 列直接依赖，锁文件记录已验证的完整环境。首次可能联网获取 Python；不替换系统 Python。
2. **取得模型**：执行 scripts/download_model.py，从固定 Hugging Face revision 下载权重、tokenizer、聊天模板和图片处理配置。逐文件核对大小和 SHA-256，记录结果。
3. **加载一次**：启动 scripts/serve.sh。服务离线读取模型，检查文件存在及大小，在专用线程加载并同步 GPU。启动检查不替代下载脚本的完整 SHA-256 校验。
4. **接收请求**：query 是材料，criterion 是可信应用规则，image 是可选原始 base64 图片；客户端不提供 system prompt。
5. **处理输入**：检查大小、图片格式与像素，应用 EXIF 方向，转 RGB，最长边缩至 1024；使用原聊天模板并关闭思考。处理后超过 4096 tokens 则拒绝，不静默截断。
6. **完成前向**：视觉特征和文本经过固定 Qwen3.5 模型；只取最后位置，通过原输出头计算 A/B 的分数。没有生成文本，也没有跨请求缓存。
7. **形成结果**：计算 sigmoid(z_A-z_B)，返回布尔值、yes/no 概率、未校准标记及版本信息。
8. **验证**：tests/test_api.py 测真实 HTTP；tests/check_forward.py 对照原生成路径的第一个答案位置。自制小样例只验证链路，业务有效性需要真实标注集。

## 本地路径和服务器迁移

默认权重目录是 model/Qwen3.5-4B-4bit。通过 JEV_MODEL_DIR 指向相同固定快照的外置盘副本；下载脚本和启动脚本都会读取这个变量。该选项只是路径覆盖，不是任意模型切换接口。

建议源码与 .venv 使用 APFS。exFAT 不支持普通 Python 环境依赖的符号链接，且小文件可能占用远大于内容大小的空间；当前 setup.sh 不负责自动改造 exFAT 环境。

服务器训练应从官方模型及适用的训练框架开始，不把本机量化权重作为默认增训输入。可以复用输入约定、测试数据、评价规则和输出语义；更换模型/量化/后端后须重测准确率、数值和延迟。仓库尚无服务器训练代码。
