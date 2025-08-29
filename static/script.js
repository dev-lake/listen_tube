// 全局变量
let tasks = new Map();
let progressInterval = null;

// DOM 元素
const elements = {
  asyncUrl: document.getElementById("asyncUrl"),
  asyncFormat: document.getElementById("asyncFormat"),
  createTaskBtn: document.getElementById("createTaskBtn"),
  taskList: document.getElementById("taskList"),
  tasksContainer: document.getElementById("tasksContainer"),
  statusMessage: document.getElementById("statusMessage"),
  loadingOverlay: document.getElementById("loadingOverlay"),
};

// 工具函数
const utils = {
  showStatus: (message, type = "info", duration = 3000) => {
    elements.statusMessage.textContent = message;
    elements.statusMessage.className = `status-message status-${type}`;
    elements.statusMessage.style.display = "block";

    setTimeout(() => {
      elements.statusMessage.style.display = "none";
    }, duration);
  },

  showLoading: () => {
    elements.loadingOverlay.style.display = "flex";
  },

  hideLoading: () => {
    elements.loadingOverlay.style.display = "none";
  },

  validateUrl: (url) => {
    if (!url) return false;
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
    return youtubeRegex.test(url);
  },

  formatBytes: (bytes) => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  },

  formatTime: (seconds) => {
    if (!seconds || seconds < 0) return "--";
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  },
};

