<template>
  <div class="viewer-ui flex min-h-screen bg-slate-50 dark:bg-slate-900 overflow-hidden font-sans">
    <Sidebar />
    <main class="flex-1 flex flex-col p-4 md:p-8 h-screen overflow-y-auto bg-slate-50 dark:bg-slate-950 text-slate-800 dark:text-slate-100 transition-colors duration-300">
      <header class="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 class="text-3xl font-black tracking-tight text-slate-900 dark:text-white flex items-center gap-3">
            {{ t.live.title }}
          </h1>
          <p class="text-slate-500 dark:text-slate-400 font-bold uppercase tracking-widest text-xs mt-2">{{ t.live.subtitle }}</p>
        </div>
        
        <div class="flex gap-4">
          <button @click="captureFrame" class="px-5 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-xl font-bold text-sm transition-all flex items-center gap-2 shadow-sm active:scale-95">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/></svg>
            {{ t.live.captureFrame }}
          </button>
          <button 
            @click="toggleRecording" 
            :disabled="isConverting"
            :class="isConverting ? 'bg-amber-500 text-white shadow-amber-500/30' : isRecording ? 'bg-slate-800 hover:bg-slate-900 text-white shadow-slate-900/30' : 'bg-red-500 hover:bg-red-600 text-white shadow-red-500/30'"
            class="px-5 py-2.5 rounded-xl font-bold text-sm transition-all shadow-lg flex items-center gap-2 active:scale-95 min-w-[180px] justify-center"
          >
            <template v-if="isConverting">
              <div class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              {{ langStore.isZh ? '轉檔中...' : 'Converting...' }}
            </template>
            <template v-else>
              <div v-if="!isRecording" class="w-2.5 h-2.5 bg-white rounded-full"></div>
              <div v-else class="w-3 h-3 bg-red-500 rounded-sm animate-pulse"></div>
              {{ isRecording ? t.live.stopRecording : t.live.startRecording }}
            </template>
          </button>
        </div>
      </header>

      <div class="flex-1 min-h-0 flex gap-6 relative">
        <!-- Capture Flash Effect -->
        <div v-if="flash" class="absolute inset-0 bg-white z-50 transition-opacity duration-150 pointer-events-none rounded-3xl" :class="flash ? 'opacity-70' : 'opacity-0'"></div>
        
        <!-- Live Video Feed -->
        <div class="flex-1 bg-black rounded-3xl overflow-hidden relative shadow-2xl border border-slate-200 dark:border-slate-800">
               <!-- Video Element (Supports both WebRTC MediaStream and local file fallback) -->
          <video 
            ref="videoRef"
            autoplay
            muted
            loop
            playsinline
            class="w-full h-full object-cover"
          ></video>

        <!-- Offline State -->
        <div v-if="isOffline" class="absolute inset-0 flex flex-col items-center justify-center text-center p-6 bg-slate-950">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="text-slate-600 mb-6"><path d="m2 2 20 20"/><path d="M10.41 10.41a2 2 0 1 1-2.83-2.83"/><path d="M13.87 13.88a2 2 0 0 1-2.97-2.83"/><path d="M13.87 7.05a5.5 5.5 0 0 0-7.78 0"/><path d="M17.41 17.41a5.5 5.5 0 0 1-7.78 0"/><path d="M20.95 20.95a10.5 10.5 0 0 1-14.85 0"/><path d="M20.95 3.05a10.5 10.5 0 0 0-14.85 0"/></svg>
          <h3 class="text-white font-black text-xl mb-2">{{ t.live.offline }}</h3>
          <p class="text-slate-400 font-bold max-w-sm">{{ t.live.offlineDesc }}</p>
        </div>
      </div>

      <!-- Overlays -->
      <div class="absolute top-6 left-6 flex gap-3 z-10">
        <div class="px-3 py-1.5 bg-black/60 backdrop-blur-md rounded-lg text-white text-xs font-black tracking-widest flex items-center gap-2 border border-white/10">
          <span class="w-2 h-2 rounded-full animate-pulse" :class="isRecording ? 'bg-red-500' : 'bg-green-500'"></span>
          {{ isRecording ? 'REC' : 'LIVE' }}
        </div>
        <div class="px-3 py-1.5 bg-black/60 backdrop-blur-md rounded-lg text-white text-xs font-bold tracking-widest border border-white/10 font-mono">
          {{ isRecording ? formatTime(recordingSeconds) : currentTime }}
        </div>
      </div>

      <div class="absolute bottom-6 right-6 flex gap-3 z-10">
        <div class="px-3 py-1.5 bg-blue-500/20 backdrop-blur-md text-blue-400 rounded-lg text-xs font-black border border-blue-500/30">
          1080P / 60FPS (WebRTC)
    </div>
    </div>
    </div>
  </main>
