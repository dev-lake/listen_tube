# ListenTube Server

基于 Flask + yt-dlp 的 YouTube 视频转音频 API 服务

## 功能特性

- 🎵 支持多种音频格式：MP3、M4A、Opus
- ⚡ 同步下载接口
- 🔄 异步任务接口（支持进度查询）
- 🧹 自动清理临时文件
- 📱 支持 GET/POST 请求
- 🌐 移动端友好的网页界面
- 📱 **PWA 支持** - 可安装到手机主屏幕，支持离线播放

## 安装依赖

```bash
# 安装 Python 依赖
pip3 install -r requirements.txt

# 安装 ffmpeg（必需）
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg

# 安装 Pillow 库（用于生成应用图标）
pip3 install Pillow
```

## 启动服务

### 方式一：使用启动脚本（推荐）

```bash
# 给脚本执行权限（首次使用）
chmod +x start.sh

# 启动服务
./start.sh
```

### 方式二：直接运行

```bash
python3 app.py
```

服务将在 `http://127.0.0.1:9000` 启动

## PWA 功能设置

### 1. 生成应用图标

首次使用 PWA 功能时，需要生成应用图标：

```bash
# 运行图标生成脚本
python3 create_icons.py
```

这将创建 `static/icon-192.png` 和 `static/icon-512.png` 文件。

### 2. PWA 特性

- **添加到主屏幕**: 支持安装到手机主屏幕，像原生应用一样使用
- **离线播放**: 已下载的音频文件支持离线播放
- **缓存管理**: 自动缓存静态资源和音频文件
- **安装提示**: 浏览器会显示"安装应用"提示

## 网页界面

启动服务后，在浏览器中访问 `http://127.0.0.1:9000` 即可使用友好的网页界面。

### 界面功能

1. **异步下载** - 创建后台任务，支持进度监控
2. **音频播放** - 直接在页面播放下载的音频
3. **任务管理** - 查看所有下载任务状态
4. **移动端优化** - 响应式设计，支持触摸操作
5. **PWA 安装** - 显示"安装应用"按钮，支持添加到主屏幕

### 使用步骤

1. 在输入框中粘贴 YouTube 视频链接
2. 选择音频格式（MP3、M4A、Opus）
3. 点击"创建任务"按钮
4. 等待下载完成后，可以：
   - 点击"播放"按钮在页面播放音频
   - 点击"下载"按钮保存到本地
   - 点击"删除"按钮清理任务
5. **PWA 功能**：
   - 点击"安装应用"按钮将应用添加到主屏幕
   - 离线时仍可播放已缓存的音频文件

## API 接口

### 1. 同步下载接口

**接口地址：** `GET /download`

**参数：**
- `url` (必需): YouTube 视频链接
- `format` (可选): 音频格式，支持 `mp3`、`m4a`、`opus`，默认 `mp3`

**示例：**

```bash
# 下载为 MP3 格式
curl -G "http://127.0.0.1:9000/download" \
  --data-urlencode "url=https://www.youtube.com/watch?v=s932K6eUEiY" \
  -o "audio.mp3"

# 下载为 M4A 格式
curl -G "http://127.0.0.1:9000/download" \
  --data-urlencode "url=https://www.youtube.com/watch?v=s932K6eUEiY" \
  --data-urlencode "format=m4a" \
  -o "audio.m4a"
```

**响应：** 直接返回音频文件

---

### 2. 创建异步任务

**接口地址：** `POST /tasks`

**参数：**
- `url` (必需): YouTube 视频链接
- `format` (可选): 音频格式，默认 `mp3`

**请求示例：**

```bash
# 使用 JSON 格式
curl -X POST "http://127.0.0.1:9000/tasks" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=s932K6eUEiY", "format": "mp3"}'

# 使用表单格式
curl -X POST "http://127.0.0.1:9000/tasks" \
  --data-urlencode "url=https://www.youtube.com/watch?v=s932K6eUEiY" \
  --data-urlencode "format=mp3"
```

**响应示例：**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### 3. 查询任务进度

**接口地址：** `GET /tasks/{task_id}`

**参数：**
- `task_id` (必需): 任务 ID

**示例：**

```bash
curl "http://127.0.0.1:9000/tasks/e50dde9c-c3c8-4ef9-bd88-8e3a8b1c04c5"
```

**响应示例：**

```json
{
  "id": "e50dde9c-c3c8-4ef9-bd88-8e3a8b1c04c5",
  "status": "downloading",
  "progress": 45.2,
  "created_at": 1703123456.789,
  "expires_at": 1703125256.789,
  "url": "https://www.youtube.com/watch?v=s932K6eUEiY",
  "format": "mp3",
  "speed": "1.2MiB/s",
  "eta": 30
}
```

