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

# 检查和设置虚拟环境
setup_venv() {
    if [ ! -d "venv" ]; then
        print_message $BLUE "创建虚拟环境..."
        python3 -m venv venv
        print_message $GREEN "✓ 虚拟环境创建完成"
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    print_message $GREEN "✓ 虚拟环境已激活"
}

# 检查依赖（智能检查，避免重复安装）
check_dependencies() {
    if [ ! -f "requirements.txt" ]; then
        print_message $RED "错误: 未找到 requirements.txt 文件"
        exit 1
    fi
    
    # 检查依赖是否已安装
    local needs_install=false
    
    # 检查主要依赖是否存在
    if ! python -c "import requests, schedule, dotenv, bs4" &> /dev/null; then
        needs_install=true
    fi
    
    if [ "$needs_install" = true ]; then
        print_message $BLUE "安装 Python 依赖..."
        pip install -r requirements.txt > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            print_message $GREEN "✓ 依赖安装完成"
        else
            print_message $RED "✗ 依赖安装失败"
            exit 1
        fi
    else
        print_message $GREEN "✓ 依赖已安装"
    fi
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
    echo "  stop    停止运行中的服务"
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

# 检查进程状态
check_process_status() {
    local pid_count=$(ps aux | grep -E "(main\.py|python.*main)" | grep -v grep | wc -l)
    local process_info=$(ps aux | grep -E "(main\.py|python.*main)" | grep -v grep)
    
    if [ "$pid_count" -gt 0 ]; then
        print_message $GREEN "✓ 系统正在运行"
        echo "$process_info" | while read line; do
            local pid=$(echo $line | awk '{print $2}')
            local start_time=$(echo $line | awk '{print $9}')
            local mode=$(echo $line | grep -o '\-\-mode [a-z]*' | awk '{print $2}')
            print_message $BLUE "  进程ID: $pid | 启动时间: $start_time | 模式: ${mode:-run}"
        done
        
        # 检查日志文件
        local log_file="logs/ai_news_$(date +%Y%m%d).log"
        if [ -f "$log_file" ]; then
            local last_log=$(tail -1 "$log_file" 2>/dev/null)
            if [ ! -z "$last_log" ]; then
                print_message $BLUE "  最新日志: $last_log"
            fi
        fi
        
        return 0
    else
        print_message $YELLOW "⚠ 系统未运行"
        return 1
    fi
}

# 停止服务
stop_service() {
    print_message $BLUE "正在停止 AI News Notification System..."
    
    local pid_count=$(ps aux | grep -E "(main\.py|python.*main)" | grep -v grep | wc -l)
    
    if [ "$pid_count" -eq 0 ]; then
        print_message $YELLOW "没有找到运行中的服务"
        return 1
    fi
    
    # 获取所有相关进程的PID
    local pids=$(ps aux | grep -E "(main\.py|python.*main)" | grep -v grep | awk '{print $2}')
    
    for pid in $pids; do
        print_message $BLUE "正在停止进程 $pid..."
        kill "$pid" 2>/dev/null
        
        # 等待进程停止
        local count=0
        while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
            sleep 1
            count=$((count + 1))
        done
        
        # 如果进程仍然存在，强制终止
        if kill -0 "$pid" 2>/dev/null; then
            print_message $YELLOW "强制终止进程 $pid..."
            kill -9 "$pid" 2>/dev/null
        fi
        
        print_message $GREEN "✓ 进程 $pid 已停止"
    done
    
    print_message $GREEN "服务已成功停止"
    return 0
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
            run|test|check|status|stop|force|init)
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
    setup_venv
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
    
    # 特殊处理 status 模式
    if [ "$mode" = "status" ]; then
        print_message $BLUE "检查系统运行状态..."
        echo ""
        
        # 检查进程状态
        check_process_status
        process_running=$?
        
        echo ""
        print_message $BLUE "获取详细系统状态..."
        
        # 调用Python程序获取详细状态
        python main.py --mode "$mode" --log-level "$log_level"
        
        echo ""
        if [ $process_running -eq 0 ]; then
            print_message $GREEN "系统运行正常"
        else
            print_message $YELLOW "系统未在后台运行"
            print_message $BLUE "要启动系统，请运行: $0 run"
        fi
        
        exit 0
    fi
    
    # 特殊处理 stop 模式
    if [ "$mode" = "stop" ]; then
        stop_service
        exit $?
    fi
    
    # 启动应用
    print_message $GREEN "启动 AI News Notification System..."
    print_message $BLUE "按 Ctrl+C 停止程序"
    echo ""
    
    python main.py --mode "$mode" --log-level "$log_level"
}

# 运行主函数
main "$@"
