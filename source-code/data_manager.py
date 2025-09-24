import os
import json
import logging
from typing import Set, Dict, List
from datetime import datetime, timezone
from config import DATA_DIR, PROCESSED_VIDEOS_FILE

logger = logging.getLogger(__name__)

class DataManager:
    """数据管理器，负责处理已处理视频的记录"""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.processed_videos_file = PROCESSED_VIDEOS_FILE
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        try:
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
                logger.info(f"Created data directory: {self.data_dir}")
        except Exception as e:
            logger.error(f"Error creating data directory: {e}")
    
    def load_processed_videos(self) -> Set[str]:
        """加载已处理的视频ID列表"""
        try:
            if os.path.exists(self.processed_videos_file):
                with open(self.processed_videos_file, 'r', encoding='utf-8') as f:
                    return set(line.strip() for line in f if line.strip())
            return set()
        except Exception as e:
            logger.error(f"Error loading processed videos: {e}")
            return set()
    
    def save_processed_video(self, video_id: str):
        """保存已处理的视频ID"""
        try:
            with open(self.processed_videos_file, 'a', encoding='utf-8') as f:
                f.write(f"{video_id}\n")
            logger.debug(f"Saved processed video: {video_id}")
        except Exception as e:
            logger.error(f"Error saving processed video: {e}")
    
    def is_video_processed(self, video_id: str) -> bool:
        """检查视频是否已处理"""
        processed_videos = self.load_processed_videos()
        return video_id in processed_videos
    
    def is_video_published_today(self, video: Dict) -> bool:
        """检查视频是否为当天发布"""
        try:
            # 获取视频发布时间戳
            pubdate = video.get('pubdate') or video.get('created')
            if not pubdate:
                logger.warning(f"Video {video.get('bvid')} missing publication date")
                return False
            
            # 转换为datetime对象
            if isinstance(pubdate, (int, float)):
                video_date = datetime.fromtimestamp(pubdate)
            elif isinstance(pubdate, str):
                # 尝试解析字符串格式的时间
                try:
                    video_date = datetime.fromisoformat(pubdate.replace('Z', '+00:00'))
                except ValueError:
                    video_date = datetime.fromtimestamp(float(pubdate))
            else:
                logger.warning(f"Unknown pubdate format for video {video.get('bvid')}: {pubdate}")
                return False
            
            # 获取当前日期
            today = datetime.now().date()
            video_date_only = video_date.date()
            
            logger.debug(f"Video {video.get('bvid')} published on {video_date_only}, today is {today}")
            return video_date_only == today
            
        except Exception as e:
            logger.error(f"Error checking video date for {video.get('bvid')}: {e}")
            return False
    
    def get_new_videos(self, all_videos: List[Dict], first_run: bool = False) -> List[Dict]:
        """获取需要处理的新视频（基于时间和处理状态）
        
        新视频定义：
        1. 必须是当天发布的视频
        2. 尚未被处理过（未在processed_videos.txt中）
        
        Args:
            all_videos: 所有视频列表
            first_run: 是否为首次运行（保留用于兼容性，但逻辑已改变）
        """
        processed_videos = self.load_processed_videos()
        new_videos = []
        today_videos = []
        
        # 首先筛选出当天发布的视频
        for video in all_videos:
            if self.is_video_published_today(video):
                today_videos.append(video)
        
        logger.info(f"Found {len(today_videos)} videos published today")
        
        # 如果没有当天发布的视频，直接返回空列表
        if not today_videos:
            logger.info("No videos published today")
            return []
        
        # 从当天视频中筛选出未处理的
        for video in today_videos:
            video_id = video.get('bvid')
            if video_id and video_id not in processed_videos:
                new_videos.append(video)
                logger.info(f"Found new video published today: {video_id} - {video.get('title', 'No title')}")
            else:
                logger.debug(f"Video {video_id} already processed today")
        
        logger.info(f"Total new videos to process: {len(new_videos)}")
        return new_videos
    
    def mark_videos_as_processed(self, videos: List[Dict]):
        """批量标记视频为已处理"""
        for video in videos:
            video_id = video.get('bvid')
            if video_id:
                self.save_processed_video(video_id)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        try:
            processed_videos = self.load_processed_videos()
            
            stats = {
                'total_processed': len(processed_videos),
                'data_dir': self.data_dir,
                'last_updated': datetime.now().isoformat()
            }
            
            # 如果文件存在，获取最后修改时间
            if os.path.exists(self.processed_videos_file):
                mtime = os.path.getmtime(self.processed_videos_file)
                stats['file_last_modified'] = datetime.fromtimestamp(mtime).isoformat()
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def cleanup_old_records(self, keep_last_n: int = 1000):
        """清理旧记录，只保留最近的N条记录"""
        try:
            processed_videos = self.load_processed_videos()
            
            if len(processed_videos) <= keep_last_n:
                logger.info(f"No cleanup needed. Total records: {len(processed_videos)}")
                return
            
            # 转换为列表并保留最后的N条记录
            video_list = list(processed_videos)
            recent_videos = video_list[-keep_last_n:]
            
            # 重写文件
            with open(self.processed_videos_file, 'w', encoding='utf-8') as f:
                for video_id in recent_videos:
                    f.write(f"{video_id}\n")
            
            logger.info(f"Cleaned up records. Kept {len(recent_videos)} out of {len(processed_videos)}")
            
        except Exception as e:
            logger.error(f"Error cleaning up old records: {e}")
    
    def export_data(self, export_file: str = None) -> str:
        """导出数据到JSON文件"""
        try:
            if not export_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_file = os.path.join(self.data_dir, f"export_{timestamp}.json")
            
            processed_videos = self.load_processed_videos()
            stats = self.get_stats()
            
            export_data = {
                'export_time': datetime.now().isoformat(),
                'stats': stats,
                'processed_videos': list(processed_videos)
            }
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Data exported to: {export_file}")
            return export_file
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return ""
    
    def reset_data(self):
        """重置所有数据（谨慎使用）"""
        try:
            if os.path.exists(self.processed_videos_file):
                os.remove(self.processed_videos_file)
                logger.warning("All processed video records have been reset")
            else:
                logger.info("No data file to reset")
        except Exception as e:
            logger.error(f"Error resetting data: {e}")
