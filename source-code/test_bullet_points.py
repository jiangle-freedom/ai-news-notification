#!/usr/bin/env python3
"""
测试新的bullet points格式功能
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_summarizer import ContentSummarizer

def test_bullet_points():
    """测试bullet points格式化功能"""
    
    summarizer = ContentSummarizer()
    
    # 测试数据：包含时间信息的描述
    test_descriptions = [
        # 测试1: 标准时间格式
        """
        今日AI早报内容概要：
        
        Google AI更新: 09:30
        Google发布了新的AI Pro和Ultra订阅服务，为Gemini CLI用户提供更高的API限额。
        
        OpenAI ChatGPT更新: 10:15  
        OpenAI宣布ChatGPT新增语音对话功能，支持实时语音交互。
        
        Microsoft Copilot发布: 11:00
        微软发布Copilot Studio，让企业用户能够自定义AI助手。
        """,
        
        # 测试2: 日期格式
        """
        本周AI资讯汇总：
        
        Meta AI发布: 9月23日
        Meta发布了新的Code Llama模型，专门优化代码生成任务。
        
        Anthropic Claude更新: 9月24日
        Anthropic发布Claude 3.5 Sonnet新版本，提升了推理能力。
        
        百度文心一言: 9月25日
        百度文心一言新增多模态功能，支持图像理解和生成。
        """,
        
        # 测试3: 无时间信息的普通文本
        """
        AI早报主要内容包括：
        人工智能技术的最新发展动态
        各大科技公司的AI产品更新
        业界专家对AI发展趋势的分析
        AI应用案例和实际效果展示
        相关政策法规的最新变化
        """,
        
        # 测试4: 混合格式
        """
        重要AI新闻: 今天
        各大公司都在加速AI发展
        
        Google发布Gemini: 08:30
        新版本大幅提升性能
        
        普通段落内容
        没有时间标记的信息
        """
    ]
    
    print("🧪 测试bullet points格式化功能")
    print("=" * 60)
    
    for i, description in enumerate(test_descriptions, 1):
        print(f"\n📝 测试 {i}:")
        print("-" * 40)
        print("原始描述:")
        print(description.strip())
        print("\n处理后的bullet points:")
        print("-" * 40)
        
        try:
            cleaned = summarizer._clean_description(description)
            print(cleaned)
        except Exception as e:
            print(f"❌ 处理出错: {e}")
        
        print("\n" + "=" * 60)

def test_summary_generation():
    """测试完整的摘要生成（无长度限制）"""
    
    print("\n🧪 测试完整摘要生成（无长度限制）")
    print("=" * 60)
    
    summarizer = ContentSummarizer()
    
    # 模拟视频数据
    test_video = {
        'title': '【AI 早报 2025-09-25】Google AI Pro和Ultra订阅用户的Gemini CLI限额提升',
        'description': """今日AI早报内容：
        
        Google AI更新: 09:30
        Google发布了新的AI Pro和Ultra订阅服务，为Gemini CLI用户提供更高的API限额，Pro用户每分钟可调用1500次，Ultra用户无限制调用。
        
        OpenAI ChatGPT更新: 10:15  
        OpenAI宣布ChatGPT新增语音对话功能，支持实时语音交互，将在未来几周内向Plus用户开放。
        
        Microsoft Copilot发布: 11:00
        微软发布Copilot Studio，让企业用户能够自定义AI助手，集成到现有工作流程中。
        
        Meta AI进展: 14:30
        Meta发布了新的Code Llama模型，专门优化代码生成任务，在编程测试中表现优异。""",
        'video_url': 'https://www.bilibili.com/video/BV1N3n4zpEk2'
    }
    
    test_video_detail = {
        'description': test_video['description'],
        'tags': ['AI', '人工智能', '科技资讯', 'Google', 'OpenAI']
    }
    
    try:
        # 先测试不带详细信息的摘要
        print("📝 不带详细信息的摘要:")
        print("-" * 40)
        summary1 = summarizer.generate_summary(test_video)
        print(summary1)
        print(f"\n📊 摘要长度: {len(summary1)} 字符")
        
        print("\n📝 带详细信息的摘要:")
        print("-" * 40)
        summary2 = summarizer.generate_summary(test_video, test_video_detail)
        print(summary2)
        print(f"\n📊 摘要长度: {len(summary2)} 字符")
        
        print("\n✅ 摘要生成成功！")
        
    except Exception as e:
        print(f"❌ 摘要生成出错: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试新的bullet points功能")
    
    test_bullet_points()
    test_summary_generation()
    
    print("\n🎉 所有测试完成！")

if __name__ == '__main__':
    main()
