#!/usr/bin/env python3
"""
系统测试脚本
用于测试各个组件是否正常工作
"""

import os
import sys
import logging
from bilibili_monitor import BilibiliMonitor
from content_summarizer import ContentSummarizer
from wechat_notifier import WeChatNotifier
from data_manager import DataManager

def setup_simple_logging():
    """设置简单日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def test_bilibili_connection():
    """测试Bilibili连接"""
    print("🔍 测试Bilibili连接...")
    try:
        monitor = BilibiliMonitor()
        videos = monitor.get_latest_videos(3)
        if videos:
            print(f"✅ 成功获取到 {len(videos)} 个视频")
            print(f"   最新视频: {videos[0].get('title', '未知')}")
            return True
        else:
            print("❌ 未获取到任何视频")
            return False
    except Exception as e:
        print(f"❌ Bilibili连接测试失败: {e}")
        return False

def test_ai_news_detection():
    """测试AI早报检测"""
    print("\n🤖 测试AI早报检测...")
    try:
        monitor = BilibiliMonitor()
        ai_videos = monitor.get_ai_news_videos()
        if ai_videos:
            print(f"✅ 找到 {len(ai_videos)} 个AI早报视频")
            for i, video in enumerate(ai_videos[:3]):
                print(f"   {i+1}. {video.get('title', '未知')}")
            return True
        else:
            print("⚠️  未找到AI早报视频（可能UP主最近没有发布）")
            return True  # 这不算错误
    except Exception as e:
        print(f"❌ AI早报检测失败: {e}")
        return False

def test_content_summarizer():
    """测试内容摘要器"""
    print("\n📝 测试内容摘要器...")
    try:
        monitor = BilibiliMonitor()
        summarizer = ContentSummarizer()
        
        videos = monitor.get_latest_videos(1)
        if videos:
            video = videos[0]
            summary = summarizer.generate_summary(video)
            print("✅ 成功生成摘要")
            print(f"   摘要长度: {len(summary)} 字符")
            print(f"   摘要预览: {summary[:100]}...")
            return True
        else:
            print("❌ 无法获取视频进行测试")
            return False
    except Exception as e:
        print(f"❌ 内容摘要器测试失败: {e}")
        return False

def test_data_manager():
    """测试数据管理器"""
    print("\n💾 测试数据管理器...")
    try:
        dm = DataManager()
        stats = dm.get_stats()
        print("✅ 数据管理器工作正常")
        print(f"   已处理视频数: {stats.get('total_processed', 0)}")
        print(f"   数据目录: {stats.get('data_dir', '未知')}")
        return True
    except Exception as e:
        print(f"❌ 数据管理器测试失败: {e}")
        return False

def test_wechat_config():
    """测试企业微信配置"""
    print("\n💬 检查企业微信配置...")
    try:
        from config import WECHAT_WEBHOOK_URL
        
        if not WECHAT_WEBHOOK_URL or 'YOUR_BOT_KEY' in WECHAT_WEBHOOK_URL:
            print("⚠️  企业微信未配置")
            print("   请在 .env 文件中设置 WECHAT_WEBHOOK_URL")
            print("   格式: WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_ACTUAL_KEY")
            return False
        else:
            print("✅ 企业微信配置存在")
            # 不测试实际发送，避免打扰
            return True
    except Exception as e:
        print(f"❌ 企业微信配置检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 AI News Notification System - 系统测试")
    print("=" * 50)
    
    setup_simple_logging()
    
    results = []
    
    # 运行所有测试
    results.append(("Bilibili连接", test_bilibili_connection()))
    results.append(("AI早报检测", test_ai_news_detection()))
    results.append(("内容摘要器", test_content_summarizer()))
    results.append(("数据管理器", test_data_manager()))
    results.append(("企业微信配置", test_wechat_config()))
    
    # 显示结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:12} : {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 项测试通过")
    
    if passed == len(results):
        print("\n🎉 所有测试通过！系统准备就绪。")
        print("\n📝 下一步:")
        print("1. 配置企业微信机器人（如果还没配置）")
        print("2. 运行: python3 main.py --mode test")
        print("3. 正式启动: python3 main.py --mode run")
    else:
        print(f"\n⚠️  有 {len(results) - passed} 项测试未通过，请检查配置。")
    
    return passed == len(results)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
