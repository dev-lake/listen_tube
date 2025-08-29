import os
import tempfile
import uuid
from typing import Tuple

from flask import Flask, request, jsonify, send_file, send_from_directory
from yt_dlp import YoutubeDL


app = Flask(__name__, static_folder='static', static_url_path='')


def get_audio_mime_and_ext(format_name: str) -> Tuple[str, str]:
    normalized = (format_name or "").strip().lower()
    if normalized in ("mp3", "audio/mpeg"):
        return "audio/mpeg", "mp3"
    if normalized in ("m4a", "aac", "audio/mp4"):
        return "audio/mp4", "m4a"
    if normalized in ("opus", "ogg", "audio/ogg"):
        return "audio/ogg", "opus"
    # default
    return "audio/mpeg", "mp3"


@app.route("/")
def index():
    return send_from_directory('static', 'index.html')


@app.route("/download", methods=["GET"])
def download_audio():
    video_url = request.args.get("url", type=str)
    requested_format = request.args.get("format", default="mp3", type=str)

    if not video_url:
        return jsonify({"error": "missing 'url' query parameter"}), 400

    mime_type, audio_ext = get_audio_mime_and_ext(requested_format)

    temp_dir = tempfile.mkdtemp(prefix="yt_audio_")
    base_name = f"{uuid.uuid4()}"
    # yt-dlp will append proper extension after post-processing
    output_template = os.path.join(temp_dir, base_name + ".%(ext)s")

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_ext,
                "preferredquality": "192",
            }
        ],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            title = info.get("title") or "audio"
    except Exception as exc:
        return jsonify({
            "error": "failed to download or process audio",
            "details": str(exc),
            "hint": "确保已安装 ffmpeg，例如: brew install ffmpeg",
        }), 500

    # After post-processing, the file should be base_name + .<audio_ext>
    audio_path = os.path.join(temp_dir, base_name + f".{audio_ext}")
    if not os.path.exists(audio_path):
        # Fallback: search for any produced file
        produced = [
            os.path.join(temp_dir, f)
            for f in os.listdir(temp_dir)
            if f.startswith(base_name + ".")
        ]
        if produced:
            audio_path = produced[0]
        else:
            return jsonify({"error": "audio file not found after processing"}), 500

    download_name = f"{title}.{audio_ext}"

    return send_file(
        audio_path,
        mimetype=mime_type,
        as_attachment=True,
        download_name=download_name,
        conditional=True,
        etag=True,
        max_age=0,
    )


# -------------------------
# 异步任务实现
# -------------------------
import threading
import time
from datetime import datetime, timedelta

_TASKS = {}
_TASKS_LOCK = threading.Lock()
_TASK_TTL_SECONDS = 1800  # 30 分钟
_CLEAN_INTERVAL_SECONDS = 60


def _now_ts() -> float:
    return time.time()


def _cleanup_task(task_id: str):
    task = _TASKS.get(task_id)
    if not task:
        return
    file_path = task.get("file_path")
    temp_dir = task.get("temp_dir")
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass
    try:
        if temp_dir and os.path.isdir(temp_dir):
            # try to remove temp dir when empty
            for name in os.listdir(temp_dir):
                try:
                    os.remove(os.path.join(temp_dir, name))
                except Exception:
                    pass
            try:
                os.rmdir(temp_dir)
            except Exception:
                pass
    except Exception:
        pass


def _janitor_loop():
    while True:
        time.sleep(_CLEAN_INTERVAL_SECONDS)
        now = _now_ts()
        expired_ids = []
        with _TASKS_LOCK:
            for tid, t in list(_TASKS.items()):
                expires_at = t.get("expires_at")
                status = t.get("status")
                if status == "expired":
                    expired_ids.append(tid)
                    continue
                if status == "deleted":
                    # 已删除状态的任务延迟清理，给用户重新播放的机会
                    if expires_at and now > expires_at + 300:  # 延迟5分钟清理
                        expired_ids.append(tid)
                    continue
                if expires_at and now > expires_at:
                    t["status"] = "expired"
                    expired_ids.append(tid)
        for tid in expired_ids:
            _cleanup_task(tid)
            with _TASKS_LOCK:
                _TASKS.pop(tid, None)


