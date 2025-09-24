import schedule
import time
import logging
from datetime import datetime
from typing import Optional
from bilibili_monitor import BilibiliMonitor
from content_summarizer import ContentSummarizer
from wechat_notifier import WeChatNotifier
from data_manager import DataManager
from config import CHECK_INTERVAL

logger = logging.getLogger(__name__)

class AINewsScheduler:
    """AI早报调度器"""
    
    def __init__(self):
        self.bilibili_monitor = BilibiliMonitor()
        self.content_summarizer = ContentSummarizer()
        self.wechat_notifier = WeChatNotifier()
        self.data_manager = DataManager()
        self.is_running = False
    
    def check_for_new_videos(self):
        """检查新视频并发送通知（基于时间的新视频检测）"""
        try:
            logger.info("Checking for new AI news videos...")
            
            # 获取AI早报视频
            ai_videos = self.bilibili_monitor.get_ai_news_videos()
            
            if not ai_videos:
                logger.info("No AI news videos found")
                return
            
            # 筛选出当天发布且未处理的新视频
            new_videos = self.data_manager.get_new_videos(ai_videos)
            
            if not new_videos:
                logger.info("No new videos to process today")
                return
            
            logger.info(f"Found {len(new_videos)} new videos published today")
            
            # 处理每个新视频
            for video in new_videos:
                try:
                    self._process_single_video(video)
                except Exception as e:
                    logger.error(f"Error processing video {video.get('bvid')}: {e}")
                    continue
            
            # 标记视频为已处理
            self.data_manager.mark_videos_as_processed(new_videos)
            
        except Exception as e:
            logger.error(f"Error in check_for_new_videos: {e}")
            # 发送错误通知
            self.wechat_notifier.send_error_notification(str(e))
    
    def _process_single_video(self, video: dict):
        """处理单个视频"""
        try:
            bvid = video.get('bvid')
            logger.info(f"Processing video: {bvid}")
            
            # 获取视频详细信息
            video_detail = self.bilibili_monitor.get_video_detail(bvid)
            
            # 生成摘要
            summary = self.content_summarizer.generate_summary(video, video_detail)
            
            # 发送通知
            success = self.wechat_notifier.send_ai_news_notification(summary, is_new=True)
            
            if success:
                logger.info(f"Successfully sent notification for video: {bvid}")
            else:
                logger.warning(f"Failed to send notification for video: {bvid}")
                
        except Exception as e:
            logger.error(f"Error processing single video: {e}")
            raise
    
    def run_once(self):
        """运行一次检查"""
        logger.info("Running manual check...")
        self.check_for_new_videos()
    
    def run_first_time_setup(self):
        """初始化设置模式：检查当天发布的视频"""
        logger.info("Running initialization setup - checking today's videos...")
        self.check_for_new_videos()
    
    def start_scheduler(self):
        """启动调度器"""
        try:
            logger.info(f"Starting AI News Scheduler with {CHECK_INTERVAL} minute intervals")
            
            # 验证配置
            if not self._validate_configuration():
                logger.error("Configuration validation failed. Please check your settings.")
                return
            
            # 设置定时任务
            schedule.every(CHECK_INTERVAL).minutes.do(self.check_for_new_videos)
            
            # 发送启动通知
            self.wechat_notifier.send_text_message(
                f"🚀 AI早报监控系统已启动\n"
                f"⏰ 检查间隔: {CHECK_INTERVAL}分钟\n"
                f"📺 监控UP主: 橘鸦Juya\n"
                f"🕐 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            self.is_running = True
            
            # 执行一次初始检查
            self.check_for_new_videos()
            
            # 开始调度循环
            while self.is_running:
                try:
                    schedule.run_pending()
                    time.sleep(30)  # 每30秒检查一次调度
                except KeyboardInterrupt:
                    logger.info("Received interrupt signal")
                    break
                except Exception as e:
                    logger.error(f"Error in scheduler loop: {e}")
                    time.sleep(60)  # 出错时等待1分钟再继续
            
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
        finally:
            self.stop_scheduler()
    
    def stop_scheduler(self):
        """停止调度器"""
        try:
            logger.info("Stopping AI News Scheduler...")
            self.is_running = False
            schedule.clear()
            
            # 发送停止通知
            self.wechat_notifier.send_text_message(
                f"🛑 AI早报监控系统已停止\n"
                f"🕐 停止时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    def _validate_configuration(self) -> bool:
        """验证配置"""
        try:
            # 检查企业微信webhook配置
            if not self.wechat_notifier.validate_webhook_url():
                logger.error("WeChat webhook URL validation failed")
                return False
            
            # 测试Bilibili API
            test_videos = self.bilibili_monitor.get_latest_videos(1)
            if not test_videos:
                logger.warning("Unable to fetch test videos from Bilibili API")
                # 不作为致命错误，可能是网络问题
            
            logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation error: {e}")
            return False
    
    def get_status(self) -> dict:
        """获取系统状态"""
        try:
            stats = self.data_manager.get_stats()
            
            status = {
                'is_running': self.is_running,
                'check_interval': CHECK_INTERVAL,
                'last_check': datetime.now().isoformat(),
                'data_stats': stats,
                'next_run': schedule.next_run().isoformat() if schedule.jobs else None
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {'error': str(e)}
    
    def send_test_notification(self):
        """发送测试通知"""
        try:
            logger.info("Sending test notification...")
            
            # 获取最新的一个AI视频作为测试
            ai_videos = self.bilibili_monitor.get_ai_news_videos()
            
            if ai_videos:
                latest_video = ai_videos[0]
                video_detail = self.bilibili_monitor.get_video_detail(latest_video.get('bvid'))
                summary = self.content_summarizer.generate_summary(latest_video, video_detail)
                
                test_content = f"🧪 **测试通知** 🧪\n\n以下是最新的AI早报内容预览：\n\n{summary}"
                
                success = self.wechat_notifier.send_ai_news_notification(test_content, is_new=False)
                
                if success:
                    logger.info("Test notification sent successfully")
                else:
                    logger.error("Failed to send test notification")
                    
            else:
                # 发送简单测试消息
                success = self.wechat_notifier.send_test_message()
                logger.info("Sent simple test message" if success else "Failed to send test message")
                
        except Exception as e:
            logger.error(f"Error sending test notification: {e}")
    
    def force_check_all_videos(self):
        """强制检查所有视频（忽略已处理状态）"""
        try:
            logger.info("Force checking all AI news videos...")
            
            ai_videos = self.bilibili_monitor.get_ai_news_videos()
            
            if not ai_videos:
                logger.info("No AI news videos found")
                return
            
            logger.info(f"Found {len(ai_videos)} AI news videos")
            
            for i, video in enumerate(ai_videos[:3]):  # 限制为最新3个视频
                try:
                    logger.info(f"Processing video {i+1}/{min(3, len(ai_videos))}: {video.get('title')}")
                    self._process_single_video(video)
                    time.sleep(2)  # 避免发送过快
                except Exception as e:
                    logger.error(f"Error processing video {video.get('bvid')}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in force_check_all_videos: {e}")
