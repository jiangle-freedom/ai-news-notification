import schedule
import time
import logging
import pytz
import os
from datetime import datetime, date
from typing import Optional
from bilibili_monitor import BilibiliMonitor
from content_summarizer import ContentSummarizer
from wechat_notifier import WeChatNotifier
from data_manager import DataManager
from config import CHECK_INTERVAL, DAILY_PUSH_TIME, CHINA_TIMEZONE, ENABLE_DAILY_PUSH, DAILY_PUSH_LOG_FILE

logger = logging.getLogger(__name__)

class AINewsScheduler:
    """AI早报调度器"""
    
    def __init__(self):
        self.bilibili_monitor = BilibiliMonitor()
        self.content_summarizer = ContentSummarizer()
        self.wechat_notifier = WeChatNotifier()
        self.data_manager = DataManager()
        self.is_running = False
        self.china_tz = pytz.timezone(CHINA_TIMEZONE)
    
    def daily_push_check(self):
        """每日定时推送检查 (9:30 AM China time)"""
        try:
            # 获取当前中国时间
            china_now = datetime.now(self.china_tz)
            today_str = china_now.strftime('%Y-%m-%d')
            
            logger.info(f"Starting daily push check for {today_str}")
            
            # 检查今天是否已经执行过定时推送
            if self._is_daily_push_done_today():
                logger.info(f"Daily push already completed for {today_str}")
                return
            
            # 获取AI早报视频
            ai_videos = self.bilibili_monitor.get_ai_news_videos()
            
            if not ai_videos:
                logger.info("No AI news videos found for daily push")
                self._mark_daily_push_done()
                return
            
            # 筛选今天的视频（从昨晚到今天9:30之前发布的）
            today_videos = self._get_videos_for_daily_push(ai_videos)
            
            if not today_videos:
                logger.info("No new videos found for today's daily push")
                self._mark_daily_push_done()
                return
            
            logger.info(f"Found {len(today_videos)} videos for daily push")
            
            # 处理每个视频并标记为已推送
            push_count = 0
            for video in today_videos:
                try:
                    # 检查是否已经被处理过
                    if not self.data_manager.is_video_processed(video.get('bvid')):
                        self._process_single_video(video)
                        push_count += 1
                        time.sleep(2)  # 避免发送过快
                except Exception as e:
                    logger.error(f"Error processing video in daily push {video.get('bvid')}: {e}")
                    continue
            
            # 标记今日定时推送已完成
            self._mark_daily_push_done()
            
            # 发送定时推送完成通知
            if push_count > 0:
                self.wechat_notifier.send_text_message(
                    f"📅 每日AI早报推送完成\n"
                    f"📊 推送数量: {push_count}个视频\n"
                    f"⏰ 推送时间: {china_now.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                logger.info(f"Daily push completed: {push_count} videos sent")
            else:
                logger.info("Daily push completed: no new videos to send")
                
        except Exception as e:
            logger.error(f"Error in daily_push_check: {e}")
    
    def _get_videos_for_daily_push(self, ai_videos):
        """获取用于定时推送的视频（昨晚到今天9:30之前发布的）"""
        try:
            china_now = datetime.now(self.china_tz)
            today = china_now.date()
            
            # 计算时间范围：昨天18:00到今天9:30
            yesterday = date.fromordinal(today.toordinal() - 1)
            start_time = self.china_tz.localize(datetime.combine(yesterday, datetime.strptime("18:00", "%H:%M").time()))
            end_time = self.china_tz.localize(datetime.combine(today, datetime.strptime(DAILY_PUSH_TIME, "%H:%M").time()))
            
            daily_videos = []
            for video in ai_videos:
                video_time = video.get('created') or video.get('pubdate')
                if video_time:
                    # 转换为datetime对象
                    if isinstance(video_time, int):
                        video_dt = datetime.fromtimestamp(video_time, tz=self.china_tz)
                    else:
                        continue
                    
                    # 检查是否在时间范围内
                    if start_time <= video_dt <= end_time:
                        daily_videos.append(video)
                        logger.debug(f"Video for daily push: {video.get('title')} at {video_dt}")
            
            return daily_videos
            
        except Exception as e:
            logger.error(f"Error getting videos for daily push: {e}")
            return []
    
    def _is_daily_push_done_today(self) -> bool:
        """检查今天是否已经执行过定时推送"""
        try:
            if not os.path.exists(DAILY_PUSH_LOG_FILE):
                return False
            
            today_str = datetime.now(self.china_tz).strftime('%Y-%m-%d')
            
            with open(DAILY_PUSH_LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                last_line = lines[-1].strip() if lines else ''
                return today_str in last_line
                
        except Exception as e:
            logger.warning(f"Error checking daily push status: {e}")
            return False
    
    def _mark_daily_push_done(self):
        """标记今日定时推送已完成"""
        try:
            os.makedirs(os.path.dirname(DAILY_PUSH_LOG_FILE), exist_ok=True)
            china_now = datetime.now(self.china_tz)
            log_entry = f"{china_now.strftime('%Y-%m-%d %H:%M:%S')} - Daily push completed\n"
            
            with open(DAILY_PUSH_LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
            logger.debug(f"Marked daily push as completed: {log_entry.strip()}")
            
        except Exception as e:
            logger.error(f"Error marking daily push as done: {e}")
    
    def check_for_new_videos(self):
        """实时检查新视频并发送通知（避免与定时推送重复）"""
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
            # 1. 实时检查：每隔6小时检查新视频
            schedule.every(CHECK_INTERVAL).minutes.do(self.check_for_new_videos)
            
            # 2. 定时推送：每日上匈9:30（中国时区）
            if ENABLE_DAILY_PUSH:
                schedule.every().day.at(DAILY_PUSH_TIME).do(self.daily_push_check)
                logger.info(f"Daily push scheduled at {DAILY_PUSH_TIME} China time")
            
            # 发送启动通知
            daily_push_status = f"\n📅 每日定时推送: {DAILY_PUSH_TIME} (中国时区)" if ENABLE_DAILY_PUSH else ""
            self.wechat_notifier.send_text_message(
                f"🚀 AI早报监控系统已启动\n"
                f"⏰ 实时检查间隔: {CHECK_INTERVAL}分钟\n"
                f"{daily_push_status}"
                f"📺 监控UP主: 橘鸦Juya\n"
                f"🕐 启动时间: {datetime.now(self.china_tz).strftime('%Y-%m-%d %H:%M:%S')}"
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
