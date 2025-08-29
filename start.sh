#!/bin/bash

echo "🎵 ListenTube Server 启动脚本"
echo "================================"

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python"
    exit 1
fi

# 检查依赖是否安装
echo "📦 检查依赖..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "⚠️  警告: Flask 未安装，正在安装依赖..."
    pip3 install -r requirements.txt
fi

if ! python3 -c "import yt_dlp" &> /dev/null; then
    echo "⚠️  警告: yt-dlp 未安装，正在安装依赖..."
    pip3 install -r requirements.txt
fi

# 检查 ffmpeg 是否安装
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  警告: ffmpeg 未安装"
    echo "    macOS: brew install ffmpeg"
    echo "    Ubuntu/Debian: sudo apt install ffmpeg"
    echo "    CentOS/RHEL: sudo yum install ffmpeg"
    echo ""
    echo "请安装 ffmpeg 后再运行服务"
    exit 1
fi

echo "✅ 所有依赖检查完成"
echo ""
echo "🚀 启动 ListenTube Server..."
echo "   网页界面: http://127.0.0.1:9000"
echo "   API 接口: http://127.0.0.1:9000/download"
echo ""
echo "按 Ctrl+C 停止服务"
echo "================================"

# 启动服务
python3 app.py 