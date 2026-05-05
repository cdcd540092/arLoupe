<template>
  <div class="video-player-wrapper space-y-6">
    <div class="bg-slate-100 dark:bg-slate-900 rounded-2xl overflow-hidden shadow-2xl border border-slate-200 dark:border-slate-800 relative group">
      <div ref="containerRef" class="aspect-video relative overflow-hidden bg-black flex items-center justify-center">
        <!-- Real Video Element -->
        <video 
          ref="videoRef"
          :src="recordingsStore.currentRecording?.videoUrl"
          @loadedmetadata="onLoadedMetadata"
          @timeupdate="onTimeUpdate"
          class="absolute inset-0 w-full h-full object-cover z-20"
        ></video>

        <div v-if="!isPlaying" class="absolute inset-0 bg-black/40 z-30 flex items-center justify-center backdrop-blur-[2px]">
          <button @click="togglePlay" class="p-8 bg-blue-600/90 text-white rounded-full hover:scale-110 active:scale-90 transition-all shadow-2xl">
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="6 3 20 12 6 21 6 3"/></svg>
          </button>
        </div>

        <div class="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900"></div>
        <div class="z-10 text-center space-y-6">
          <div class="relative inline-block">
             <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="opacity-40"><path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.834a.5.5 0 0 0-.777-.416L16 11"/><rect width="14" height="12" x="2" y="6" rx="2"/></svg>
             <div class="absolute inset-0 bg-blue-500 blur-3xl opacity-10 -z-10 rounded-full scale-150"></div>
          </div>
          <div>
            <p class="text-white font-black text-lg tracking-tight">{{ recordingsStore.currentRecording?.patientName || t.player.noVideoSelected }}</p>
            <p class="text-slate-500 font-bold tracking-widest uppercase text-[10px] mt-2">{{ recordingsStore.currentRecording?.date || t.player.selectRecording }}</p>
          </div>
        </div>
        
        <div class="absolute bottom-0 inset-x-0 bg-gradient-to-t from-slate-950/90 via-slate-950/40 to-transparent p-6 opacity-0 group-hover:opacity-100 transition-all duration-500 transform translate-y-4 group-hover:translate-y-0 z-40">
          <div class="flex items-center gap-6">
            <button @click="togglePlay" class="p-4 bg-white/10 hover:bg-white/20 rounded-2xl text-white transition-all hover:scale-105 active:scale-95 shadow-xl">
              <svg v-if="!isPlaying" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="6 3 20 12 6 21 6 3"/></svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="4" height="16" x="6" y="4"/><rect width="4" height="16" x="14" y="4"/></svg>
            </button>
            <div class="flex-1 space-y-2">
              <div class="flex justify-between text-xs text-slate-300 font-bold uppercase tracking-wider">
                <span>{{ formatTime(currentTime) }}</span>
                <span>{{ formatTime(duration) }}</span>
              </div>
              <div class="h-1.5 bg-white/10 rounded-full overflow-hidden relative cursor-pointer" @click="seekTo($event)">
                <div class="absolute left-0 top-0 bottom-0 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all" :style="{ width: progressPercent + '%' }"></div>
              </div>
            </div>
            <button @click="cycleSpeed" class="px-3 py-1.5 bg-white/10 hover:bg-white/20 rounded-xl text-white text-xs font-black transition-all">{{ playbackSpeed }}x</button>
            <button @click="toggleFullscreen" class="p-2 text-slate-300 hover:text-white transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M21 8V5a2 2 0 0 0-2-2h-3"/><path d="M3 16v3a2 2 0 0 0 2 2h3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/></svg>
            </button>
          </div>
        </div>
      </div>
      
      <div class="p-4 bg-white dark:bg-slate-800 border-t border-slate-200 dark:border-slate-700 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10 text-blue-500 border border-blue-500/20">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.834a.5.5 0 0 0-.777-.416L16 11"/><rect width="14" height="12" x="2" y="6" rx="2"/></svg>
          </div>
          <div>
            <h3 class="font-bold text-slate-800 dark:text-slate-100 text-[15px]">{{ recordingsStore.currentRecording?.patientName || 'Dental Procedure Recording' }}</h3>
            <p class="text-[11px] font-bold text-slate-400 tracking-wider">{{ t.player.recorded }}: {{ recordingsStore.currentRecording?.date || '—' }} • {{ t.player.duration }}: {{ formatTime(duration) }}</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <div class="px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 flex items-center gap-2">
            <div class="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
            <span class="text-[12px] font-bold tracking-tighter">HD 1080P</span>
          </div>
          <button @click="showShareModal = !showShareModal" class="relative px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl transition-all active:scale-95 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/></svg>
            {{ t.player.share }}
          </button>
        </div>
      </div>

      <!-- Share Modal -->
      <div v-if="showShareModal" class="absolute right-4 bottom-20 z-50 bg-white dark:bg-slate-800 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-700 p-6 w-80 animate-fade-in">
        <h4 class="font-black text-sm text-slate-800 dark:text-white mb-4 flex items-center justify-between">
          {{ t.player.shareTitle }}
          <button @click="showShareModal = false" class="text-slate-400 hover:text-slate-600">✕</button>
        </h4>
        <div class="space-y-3">
          <button @click="copyLink" class="w-full flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-900 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700 transition-all text-left">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="2" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
            <div>
              <p class="font-bold text-xs text-slate-800 dark:text-white">{{ linkCopied ? t.player.linkCopied : t.player.copyLink }}</p>
              <p class="text-[10px] text-slate-400">{{ t.player.copyLinkDesc }}</p>
            </div>
          </button>
          <button class="w-full flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-900 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700 transition-all text-left">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" x2="19" y1="8" y2="14"/><line x1="22" x2="16" y1="11" y2="11"/></svg>
            <div>
              <p class="font-bold text-xs text-slate-800 dark:text-white">{{ t.player.sendToStaff }}</p>
              <p class="text-[10px] text-slate-400">{{ t.player.sendToStaffDesc }}</p>
            </div>
          </button>
          <button class="w-full flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-900 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700 transition-all text-left">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
            <div>
              <p class="font-bold text-xs text-slate-800 dark:text-white">{{ t.player.generatePatientLink }}</p>
              <p class="text-[10px] text-slate-400">{{ t.player.generatePatientLinkDesc }}</p>
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- Clip Editor -->
    <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-6 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-indigo-500/10 text-indigo-500 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="3"/><path d="M8.12 8.12 12 12"/><path d="M20 4 8.12 15.88"/><circle cx="6" cy="18" r="3"/><path d="M14.8 14.8 20 20"/></svg>
          </div>
          <div>
            <h3 class="font-bold text-sm text-slate-800 dark:text-white">{{ t.player.clipEditor }}</h3>
            <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">{{ t.player.clipEditorDesc }}</p>
          </div>
        </div>
        <button @click="showClipEditor = !showClipEditor" class="text-xs font-black text-blue-500 hover:underline uppercase tracking-widest">{{ showClipEditor ? t.player.collapse : t.player.expand }}</button>
      </div>
      
      <div v-show="showClipEditor" class="p-6 space-y-6">
        <div class="grid grid-cols-2 gap-6">
          <div>
            <label class="text-[10px] font-black text-slate-500 uppercase block mb-2 tracking-widest">{{ t.player.startTime }}</label>
            <div class="flex gap-2">
              <input v-model="clipStart" type="text" placeholder="00:00:00" class="flex-1 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-mono font-bold focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
              <button @click="clipStart = formatTime(currentTime)" class="px-3 bg-slate-100 dark:bg-slate-700 rounded-xl text-xs font-bold text-slate-500 hover:text-blue-500 transition-colors border border-slate-200 dark:border-slate-600">NOW</button>
            </div>
          </div>
          <div>
            <label class="text-[10px] font-black text-slate-500 uppercase block mb-2 tracking-widest">{{ t.player.endTime }}</label>
            <div class="flex gap-2">
              <input v-model="clipEnd" type="text" placeholder="00:00:00" class="flex-1 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-mono font-bold focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
              <button @click="clipEnd = formatTime(duration)" class="px-3 bg-slate-100 dark:bg-slate-700 rounded-xl text-xs font-bold text-slate-500 hover:text-blue-500 transition-colors border border-slate-200 dark:border-slate-600">END</button>
            </div>
          </div>
        </div>
        <div class="relative h-12 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
          <div class="absolute inset-y-0 bg-blue-500/20 border-x-2 border-blue-500 rounded transition-all duration-300" :style="{ left: clipStartPercent + '%', width: clipWidthPercent + '%' }"></div>
          <div class="absolute top-1/2 -translate-y-1/2 w-3 h-8 bg-blue-600 rounded-full cursor-ew-resize shadow-lg transition-all duration-300" style="transform: translate(-50%, -50%);" :style="{ left: clipStartPercent + '%' }"></div>
          <div class="absolute top-1/2 -translate-y-1/2 w-3 h-8 bg-blue-600 rounded-full cursor-ew-resize shadow-lg transition-all duration-300" style="transform: translate(-50%, -50%);" :style="{ left: (clipStartPercent + clipWidthPercent) + '%' }"></div>
        </div>
        <div class="flex gap-4">
          <button @click="createClip" class="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-black py-3 rounded-xl shadow-lg shadow-indigo-500/20 transition-all active:scale-[0.98] flex items-center justify-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="3"/><path d="M8.12 8.12 12 12"/><path d="M20 4 8.12 15.88"/><circle cx="6" cy="18" r="3"/><path d="M14.8 14.8 20 20"/></svg>
            {{ t.player.createClip }}
          </button>
          <button @click="previewClip(clipStart, clipEnd)" class="px-6 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 font-bold rounded-xl transition-all text-sm flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" :class="isPreviewing ? 'text-blue-500 animate-pulse' : ''"><polygon points="6 3 20 12 6 21 6 3"/></svg>
            {{ t.player.preview }}
          </button>
        </div>
        <div v-if="savedClips.length > 0">
          <h4 class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">{{ t.player.savedClips }} ({{ savedClips.length }})</h4>
          <div class="space-y-2">
            <div v-for="clip in savedClips" :key="clip.id" class="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-700 group hover:border-indigo-500/30 transition-all cursor-pointer" @click="previewClip(clip.start, clip.end)">
              <div class="flex items-center gap-3">
                <div class="p-2 bg-indigo-500/10 text-indigo-500 rounded-lg group-hover:bg-indigo-500 group-hover:text-white transition-all">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="6 3 20 12 6 21 6 3"/></svg>
                </div>
                <div>
                  <p class="font-bold text-xs text-slate-800 dark:text-white group-hover:text-indigo-500 transition-colors">{{ clip.name }}</p>
                  <p class="text-[10px] text-slate-400 font-mono">{{ clip.start }} → {{ clip.end }}</p>
                </div>
              </div>
              <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-all">
                <button @click.stop class="px-3 py-1.5 bg-blue-600 text-white text-[10px] font-black rounded-lg hover:bg-blue-700">{{ t.player.share }}</button>
                <button @click.stop="deleteClip(clip.id)" class="px-3 py-1.5 bg-red-500/10 text-red-500 text-[10px] font-black rounded-lg hover:bg-red-500/20">{{ t.player.deleteClip }}</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useLangStore } from '@/store/langStore';
