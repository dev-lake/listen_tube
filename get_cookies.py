#!/usr/bin/env python3
"""
获取 YouTube cookies 的辅助脚本
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def check_yt_dlp():
    """检查 yt-dlp 是否安装"""
    try:
        result = subprocess.run(['yt-dlp', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ yt-dlp 已安装，版本: {result.stdout.strip()}")
            return True
        else:
            print("❌ yt-dlp 未正确安装")
            return False
    except FileNotFoundError:
        print("❌ yt-dlp 未安装")
        return False

def get_cookies_with_yt_dlp():
    """使用 yt-dlp 获取 cookies"""
    print("\n🔐 使用 yt-dlp 获取 cookies...")
    print("1. 浏览器将自动打开 YouTube 登录页面")
    print("2. 请登录你的 YouTube 账户")
    print("3. 登录成功后，yt-dlp 会自动获取 cookies")
    
    try:
        # 打开 YouTube 登录页面
        webbrowser.open('https://accounts.google.com/signin/v2/identifier?service=youtube')
        
        # 使用 yt-dlp 获取 cookies
        cmd = [
            'yt-dlp', 
            '--cookies-from-browser', 'chrome',  # 或者 'firefox', 'safari'
            '--cookies', 'cookies.txt',
            '--extract-audio',
            '--audio-format', 'mp3',
            '--audio-quality', '192',
            '--no-download',  # 不下载，只获取 cookies
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ'  # 测试视频
        ]
        
        print("\n正在获取 cookies...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ cookies 获取成功！")
            if os.path.exists('cookies.txt'):
                print(f"📁 cookies 文件已保存: {os.path.abspath('cookies.txt')}")
                return True
            else:
                print("⚠️  cookies 文件未找到")
                return False
        else:
            print("❌ cookies 获取失败")
            print(f"错误信息: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 获取 cookies 时出错: {e}")
        return False

def manual_cookies_guide():
    """手动获取 cookies 的指南"""
    print("\n📖 手动获取 cookies 指南:")
    print("1. 安装浏览器扩展 'Get cookies.txt' 或 'Cookie Quick Manager'")
    print("2. 在浏览器中登录 YouTube")
    print("3. 使用扩展导出 cookies 到 cookies.txt 文件")
    print("4. 将 cookies.txt 文件放在项目根目录")
    print("5. 重新启动服务")

def main():
    """主函数"""
    print("🍪 YouTube Cookies 获取工具")
    print("=" * 40)
    
    # 检查 yt-dlp
    if not check_yt_dlp():
        print("\n请先安装 yt-dlp:")
        print("pip install yt-dlp")
        return
    
    # 检查是否已有 cookies 文件
    if os.path.exists('cookies.txt'):
        print(f"\n✅ 发现现有的 cookies.txt 文件")
        choice = input("是否重新获取？(y/N): ").strip().lower()
        if choice != 'y':
            print("使用现有 cookies 文件")
            return
    
    # 尝试自动获取 cookies
    if get_cookies_with_yt_dlp():
        print("\n🎉 cookies 设置完成！")
        print("现在可以重新启动服务，应该可以绕过人机验证了")
    else:
        print("\n⚠️  自动获取失败，请使用手动方法")
        manual_cookies_guide()

if __name__ == "__main__":
    main() 