const video = document.querySelector("#promo-video");
const fallback = document.querySelector("#video-fallback");
const source = "https://storage.yandexcloud.net/dtm-presets/video/DTM_hi.m3u8";

function showVideoFallback() {
  fallback.hidden = false;
}

if (video.canPlayType("application/vnd.apple.mpegurl")) {
  video.src = source;
} else if (window.Hls?.isSupported()) {
  const hls = new window.Hls({ enableWorker: true });
  hls.loadSource(source);
  hls.attachMedia(video);
  hls.on(window.Hls.Events.ERROR, (_, data) => {
    if (data.fatal) showVideoFallback();
  });
} else {
  showVideoFallback();
}

const observer = new IntersectionObserver(
  (entries) => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    }
  },
  { threshold: 0.12 },
);

document.querySelectorAll(".reveal").forEach((element, index) => {
  element.style.transitionDelay = `${Math.min(index % 4, 3) * 65}ms`;
  observer.observe(element);
});
