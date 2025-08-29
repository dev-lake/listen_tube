#!/usr/bin/env python3
"""
测试进度信息修复的脚本
"""

import json
import time
import requests

BASE_URL = "http://127.0.0.1:9000"

def test_progress_info():
    """测试进度信息是否正确显示"""
    
    print("🧪 测试 ListenTube 进度信息修复")
    print("=" * 50)
    
    # 测试用的 YouTube 链接（一个短视频）
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        print(f"📝 创建下载任务: {test_url}")
        
        # 创建任务
        response = requests.post(f"{BASE_URL}/tasks", json={
            "url": test_url,
            "format": "mp3"
        })
        
        if response.status_code != 201:
            print(f"❌ 创建任务失败: {response.status_code}")
            print(f"响应: {response.text}")
            return
        
        task_data = response.json()
        task_id = task_data["id"]
        print(f"✅ 任务创建成功，ID: {task_id}")
        
        # 监控进度
        print("\n📊 监控下载进度...")
        print("-" * 50)
        
        max_attempts = 30  # 最多等待30次
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            
            # 获取任务状态
            status_response = requests.get(f"{BASE_URL}/tasks/{task_id}")
            if status_response.status_code != 200:
                print(f"❌ 获取任务状态失败: {status_response.status_code}")
                break
            
            task = status_response.json()
            status = task.get("status")
            progress = task.get("progress", 0)
            speed = task.get("speed", "未知")
            eta = task.get("eta")
            downloaded = task.get("downloaded_bytes", 0)
            total = task.get("total_bytes", 0)
            
            # 显示进度信息
            progress_bar = "█" * int(progress / 5) + "░" * (20 - int(progress / 5))
            print(f"[{progress_bar}] {progress:.1f}% | 速度: {speed} | ETA: {eta or '--'} | 下载: {downloaded}/{total}")
            
            # 检查任务状态
            if status == "finished":
                print(f"\n🎉 任务完成！")
                break
            elif status == "error":
                print(f"\n❌ 任务出错: {task.get('error', '未知错误')}")
                break
            elif status == "expired":
                print(f"\n⏰ 任务已过期")
                break
            
            # 等待2秒后再次检查
            time.sleep(2)
        
        if attempt >= max_attempts:
            print(f"\n⏱️  等待超时，任务可能仍在进行中")
        
        print("\n" + "=" * 50)
        print("测试完成！")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保 ListenTube 服务正在运行")
        print("运行命令: python3 app.py")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    test_progress_info() 