import { useRecordingsStore } from '@/store/recordingsStore';

const langStore = useLangStore();
const recordingsStore = useRecordingsStore();
const t = computed(() => langStore.t);

const videoRef = ref(null);
const containerRef = ref(null);
const isPlaying = ref(false);
const isPreviewing = ref(false); // 儲存預覽結束的秒數，若為false代表一般播放
const currentTime = ref(0);
const duration = ref(0);
const playbackSpeed = ref(1);
const showShareModal = ref(false);
const linkCopied = ref(false);
const showClipEditor = ref(true);
const clipStart = ref('00:00:00');
const clipEnd = ref('00:00:00');
const savedClips = ref([]);
let clipCounter = 1;

const parseTimeToSeconds = (timeStr) => {
  if (!timeStr) return 0;
  const parts = String(timeStr).split(':').map(Number);
  if (parts.length === 3) return parts[0]*3600 + parts[1]*60 + parts[2];
  return 0;
};

const clipStartPercent = computed(() => {
  if (duration.value <= 0) return 0;
  return (parseTimeToSeconds(clipStart.value) / duration.value) * 100;
});

const clipWidthPercent = computed(() => {
  if (duration.value <= 0) return 0;
  const width = (parseTimeToSeconds(clipEnd.value) - parseTimeToSeconds(clipStart.value)) / duration.value * 100;
  return Math.max(0, width);
});

