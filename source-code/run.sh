#!/bin/bash

# AI News Notification System 启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 检查Python环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_message $RED "错误: 未找到 python3，请先安装 Python 3.6+"
        exit 1
    fi
    
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_message $GREEN "✓ Python 版本: $python_version"
}

# 检查依赖
check_dependencies() {
    if [ ! -f "requirements.txt" ]; then
        print_message $RED "错误: 未找到 requirements.txt 文件"
        exit 1
    fi
    
    print_message $BLUE "检查 Python 依赖..."
    pip3 install -r requirements.txt > /dev/null 2>&1
    print_message $GREEN "✓ 依赖安装完成"
}

# 检查配置文件
check_config() {
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_message $YELLOW "警告: 未找到 .env 文件，正在从 .env.example 创建..."
            cp .env.example .env
            print_message $YELLOW "请编辑 .env 文件并设置正确的配置值"
        else
            print_message $RED "错误: 未找到配置文件 .env 或 .env.example"
            exit 1
        fi
    fi
    
    # 检查关键配置
    if grep -q "YOUR_BOT_KEY" .env; then
        print_message $YELLOW "警告: 请在 .env 文件中设置正确的 WECHAT_WEBHOOK_URL"
    fi
    
    print_message $GREEN "✓ 配置文件检查完成"
}

# 创建必要目录
create_directories() {
    mkdir -p data logs
    print_message $GREEN "✓ 目录结构创建完成"
}

# 显示帮助信息
show_help() {
    echo "AI News Notification System 启动脚本"
    echo ""
    echo "用法: $0 [选项] [模式]"
    echo ""
    echo "模式:"
    echo "  run     持续运行监控 (默认)"
    echo "  test    发送测试消息"
    echo "  check   执行一次检查"
    echo "  status  查看系统状态"
    echo "  force   强制检查最新视频"
    echo "  init    初始化模式 - 检查并处理当天发布的视频"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -v, --verbose  详细输出 (DEBUG 级别)"
    echo "  --install      仅安装依赖"
    echo "  --config       检查配置"
    echo ""
    echo "示例:"
    echo "  $0 init         # 初始化系统，处理当天发布的视频"
    echo "  $0 test         # 发送测试消息"
    echo "  $0 run -v       # 详细模式运行"
    echo "  $0 --install    # 仅安装依赖"
}

# 主函数
main() {
    local mode="run"
    local log_level="INFO"
    local install_only=false
    local config_only=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                log_level="DEBUG"
                shift
                ;;
            --install)
                install_only=true
                shift
                ;;
            --config)
                config_only=true
                shift
                ;;
            run|test|check|status|force|init)
                mode=$1
                shift
                ;;
            *)
                print_message $RED "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    print_message $BLUE "=== AI News Notification System ==="
    print_message $BLUE "模式: $mode"
    print_message $BLUE "日志级别: $log_level"
    print_message $BLUE "=================================="
    
    # 检查环境
    check_python
    check_dependencies
    
    if [ "$install_only" = true ]; then
        print_message $GREEN "依赖安装完成！"
        exit 0
    fi
    
    check_config
    
    if [ "$config_only" = true ]; then
        print_message $GREEN "配置检查完成！"
        exit 0
    fi
    
    create_directories
    
    # 启动应用
    print_message $GREEN "启动 AI News Notification System..."
    print_message $BLUE "按 Ctrl+C 停止程序"
    echo ""
    
    python3 main.py --mode "$mode" --log-level "$log_level"
}

# 运行主函数
main "$@"
