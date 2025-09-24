import requests
import logging
from typing import Optional, Dict
from bs4 import BeautifulSoup
from config import HEADERS

logger = logging.getLogger(__name__)

class ContentSummarizer:
    """视频内容总结器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def extract_video_info(self, video_detail: Dict) -> Dict:
        """从视频详情中提取关键信息"""
        try:
            # 基本信息
            title = video_detail.get('title', '')
            desc = video_detail.get('desc', '')
            duration = video_detail.get('duration', 0)
            view_count = video_detail.get('stat', {}).get('view', 0)
            
            # 标签信息
            tags = [tag.get('tag_name', '') for tag in video_detail.get('tag', [])]
            
            # 分P信息 (如果有)
            pages = video_detail.get('pages', [])
            
            return {
                'title': title,
                'description': desc,
                'duration': duration,
                'view_count': view_count,
                'tags': tags,
                'pages': len(pages),
                'has_multiple_parts': len(pages) > 1
            }
            
        except Exception as e:
            logger.error(f"Error extracting video info: {e}")
            return {}
    
    def generate_summary(self, video: Dict, video_detail: Optional[Dict] = None) -> str:
        """生成视频内容摘要"""
        try:
            title = video.get('title', '')
            description = video.get('description', '')
            video_url = video.get('video_url', '')
            
            # 如果有详细信息，使用更丰富的描述
            if video_detail:
                video_info = self.extract_video_info(video_detail)
                desc = video_info.get('description', description)
                tags = video_info.get('tags', [])
                
                # 构建更详细的摘要
                summary_parts = []
                
                # 标题
                summary_parts.append(f"📺 **{title}**")
                
                # 描述 (清理后的内容，保持换行格式)
                if desc and desc.strip():
                    clean_desc = self._clean_description(desc)
                    if clean_desc:
                        # 限制内容长度，但保持完整性
                        if len(clean_desc) > 300:
                            # 找到最近的句号或换行符来截断
                            truncate_pos = clean_desc.find('\n', 250)
                            if truncate_pos == -1:
                                truncate_pos = clean_desc.find('。', 250)
                            if truncate_pos != -1:
                                clean_desc = clean_desc[:truncate_pos + 1] + "..."
                            else:
                                clean_desc = clean_desc[:300] + "..."
                        summary_parts.append(f"\n\n📋 **内容概要：**\n{clean_desc}")
                
                # 标签
                if tags:
                    relevant_tags = [tag for tag in tags[:5] if tag]  # 取前5个标签
                    if relevant_tags:
                        summary_parts.append(f"\n\n🏷️ **相关标签：** {' | '.join(relevant_tags)}")
                
                # 观看链接 - 这是唯一保留的链接
                summary_parts.append(f"\n\n🔗 **观看链接：** {video_url}")
                
                return "".join(summary_parts)
            
            else:
                # 简单摘要
                summary_parts = []
                summary_parts.append(f"📺 **{title}**")
                
                if description and description.strip():
                    clean_desc = self._clean_description(description)
                    if clean_desc:
                        if len(clean_desc) > 200:
                            # 找到最近的句号或换行符来截断
                            truncate_pos = clean_desc.find('\n', 150)
                            if truncate_pos == -1:
                                truncate_pos = clean_desc.find('。', 150)
                            if truncate_pos != -1:
                                clean_desc = clean_desc[:truncate_pos + 1] + "..."
                            else:
                                clean_desc = clean_desc[:200] + "..."
                        summary_parts.append(f"\n\n📋 **内容概要：**\n{clean_desc}")
                
                # 观看链接 - 这是唯一保留的链接
                summary_parts.append(f"\n\n🔗 **观看链接：** {video_url}")
                
                return "".join(summary_parts)
                
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"📺 {video.get('title', '未知标题')}\n🔗 {video.get('video_url', '')}"
    
    def _clean_description(self, description: str) -> str:
        """清理描述文本"""
        try:
            import re
            
            # 移除HTML标签（如果存在）
            if '<' in description and '>' in description:
                soup = BeautifulSoup(description, 'html.parser')
                clean_text = soup.get_text()
            else:
                clean_text = description
            
            # 移除所有链接信息
            # 移除 http/https 链接
            clean_text = re.sub(r'https?://[^\s\n\r\t]+', ' ', clean_text)
            
            # 移除 www 开头的链接
            clean_text = re.sub(r'www\.[^\s\n\r\t]+', ' ', clean_text)
            
            # 移除邮箱
            clean_text = re.sub(r'\S+@\S+\.\S+', ' ', clean_text)
            
            # 移除B站相关链接格式
            clean_text = re.sub(r'BV[0-9A-Za-z]+', ' ', clean_text)
            clean_text = re.sub(r'av[0-9]+', ' ', clean_text)
            
            # 移除多余的空格
            clean_text = re.sub(r'\s+', ' ', clean_text)
            
            # 移除一些常见的无用信息
            unwanted_phrases = [
                '点击展开',
                '展开全部',
                '收起',
                '更多精彩内容',
                '关注我们',
                '订阅频道',
                '链接：',
                '网址：',
                '地址：',
                '官网：',
                '详情：',
                '查看更多',
                '点击查看',
                '复制链接',
                '分享链接'
            ]
            
            for phrase in unwanted_phrases:
                clean_text = clean_text.replace(phrase, '')
            
            # 分段处理，保持换行
            lines = clean_text.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                # 过滤掉只包含特殊字符、数字或很短的行
                if line and len(line) > 3 and not re.match(r'^[^\w\u4e00-\u9fff]*$', line):
                    cleaned_lines.append(line)
            
            # 用换行符连接不同内容
            result = '\n'.join(cleaned_lines)
            
            # 移除多余的连续换行符
            result = re.sub(r'\n{3,}', '\n\n', result)
            
            return result.strip()
            
        except Exception as e:
            logger.error(f"Error cleaning description: {e}")
            return description
    
    def extract_key_points(self, description: str) -> list:
        """从描述中提取关键要点"""
        try:
            # 简单的关键词提取逻辑
            key_indicators = [
                '重点', '要点', '核心', '关键', '重要',
                '新功能', '更新', '发布', '突破', '技术',
                'AI', '人工智能', '机器学习', '深度学习',
                '模型', '算法', '数据', '应用'
            ]
            
            points = []
            lines = description.split('\n')
            
            for line in lines:
                line = line.strip()
                if any(indicator in line for indicator in key_indicators) and len(line) > 10:
                    points.append(line)
            
            return points[:5]  # 返回最多5个要点
            
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return []