// 監聽病患切換
watch(() => recordingsStore.selectedId, () => {
  isPlaying.value = false;
  isPreviewing.value = false;
  if (videoRef.value) {
    videoRef.value.load();
  }
  // 切換病患時重置剪輯區
  savedClips.value = [];
  clipStart.value = '00:00:00';
  clipEnd.value = '00:00:00';
});

const onLoadedMetadata = () => {
  if (videoRef.value) {
    duration.value = videoRef.value.duration;
    clipEnd.value = formatTime(duration.value);
  }
};

const onTimeUpdate = () => {
  if (videoRef.value) {
    currentTime.value = videoRef.value.currentTime;
    
    // 如果正在預覽模式，且已經播到結束時間，則自動暫停
    if (isPreviewing.value !== false && currentTime.value >= isPreviewing.value) {
      videoRef.value.pause();
      isPlaying.value = false;
      isPreviewing.value = false; // 退出預覽模式
    }
  }
};

const progressPercent = computed(() => duration.value > 0 ? (currentTime.value / duration.value) * 100 : 0);

const formatTime = (seconds) => {
  if (!seconds || isNaN(seconds)) return '00:00:00';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
};

const togglePlay = () => {
  if (!videoRef.value) return;
  if (isPlaying.value) {
    videoRef.value.pause();
  } else {
    videoRef.value.play();
    isPreviewing.value = false; // 如果手動播放，取消自動暫停預覽機制
  }
  isPlaying.value = !isPlaying.value;
};

