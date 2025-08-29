#!/bin/bash

# ListenTube Docker 构建和运行脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
}

# 构建镜像
build_image() {
    print_header "构建 ListenTube Docker 镜像"
    docker build -t listentube:latest .
    print_message "镜像构建完成"
}

# 运行生产环境
run_production() {
    print_header "启动 ListenTube 生产环境"
    docker-compose up -d listentube
    print_message "服务已启动，访问地址: http://localhost:9000"
}

# 运行开发环境
run_development() {
    print_header "启动 ListenTube 开发环境"
    docker-compose --profile dev up -d listentube-dev
    print_message "开发环境已启动，访问地址: http://localhost:9001"
}

# 停止服务
stop_services() {
    print_header "停止 ListenTube 服务"
    docker-compose down
    print_message "服务已停止"
}

# 查看日志
show_logs() {
    print_header "查看服务日志"
    docker-compose logs -f
}

# 清理
cleanup() {
    print_header "清理 Docker 资源"
    docker-compose down --rmi all --volumes --remove-orphans
    docker system prune -f
    print_message "清理完成"
}

# 显示帮助信息
show_help() {
    echo "ListenTube Docker 管理脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  build       构建 Docker 镜像"
    echo "  run         启动生产环境"
    echo "  dev         启动开发环境"
    echo "  stop        停止所有服务"
    echo "  logs        查看服务日志"
    echo "  cleanup     清理 Docker 资源"
    echo "  help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 build     # 构建镜像"
    echo "  $0 run       # 启动生产环境"
    echo "  $0 dev       # 启动开发环境"
}

# 主函数
main() {
    check_docker
    
    case "${1:-help}" in
        build)
            build_image
            ;;
        run)
            build_image
            run_production
            ;;
        dev)
            build_image
            run_development
            ;;
        stop)
            stop_services
            ;;
        logs)
            show_logs
            ;;
        cleanup)
            cleanup
            ;;
        help|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@" 