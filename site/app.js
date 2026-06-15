const video = document.querySelector("#promo-video");
const fallback = document.querySelector("#video-fallback");
const source = "https://storage.yandexcloud.net/dtm-presets/video/DTM_hi.m3u8";

function showVideoFallback() {
  if (fallback) fallback.hidden = false;
}

if (video) {
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
}

const tabs = [...document.querySelectorAll(".tab")];
const panels = [...document.querySelectorAll(".media-panel")];

function activatePanel(name, updateHash = true) {
  for (const tab of tabs) {
    const isActive = tab.dataset.panel === name;
    tab.classList.toggle("active", isActive);
    tab.setAttribute("aria-selected", String(isActive));
  }

  for (const panel of panels) {
    const isActive = panel.dataset.panel === name;
    panel.classList.toggle("active", isActive);
    panel.hidden = !isActive;
  }

  if (updateHash) {
    history.replaceState(null, "", `#${name}`);
  }
}

for (const tab of tabs) {
  tab.addEventListener("click", () => activatePanel(tab.dataset.panel));
}

const initialPanel = location.hash.replace("#", "");
if (tabs.some((tab) => tab.dataset.panel === initialPanel)) {
  activatePanel(initialPanel, false);
}
