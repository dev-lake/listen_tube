#!/bin/bash

echo "🚀 ListenTube 播放功能测试"
echo "================================"

# 检查服务是否运行
echo "1. 检查服务状态..."
if curl -s http://127.0.0.1:9000/ > /dev/null; then
    echo "✅ 服务正在运行"
else
    echo "❌ 服务未运行，正在启动..."
    if [ -f "start.sh" ]; then
        chmod +x start.sh
        ./start.sh &
        sleep 3
        echo "✅ 服务已启动"
    else
        echo "❌ 找不到启动脚本，请手动启动服务"
        exit 1
    fi
fi

echo ""
echo "2. 测试播放端点..."
echo "   访问 http://127.0.0.1:9000 创建下载任务"
echo "   等待任务完成后点击播放按钮测试"

echo ""
echo "3. 如果仍有问题，运行详细测试："
echo "   python3 test_play.py"

echo ""
echo "4. 检查浏览器控制台是否有错误信息"
echo "   按 F12 打开开发者工具查看 Console 标签"

echo ""
echo "🎵 现在可以测试在线播放功能了！" 