def _clean_ansi(text):
    """清理 ANSI 转义字符"""
    if isinstance(text, str):
        import re
        return re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text).strip()
    return text

def _progress_hook(task_id: str):
    def _hook(d):
        with _TASKS_LOCK:
            task = _TASKS.get(task_id)
            if not task:
                return
            if d.get("status") == "downloading":
                # 处理进度百分比
                progress = 0.0
                if d.get("_percent_str"):
                    try:
                        percent_str = _clean_ansi(d.get("_percent_str"))
                        progress = float(percent_str.replace("%", ""))
                    except (ValueError, AttributeError):
                        pass
                elif d.get("downloaded_bytes") and d.get("total_bytes"):
                    try:
                        progress = (d.get("downloaded_bytes") / d.get("total_bytes")) * 100
                    except (TypeError, ZeroDivisionError):
                        pass
                
                task["progress"] = progress
                
                # 处理下载速度
                speed = d.get("speed_str") or d.get("_speed_str") or "未知"
                task["speed"] = _clean_ansi(speed)
                
                # 处理剩余时间
                eta = d.get("eta") or d.get("eta_str") or None
                if isinstance(eta, str):
                    eta = _clean_ansi(eta)
                    # 尝试转换为数字
                    try:
                        eta = int(eta)
                    except (ValueError, TypeError):
                        pass
                task["eta"] = eta
                
                # 添加更多有用的信息
                if d.get("downloaded_bytes"):
                    task["downloaded_bytes"] = d.get("downloaded_bytes")
                if d.get("total_bytes"):
                    task["total_bytes"] = d.get("total_bytes")
                    
            elif d.get("status") == "finished":
                task["progress"] = 100.0
                task["speed"] = "完成"
                task["eta"] = 0
    return _hook


def _run_download_task(task_id: str, video_url: str, audio_ext: str):
    temp_dir = tempfile.mkdtemp(prefix=f"yt_task_{task_id}_")
    base_name = f"{uuid.uuid4()}"
    output_template = os.path.join(temp_dir, base_name + ".%(ext)s")

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_ext,
                "preferredquality": "192",
            }
        ],
        "progress_hooks": [_progress_hook(task_id)],
        # 添加 cookies 支持
        "cookiefile": "cookies.txt",  # 如果存在 cookies.txt 文件
        # 设置用户代理
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
        # 添加更多选项来绕过验证
        "extractor_retries": 3,
        "fragment_retries": 3,
        "retries": 3,
        "file_access_retries": 3,
        "sleep_interval": 1,
        "max_sleep_interval": 5,
        # 额外的绕过选项
        "no_check_certificate": True,
        "prefer_insecure": True,
        "add_header": [
            "Accept-Language: en-US,en;q=0.9",
            "Accept-Encoding: gzip, deflate, br",
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "DNT: 1",
            "Connection: keep-alive",
            "Upgrade-Insecure-Requests: 1",
        ],
        # 使用不同的提取器
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
                "player_skip": ["webpage", "configs"],
            }
        }
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            title = info.get("title") or "audio"
        audio_path = os.path.join(temp_dir, base_name + f".{audio_ext}")
        if not os.path.exists(audio_path):
            # Fallback
            produced = [
                os.path.join(temp_dir, f)
                for f in os.listdir(temp_dir)
                if f.startswith(base_name + ".")
            ]
            audio_path = produced[0] if produced else None
        if not audio_path or not os.path.exists(audio_path):
            raise RuntimeError("audio file not found after processing")
        with _TASKS_LOCK:
            task = _TASKS.get(task_id)
            if task is not None:
                task.update({
                    "status": "finished",
                    "file_path": audio_path,
                    "temp_dir": temp_dir,
                    "title": title,
                    "expires_at": _now_ts() + _TASK_TTL_SECONDS,
                })
    except Exception as exc:
        with _TASKS_LOCK:
            task = _TASKS.get(task_id)
            if task is not None:
                task.update({
                    "status": "error",
                    "error": str(exc),
                    "expires_at": _now_ts() + _TASK_TTL_SECONDS,
                })
        # best-effort cleanup
        try:
            for name in os.listdir(temp_dir):
                try:
                    os.remove(os.path.join(temp_dir, name))
                except Exception:
                    pass
            os.rmdir(temp_dir)
        except Exception:
            pass