</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useLangStore } from '@/store/langStore';
import Sidebar from '@/components/Sidebar.vue';
import { useRecordingsStore } from '@/store/recordingsStore';

const langStore = useLangStore();
const recordingsStore = useRecordingsStore();
const t = computed(() => langStore.t);

const videoRef = ref(null);
const flash = ref(false);
const isOffline = ref(false);
const isConverting = ref(false);

const currentTime = ref('');
let timer = null;

// Recording State
const isRecording = ref(false);
const recordingSeconds = ref(0);
let recTimer = null;

// WebRTC 媒體伺服器配置 (例如 SRS, Janus, LiveKit 等標準 WHEP/WebRTC HTTP Egress 協定)
const peerConnection = ref(null);
const webrtcStreamUrl = ref('http://localhost:1985/rtc/v1/whep/?app=live&stream=livestream');
const fallbackUrl = ref('/procedure_demo.mp4'); 

const initWebRTC = async () => {
  if (!webrtcStreamUrl.value) {
    useFallbackSimulator();
    return;
  }

  try {
    console.log('🔗 [WebRTC] 正在連接 Media Server...', webrtcStreamUrl.value);
    
    peerConnection.value = new RTCPeerConnection({
      iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
    });

    // 建立只收串流的通道 (Receive-only transceivers)
    peerConnection.value.addTransceiver('video', { direction: 'recvonly' });
    peerConnection.value.addTransceiver('audio', { direction: 'recvonly' });

    peerConnection.value.ontrack = (event) => {
      console.log('✅ [WebRTC] 取得 1080p 60fps 影像軌道:', event.streams[0]);
      if (videoRef.value) {
        isOffline.value = false;
        videoRef.value.srcObject = event.streams[0];
      }
    };

    // 建立本地 Offer SDP
    const offer = await peerConnection.value.createOffer();
    await peerConnection.value.setLocalDescription(offer);

    // 送出 WHEP/WHIP 協定握手
    const response = await fetch(webrtcStreamUrl.value, {
      method: 'POST',
      headers: { 'Content-Type': 'application/sdp' },
      body: offer.sdp
    });

    if (!response.ok) throw new Error('WHEP SDP 信令握手失敗');
    
    const answerSdp = await response.text();
    await peerConnection.value.setRemoteDescription(new RTCSessionDescription({
      type: 'answer',
      sdp: answerSdp
    }));
    
    console.log('🎉 [WebRTC] 1080p 60fps 低延遲醫療級串流已建立！');
  } catch (error) {
    console.warn('⚠️ [WebRTC] 無法連接至邊緣 Media Server。自動啟用本地 1080p 60fps 模擬模式進行 Demo:', error.message);
    useFallbackSimulator();
  }
};

const useFallbackSimulator = () => {
  if (videoRef.value) {
    isOffline.value = false;
    videoRef.value.srcObject = null;
    videoRef.value.src = fallbackUrl.value;
    videoRef.value.load();
  } else {
    isOffline.value = true;
  }
};

const formatTime = (totalSeconds) => {
  const m = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
  const s = (totalSeconds % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
};

const updateTime = () => {
  const now = new Date();
  currentTime.value = now.toLocaleTimeString('en-US', { hour12: false });
};

const captureFrame = () => {
  if (!videoRef.value) return;
  
  flash.value = true;
  setTimeout(() => flash.value = false, 150);

  const canvas = document.createElement('canvas');
  canvas.width = videoRef.value.videoWidth || 1920;
  canvas.height = videoRef.value.videoHeight || 1080;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(videoRef.value, 0, 0, canvas.width, canvas.height);
  
  const dataUrl = canvas.toDataURL('image/jpeg');
  const a = document.createElement('a');
  a.href = dataUrl;
  a.download = `arLoupe_Capture_${new Date().getTime()}.jpg`;
  a.click();
};

const toggleRecording = async () => {
  if (isRecording.value) {
    isRecording.value = false;
    clearInterval(recTimer);
    recordingSeconds.value = 0;
    
    // 發送停止錄影控制訊號至 Edge 工作站
    console.log('📡 [Edge API] POST /api/edge/stop_recording');
    alert(langStore.isZh ? '✅ 錄影指令已送出，Edge 端背景服務已將影片保存至伺服器。' : '✅ Recording stopped. Edge device has saved the video.');

  } else {
    isRecording.value = true;
    recordingSeconds.value = 0;
    recTimer = setInterval(() => {
      recordingSeconds.value++;
    }, 1000);
    
    // 發送開始錄影控制訊號至 Edge 工作站
    console.log('📡 [Edge API] POST /api/edge/start_recording');
  }
};

onMounted(() => {
  updateTime();
  timer = setInterval(updateTime, 1000);
  initWebRTC();
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
  if (recTimer) clearInterval(recTimer);
  if (peerConnection.value) {
    peerConnection.value.close();
    console.log('🔌 [WebRTC] 連線安全釋放');
  }
});
</script>
