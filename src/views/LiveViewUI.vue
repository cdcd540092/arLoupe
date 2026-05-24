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
          <button 
            @click="captureFrame" 
            :disabled="isOffline"
            :class="isOffline ? 'opacity-40 cursor-not-allowed border-slate-200 dark:border-slate-800' : 'hover:bg-slate-50 dark:hover:bg-slate-700'"
            class="px-5 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl font-bold text-sm transition-all flex items-center gap-2 shadow-sm active:scale-95"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/></svg>
            {{ t.live.captureFrame }}
          </button>
          <button 
            @click="toggleRecording" 
            :disabled="isConverting || isOffline"
            :class="isOffline ? 'bg-slate-200 dark:bg-slate-800 text-slate-400 dark:text-slate-600 shadow-none cursor-not-allowed opacity-50' : isConverting ? 'bg-amber-500 text-white shadow-amber-500/30' : isRecording ? 'bg-slate-800 hover:bg-slate-900 text-white shadow-slate-900/30' : 'bg-red-500 hover:bg-red-600 text-white shadow-red-500/30'"
            class="px-5 py-2.5 rounded-xl font-bold text-sm transition-all shadow-lg flex items-center gap-2 active:scale-95 min-w-[180px] justify-center"
          >
            <template v-if="isConverting">
              <div class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              {{ langStore.isZh ? '轉檔中...' : 'Converting...' }}
            </template>
            <template v-else>
              <div v-if="!isRecording" class="w-2.5 h-2.5 bg-white rounded-full" :class="isOffline ? 'bg-slate-400 dark:bg-slate-600' : 'bg-white'"></div>
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
          <button @click="showTroubleshoot = true" class="mt-4 text-blue-400 hover:text-blue-300 font-bold text-sm underline transition-all flex items-center gap-1 active:scale-95">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
            {{ langStore.isZh ? '排除連線問題步驟' : 'Troubleshooting Steps' }}
          </button>
        </div>
      </div>

      <!-- Overlays -->
      <div class="absolute top-6 left-6 flex gap-3 z-10">
        <div class="px-3 py-1.5 bg-black/60 backdrop-blur-md rounded-lg text-white text-xs font-black tracking-widest flex items-center gap-2 border border-white/10">
          <span class="w-2 h-2 rounded-full" :class="isOffline ? 'bg-slate-500' : isRecording ? 'bg-red-500 animate-pulse' : 'bg-green-500 animate-pulse'"></span>
          {{ isOffline ? 'OFFLINE' : isRecording ? 'REC' : 'LIVE' }}
        </div>
        <div class="px-3 py-1.5 bg-black/60 backdrop-blur-md rounded-lg text-white text-xs font-bold tracking-widest border border-white/10 font-mono">
          {{ isOffline ? '--:--:--' : isRecording ? formatTime(recordingSeconds) : currentTime }}
        </div>
      </div>

      <div class="absolute bottom-6 right-6 flex gap-3 z-10">
        <div class="px-3 py-1.5 bg-blue-500/20 backdrop-blur-md text-blue-400 rounded-lg text-xs font-black border border-blue-500/30">
          1080P / 60FPS (WebRTC)
    </div>
    </div>
    </div>

    <!-- Troubleshooting Modal -->
    <div v-if="showTroubleshoot" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm transition-all duration-300">
      <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 md:p-8 max-w-lg w-full shadow-2xl relative animate-in fade-in zoom-in duration-200">
        <!-- Close Button -->
        <button @click="showTroubleshoot = false" class="absolute top-6 right-6 text-slate-400 hover:text-white transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>

        <!-- Header -->
        <div class="flex items-center gap-3 mb-6">
          <div class="p-2.5 bg-blue-500/10 text-blue-400 rounded-2xl">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
          </div>
          <div>
            <h3 class="text-white font-black text-xl">{{ langStore.isZh ? 'arLoupe 連線問題排除步驟' : 'arLoupe Troubleshooting' }}</h3>
            <p class="text-xs text-slate-500 font-bold uppercase tracking-widest mt-0.5">Connection Diagnostics</p>
          </div>
        </div>

        <!-- Content Steps -->
        <div class="space-y-4 text-slate-300 text-sm mb-6">
          <div class="flex gap-3 items-start">
            <span class="w-6 h-6 rounded-full bg-blue-500/10 text-blue-400 font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">1</span>
            <div>
              <h4 class="text-white font-bold mb-0.5">{{ langStore.isZh ? '檢查 arLoupe 眼鏡電源' : 'Check arLoupe Power' }}</h4>
              <p class="text-slate-400 text-xs">{{ langStore.isZh ? '請確認鏡腳右側開關已開啟，且 LED 指示燈呈現藍色恆亮或綠色呼吸燈狀態。' : 'Verify the right arm power switch is ON and the LED light is glowing blue/green.' }}</p>
            </div>
          </div>

          <div class="flex gap-3 items-start">
            <span class="w-6 h-6 rounded-full bg-blue-500/10 text-blue-400 font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">2</span>
            <div>
              <h4 class="text-white font-bold mb-0.5">{{ langStore.isZh ? '檢查區域 Wi-Fi 網路連線' : 'Verify Local Wi-Fi Connection' }}</h4>
              <p class="text-slate-400 text-xs">{{ langStore.isZh ? '眼鏡設備需與此台筆電連線至同一個 Wi-Fi 網域（例如 arLoupe-Local-Net）。' : 'Ensure both the glasses and this laptop are connected to the same local Wi-Fi network.' }}</p>
            </div>
          </div>

          <div class="flex gap-3 items-start">
            <span class="w-6 h-6 rounded-full bg-blue-500/10 text-blue-400 font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">3</span>
            <div>
              <h4 class="text-white font-bold mb-0.5">{{ langStore.isZh ? '確認 MediaMTX 伺服器已啟動' : 'Check MediaMTX Server Status' }}</h4>
              <p class="text-slate-400 text-xs">{{ langStore.isZh ? '請在筆電執行資料夾內的 mediamtx.exe，並確認黑框畫面中顯示 "published" 串流已就緒。' : 'Launch mediamtx.exe on the laptop and verify the terminal displays the stream is "published".' }}</p>
            </div>
          </div>

          <div class="flex gap-3 items-start">
            <span class="w-6 h-6 rounded-full bg-blue-500/10 text-blue-400 font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">4</span>
            <div>
              <h4 class="text-white font-bold mb-0.5">{{ langStore.isZh ? '排解 CORS 跨網域阻擋' : 'Troubleshoot CORS Policy Block' }}</h4>
              <p class="text-slate-400 text-xs">{{ langStore.isZh ? '若瀏覽器 Console 顯示 CORS 阻擋，請開啟 mediamtx.yml 將 "webrtcAllowOrigin" 修改為 "*" 後重啟服務。' : 'If F12 displays CORS blocks, update "webrtcAllowOrigin: \'*\'" inside mediamtx.yml and restart.' }}</p>
            </div>
          </div>
        </div>

        <!-- Footer Action -->
        <div class="flex gap-3 justify-end">
          <button @click="showTroubleshoot = false" class="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold text-xs transition-colors shadow-lg shadow-blue-500/20 active:scale-95">
            {{ langStore.isZh ? '我已瞭解，關閉視窗' : 'Understood, Close' }}
          </button>
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
const showTroubleshoot = ref(false);

