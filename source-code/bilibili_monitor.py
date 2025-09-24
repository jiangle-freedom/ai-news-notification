import requests
import json
import logging
import time
import random
import os
from typing import List, Dict, Optional
from config import BILIBILI_UP_UID, BILIBILI_API_BASE, HEADERS

logger = logging.getLogger(__name__)

class BilibiliMonitor:
    """监控Bilibili UP主的视频更新"""
    
    def __init__(self, up_uid: str = BILIBILI_UP_UID):
        self.up_uid = up_uid
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.last_request_time = 0
        self.min_request_interval = 3  # 最小请求间隔3秒
        self.cache_file = 'data/video_cache.json'
        self.cache_duration = 300  # 缓存5分钟
        
    def _ensure_data_dir(self):
        """确保data目录存在"""
        os.makedirs('data', exist_ok=True)
    
    def _wait_for_rate_limit(self):
        """等待请求间隔以避免频率限制"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last + random.uniform(0.5, 1.5)
            logger.debug(f"Rate limiting: waiting {wait_time:.2f} seconds")
            time.sleep(wait_time)
        self.last_request_time = time.time()
    
    def _load_cache(self) -> Optional[List[Dict]]:
        """加载缓存的视频数据"""
        try:
            if not os.path.exists(self.cache_file):
                return None
            
            # 检查缓存是否过期
            cache_age = time.time() - os.path.getmtime(self.cache_file)
            if cache_age > self.cache_duration:
                logger.debug("Cache expired")
                return None
                
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                logger.info(f"Loaded {len(cached_data)} videos from cache")
                return cached_data
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            return None
    
    def _save_cache(self, videos: List[Dict]):
        """保存视频数据到缓存"""
        try:
            self._ensure_data_dir()
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(videos, f, ensure_ascii=False, indent=2)
            logger.debug(f"Cached {len(videos)} videos")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def get_latest_videos(self, page_size: int = 10) -> List[Dict]:
        """获取UP主最新的视频列表"""
        # 首先尝试从缓存加载
        cached_videos = self._load_cache()
        if cached_videos:
            return cached_videos[:page_size]
        
        try:
            # 等待避免频率限制
            self._wait_for_rate_limit()
            
            # 使用官方API规范中的接口
            url = f"{BILIBILI_API_BASE}/x/space/wbi/arc/search"
            params = {
                'mid': self.up_uid,
                'ps': min(page_size, 30),  # API限制最大30
                'tid': 0,
                'pn': 1,
                'keyword': '',
                'order': 'pubdate'
            }
            
            # 添加标准请求头
            headers = {
                **HEADERS,
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') != 0:
                logger.warning(f"Primary API failed: {data.get('message', 'Unknown error')}")
                return self._try_alternative_api(page_size)
            
            # 根据API规范解析响应数据
            video_data = data.get('data', {})
            if 'list' in video_data and 'vlist' in video_data['list']:
                videos = video_data['list']['vlist']
            else:
                logger.warning("Unexpected API response structure")
                return self._try_alternative_api(page_size)
            
            formatted_videos = self._format_videos(videos)
            # 保存到缓存
            self._save_cache(formatted_videos)
            
            logger.info(f"Successfully fetched {len(videos)} videos from primary API")
            return formatted_videos
            
        except Exception as e:
            logger.warning(f"Error with primary API: {e}")
            return self._try_alternative_api(page_size)
    
    def _try_alternative_api(self, page_size: int) -> List[Dict]:
        """尝试备用API"""
        try:
            # 等待避免频率限制
            self._wait_for_rate_limit()
            
            # 使用简化的用户投稿接口
            url = f"{BILIBILI_API_BASE}/x/space/arc/search"
            params = {
                'mid': self.up_uid,
                'ps': min(page_size, 20),  # 限制数量
                'pn': 1,
                'order': 'pubdate'
            }
            
            # 添加更完整的浏览器headers
            headers = {
                **HEADERS,
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': f'https://space.bilibili.com/{self.up_uid}',
                'Origin': 'https://space.bilibili.com',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site'
            }
            
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') == 0:
                # 处理不同的响应结构
                video_data = data.get('data', {})
                if 'list' in video_data and 'vlist' in video_data['list']:
                    videos = video_data['list']['vlist']
                elif 'vlist' in video_data:
                    videos = video_data['vlist']
                else:
                    videos = []
                
                formatted_videos = self._format_videos(videos)
                # 保存到缓存
                if formatted_videos:
                    self._save_cache(formatted_videos)
                
                logger.info(f"Alternative API succeeded, got {len(videos)} videos")
                return formatted_videos
            else:
                logger.error(f"Alternative API failed: {data.get('message', 'Unknown error')}")
                return self._fallback_to_cache_or_mock(page_size)
                
        except Exception as e:
            logger.error(f"Alternative API error: {e}")
            return self._fallback_to_cache_or_mock(page_size)
    
    def _fallback_to_cache_or_mock(self, page_size: int) -> List[Dict]:
        """回退到缓存或模拟数据"""
        # 尝试加载过期的缓存
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    logger.info(f"Using expired cache with {len(cached_data)} videos")
                    return cached_data[:page_size]
        except Exception as e:
            logger.warning(f"Failed to load expired cache: {e}")
        
        logger.warning("All API attempts failed. Returning empty list.")
        return []
    
    def get_ai_news_videos(self) -> List[Dict]:
        """获取AI早报相关的视频"""
        videos = self.get_latest_videos(20)  # 获取更多视频以筛选AI早报
        ai_news_videos = []
        
        for video in videos:
            title = video.get('title', '').lower()
            if any(keyword in title for keyword in ['ai早报', 'ai 早报', 'ai日报', 'ai简报', 'ai资讯']):
                ai_news_videos.append(video)
        
        return ai_news_videos
    
    def get_video_detail(self, bvid: str) -> Optional[Dict]:
        """获取视频详细信息"""
        try:
            # 使用官方API规范中的视频详情接口
            url = f"{BILIBILI_API_BASE}/x/web-interface/view"
            params = {'bvid': bvid}
            
            # 按照API文档要求添加请求头
            headers = {
                **HEADERS,
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Cache-Control': 'no-cache',
                'Referer': f'https://www.bilibili.com/video/{bvid}',
                'Origin': 'https://www.bilibili.com'
            }
            
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') != 0:
                logger.error(f"Error getting video detail: {data.get('message', 'Unknown error')}")
                return None
            
            video_info = data.get('data')
            if video_info:
                logger.debug(f"Successfully fetched detail for video: {bvid}")
            return video_info
            
        except Exception as e:
            logger.error(f"Error fetching video detail: {e}")
            return None
    
    def _format_videos(self, videos: List[Dict]) -> List[Dict]:
        """格式化视频信息，基于API规范"""
        formatted_videos = []
        for video in videos:
            # 确保必要字段存在
            bvid = video.get('bvid')
            if not bvid:
                logger.warning(f"Video missing bvid, skipping: {video}")
                continue
                
            formatted_video = {
                'bvid': bvid,
                'aid': video.get('aid'),  # 添加aid字段
                'title': video.get('title', ''),
                'description': video.get('description', ''),
                'created': video.get('created'),
                'length': video.get('length', ''),
                'play': video.get('play', 0),
                'video_url': f"https://www.bilibili.com/video/{bvid}",
                'pic': video.get('pic', ''),
                'author': video.get('author', ''),  # UP主名称
                'mid': video.get('mid', self.up_uid),  # UP主ID
                'typeid': video.get('typeid'),  # 分区ID
                'typename': video.get('typename', ''),  # 分区名称
                'pubdate': video.get('created'),  # 发布时间戳
                'comment': video.get('comment', 0),  # 评论数
                'review': video.get('review', 0)  # 弹幕数
            }
            formatted_videos.append(formatted_video)
        
        logger.debug(f"Formatted {len(formatted_videos)} videos")
        return formatted_videos
