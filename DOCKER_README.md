# ListenTube Docker 部署指南

## 问题解决

### 构建卡住的原因
1. **磁盘空间不足**：之前磁盘使用率达到 95%，清理后降至 89%
2. **网络连接问题**：某些包的下载失败，可能是代理或网络不稳定导致
3. **依赖过多**：原始 Dockerfile 包含过多不必要的依赖

### 解决方案
1. 清理 Docker 缓存：`docker system prune -af`
2. 使用简化的 Dockerfile，减少依赖
3. 优化构建顺序，先安装 Python 依赖再安装系统依赖

## 快速开始

### 1. 构建镜像
```bash
docker build -t listentube:latest .
```

### 2. 运行容器
```bash
# 生产环境
docker run -d -p 9000:9000 --name listentube listentube:latest

# 开发环境（挂载源代码）
docker run -d -p 9000:9000 -v $(pwd):/app --name listentube-dev listentube:latest
```

### 3. 使用 Docker Compose
```bash
# 启动生产环境
docker-compose up -d

# 启动开发环境
docker-compose --profile dev up -d
```

### 4. 使用便捷脚本
```bash
# 构建并启动
./docker-build.sh run

# 开发环境
./docker-build.sh dev

# 查看日志
./docker-build.sh logs
```

## 访问应用

- **生产环境**：http://localhost:9000
- **开发环境**：http://localhost:9001

## 故障排除

### 构建失败
1. 检查磁盘空间：`df -h`
2. 清理 Docker 缓存：`docker system prune -af`
3. 检查网络连接
4. 使用简化版 Dockerfile

### 容器启动失败
1. 查看容器日志：`docker logs <container_name>`
2. 检查端口占用：`lsof -i :9000`
3. 检查文件权限

### 网络问题
1. 检查防火墙设置
2. 确认端口映射正确
3. 检查 Docker 网络配置

## 性能优化

### 镜像大小优化
- 使用 `--no-install-recommends` 减少不必要的包
- 清理 apt 缓存
- 使用多阶段构建（如需要）

### 构建速度优化
- 利用 Docker 层缓存
- 合理排序 Dockerfile 指令
- 使用 `.dockerignore` 减少构建上下文

## 安全考虑

1. **非 root 用户**：容器以非 root 用户运行
2. **最小权限原则**：只安装必要的依赖
3. **定期更新**：定期更新基础镜像和依赖

## 监控和日志

### 健康检查
容器包含健康检查，每 30 秒检查一次服务状态

### 日志查看
```bash
# 查看实时日志
docker logs -f listentube

# 查看最近 100 行日志
docker logs --tail 100 listentube
```

## 备份和恢复

### 数据备份
```bash
# 备份容器数据
docker cp listentube:/app/data ./backup/

# 备份镜像
docker save listentube:latest > listentube-backup.tar
```

### 恢复
```bash
# 恢复镜像
docker load < listentube-backup.tar

# 恢复数据
docker cp ./backup/ listentube:/app/data
``` 