**状态说明：**
- `queued`: 排队中
- `downloading`: 下载中
- `finished`: 已完成
- `error`: 出错
- `expired`: 已过期
- `deleted`: 已删除

---

### 4. 下载任务文件

**接口地址：** `GET /tasks/{task_id}/download`

**参数：**
- `task_id` (必需): 任务 ID

**说明：** 此接口为一次性使用，下载后文件会被自动删除

**示例：**

```bash
curl -o "audio.mp3" \
  "http://127.0.0.1:9000/tasks/e50dde9c-c3c8-4ef9-bd88-8e3a8b1c04c5/download"
```

**响应：** 直接返回音频文件

---

## 完整使用流程示例

### 异步下载流程

```bash
# 1. 创建任务
TASK_ID=$(curl -s -X POST "http://127.0.0.1:9000/tasks" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=s932K6eUEiY"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

echo "任务ID: $TASK_ID"

# 2. 轮询进度
while true; do
  STATUS=$(curl -s "http://127.0.0.1:9000/tasks/$TASK_ID" | \
    python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
  
  if [ "$STATUS" = "finished" ]; then
    echo "下载完成！"
    break
  elif [ "$STATUS" = "error" ]; then
    echo "下载出错！"
    exit 1
  fi
  
  echo "状态: $STATUS，等待 5 秒..."
  sleep 5
done

# 3. 下载文件
curl -o "audio.mp3" \
  "http://127.0.0.1:9000/tasks/$TASK_ID/download"
```

---

## 配置说明

### 任务超时时间

默认任务超时时间为 30 分钟（1800 秒），可在代码中修改：

```python
_TASK_TTL_SECONDS = 1800  # 30 分钟
```

### 清理间隔

后台清理线程每 60 秒检查一次过期任务：

```python
_CLEAN_INTERVAL_SECONDS = 60
```

---

## 注意事项

1. **必需依赖**: 确保系统已安装 `ffmpeg`
2. **文件清理**: 下载完成后文件会自动删除，避免占用磁盘空间
3. **任务超时**: 未下载的任务会在 30 分钟后自动过期清理
4. **并发限制**: 当前版本无并发限制，生产环境建议添加限流
5. **错误处理**: 下载失败的任务会保留错误信息供查询
6. **移动端优化**: 网页界面针对手机端进行了优化，支持触摸操作

---

## 故障排除

### 常见错误

1. **ffmpeg 未安装**
   ```
   Error: ffmpeg not found
   ```
   解决：安装 ffmpeg

2. **视频链接无效**
   ```
   Error: Video unavailable
   ```
   解决：检查 YouTube 链接是否正确

3. **格式不支持**
   ```
   Error: No video formats found
   ```
   解决：尝试其他视频或检查网络连接

4. **进度信息显示异常**
   ```
   下载速度显示为乱码或包含特殊字符
   ```
   解决：已修复，现在会自动清理 ANSI 转义字符

5. **在线播放功能无法使用**
   ```
   点击播放按钮后音频无法播放
   ```
   解决：已修复，现在播放和下载使用不同的端点，播放不会删除文件

6. **YouTube 人机验证错误**
   ```
   ERROR: [youtube] xxx: Sign in to confirm you're not a bot
   ```
   解决：使用 cookies 文件绕过验证，详见下方说明

### YouTube 人机验证解决方案

当遇到 YouTube 人机验证时，可以使用以下方法：

#### 方法一：自动获取 Cookies（推荐）

```bash
# 运行 cookies 获取脚本
python3 get_cookies.py
```

脚本会自动：
1. 打开浏览器登录页面
2. 引导你登录 YouTube 账户
3. 自动获取 cookies 文件

#### 方法二：手动获取 Cookies

1. 安装浏览器扩展：
   - Chrome: "Get cookies.txt" 或 "Cookie Quick Manager"
   - Firefox: "Cookie Quick Manager"

2. 在浏览器中登录 YouTube

3. 使用扩展导出 cookies 到 `cookies.txt` 文件

4. 将文件放在项目根目录

#### 方法三：使用现有 Cookies

如果你已经在其他地方有 cookies 文件，直接复制到项目根目录即可。

### 在线播放功能说明

ListenTube 现在支持在线播放功能：

- **播放端点**: `/tasks/{task_id}/play` - 用于在线播放，不会删除文件
- **下载端点**: `/tasks/{task_id}/download` - 用于下载文件，下载后文件会被删除
- **缓存支持**: 播放的音频文件会被 Service Worker 缓存，支持离线播放

### 日志查看

启动服务时会显示详细日志，包括：
- 下载进度
- 错误信息
- 清理操作

---

## 许可证

MIT License 