// API 调用函数
const api = {
  async createTask(url, format) {
    try {
      const response = await fetch("/tasks", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url, format }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "创建任务失败");
      }

      const data = await response.json();
      return data.id;
    } catch (error) {
      throw error;
    }
  },

  async getTask(taskId) {
    try {
      const response = await fetch(`/tasks/${taskId}`);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "获取任务信息失败");
      }

      const data = await response.json();
      return data;
    } catch (error) {
      throw error;
    }
  },

  async downloadTask(taskId) {
    try {
      const response = await fetch(`/tasks/${taskId}/download`);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "下载文件失败");
      }

      // 创建下载链接
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = `audio.${tasks.get(taskId).format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);

      return true;
    } catch (error) {
      throw error;
    }
  },
};

// 任务管理
const taskManager = {
  addTask(taskId, taskData) {
    tasks.set(taskId, taskData);
    this.renderTasks();
    this.startProgressMonitoring();
  },

  updateTask(taskId, updates) {
    const task = tasks.get(taskId);
    if (task) {
      Object.assign(task, updates);
      this.renderTasks();
    }
  },

  removeTask(taskId) {
    tasks.delete(taskId);
    this.renderTasks();

    if (tasks.size === 0) {
      this.stopProgressMonitoring();
      elements.taskList.style.display = "none";
    }
  },

  renderTasks() {
    if (tasks.size === 0) {
      elements.taskList.style.display = "none";
      return;
    }

    elements.taskList.style.display = "block";
    elements.tasksContainer.innerHTML = "";

    tasks.forEach((task, taskId) => {
      const taskElement = this.createTaskElement(taskId, task);
      elements.tasksContainer.appendChild(taskElement);
    });
  },

  createTaskElement(taskId, task) {
    const div = document.createElement("div");
    div.className = "task-card";
    div.setAttribute("data-task-id", taskId);
    div.innerHTML = `
            <div class="task-header">
                <span class="task-id">${taskId.substring(0, 8)}...</span>
                <span class="task-status status-${
                  task.status
                }">${this.getStatusText(task.status)}</span>
            </div>
            
            <div class="task-progress">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${
                      task.progress || 0
                    }%"></div>
                </div>
                <div style="text-align: center; margin-top: 0.5rem; font-size: 0.9rem;">
                    ${task.progress ? `${task.progress.toFixed(1)}%` : "0%"}
                    ${
                      task.downloaded_bytes && task.total_bytes
                        ? ` (${utils.formatBytes(
                            task.downloaded_bytes
                          )} / ${utils.formatBytes(task.total_bytes)})`
                        : ""
                    }
                </div>
            </div>
            
            <div class="task-info">
                <div><span>格式:</span> ${task.format.toUpperCase()}</div>
                <div><span>速度:</span> ${task.speed || "--"}</div>
                <div><span>剩余时间:</span> ${utils.formatTime(task.eta)}</div>
                <div><span>创建时间:</span> ${new Date(
                  task.created_at * 1000
                ).toLocaleTimeString()}</div>
            </div>
            
            ${this.getTaskActions(taskId, task)}
        `;

    return div;
  },

  getStatusText(status) {
    const statusMap = {
      queued: "排队中",
      downloading: "下载中",
      finished: "已完成",
      error: "出错",
      expired: "已过期",
      deleted: "已删除",
    };
    return statusMap[status] || status;
  },

  getTaskActions(taskId, task) {
    if (task.status === "finished") {
      return `
                <div class="task-actions">
                    <button class="btn btn-small btn-primary" onclick="taskManager.playAudio('${taskId}')">
                        <i class="fas fa-play"></i> 播放
                    </button>
                    <button class="btn btn-small btn-success" onclick="taskManager.downloadTask('${taskId}')">
                        <i class="fas fa-download"></i> 下载
                    </button>
                    <button class="btn btn-small btn-danger" onclick="taskManager.removeTask('${taskId}')">
                        <i class="fas fa-trash"></i> 删除
                    </button>
                </div>
            `;
    } else if (task.status === "error") {
      return `
                <div class="tasks-actions">
                    <button class="btn btn-small btn-danger" onclick="taskManager.removeTask('${taskId}')">
                        <i class="fas fa-trash"></i> 删除
                    </button>
                </div>
            `;
    }
    return "";
  },

  startProgressMonitoring() {
    if (progressInterval) return;

    progressInterval = setInterval(async () => {
      for (const [taskId, task] of tasks) {
        if (task.status === "queued" || task.status === "downloading") {
          try {
            const updatedTask = await api.getTask(taskId);
            this.updateTask(taskId, updatedTask);

            // 如果任务完成或出错，停止监控
            if (
              ["finished", "error", "expired", "deleted"].includes(
                updatedTask.status
              )
            ) {
              if (updatedTask.status === "finished") {
                utils.showStatus("任务完成！", "success");
              } else if (updatedTask.status === "error") {
                utils.showStatus("任务出错！", "error");
              }
            }
          } catch (error) {
            console.error("获取任务状态失败:", error);
          }
        }
      }
    }, 2000);
  },

  stopProgressMonitoring() {
    if (progressInterval) {
      clearInterval(progressInterval);
      progressInterval = null;
    }
  },

  async downloadTask(taskId) {
    try {
      utils.showLoading();
      await api.downloadTask(taskId);
      utils.showStatus("下载成功！", "success");
      this.removeTask(taskId);
    } catch (error) {
      utils.showStatus(error.message, "error");
    } finally {
      utils.hideLoading();
    }
  },

  async playAudio(taskId) {
    try {
      const task = tasks.get(taskId);
      if (!task) {
        utils.showStatus("任务不存在", "error");
        return;
      }

      // 创建音频播放器
      const audioPlayer = this.createAudioPlayer(taskId, task);

      // 显示播放器
      this.showAudioPlayer(taskId, audioPlayer);
    } catch (error) {
      utils.showStatus("播放失败: " + error.message, "error");
    }
  },

  createAudioPlayer(taskId, task) {
    const playerDiv = document.createElement("div");
    playerDiv.className = "audio-player";
    playerDiv.innerHTML = `
      <div class="player-header">
        <h4><i class="fas fa-music"></i> ${task.title || "音频播放"}</h4>
        <button class="btn btn-small btn-danger close-btn" onclick="taskManager.closeAudioPlayer('${taskId}')">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <audio controls preload="metadata" style="width: 100%;">
        <source src="/tasks/${taskId}/play" type="audio/${task.format}">
        您的浏览器不支持音频播放
      </audio>
      <div class="player-info">
        <span>格式: ${task.format.toUpperCase()}</span>
        <span>大小: ${
          task.downloaded_bytes
            ? utils.formatBytes(task.downloaded_bytes)
            : "未知"
        }</span>
      </div>
    `;

    return playerDiv;
  },

  showAudioPlayer(taskId, playerElement) {
    // 移除现有的播放器
    this.closeAudioPlayer(taskId);

    // 添加到任务卡片下方
    const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
    if (taskCard) {
      taskCard.appendChild(playerElement);
    }
  },

  closeAudioPlayer(taskId) {
    const existingPlayer = document.querySelector(
      `[data-task-id="${taskId}"] .audio-player`
    );
    if (existingPlayer) {
      existingPlayer.remove();
    }
  },
};

// 事件处理
const eventHandlers = {
  async handleCreateTask() {
    const url = elements.asyncUrl.value.trim();
    const format = elements.asyncFormat.value;

    if (!utils.validateUrl(url)) {
      utils.showStatus("请输入有效的 YouTube 链接", "error");
      return;
    }

    try {
      utils.showLoading();
      elements.createTaskBtn.disabled = true;

      const taskId = await api.createTask(url, format);

      // 添加任务到列表
      taskManager.addTask(taskId, {
        id: taskId,
        status: "queued",
        progress: 0,
        created_at: Date.now() / 1000,
        url: url,
        format: format,
        speed: "等待中",
        eta: null,
        downloaded_bytes: 0,
        total_bytes: 0,
      });

      utils.showStatus("任务创建成功！", "success");
      elements.asyncUrl.value = "";
    } catch (error) {
      utils.showStatus(error.message, "error");
    } finally {
      utils.hideLoading();
      elements.createTaskBtn.disabled = false;
    }
  },
};

// 初始化
document.addEventListener("DOMContentLoaded", () => {
  // 绑定事件
  elements.createTaskBtn.addEventListener(
    "click",
    eventHandlers.handleCreateTask
  );

  // 回车键支持
  elements.asyncUrl.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      eventHandlers.handleCreateTask();
    }
  });

  // 粘贴支持
  elements.asyncUrl.addEventListener("paste", (e) => {
    setTimeout(() => {
      if (utils.validateUrl(elements.asyncUrl.value)) {
        elements.asyncFormat.focus();
      }
    }, 100);
  });

  // 初始化状态
  utils.showStatus("欢迎使用 ListenTube！", "info", 2000);

  // 初始化 PWA 功能
  pwaManager.init();
});

// 错误处理
window.addEventListener("error", (e) => {
  console.error("JavaScript 错误:", e.error);
  utils.showStatus("发生未知错误，请刷新页面重试", "error");
});

// 未处理的 Promise 拒绝
window.addEventListener("unhandledrejection", (e) => {
  console.error("未处理的 Promise 拒绝:", e.reason);
  utils.showStatus("网络请求失败，请检查网络连接", "error");
});

// PWA 安装提示功能
const pwaManager = {
  deferredPrompt: null,
  installButton: null,

  init() {
    // 创建安装按钮
    this.createInstallButton();

    // 监听 beforeinstallprompt 事件
    window.addEventListener("beforeinstallprompt", (e) => {
      e.preventDefault();
      this.deferredPrompt = e;
      this.showInstallButton();
    });

    // 监听 appinstalled 事件
    window.addEventListener("appinstalled", () => {
      this.hideInstallButton();
      utils.showStatus("应用已成功安装到主屏幕！", "success", 5000);
    });
  },

  createInstallButton() {
    // 在 header 下方创建安装按钮
    const header = document.querySelector(".header");
    this.installButton = document.createElement("button");
    this.installButton.className = "btn btn-install";
    this.installButton.innerHTML = '<i class="fas fa-download"></i> 安装应用';
    this.installButton.style.display = "none";
    this.installButton.style.margin = "10px auto";
    this.installButton.style.display = "block";

    // 插入到 header 后面
    header.parentNode.insertBefore(this.installButton, header.nextSibling);

    // 绑定点击事件
    this.installButton.addEventListener("click", () => {
      this.installApp();
    });
  },

  showInstallButton() {
    if (this.installButton) {
      this.installButton.style.display = "block";
    }
  },

  hideInstallButton() {
    if (this.installButton) {
      this.installButton.style.display = "none";
    }
  },

  async installApp() {
    if (!this.deferredPrompt) {
      utils.showStatus("无法安装应用", "error");
      return;
    }

    try {
      this.deferredPrompt.prompt();
      const { outcome } = await this.deferredPrompt.userChoice;

      if (outcome === "accepted") {
        utils.showStatus("正在安装应用...", "info");
      } else {
        utils.showStatus("安装已取消", "info");
      }

      this.deferredPrompt = null;
      this.hideInstallButton();
    } catch (error) {
      console.error("安装失败:", error);
      utils.showStatus("安装失败，请重试", "error");
    }
  },
};