@app.route("/tasks", methods=["POST"])
def create_task():
    payload = request.get_json(silent=True) or {}
    video_url = payload.get("url") or request.args.get("url")
    requested_format = payload.get("format") or request.args.get("format") or "mp3"
    if not video_url:
        return jsonify({"error": "missing 'url'"}), 400

    _, audio_ext = get_audio_mime_and_ext(requested_format)
    task_id = str(uuid.uuid4())
    with _TASKS_LOCK:
        _TASKS[task_id] = {
            "id": task_id,
            "status": "queued",
            "progress": 0.0,
            "created_at": _now_ts(),
            "expires_at": _now_ts() + _TASK_TTL_SECONDS,
            "url": video_url,
            "format": audio_ext,
            "speed": "等待中",
            "eta": None,
            "downloaded_bytes": 0,
            "total_bytes": 0,
        }

    t = threading.Thread(target=_run_download_task, args=(task_id, video_url, audio_ext), daemon=True)
    t.start()

    return jsonify({"id": task_id}), 201


@app.route("/tasks/<task_id>", methods=["GET"])
def get_task(task_id: str):
    with _TASKS_LOCK:
        task = _TASKS.get(task_id)
        if not task:
            return jsonify({"error": "task not found"}), 404
        # do not leak file path
        public = {k: v for k, v in task.items() if k not in ("file_path", "temp_dir")}
    return jsonify(public)


@app.route("/tasks/<task_id>/play", methods=["GET"])
def play_task_file(task_id: str):
    """播放音频文件，不会删除文件"""
    with _TASKS_LOCK:
        task = _TASKS.get(task_id)
        if not task:
            return jsonify({"error": "task not found"}), 404
        
        # 允许已删除状态的任务重新播放（如果文件仍然存在）
        status = task.get("status")
        if status not in ["finished", "deleted"]:
            return jsonify({"error": f"task not ready, status={status}"}), 409
            
        file_path = task.get("file_path")
        title = task.get("title") or "audio"
        audio_ext = task.get("format") or "mp3"
        mime_type, _ = get_audio_mime_and_ext(audio_ext)

    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "file not found"}), 404

    download_name = f"{title}.{audio_ext}"

    return send_file(
        file_path,
        mimetype=mime_type,
        as_attachment=False,  # 不强制下载
        download_name=download_name,
        conditional=True,
        etag=True,
        max_age=0,
    )


@app.route("/tasks/<task_id>/download", methods=["GET"])
def download_task_file(task_id: str):
    with _TASKS_LOCK:
        task = _TASKS.get(task_id)
        if not task:
            return jsonify({"error": "task not found"}), 404
        
        # 允许已删除状态的任务重新下载（如果文件仍然存在）
        status = task.get("status")
        if status not in ["finished", "deleted"]:
            return jsonify({"error": f"task not ready, status={status}"}), 409
            
        file_path = task.get("file_path")
        title = task.get("title") or "audio"
        audio_ext = task.get("format") or "mp3"
        mime_type, _ = get_audio_mime_and_ext(audio_ext)
        
        # 如果任务已经是删除状态，不需要再次标记
        if status == "finished":
            task["status"] = "deleted"
            # 不立即设置 expires_at，让清理线程延迟处理

    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "file not found"}), 404

    download_name = f"{title}.{audio_ext}"

    # send file, then cleanup
    from flask import after_this_request

    @after_this_request
    def _remove_file(response):
        try:
            _cleanup_task(task_id)
        finally:
            return response

    return send_file(
        file_path,
        mimetype=mime_type,
        as_attachment=True,
        download_name=download_name,
        conditional=True,
        etag=True,
        max_age=0,
    )


# 启动清理线程
_janitor = threading.Thread(target=_janitor_loop, daemon=True)
_janitor.start()


if __name__ == "__main__":
    # Example: python app.py -> http://127.0.0.1:5000/download?url=...&format=mp3
    app.run(host="0.0.0.0", port=9000) 