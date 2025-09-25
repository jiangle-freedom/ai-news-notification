import os
from dotenv import load_dotenv

load_dotenv()

# WeChat Work Configuration
WECHAT_WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL')

# Bilibili Configuration
BILIBILI_UP_UID = os.getenv('BILIBILI_UP_UID', '285286947')  # 橘鸦Juya的UID
BILIBILI_API_BASE = 'https://api.bilibili.com'

# Application Configuration
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 360))  # minutes
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Scheduling Configuration
DAILY_PUSH_TIME = os.getenv('DAILY_PUSH_TIME', '09:30')  # Daily push time in China timezone
CHINA_TIMEZONE = 'Asia/Shanghai'  # China timezone UTC+8
ENABLE_DAILY_PUSH = os.getenv('ENABLE_DAILY_PUSH', 'true').lower() == 'true'

# Data Storage
DATA_DIR = 'data'
PROCESSED_VIDEOS_FILE = os.path.join(DATA_DIR, 'processed_videos.txt')
DAILY_PUSH_LOG_FILE = os.path.join(DATA_DIR, 'daily_push_log.txt')  # Record daily push history

# Headers for requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
