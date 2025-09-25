#!/bin/bash

# 创建 .env 配置文件脚本

echo "🔧 创建 AI News Notification 配置文件"
echo "=================================="

# 检查是否已存在 .env 文件
if [ -f ".env" ]; then
    echo "⚠️  .env 文件已存在"
    read -p "是否覆盖现有文件? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "取消操作"
        exit 0
    fi
fi

# 获取用户输入
echo ""
echo "请提供以下配置信息："
echo ""

# 企业微信 Webhook URL
read -p "企业微信机器人 Webhook URL: " webhook_url
if [ -z "$webhook_url" ]; then
    webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_BOT_KEY"
fi

# Bilibili UP主 UID
read -p "Bilibili UP主 UID (默认: 285286947): " bilibili_uid
if [ -z "$bilibili_uid" ]; then
    bilibili_uid="285286947"
fi

# 检查间隔
read -p "实时检查间隔/分钟 (默认: 360): " check_interval
if [ -z "$check_interval" ]; then
    check_interval="360"
fi

# 是否启用定时推送
read -p "启用每日定时推送? (Y/n): " enable_daily
if [[ $enable_daily =~ ^[Nn]$ ]]; then
    enable_daily="false"
else
    enable_daily="true"
fi

# 定时推送时间
if [ "$enable_daily" = "true" ]; then
    read -p "每日推送时间 (默认: 09:30): " daily_time
    if [ -z "$daily_time" ]; then
        daily_time="09:30"
    fi
else
    daily_time="09:30"
fi

# 日志级别
read -p "日志级别 (默认: INFO): " log_level
if [ -z "$log_level" ]; then
    log_level="INFO"
fi

echo ""
echo "正在创建 .env 文件..."

# 创建 .env 文件
cat > .env << EOF
# AI News Notification System Configuration

# WeChat Work Bot Configuration
# 请在企业微信中创建机器人并替换下面的YOUR_BOT_KEY
WECHAT_WEBHOOK_URL=$webhook_url

# Bilibili Configuration
# 橘鸦Juya的UID，一般不需要修改
BILIBILI_UP_UID=$bilibili_uid

# Monitoring Configuration
# 实时检查间隔（分钟）
CHECK_INTERVAL=$check_interval

# Daily Push Configuration
# 是否启用每日定时推送
ENABLE_DAILY_PUSH=$enable_daily
# 每日推送时间（中国时区，24小时制）
DAILY_PUSH_TIME=$daily_time

# Logging Configuration
LOG_LEVEL=$log_level
EOF

echo "✅ .env 文件创建成功！"
echo ""
echo "📋 配置总结："
echo "  - 企业微信 Webhook: $webhook_url"
echo "  - Bilibili UP主 UID: $bilibili_uid"
echo "  - 实时检查间隔: $check_interval 分钟"
echo "  - 启用定时推送: $enable_daily"
if [ "$enable_daily" = "true" ]; then
    echo "  - 定时推送时间: $daily_time (中国时区)"
fi
echo "  - 日志级别: $log_level"
echo ""

if [[ "$webhook_url" == *"YOUR_BOT_KEY"* ]]; then
    echo "⚠️  请记得在企业微信中创建机器人，并将 YOUR_BOT_KEY 替换为实际的密钥！"
fi

echo "🚀 现在可以运行 ./run.sh run 启动系统"
