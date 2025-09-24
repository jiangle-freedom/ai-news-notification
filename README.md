# AI News Notification System 🤖

一个智能的AI资讯监控和通知系统，自动监控Bilibili UP主橘鸦Juya的AI早报更新，并通过企业微信机器人第一时间推送通知给团队成员。

## ✨ 核心特性

### 🎯 智能监控
- **基于时间的新视频检测**：只处理当天发布的视频，避免历史视频干扰
- **防重复推送机制**：每个视频只推送一次，确保团队不被重复消息打扰
- **多模式运行**：支持测试、检查、状态查看、强制检查等多种运行模式

### 📱 即时通知
- **企业微信集成**：通过企业微信机器人自动推送通知
- **智能内容摘要**：自动提取视频信息并生成简洁摘要
- **链接清理**：移除描述中的多余链接，只保留观看链接

### 🛠️ 易于部署
- **Docker支持**：提供完整的容器化部署方案
- **配置向导**：交互式配置工具，快速完成系统设置
- **健康检查**：内置系统状态监控和测试工具

## 🚀 快速开始

### 方法1：使用源码部署

```bash
# 克隆项目
git clone git@github.com:jiangle-freedom/ai-news-notification.git
cd ai-news-notification/source-code

# 运行配置向导
python3 setup_wizard.py

# 或手动配置
cp .env.template .env
# 编辑 .env 文件，设置企业微信机器人 Webhook URL

# 启动系统
./run.sh run
```

### 方法2：使用Docker部署

```bash
# 克隆项目
git clone git@github.com:jiangle-freedom/ai-news-notification.git
cd ai-news-notification/source-code

# 配置环境变量
cp .env.template .env
# 编辑 .env 文件

# 使用Docker Compose启动
docker-compose up -d
```

## 📋 运行模式

| 模式 | 命令 | 描述 |
|------|------|------|
| `run` | `./run.sh run` | 持续运行监控（生产环境） |
| `test` | `./run.sh test` | 发送测试消息 |
| `check` | `./run.sh check` | 执行一次检查 |
| `status` | `./run.sh status` | 查看系统状态 |
| `init` | `./run.sh init` | 初始化模式，只处理当天视频 |
| `force` | `./run.sh force` | 强制检查最新视频 |

## 🎯 新视频定义

系统采用**基于时间**的新视频定义策略：

- **时间标准**：只有当天发布的AI早报视频才被认为是"新视频"
- **处理逻辑**：
  - ✅ 当天发布的视频 → 立即推送通知
  - ✅ 多个当天视频 → 每个都推送（但只推送一次）
  - ❌ 昨天的视频 → 完全忽略，不推送
  - ❌ 已推送的视频 → 不再重复推送

这种设计确保了：
- 📈 **时效性**：只关注当天的最新资讯
- 🚫 **防骚扰**：避免历史视频轰炸
- ✅ **完整性**：当天的每个AI早报都会被及时推送
- 🔒 **防重复**：每个视频只推送一次

## 📁 项目结构

```
ai-news-notification/
├── README.md                    # 项目说明
├── .gitignore                   # Git忽略文件
├── api-contracts/               # API接口文档
│   └── bilibili/
├── prompts/                     # 需求文档
│   └── requirements.md
└── source-code/                 # 核心代码
    ├── main.py                  # 主程序入口
    ├── scheduler.py             # 任务调度器
    ├── bilibili_monitor.py      # B站监控模块
    ├── content_summarizer.py    # 内容摘要器
    ├── wechat_notifier.py       # 企业微信通知器
    ├── data_manager.py          # 数据管理器
    ├── config.py               # 配置管理
    ├── setup_wizard.py         # 配置向导
    ├── test_system.py          # 系统测试
    ├── run.sh                  # 启动脚本
    ├── requirements.txt        # Python依赖
    ├── Dockerfile              # Docker镜像
    ├── docker-compose.yml      # Docker编排
    └── README.md              # 详细文档
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 描述 | 默认值 | 必需 |
|--------|------|--------|------|
| `WECHAT_WEBHOOK_URL` | 企业微信机器人Webhook | 无 | ✅ |
| `BILIBILI_UP_UID` | B站UP主UID | 285286947 | ❌ |
| `CHECK_INTERVAL` | 检查间隔（分钟） | 360 | ❌ |
| `LOG_LEVEL` | 日志级别 | INFO | ❌ |

### 企业微信机器人配置

1. 在企业微信群中添加自定义机器人
2. 复制生成的Webhook URL
3. 设置到环境变量中：
   ```bash
   WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_ACTUAL_KEY
   ```

## 🐳 Docker部署

### 使用Docker Compose（推荐）

```bash
# 克隆并进入项目目录
git clone git@github.com:jiangle-freedom/ai-news-notification.git
cd ai-news-notification/source-code

# 配置环境变量
cp .env.template .env
# 编辑 .env 文件，设置企业微信机器人URL

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 使用纯Docker

```bash
# 构建镜像
docker build -t ai-news-notification .

# 运行容器
docker run -d --name ai-news \
  -e WECHAT_WEBHOOK_URL="YOUR_WEBHOOK_URL" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  ai-news-notification
```

## 🧪 测试和调试

```bash
# 运行系统测试
python3 test_system.py

# 发送测试消息
./run.sh test

# 检查系统状态
./run.sh status

# 查看日志
tail -f logs/ai_news_$(date +%Y%m%d).log
```

## 🔧 故障排除

### 常见问题

1. **企业微信通知失败**
   - 检查Webhook URL是否正确
   - 确认机器人在目标群组中
   - 验证网络连接

2. **无法获取视频信息**
   - 检查网络连接
   - 确认Bilibili API可访问
   - 验证UP主UID正确

3. **重复通知**
   - 检查`data/processed_videos.txt`文件
   - 确认数据管理器正常工作

## 📈 监控指标

系统提供以下监控信息：
- 运行状态
- 检查间隔
- 已处理视频数量
- 最后检查时间
- 下次运行时间

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [橘鸦Juya](https://space.bilibili.com/285286947) - AI早报内容源
- [Bilibili API](https://github.com/SocialSisterYi/bilibili-API-collect) - 视频数据获取
- [企业微信机器人](https://developer.work.weixin.qq.com/document/path/91770) - 消息通知

---

**🎯 让AI资讯触手可得，让团队学习永不止步！**
