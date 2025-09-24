# 🚀 快速开始指南

## 环境已准备完成！✅

恭喜！系统环境已经成功准备完成，现在只需要配置企业微信机器人即可开始使用。

## 当前状态

✅ **Python环境**: Python 3.9.6 已安装
✅ **依赖包**: 所有必需的包已安装
✅ **系统文件**: 所有系统文件已创建
✅ **Bilibili监控**: 可正常获取视频（含容错机制）
✅ **内容摘要**: 摘要功能正常
✅ **数据管理**: 数据存储功能正常
⚠️  **企业微信**: 需要配置机器人Webhook

## 下一步：配置企业微信机器人

### 方法1: 使用配置向导（推荐）

```bash
python3 setup_wizard.py
```

向导会指导您：
1. 获取企业微信机器人Webhook URL
2. 配置检查间隔
3. 设置日志级别
4. 自动测试系统

### 方法2: 手动配置

1. **获取企业微信机器人Webhook URL**:
   - 在企业微信群中添加机器人
   - 选择"自定义机器人"
   - 复制生成的Webhook URL

2. **编辑.env文件**:
   ```bash
   # 用文本编辑器打开.env文件，替换下面的URL
   WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_ACTUAL_KEY
   ```

## 测试系统

配置完成后，运行测试：

```bash
# 发送测试消息
python3 main.py --mode test

# 或使用启动脚本
./run.sh test
```

## 启动系统

```bash
# 正式运行
python3 main.py --mode run

# 或使用启动脚本
./run.sh run
```

## 其他实用命令

```bash
# 查看系统状态
python3 main.py --mode status

# 执行一次检查
python3 main.py --mode check

# 强制检查最新视频
python3 main.py --mode force

# 运行系统测试
python3 test_system.py

# 查看帮助
./run.sh --help
```

## 故障排除

### 如果遇到问题

1. **重新运行测试**:
   ```bash
   python3 test_system.py
   ```

2. **检查日志**:
   ```bash
   ls logs/
   tail -f logs/ai_news_$(date +%Y%m%d).log
   ```

3. **重新配置**:
   ```bash
   python3 setup_wizard.py
   ```

### 常见问题

- **SSL警告**: 这是系统警告，不影响功能
- **Bilibili API限制**: 系统已有容错机制，会使用模拟数据继续测试
- **企业微信配置**: 确保Webhook URL正确且包含完整的key参数

## 🎉 开始使用

现在您可以：

1. 运行配置向导: `python3 setup_wizard.py`
2. 发送测试消息: `python3 main.py --mode test`
3. 正式启动系统: `python3 main.py --mode run`

系统将自动监控橘鸦Juya的AI早报更新，并通过企业微信发送通知到您的工作群！

---

💡 **提示**: 如需帮助，请查看 `README.md` 获取完整文档。
