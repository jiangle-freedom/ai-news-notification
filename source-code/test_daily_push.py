#!/usr/bin/env python3
"""
测试新的定时推送功能
"""

import sys
import os
import logging
from datetime import datetime
import pytz

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scheduler import AINewsScheduler
from config import CHINA_TIMEZONE, DAILY_PUSH_TIME, ENABLE_DAILY_PUSH

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_daily_push_timing():
    """测试定时推送时间逻辑"""
    print("🧪 测试定时推送时间逻辑")
    
    # 创建调度器实例
    scheduler = AINewsScheduler()
    
    # 获取中国时间
    china_tz = pytz.timezone(CHINA_TIMEZONE)
    china_now = datetime.now(china_tz)
    
    print(f"当前中国时间: {china_now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"配置的推送时间: {DAILY_PUSH_TIME}")
    print(f"是否启用定时推送: {ENABLE_DAILY_PUSH}")
    
    # 测试是否已经执行过今日推送
    is_done = scheduler._is_daily_push_done_today()
    print(f"今日是否已执行定时推送: {is_done}")
    
    return True

def test_video_time_filtering():
    """测试视频时间筛选逻辑"""
    print("\n🧪 测试视频时间筛选逻辑")
    
    scheduler = AINewsScheduler()
    
    # 模拟视频数据
    mock_videos = [
        {
            'bvid': 'BV1test1',
            'title': '测试视频1',
            'created': int(datetime.now().timestamp()) - 3600,  # 1小时前
        },
        {
            'bvid': 'BV1test2', 
            'title': '测试视频2',
            'created': int(datetime.now().timestamp()) - 86400,  # 1天前
        }
    ]
    
    # 测试时间筛选
    daily_videos = scheduler._get_videos_for_daily_push(mock_videos)
    print(f"找到 {len(daily_videos)} 个适合定时推送的视频")
    
    for video in daily_videos:
        created_time = datetime.fromtimestamp(video['created'], tz=scheduler.china_tz)
        print(f"  - {video['title']} (发布于: {created_time.strftime('%Y-%m-%d %H:%M:%S')})")
    
    return True

def test_configuration():
    """测试配置"""
    print("\n🧪 测试配置")
    
    print(f"检查间隔: {os.getenv('CHECK_INTERVAL', '360')} 分钟")
    print(f"定时推送时间: {DAILY_PUSH_TIME}")
    print(f"中国时区: {CHINA_TIMEZONE}")
    print(f"启用定时推送: {ENABLE_DAILY_PUSH}")
    
    return True

def main():
    """主测试函数"""
    setup_logging()
    
    print("🚀 开始测试新的定时推送功能")
    print("=" * 50)
    
    try:
        # 运行所有测试
        tests = [
            test_configuration,
            test_daily_push_timing,
            test_video_time_filtering,
        ]
        
        all_passed = True
        for test in tests:
            try:
                result = test()
                if not result:
                    all_passed = False
                    print(f"❌ {test.__name__} 失败")
                else:
                    print(f"✅ {test.__name__} 通过")
            except Exception as e:
                print(f"❌ {test.__name__} 出错: {e}")
                all_passed = False
        
        print("\n" + "=" * 50)
        if all_passed:
            print("🎉 所有测试通过！")
        else:
            print("⚠️  部分测试失败，请检查配置和代码")
            
    except Exception as e:
        print(f"💥 测试过程中出现错误: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