const currentTime = ref('');
let timer = null;

// Recording State
const isRecording = ref(false);
const recordingSeconds = ref(0);
let recTimer = null;

// WebRTC 媒體伺服器配置 (使用 MediaMTX 提供的標準 WHEP 端點)
const peerConnection = ref(null);
const webrtcStreamUrl = ref('http://localhost:8889/arloupe/whep');

const initWebRTC = async () => {
  if (!webrtcStreamUrl.value) {
    setDeviceOffline();
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
    console.warn('⚠️ [WebRTC] 串流中斷或 Media Server 未啟動。顯示離線狀態:', error.message);
    setDeviceOffline();
  }
};

const setDeviceOffline = () => {
  isOffline.value = true;
  if (videoRef.value) {
    videoRef.value.srcObject = null;
    videoRef.value.src = '';
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

const PI5_API_BASE_URL = 'http://192.168.1.150:7000';

const toggleRecording = async () => {
  if (isRecording.value) {
    try {
      console.log(`📡 [Pi 5 API] 停止錄影: POST ${PI5_API_BASE_URL}/api/capture/stop`);
      const res = await fetch(`${PI5_API_BASE_URL}/api/capture/stop`, { method: "POST" });
      if (!res.ok) throw new Error('API Error: ' + await res.text());
      
      isRecording.value = false;
      clearInterval(recTimer);
      recordingSeconds.value = 0;
      
      alert(langStore.isZh ? '✅ 錄影指令已送出，設備即將進行影片上傳。' : '✅ Recording stopped. Device is uploading the video.');
    } catch (err) {
      console.error('停止錄影失敗', err);
      alert('停止錄影失敗：' + err.message);
    }
  } else {
    try {
      const caseId = recordingsStore.currentRecording?.patientName || 'demo_case_001';
      console.log(`📡 [Pi 5 API] 開始錄影: POST ${PI5_API_BASE_URL}/api/capture/start (case: ${caseId})`);
      
      const res = await fetch(`${PI5_API_BASE_URL}/api/capture/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          case_id: caseId.replace(/\s+/g, '_'),
          operator_id: "arLoupe_Admin"
        }),
      });
      if (!res.ok) throw new Error('API Error: ' + await res.text());
      
      isRecording.value = true;
      recordingSeconds.value = 0;
      recTimer = setInterval(() => {
        recordingSeconds.value++;
      }, 1000);
      
    } catch (err) {
      console.error('開始錄影失敗', err);
      alert('開始錄影失敗，請確認 Pi 5 設備連線狀態：\n' + err.message);
    }
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