const cycleSpeed = () => {
  const speeds = [0.5, 1, 1.5, 2];
  const next = speeds[(speeds.indexOf(playbackSpeed.value) + 1) % speeds.length];
  playbackSpeed.value = next;
  if (videoRef.value) videoRef.value.playbackRate = next;
};

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    if (containerRef.value?.requestFullscreen) {
      containerRef.value.requestFullscreen();
    } else if (videoRef.value?.webkitEnterFullscreen) {
      videoRef.value.webkitEnterFullscreen(); // iOS Safari fallback
    }
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    }
  }
};

const seekTo = (e) => {
  const r = e.currentTarget.getBoundingClientRect();
  const time = ((e.clientX - r.left) / r.width) * duration.value;
  if (videoRef.value) {
    videoRef.value.currentTime = time;
  }
};

const previewClip = (startStr, endStr) => {
  if (!videoRef.value) return;
  const startSec = parseTimeToSeconds(startStr);
  const endSec = parseTimeToSeconds(endStr);
  
  if (startSec >= endSec) return;

  videoRef.value.currentTime = startSec;
  videoRef.value.play();
  isPlaying.value = true;
  isPreviewing.value = endSec; // 標記為預覽模式，結束時間為 endSec
};

const copyLink = () => { linkCopied.value = true; setTimeout(() => { linkCopied.value = false; }, 2000); };
const createClip = () => { 
  if (parseTimeToSeconds(clipStart.value) >= parseTimeToSeconds(clipEnd.value)) return;
  savedClips.value.push({ id: clipCounter++, name: `Clip ${clipCounter - 1} — Custom Segment`, start: clipStart.value, end: clipEnd.value }); 
};
const deleteClip = (id) => { savedClips.value = savedClips.value.filter(c => c.id !== id); };
</script>
