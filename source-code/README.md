# AI News Notification System

一个简单高效的AI早报通知系统，监控Bilibili UP主橘鸦Juya的AI早报合集，并通过企业微信机器人自动推送更新通知。

## 功能特性

- 🤖 **自动监控**: 定时监控Bilibili UP主的AI早报视频更新
- 📱 **即时通知**: 通过企业微信机器人第一时间推送通知
- 📋 **智能摘要**: 自动提取视频信息并生成简洁摘要
- 🔄 **去重机制**: 避免重复推送已处理的视频
- 🛠️ **易于配置**: 简单的环境变量配置
- 📊 **状态监控**: 支持查看系统运行状态
- 🧪 **测试模式**: 提供多种运行模式便于调试

## 系统架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Bilibili      │    │  Content         │    │  WeChat Work    │
│   Monitor       │───▶│  Summarizer      │───▶│  Notifier       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         ▼                        ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Data Manager   │    │    Scheduler     │    │   Log System    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd ai-news-notification/source-code

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 企业微信机器人 Webhook URL
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_ACTUAL_BOT_KEY

# Bilibili UP主 ID (橘鸦Juya，默认已设置)
BILIBILI_UP_UID=285286947

# 检查间隔（分钟）
CHECK_INTERVAL=30

# 日志级别
LOG_LEVEL=INFO
```

### 3. 获取企业微信机器人 Webhook

1. 在企业微信群中添加机器人
2. 复制机器人的 Webhook URL
3. 将 URL 中的 `key` 参数值替换到 `.env` 文件中

### 4. 运行系统

```bash
# 测试配置
python main.py --mode test

# 单次检查
python main.py --mode check

# 持续运行（默认模式）
python main.py --mode run

# 查看状态
python main.py --mode status

# 强制检查最近视频
python main.py --mode force
```

## 运行模式说明

| 模式 | 描述 | 使用场景 |
|------|------|----------|
| `run` | 持续运行，定时检查 | 生产环境 |
| `test` | 发送测试消息 | 验证配置 |
| `check` | 执行一次检查 | 手动触发 |
| `status` | 查看系统状态 | 监控调试 |
| `force` | 强制检查最新视频 | 初始化或调试 |

## 配置说明

### 环境变量

| 变量名 | 描述 | 默认值 | 必需 |
|--------|------|--------|------|
| `WECHAT_WEBHOOK_URL` | 企业微信机器人 Webhook | 无 | ✅ |
| `BILIBILI_UP_UID` | Bilibili UP主 UID | 285286947 | ❌ |
| `CHECK_INTERVAL` | 检查间隔（分钟） | 30 | ❌ |
| `LOG_LEVEL` | 日志级别 | INFO | ❌ |

### 数据存储

系统使用简单的文件存储：

- `data/processed_videos.txt`: 已处理的视频ID列表
- `logs/`: 日志文件目录

## 项目结构

```
source-code/
├── main.py                 # 主程序入口
├── scheduler.py            # 调度器
├── bilibili_monitor.py     # Bilibili监控器
├── content_summarizer.py   # 内容摘要器
├── wechat_notifier.py      # 企业微信通知器
├── data_manager.py         # 数据管理器
├── config.py              # 配置管理
├── requirements.txt       # Python依赖
├── .env.example          # 环境变量示例
├── .env                  # 环境变量配置（需自行创建）
├── data/                 # 数据存储目录
├── logs/                 # 日志文件目录
└── README.md            # 项目说明
```

## 部署建议

### 本地开发

```bash
# 开发模式运行
python main.py --mode test --log-level DEBUG
```

### 生产部署

#### 方式1: 直接运行

```bash
# 后台运行
nohup python main.py --mode run > /dev/null 2>&1 &

# 或使用 screen
screen -S ai-news python main.py --mode run
```

#### 方式2: 使用 systemd (Linux)

创建服务文件 `/etc/systemd/system/ai-news.service`:

```ini
[Unit]
Description=AI News Notification System
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/ai-news-notification/source-code
ExecStart=/usr/bin/python3 main.py --mode run
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl enable ai-news
sudo systemctl start ai-news
sudo systemctl status ai-news
```

#### 方式3: 使用 Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py", "--mode", "run"]
```

### 监控和维护

```bash
# 查看日志
tail -f logs/ai_news_$(date +%Y%m%d).log

# 检查系统状态
python main.py --mode status

# 手动触发检查
python main.py --mode check
```

## 故障排除

### 常见问题

1. **企业微信通知失败**
   - 检查 Webhook URL 是否正确
   - 确认机器人是否在目标群组中
   - 验证网络连接

2. **无法获取视频信息**
   - 检查网络连接
   - 确认 Bilibili API 可访问
   - 验证 UP主 UID 是否正确

3. **重复通知**
   - 检查 `data/processed_videos.txt` 文件
   - 确认数据管理器正常工作

### 日志级别

- `DEBUG`: 详细调试信息
- `INFO`: 一般运行信息（推荐）
- `WARNING`: 警告信息
- `ERROR`: 错误信息

## 扩展功能

### 添加新的信息源

1. 创建新的监控器类（参考 `bilibili_monitor.py`）
2. 在 `scheduler.py` 中集成新的监控器
3. 更新配置文件添加相关配置

### 自定义通知格式

修改 `content_summarizer.py` 中的 `generate_summary` 方法来自定义通知内容格式。

### 添加新的通知渠道

参考 `wechat_notifier.py` 创建新的通知器类，支持其他平台如钉钉、Slack 等。

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交变更
4. 创建 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或联系维护者。
