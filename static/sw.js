const CACHE_NAME = "listentube-v1";
const STATIC_CACHE = "listentube-static-v1";
const AUDIO_CACHE = "listentube-audio-v1";

// 需要缓存的静态资源
const STATIC_FILES = [
  "/",
  "/index.html",
  "/style.css",
  "/script.js",
  "/manifest.json",
];

// 安装时缓存静态资源
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      return cache.addAll(STATIC_FILES);
    })
  );
});

// 激活时清理旧缓存
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== STATIC_CACHE && cacheName !== AUDIO_CACHE) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// 拦截请求，实现缓存策略
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // 处理音频文件下载请求
  if (
    url.pathname.startsWith("/tasks/") &&
    url.pathname.endsWith("/download")
  ) {
    event.respondWith(handleAudioDownload(request));
    return;
  }

  // 处理音频文件播放请求
  if (url.pathname.startsWith("/tasks/") && url.pathname.endsWith("/play")) {
    event.respondWith(handleAudioPlay(request));
    return;
  }

  // 处理静态资源请求
  if (STATIC_FILES.includes(url.pathname) || url.pathname === "/") {
    event.respondWith(handleStaticRequest(request));
    return;
  }

  // 其他请求直接发送到网络
  event.respondWith(fetch(request));
});

// 处理静态资源请求
async function handleStaticRequest(request) {
  try {
    // 优先从缓存获取
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    // 缓存中没有则从网络获取并缓存
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    // 网络失败时返回缓存版本
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
}

// 处理音频下载请求
async function handleAudioDownload(request) {
  try {
    // 先尝试从网络获取
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      // 下载成功后缓存音频文件
      const cache = await caches.open(AUDIO_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    // 网络失败时尝试从缓存获取
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
}

// 处理音频播放请求
async function handleAudioPlay(request) {
  try {
    // 先尝试从网络获取
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      // 播放成功后缓存音频文件
      const cache = await caches.open(AUDIO_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    // 网络失败时尝试从缓存获取
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
}

// 清理音频缓存（当缓存过大时）
async function cleanAudioCache() {
  const cache = await caches.open(AUDIO_CACHE);
  const keys = await cache.keys();

  // 如果缓存超过 50 个文件，删除最旧的
  if (keys.length > 50) {
    const oldestKeys = keys.slice(0, keys.length - 50);
    await Promise.all(oldestKeys.map((key) => cache.delete(key)));
  }
}

// 定期清理音频缓存
setInterval(cleanAudioCache, 300000); // 每5分钟清理一次
