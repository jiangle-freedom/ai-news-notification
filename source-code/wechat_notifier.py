import requests
import json
import logging
from typing import Optional
from config import WECHAT_WEBHOOK_URL

logger = logging.getLogger(__name__)

class WeChatNotifier:
    """企业微信通知器"""
    
    def __init__(self, webhook_url: str = WECHAT_WEBHOOK_URL):
        self.webhook_url = webhook_url
        self.session = requests.Session()
    
    def validate_webhook_url(self) -> bool:
        """验证webhook URL"""
        if not self.webhook_url:
            logger.error("WeChat webhook URL not configured")
            return False
        
        if 'YOUR_BOT_KEY' in self.webhook_url:
            logger.error("WeChat webhook URL contains placeholder")
            return False
        
        if not self.webhook_url.startswith('https://qyapi.weixin.qq.com/'):
            logger.error("Invalid WeChat webhook URL format")
            return False
        
        return True
    
    def send_text_message(self, content: str) -> bool:
        """发送文本消息"""
        try:
            if not self.validate_webhook_url():
                return False
            
            payload = {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
            
            response = self.session.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get('errcode') == 0:
                logger.info("Message sent successfully")
                return True
            else:
                logger.error(f"Failed to send message: {result.get('errmsg', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending text message: {e}")
            return False
    
    def send_markdown_message(self, content: str) -> bool:
        """发送Markdown消息"""
        try:
            if not self.validate_webhook_url():
                return False
            
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content
                }
            }
            
            response = self.session.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get('errcode') == 0:
                logger.info("Markdown message sent successfully")
                return True
            else:
                logger.error(f"Failed to send markdown message: {result.get('errmsg', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending markdown message: {e}")
            return False
    
    def send_ai_news_notification(self, summary: str, is_new: bool = True) -> bool:
        """发送AI早报通知"""
        try:
            prefix = "🆕 **AI早报更新**" if is_new else "📰 **AI早报**"
            content = f"{prefix}\n\n{summary}"
            
            # 尝试发送Markdown消息
            success = self.send_markdown_message(content)
            
            # 如果Markdown失败，尝试文本消息
            if not success:
                logger.info("Markdown failed, trying text message")
                return self.send_text_message(content)
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending AI news notification: {e}")
            return False
    
    def send_test_message(self) -> bool:
        """发送测试消息"""
        test_content = """🧪 **AI早报监控系统测试**

系统运行正常！

📺 监控对象: 橘鸦Juya AI早报
🤖 通知方式: 企业微信机器人
⏰ 测试时间: 系统启动测试

如果您收到此消息，说明通知配置正确！"""
        
        return self.send_markdown_message(test_content)
    
    def send_error_notification(self, error_message: str) -> bool:
        """发送错误通知"""
        try:
            content = f"""❌ **AI早报监控系统错误**

系统运行时出现错误，请检查：

**错误信息:**
{error_message}

**建议操作:**
1. 检查网络连接
2. 查看系统日志
3. 重启监控服务

⏰ 错误时间: {self._get_current_time()}"""
            
            return self.send_markdown_message(content)
            
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
            return False
    
    def send_startup_notification(self, check_interval: int) -> bool:
        """发送启动通知"""
        try:
            content = f"""🚀 **AI早报监控系统启动**

系统已成功启动，开始监控AI早报更新！

⚙️ **配置信息:**
- 监控对象: 橘鸦Juya AI早报
- 检查间隔: {check_interval} 分钟
- 启动时间: {self._get_current_time()}

📱 **通知规则:**
- 只推送当天发布的新视频
- 每个视频仅推送一次
- 自动清理链接，保留纯文字内容

系统将持续监控，有新的AI早报时会第一时间通知！"""
            
            return self.send_markdown_message(content)
            
        except Exception as e:
            logger.error(f"Error sending startup notification: {e}")
            return False
    
    def send_shutdown_notification(self) -> bool:
        """发送关闭通知"""
        try:
            content = f"""🛑 **AI早报监控系统停止**

系统已停止运行。

⏰ 停止时间: {self._get_current_time()}

如需重新启动，请执行启动命令。"""
            
            return self.send_markdown_message(content)
            
        except Exception as e:
            logger.error(f"Error sending shutdown notification: {e}")
            return False
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')