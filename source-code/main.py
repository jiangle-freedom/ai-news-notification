#!/usr/bin/env python3
"""
AI News Notification System
监控Bilibili UP主橘鸦Juya的AI早报，并通过企业微信机器人发送通知
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from scheduler import AINewsScheduler

def setup_logging(log_level: str = 'INFO'):
    """设置日志配置"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 创建logs目录
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 设置日志文件
    log_file = os.path.join(log_dir, f'ai_news_{datetime.now().strftime("%Y%m%d")}.log')
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging setup complete. Log file: {log_file}")
    return logger

def validate_environment(skip_wechat=False):
    """验证环境配置"""
    logger = logging.getLogger(__name__)
    
    # 检查必要的环境变量
    from config import WECHAT_WEBHOOK_URL, BILIBILI_UP_UID
    
    if not skip_wechat and (not WECHAT_WEBHOOK_URL or 'YOUR_BOT_KEY' in WECHAT_WEBHOOK_URL):
        logger.warning("WeChat webhook URL not configured. Please set WECHAT_WEBHOOK_URL in .env file")
        logger.warning("You can still test other functions, but notifications won't work")
        return False
    
    if not BILIBILI_UP_UID:
        logger.error("Bilibili UP UID not configured. Please set BILIBILI_UP_UID in .env file")
        return False
    
    logger.info("Environment validation passed")
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI News Notification System')
    parser.add_argument('--mode', choices=['run', 'test', 'check', 'status', 'force', 'init'], 
                       default='run', help='运行模式')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='日志级别')
    
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logging(args.log_level)
    
    try:
        logger.info("=" * 50)
        logger.info("AI News Notification System Starting")
        logger.info(f"Mode: {args.mode}")
        logger.info(f"Log Level: {args.log_level}")
        logger.info("=" * 50)
        
        # 验证环境（状态模式跳过微信验证）
        skip_wechat = args.mode == 'status'
        if not validate_environment(skip_wechat) and args.mode not in ['status']:
            logger.error("Environment validation failed. Exiting.")
            sys.exit(1)
        
        # 创建调度器
        scheduler = AINewsScheduler()
        
        if args.mode == 'run':
            # 正常运行模式
            logger.info("Starting in normal run mode...")
            scheduler.start_scheduler()
            
        elif args.mode == 'test':
            # 测试模式
            logger.info("Running in test mode...")
            scheduler.send_test_notification()
            
        elif args.mode == 'check':
            # 单次检查模式
            logger.info("Running single check...")
            scheduler.run_once()
            
        elif args.mode == 'status':
            # 状态查看模式
            logger.info("Getting system status...")
            status = scheduler.get_status()
            print("\n=== System Status ===")
            for key, value in status.items():
                print(f"{key}: {value}")
            return
                
        elif args.mode == 'force':
            # 强制检查模式
            logger.info("Running force check mode...")
            scheduler.force_check_all_videos()
            
        elif args.mode == 'init':
            # 初始化模式 - 只处理最新视频
            logger.info("Running initialization mode...")
            scheduler.run_first_time_setup()
        
        logger.info("Program completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("AI News Notification System Stopped")

if __name__ == '__main__':
    main()
