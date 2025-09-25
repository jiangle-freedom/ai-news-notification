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
            
            # 构建摘要
            summary_parts = []
            
            # 标题
            summary_parts.append(f"📺 **{title}**")
            
            # 获取描述内容
            desc = description
            tags = []
            
            # 如果有详细信息，使用更丰富的描述
            if video_detail:
                video_info = self.extract_video_info(video_detail)
                desc = video_info.get('description', description)
                tags = video_info.get('tags', [])
            
            # 描述 (清理后的内容，转换为bullet points格式)
            if desc and desc.strip():
                clean_desc = self._clean_description(desc)
                if clean_desc:
                    summary_parts.append(f"\n\n📋 **内容概要：**\n{clean_desc}")
            
            # 标签（仅在有详细信息时显示）
            if tags:
                relevant_tags = [tag for tag in tags[:5] if tag]  # 取前5个标签
                if relevant_tags:
                    summary_parts.append(f"\n\n🏷️ **相关标签：** {' | '.join(relevant_tags)}")
            
            # 观看链接 - 这是唯一保留的链接
            summary_parts.append(f"\n\n🔗 **观看链接：** {video_url}")
            
            return "".join(summary_parts)
                
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"📺 {video.get('title', '未知标题')}\n🔗 {video.get('video_url', '')}"
    
    def _clean_description(self, description: str) -> str:
        """清理描述文本并按时间信息分割为bullet points"""
        try:
            import re
            
            # 移除HTML标签（如果存在）
            if '<' in description and '>' in description:
                soup = BeautifulSoup(description, 'html.parser')
                clean_text = soup.get_text()
            else:
                clean_text = description
            
            # 将 ⬛ 替换为换行符
            clean_text = clean_text.replace('⬛', '\n\n')
            
            # 移除所有emoji表情符号（精确范围，避免误删汉字）
            # 汉字范围: U+4E00-U+9FFF，要避免这个范围
            emoji_pattern = re.compile(
                "["
                "\U0001F600-\U0001F64F"  # emoticons (😀-🙏)
                "\U0001F300-\U0001F5FF"  # symbols & pictographs (🌀-🗿) 
                "\U0001F680-\U0001F6FF"  # transport & map symbols (🚀-🛿)
                "\U0001F1E0-\U0001F1FF"  # flags (🇠-🇿)
                "\U0001F900-\U0001F9FF"  # supplemental symbols (🤀-🧿)
                "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
                "\U00002600-\U000026FF"  # miscellaneous symbols (☀-⛿) 
                "\U00002700-\U000027BF"  # dingbats (✀-➿)
                "\U0001F000-\U0001F02F"  # mahjong tiles
                "\U0001F0A0-\U0001F0FF"  # playing cards
                "]+", flags=re.UNICODE)
            clean_text = emoji_pattern.sub('', clean_text)
            
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
            
            # 按时间信息分割内容：寻找 ": {时间信息}" 模式
            # 改进的时间模式匹配逻辑
            time_pattern = r'([^:\n]+):\s*(\d{1,2}:\d{2}|\d{4}-\d{1,2}-\d{1,2}|\d{1,2}月\d{1,2}日|\d{1,2}/\d{1,2}|\d{1,2}-\d{1,2}|今天|昨天|明天|本周|上周|下周)'
            
            # 寻找所有匹配的时间模式
            time_matches = list(re.finditer(time_pattern, clean_text))
            bullet_points = []
            
            if time_matches:
                # 按照匹配的位置分割文本
                last_end = 0
                
                for match in time_matches:
                    # 获取匹配前的内容作为前置描述
                    prefix_content = clean_text[last_end:match.start()].strip()
                    
                    # 获取匹配的标题和时间
                    title_part = match.group(1).strip()
                    time_part = match.group(2).strip()
                    
                    # 获取匹配后的内容（到下一个匹配或文本结尾）
                    next_match_start = time_matches[time_matches.index(match) + 1].start() if time_matches.index(match) + 1 < len(time_matches) else len(clean_text)
                    content_part = clean_text[match.end():next_match_start].strip()
                    
                    # 构建条目
                    if title_part and content_part:
                        # 清理内容，移除多余的换行和空格
                        content_part = re.sub(r'\s+', ' ', content_part)
                        entry = f"{title_part} ({time_part}): {content_part}"
                    elif title_part:
                        entry = f"{title_part} ({time_part})"
                    else:
                        continue
                    
                    if len(entry.strip()) > 10:  # 过滤太短的条目
                        bullet_points.append(entry.strip())
                    
                    last_end = next_match_start
            
            # 如果没有找到时间模式，尝试其他分割方式
            if not bullet_points:
                # 按段落分割
                paragraphs = clean_text.split('\n')
                for para in paragraphs:
                    para = para.strip()
                    if para and len(para) > 10:  # 过滤太短的段落
                        # 清理段落内容
                        if not re.match(r'^[^\w\u4e00-\u9fff]*$', para):
                            bullet_points.append(para)
            
            # 如果仍然没有条目，使用原始清理逻辑
            if not bullet_points:
                lines = clean_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 3 and not re.match(r'^[^\w\u4e00-\u9fff]*$', line):
                        bullet_points.append(line)
            
            # 格式化为bullet points
            if bullet_points:
                # 限制条目数量，避免过长
                max_entries = 8
                if len(bullet_points) > max_entries:
                    bullet_points = bullet_points[:max_entries]
                
                # 添加bullet point符号
                formatted_points = []
                for point in bullet_points:
                    # 确保每个条目不会太长
                    if len(point) > 200:
                        point = point[:197] + "..."
                    formatted_points.append(f"• {point}")
                
                return '\n'.join(formatted_points)
            else:
                # 如果没有找到有效条目，返回原始清理后的文本
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
