const tabs = [...document.querySelectorAll(".tab")];
const panels = [...document.querySelectorAll(".media-panel")];
const promoVideo = document.querySelector("#promo-video");
const videoFallback = document.querySelector("#video-fallback");

const promoHlsSource = "https://storage.yandexcloud.net/dtm-presets/video/DTM_hi.m3u8";
const promoMp4Fallback = "./assets/DTM_promo_h264.mp4";

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

function showVideoFallback() {
  if (videoFallback) {
    videoFallback.hidden = false;
  }
}

function useMp4VideoFallback() {
  if (!promoVideo || promoVideo.currentSrc.endsWith("DTM_promo_h264.mp4")) {
    showVideoFallback();
    return;
  }

  promoVideo.src = promoMp4Fallback;
  promoVideo.load();
}

if (promoVideo) {
  if (promoVideo.canPlayType("application/vnd.apple.mpegurl")) {
    promoVideo.src = promoHlsSource;
  } else if (window.Hls?.isSupported()) {
    const hls = new window.Hls({ enableWorker: true });
    hls.loadSource(promoHlsSource);
    hls.attachMedia(promoVideo);
    hls.on(window.Hls.Events.ERROR, (_event, data) => {
      if (data.fatal) {
        hls.destroy();
        useMp4VideoFallback();
      }
    });
  } else {
    useMp4VideoFallback();
  }

  promoVideo.addEventListener("error", useMp4VideoFallback);
}
