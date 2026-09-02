// 파르데아 도감 - 오프라인에서도 쓸 수 있도록 앱 파일을 캐시한다.
// (포켓몬 이미지는 외부 URL이라 캐시하지 않는다 - 인터넷 있을 때만 보임)
const CACHE_NAME = "paldea-dex-v1";
const CORE_ASSETS = [
  "./index.html",
  "./style.css",
  "./app.js",
  "./data.js",
  "./manifest.json",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(CORE_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  );
});
