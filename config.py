#!/usr/bin/env python3
"""
ListenTube 配置文件
"""

# yt-dlp 配置选项
YT_DLP_CONFIG = {
    # 基本设置
    "quiet": True,
    "no_warnings": True,
    "format": "bestaudio/best",
    
    # 音频处理
    "audio_quality": "192",
    
    # Cookies 设置
    "cookiefile": "cookies.txt",  # cookies 文件路径
    
    # 用户代理和请求头
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    },
    
    # 重试设置
    "extractor_retries": 3,
    "fragment_retries": 3,
    "retries": 3,
    "file_access_retries": 3,
    
    # 延迟设置
    "sleep_interval": 1,
    "max_sleep_interval": 5,
    
    # 绕过验证选项
    "no_check_certificate": True,
    "prefer_insecure": True,
    
    # 额外请求头
    "add_header": [
        "Accept-Language: en-US,en;q=0.9",
        "Accept-Encoding: gzip, deflate, br",
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "DNT: 1",
        "Connection: keep-alive",
        "Upgrade-Insecure-Requests: 1",
    ],
    
    # YouTube 特定设置
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "web"],
            "player_skip": ["webpage", "configs"],
        }
    }
}

# 服务器配置
SERVER_CONFIG = {
    "host": "0.0.0.0",
    "port": 9000,
    "debug": False
}

# 任务配置
TASK_CONFIG = {
    "ttl_seconds": 1800,  # 30 分钟
    "clean_interval_seconds": 60,  # 1 分钟
    "deleted_delay_seconds": 300,  # 5 分钟延迟清理
}

# 音频格式配置
AUDIO_FORMATS = {
    "mp3": {
        "mime_type": "audio/mpeg",
        "extension": "mp3",
        "quality": "192"
    },
    "m4a": {
        "mime_type": "audio/mp4",
        "extension": "m4a",
        "quality": "192"
    },
    "opus": {
        "mime_type": "audio/ogg",
        "extension": "opus",
        "quality": "192"
    }
} 