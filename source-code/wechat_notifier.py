import requests
import json
import logging
from typing import Dict, Optional
from config import WECHAT_WEBHOOK_URL, HEADERS

logger = logging.getLogger(__name__)

class WeChatNotifier:
    """企业微信机器人通知器"""
    
    def __init__(self, webhook_url: str = WECHAT_WEBHOOK_URL):
        self.webhook_url = webhook_url
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def send_text_message(self, content: str, mentioned_list: Optional[list] = None) -> bool:
        """发送文本消息"""
        try:
            if not self.webhook_url or 'YOUR_BOT_KEY' in self.webhook_url:
                logger.warning("WeChat webhook URL not configured properly")
                return False
            
            payload = {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
            
            # 添加@用户列表
            if mentioned_list:
                payload["text"]["mentioned_list"] = mentioned_list
            
            response = self.session.post(self.webhook_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if result.get('errcode') == 0:
                logger.info("Message sent successfully")
                return True
            else:
                logger.error(f"Failed to send message: {result.get('errmsg')}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WeChat message: {e}")
            return False
    
    def send_markdown_message(self, content: str) -> bool:
        """发送Markdown格式消息"""
        try:
            if not self.webhook_url or 'YOUR_BOT_KEY' in self.webhook_url:
                logger.warning("WeChat webhook URL not configured properly")
                return False
            
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content
                }
            }
            
            response = self.session.post(self.webhook_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if result.get('errcode') == 0:
                logger.info("Markdown message sent successfully")
                return True
            else:
                logger.error(f"Failed to send markdown message: {result.get('errmsg')}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WeChat markdown message: {e}")
            return False
    
    def send_ai_news_notification(self, video_summary: str, is_new: bool = True) -> bool:
        """发送AI早报通知"""
        try:
            # 构建通知内容
            if is_new:
                header = "🤖 **AI早报更新提醒** 🤖\n\n"
                footer = "\n\n---\n💡 *及时了解AI前沿动态，把握技术发展趋势*"
            else:
                header = "📋 **AI早报内容回顾** 📋\n\n"
                footer = "\n\n---\n💡 *定期回顾AI资讯，保持技术敏感度*"
            
            full_content = header + video_summary + footer
            
            # 尝试发送Markdown格式，如果失败则发送纯文本
            if not self.send_markdown_message(full_content):
                # 转换为纯文本格式
                text_content = self._markdown_to_text(full_content)
                return self.send_text_message(text_content)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending AI news notification: {e}")
            return False
    
    def send_error_notification(self, error_message: str) -> bool:
        """发送错误通知"""
        try:
            content = f"⚠️ **AI早报监控系统错误**\n\n错误信息：{error_message}\n\n请检查系统状态。"
            return self.send_text_message(content)
            
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
            return False
    
    def send_test_message(self) -> bool:
        """发送测试消息"""
        try:
            content = "🧪 **系统测试消息**\n\nAI早报通知系统运行正常！"
            return self.send_text_message(content)
            
        except Exception as e:
            logger.error(f"Error sending test message: {e}")
            return False
    
    def _markdown_to_text(self, markdown_content: str) -> str:
        """将Markdown内容转换为纯文本"""
        try:
            # 移除Markdown格式标记
            text = markdown_content
            text = text.replace('**', '')  # 移除粗体标记
            text = text.replace('*', '')   # 移除斜体标记
            text = text.replace('#', '')   # 移除标题标记
            text = text.replace('`', '')   # 移除代码标记
            text = text.replace('---', '————————————')  # 转换分隔线
            
            return text
            
        except Exception as e:
            logger.error(f"Error converting markdown to text: {e}")
            return markdown_content
    
    def validate_webhook_url(self) -> bool:
        """验证webhook地址是否有效"""
        try:
            if not self.webhook_url or 'YOUR_BOT_KEY' in self.webhook_url:
                return False
            
            # 发送一个测试消息来验证
            test_payload = {
                "msgtype": "text",
                "text": {
                    "content": "连接测试"
                }
            }
            
            response = self.session.post(self.webhook_url, json=test_payload)
            result = response.json()
            
            return result.get('errcode') == 0
            
        except Exception as e:
            logger.error(f"Error validating webhook URL: {e}")
            return False
