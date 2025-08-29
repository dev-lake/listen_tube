# Google Cloud Run 部署指南

## 问题解决

### 部署失败的原因
1. **端口配置错误**：应用配置在端口 9000，但 Cloud Run 期望端口 8080
2. **环境变量缺失**：没有正确设置 PORT 环境变量
3. **启动超时**：容器启动时间超过 Cloud Run 的默认超时时间

### 解决方案
1. 修改应用代码支持 PORT 环境变量
2. 创建专门的 Cloud Run Dockerfile
3. 配置适当的启动探针和健康检查

## 快速部署

### 方法一：使用部署脚本（推荐）

```bash
# 完整部署流程
./deploy-cloudrun.sh deploy

# 仅构建镜像
./deploy-cloudrun.sh build

# 仅部署（不重新构建）
./deploy-cloudrun.sh deploy-only

# 查看日志
./deploy-cloudrun.sh logs
```

### 方法二：手动部署

```bash
# 1. 设置项目
gcloud config set project mysmallservice

# 2. 启用 API
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# 3. 构建镜像
docker build -f Dockerfile.cloudrun -t gcr.io/mysmallservice/listen-tube .

# 4. 推送镜像
gcloud auth configure-docker
docker push gcr.io/mysmallservice/listen-tube

# 5. 部署服务
gcloud run deploy listen-tube \
    --image gcr.io/mysmallservice/listen-tube \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --concurrency 80 \
    --max-instances 10
```

### 方法三：使用配置文件

```bash
# 使用 YAML 配置文件部署
gcloud run services replace cloudrun.yaml --region=us-central1
```

## 配置说明

### 环境变量
- `PORT=8080`：Cloud Run 要求的端口
- `PYTHONUNBUFFERED=1`：确保 Python 输出不被缓存

### 资源配置
- **内存**：1Gi（适合音频处理）
- **CPU**：1 核
- **超时**：300 秒（5 分钟）
- **并发**：80 个请求
- **最大实例**：10 个

### 健康检查
- **启动探针**：10 秒延迟，5 秒间隔
- **存活探针**：30 秒间隔
- **路径**：`/`（根路径）

## 故障排除

### 常见错误

#### 1. 容器启动失败
```bash
# 查看详细日志
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=listen-tube" --limit=50
```

#### 2. 端口配置错误
确保 Dockerfile 中：
```dockerfile
EXPOSE 8080
ENV PORT=8080
```

#### 3. 内存不足
增加内存配置：
```bash
gcloud run services update listen-tube --memory 2Gi --region=us-central1
```

#### 4. 启动超时
增加启动时间：
```bash
gcloud run services update listen-tube --timeout 600 --region=us-central1
```

### 调试步骤

1. **检查镜像构建**
```bash
docker build -f Dockerfile.cloudrun -t test-image .
docker run -p 8080:8080 test-image
```

2. **检查本地运行**
```bash
PORT=8080 python app.py
curl http://localhost:8080/
```

3. **查看 Cloud Run 日志**
```bash
gcloud run services logs read listen-tube --region=us-central1
```

## 性能优化

### 冷启动优化
1. **使用第二代执行环境**
2. **启用 CPU 提升**
3. **禁用 CPU 限制**

### 资源配置优化
```bash
# 根据实际需求调整
gcloud run services update listen-tube \
    --memory 2Gi \
    --cpu 2 \
    --concurrency 100 \
    --max-instances 20 \
    --region=us-central1
```

### 网络优化
1. **使用 VPC 连接器**（如需要）
2. **配置 CDN**（如需要）

## 监控和维护

### 查看指标
```bash
# 查看服务指标
gcloud run services describe listen-tube --region=us-central1

# 查看请求统计
gcloud run services logs read listen-tube --region=us-central1 --limit=100
```

### 自动扩缩容
- **最小实例**：0（节省成本）
- **最大实例**：10（控制成本）
- **并发请求**：80（优化性能）

### 成本优化
1. **设置预算告警**
2. **监控资源使用**
3. **优化代码效率**

## 安全配置

### 身份验证
```bash
# 允许未认证访问（当前配置）
--allow-unauthenticated

# 或要求认证
--no-allow-unauthenticated
```

### 网络安全
1. **VPC 连接器**
2. **私有服务连接**
3. **Cloud Armor**（如需要）

## 更新部署

### 滚动更新
```bash
# 自动滚动更新
gcloud run services update listen-tube --image gcr.io/mysmallservice/listen-tube:latest
```

### 蓝绿部署
```bash
# 创建新版本
gcloud run services update listen-tube --image gcr.io/mysmallservice/listen-tube:v2

# 回滚到旧版本
gcloud run services update listen-tube --image gcr.io/mysmallservice/listen-tube:v1
```

## 备份和恢复

### 镜像备份
```bash
# 导出镜像
docker save gcr.io/mysmallservice/listen-tube > backup.tar

# 导入镜像
docker load < backup.tar
```

### 配置备份
```bash
# 导出服务配置
gcloud run services describe listen-tube --region=us-central1 > service-config.yaml
``` 