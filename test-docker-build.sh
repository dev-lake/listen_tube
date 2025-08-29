#!/bin/bash

# Docker 构建测试脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 检查 Docker 状态
check_docker_status() {
    print_header "检查 Docker 状态"
    
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker 守护进程未运行"
        exit 1
    fi
    
    print_message "Docker 守护进程运行正常"
    
    # 检查磁盘空间
    DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -gt 90 ]; then
        print_warning "磁盘空间不足: ${DISK_USAGE}%"
    else
        print_message "磁盘空间充足: ${DISK_USAGE}%"
    fi
}

# 清理旧的构建缓存
cleanup_build_cache() {
    print_header "清理构建缓存"
    
    docker system prune -f
    docker builder prune -f
    
    print_message "构建缓存已清理"
}

# 测试基础镜像拉取
test_base_image() {
    print_header "测试基础镜像拉取"
    
    print_message "拉取 Python 3.11-slim 镜像..."
    docker pull python:3.11-slim
    
    print_message "基础镜像拉取成功"
}

# 构建测试版本
build_test_version() {
    print_header "构建测试版本"
    
    print_message "使用简化版 Dockerfile 构建..."
    
    # 设置构建超时
    timeout 600 docker build -f Dockerfile.test -t listentube:test . || {
        print_error "构建超时或失败"
        return 1
    }
    
    print_message "测试版本构建成功"
}

# 构建完整版本
build_full_version() {
    print_header "构建完整版本"
    
    print_message "使用完整版 Dockerfile 构建..."
    
    # 设置构建超时
    timeout 900 docker build -t listentube:latest . || {
        print_error "构建超时或失败"
        return 1
    }
    
    print_message "完整版本构建成功"
}

# 测试运行容器
test_container() {
    print_header "测试容器运行"
    
    print_message "启动测试容器..."
    
    # 启动容器并等待
    CONTAINER_ID=$(docker run -d -p 9000:9000 listentube:test)
    
    # 等待服务启动
    sleep 10
    
    # 检查容器状态
    if docker ps | grep -q "$CONTAINER_ID"; then
        print_message "容器运行正常"
        
        # 测试健康检查
        if curl -f http://localhost:9000/ > /dev/null 2>&1; then
            print_message "服务响应正常"
        else
            print_warning "服务响应异常"
        fi
        
        # 停止容器
        docker stop "$CONTAINER_ID"
        docker rm "$CONTAINER_ID"
    else
        print_error "容器启动失败"
        docker logs "$CONTAINER_ID"
        docker rm "$CONTAINER_ID" 2>/dev/null || true
        return 1
    fi
}

# 显示构建信息
show_build_info() {
    print_header "构建信息"
    
    echo "Docker 版本: $(docker --version)"
    echo "Docker Compose 版本: $(docker-compose --version)"
    echo "系统架构: $(uname -m)"
    echo "可用内存: $(free -h | grep Mem | awk '{print $7}')"
    echo "可用磁盘: $(df -h . | tail -1 | awk '{print $4}')"
}

# 主函数
main() {
    case "${1:-all}" in
        "check")
            check_docker_status
            show_build_info
            ;;
        "test")
            check_docker_status
            cleanup_build_cache
            test_base_image
            build_test_version
            test_container
            ;;
        "full")
            check_docker_status
            cleanup_build_cache
            build_full_version
            ;;
        "all")
            check_docker_status
            show_build_info
            cleanup_build_cache
            test_base_image
            build_test_version
            test_container
            build_full_version
            ;;
        *)
            echo "用法: $0 [check|test|full|all]"
            echo "  check - 检查 Docker 状态"
            echo "  test  - 构建和测试简化版本"
            echo "  full  - 构建完整版本"
            echo "  all   - 执行所有步骤"
            ;;
    esac
}

# 执行主函数
main "$@" 