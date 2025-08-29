#!/bin/bash

# Google Cloud Run 部署脚本

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

# 配置变量
PROJECT_ID="mysmallservice"
SERVICE_NAME="listen-tube"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# 检查 gcloud 是否安装
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI 未安装，请先安装 Google Cloud SDK"
        exit 1
    fi
    
    print_message "gcloud CLI 已安装"
}

# 检查认证状态
check_auth() {
    print_header "检查认证状态"
    
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "未找到活跃的认证，请先运行: gcloud auth login"
        exit 1
    fi
    
    print_message "认证状态正常"
}

# 设置项目
set_project() {
    print_header "设置项目"
    
    gcloud config set project $PROJECT_ID
    print_message "项目已设置为: $PROJECT_ID"
}

# 启用必要的 API
enable_apis() {
    print_header "启用必要的 API"
    
    gcloud services enable run.googleapis.com
    gcloud services enable containerregistry.googleapis.com
    
    print_message "API 已启用"
}

# 构建镜像
build_image() {
    print_header "构建 Docker 镜像"
    
    print_message "使用 Cloud Run 专用 Dockerfile 构建..."
    docker build -f Dockerfile.cloudrun -t $IMAGE_NAME .
    
    print_message "镜像构建完成: $IMAGE_NAME"
}

# 推送镜像到 Google Container Registry
push_image() {
    print_header "推送镜像到 Google Container Registry"
    
    gcloud auth configure-docker
    docker push $IMAGE_NAME
    
    print_message "镜像已推送到: $IMAGE_NAME"
}

# 部署到 Cloud Run
deploy_service() {
    print_header "部署到 Cloud Run"
    
    gcloud run deploy $SERVICE_NAME \
        --image $IMAGE_NAME \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 1Gi \
        --cpu 1 \
        --timeout 300 \
        --concurrency 80 \
        --max-instances 10
    
    print_message "服务部署完成"
}

# 获取服务 URL
get_service_url() {
    print_header "获取服务 URL"
    
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    print_message "服务 URL: $SERVICE_URL"
}

# 测试服务
test_service() {
    print_header "测试服务"
    
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    
    print_message "等待服务启动..."
    sleep 10
    
    if curl -f "$SERVICE_URL" > /dev/null 2>&1; then
        print_message "服务测试成功！"
        print_message "访问地址: $SERVICE_URL"
    else
        print_warning "服务测试失败，请检查日志"
    fi
}

# 查看日志
show_logs() {
    print_header "查看服务日志"
    
    gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
        --limit=50 \
        --format="table(timestamp,severity,textPayload)"
}

# 清理本地镜像
cleanup() {
    print_header "清理本地镜像"
    
    docker rmi $IMAGE_NAME 2>/dev/null || true
    print_message "清理完成"
}

# 显示帮助信息
show_help() {
    echo "Google Cloud Run 部署脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  deploy    完整部署流程"
    echo "  build     构建镜像"
    echo "  push      推送镜像"
    echo "  deploy-only 仅部署（不构建）"
    echo "  logs      查看日志"
    echo "  test      测试服务"
    echo "  cleanup   清理本地镜像"
    echo "  help      显示此帮助信息"
    echo ""
    echo "环境变量:"
    echo "  PROJECT_ID: $PROJECT_ID"
    echo "  SERVICE_NAME: $SERVICE_NAME"
    echo "  REGION: $REGION"
    echo "  IMAGE_NAME: $IMAGE_NAME"
}

# 主函数
main() {
    case "${1:-help}" in
        "deploy")
            check_gcloud
            check_auth
            set_project
            enable_apis
            build_image
            push_image
            deploy_service
            get_service_url
            test_service
            ;;
        "build")
            check_gcloud
            build_image
            ;;
        "push")
            check_gcloud
            check_auth
            set_project
            push_image
            ;;
        "deploy-only")
            check_gcloud
            check_auth
            set_project
            deploy_service
            get_service_url
            ;;
        "logs")
            check_gcloud
            check_auth
            set_project
            show_logs
            ;;
        "test")
            check_gcloud
            check_auth
            set_project
            test_service
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@" 