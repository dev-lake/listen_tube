#!/usr/bin/env python3
"""
测试 ListenTube 播放功能的脚本
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:9000"

def test_play_functionality():
    """测试播放功能"""
    print("🧪 测试 ListenTube 播放功能")
    print("=" * 50)
    
    # 1. 创建下载任务
    print("1. 创建下载任务...")
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # 测试视频
    
    try:
        response = requests.post(f"{BASE_URL}/tasks", json={
            "url": test_url,
            "format": "mp3"
        })
        
        if response.status_code != 201:
            print(f"❌ 创建任务失败: {response.status_code}")
            return
            
        task_data = response.json()
        task_id = task_data["id"]
        print(f"✅ 任务创建成功，ID: {task_id}")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务已启动")
        return
    except Exception as e:
        print(f"❌ 创建任务时出错: {e}")
        return
    
    # 2. 监控任务进度
    print("2. 监控任务进度...")
    max_wait = 60  # 最多等待60秒
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{BASE_URL}/tasks/{task_id}")
            if response.status_code == 200:
                task = response.json()
                status = task.get("status")
                progress = task.get("progress", 0)
                
                print(f"   状态: {status}, 进度: {progress:.1f}%")
                
                if status == "finished":
                    print("✅ 任务下载完成！")
                    break
                elif status == "error":
                    print(f"❌ 任务出错: {task.get('error', '未知错误')}")
                    return
                    
            time.sleep(2)
        except Exception as e:
            print(f"   获取任务状态时出错: {e}")
            time.sleep(2)
    else:
        print("⏰ 等待超时，任务可能仍在进行中")
        return
    
    # 3. 测试播放端点
    print("3. 测试播放端点...")
    try:
        response = requests.get(f"{BASE_URL}/tasks/{task_id}/play")
        
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            content_length = response.headers.get("content-length", "未知")
            
            print(f"✅ 播放端点正常")
            print(f"   内容类型: {content_type}")
            print(f"   文件大小: {content_length} 字节")
            
            # 检查是否真的是音频文件
            if "audio/" in content_type:
                print("✅ 确认是音频文件")
            else:
                print("⚠️  警告：内容类型可能不是音频")
                
        else:
            print(f"❌ 播放端点返回错误: {response.status_code}")
            if response.status_code == 404:
                print("   可能原因：文件不存在或已被删除")
            elif response.status_code == 409:
                print("   可能原因：任务状态不正确")
                
    except Exception as e:
        print(f"❌ 测试播放端点时出错: {e}")
    
    # 4. 测试下载端点（对比）
    print("4. 测试下载端点...")
    try:
        response = requests.get(f"{BASE_URL}/tasks/{task_id}/download")
        
        if response.status_code == 200:
            print("✅ 下载端点正常")
        else:
            print(f"❌ 下载端点返回错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试下载端点时出错: {e}")
    
    print("\n" + "=" * 50)
    print("🎵 测试完成！")
    print("\n💡 提示：")
    print("- 如果播放端点正常，在线播放功能应该可以工作")
    print("- 如果仍有问题，请检查浏览器控制台的错误信息")
    print("- 确保浏览器支持音频播放格式")

if __name__ == "__main__":
    test_play_functionality() 