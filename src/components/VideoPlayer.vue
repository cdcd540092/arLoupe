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

        <!-- X-Ray / Apical Overlay -->
        <div v-if="overlayMode !== 'off'" class="absolute top-4 right-4 z-50 w-1/3 max-w-[300px] bg-black/80 p-1.5 rounded-xl shadow-2xl border border-white/20 backdrop-blur-md transition-all hover:scale-150 origin-top-right cursor-crosshair">
           <img v-if="overlayMode === 'xray'" :src="xrayImg" alt="X-Ray" class="w-full h-auto rounded-lg object-contain" />
           <img v-else-if="overlayMode === 'apical'" :src="apicalImg" alt="Apical" class="w-full h-auto rounded-lg object-contain" />
           <div class="absolute bottom-3 left-3 bg-black/60 px-2 py-1 rounded text-[10px] text-white font-bold tracking-widest backdrop-blur-md border border-white/10">
             {{ overlayMode === 'xray' ? '全口 X 光片' : '根尖片' }}
           </div>
        </div>

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
      
      <div class="p-4 bg-white dark:bg-slate-800 border-t border-slate-200 dark:border-slate-700 flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-4">
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-500/10 text-blue-500 border border-blue-500/20 shadow-inner">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.834a.5.5 0 0 0-.777-.416L16 11"/><rect width="14" height="12" x="2" y="6" rx="2"/></svg>
          </div>
          <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-5">
            <div>
              <h3 class="font-black text-slate-800 dark:text-slate-100 text-[16px] tracking-tight">{{ recordingsStore.currentRecording?.patientName || 'Dental Procedure Recording' }}</h3>
              <p class="text-[11px] font-bold text-slate-400 tracking-wider mt-0.5">{{ t.player.recorded }}: {{ recordingsStore.currentRecording?.date || '—' }} • {{ t.player.duration }}: {{ formatTime(duration) }}</p>
            </div>
            
            <div class="flex bg-slate-100 dark:bg-slate-900/50 p-1 rounded-lg border border-slate-200 dark:border-slate-700 shadow-inner h-fit">
              <button @click="overlayMode = 'off'" :class="overlayMode === 'off' ? 'bg-white dark:bg-slate-800 shadow text-slate-800 dark:text-white' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'" class="px-4 py-1.5 text-[11px] font-black rounded-md transition-all uppercase tracking-widest">關閉</button>
              <button @click="overlayMode = 'xray'" :class="overlayMode === 'xray' ? 'bg-blue-600 shadow-md shadow-blue-600/30 text-white' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'" class="px-4 py-1.5 text-[11px] font-black rounded-md transition-all uppercase tracking-widest flex items-center gap-1.5">
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>
                X光片
              </button>
              <button @click="overlayMode = 'apical'" :class="overlayMode === 'apical' ? 'bg-indigo-600 shadow-md shadow-indigo-600/30 text-white' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'" class="px-4 py-1.5 text-[11px] font-black rounded-md transition-all uppercase tracking-widest flex items-center gap-1.5">
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/></svg>
                根尖片
              </button>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <div class="px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 flex items-center gap-2">
            <div class="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
            <span class="text-[12px] font-bold tracking-tighter">HD 1080P</span>
          </div>
          <button @click="downloadCurrentVideo" class="relative px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs rounded-xl transition-all active:scale-95 flex items-center gap-2 shadow-lg shadow-indigo-500/30">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
            {{ t.player.downloadVideo }}
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
              <button @click="clipEnd = formatTime(currentTime)" class="px-3 bg-slate-100 dark:bg-slate-700 rounded-xl text-xs font-bold text-slate-500 hover:text-blue-500 transition-colors border border-slate-200 dark:border-slate-600">NOW</button>
            </div>
          </div>
        </div>
        <div ref="timelineRef" class="relative h-12 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden select-none">
          <div class="absolute inset-y-0 bg-blue-500/20 border-x-2 border-blue-500 rounded" :style="{ left: clipStartPercent + '%', width: clipWidthPercent + '%' }"></div>
          <div @mousedown="startDrag('start', $event)" class="absolute top-1/2 -translate-y-1/2 w-3 h-8 bg-blue-600 rounded-full cursor-ew-resize shadow-lg z-10" style="transform: translate(-50%, -50%);" :style="{ left: clipStartPercent + '%' }"></div>
          <div @mousedown="startDrag('end', $event)" class="absolute top-1/2 -translate-y-1/2 w-3 h-8 bg-blue-600 rounded-full cursor-ew-resize shadow-lg z-10" style="transform: translate(-50%, -50%);" :style="{ left: (clipStartPercent + clipWidthPercent) + '%' }"></div>
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
                <button @click.stop="exportClip(clip)" :disabled="isExporting" class="px-3 py-1.5 bg-emerald-600 text-white text-[10px] font-black rounded-lg hover:bg-emerald-700 disabled:opacity-50 flex items-center gap-1 min-w-[80px] justify-center">
                   <svg v-if="isExporting" class="animate-spin h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                   {{ isExporting ? (exportStatus || (Math.round(exportProgress) + '%')) : t.player.exportMp4 }}
                </button>
                <button @click.stop="triggerSaveToCloud(clip)" :disabled="clip.isSaved || clip.isSaving || isExporting" class="px-3 py-1.5 bg-blue-600 text-white text-[10px] font-black rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:bg-blue-800 transition-all flex items-center gap-1 justify-center min-w-[80px]">
                   <svg v-if="clip.isSaving" class="animate-spin h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                   <svg v-else-if="clip.isSaved" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                   {{ clip.isSaving ? (exportStatus || t.player.processing) : clip.isSaved ? t.player.saved : t.player.saveToCloud }}
                </button>
                <button @click.stop="deleteClip(clip.id)" class="px-3 py-1.5 bg-red-500/10 text-red-500 text-[10px] font-black rounded-lg hover:bg-red-500/20">{{ t.player.deleteClip }}</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Rename Modal -->
    <div v-if="showRenameModal" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in">
      <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-700 p-6 w-96 transform transition-all scale-100">
        <h4 class="font-black text-lg text-slate-800 dark:text-white mb-2">{{ t.player.renameClip }}</h4>
        <p class="text-xs text-slate-500 mb-4">{{ t.player.renameDesc }}</p>
        <input v-model="renameInput" type="text" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-6 text-slate-800 dark:text-white" :placeholder="t.player.enterClipName" @keyup.enter="confirmSaveToCloud" autofocus />
        <div class="flex justify-end gap-3">
          <button @click="showRenameModal = false" class="px-4 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-300 rounded-xl text-sm font-bold transition-all">{{ t.player.cancel }}</button>
          <button @click="confirmSaveToCloud" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-bold transition-all shadow-lg shadow-blue-500/30">{{ t.player.confirmSave }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { FFmpeg } from '@ffmpeg/ffmpeg';
import { fetchFile, toBlobURL } from '@ffmpeg/util';
import { useLangStore } from '@/store/langStore';
import { useRecordingsStore } from '@/store/recordingsStore';
import xrayImg from '@/assets/xray.jpg';
import apicalImg from '@/assets/apical.jpg';

const langStore = useLangStore();
const recordingsStore = useRecordingsStore();
const t = computed(() => langStore.t);

const videoRef = ref(null);
const containerRef = ref(null);
const timelineRef = ref(null);
const isPlaying = ref(false);
const isPreviewing = ref(false); // 儲存預覽結束的秒數，若為false代表一般播放
const currentTime = ref(0);
const duration = ref(0);
const playbackSpeed = ref(1);
const showClipEditor = ref(true);
const overlayMode = ref('off');
const clipStart = ref('00:00:00');
const clipEnd = ref('00:00:00');
const savedClips = ref([]);
let clipCounter = 1;

const ffmpeg = new FFmpeg();
const isFFmpegLoaded = ref(false);
const isExporting = ref(false);
const exportProgress = ref(0);
const exportStatus = ref('');

const showRenameModal = ref(false);
const renameInput = ref('');
const clipToSave = ref(null);

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

const downloadCurrentVideo = () => {
    const currentRec = recordingsStore.currentRecording;
    if (!currentRec || !currentRec.videoUrl) return;
    
    const url = currentRec.videoUrl;
    // 如果是 blob 網址或是真實網址，過濾掉 #t= 時間戳記再下載
    const cleanUrl = url.startsWith('blob:') ? url : url.split('#')[0];
    
    const a = document.createElement('a');
    a.href = cleanUrl;
    
    // 設定合適的檔名
    const safeName = (currentRec.patientName || 'Patient').replace(/[\s\(\)]+/g, '_').replace(/_+$/, '');
    const safeType = (currentRec.type || 'Video').replace(/\s+/g, '_');
    a.download = `arLoupe_${safeName}_${safeType}.mp4`;
    
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
};

const seekTo = (e) => {
  const r = e.currentTarget.getBoundingClientRect();
  const time = ((e.clientX - r.left) / r.width) * duration.value;
  if (videoRef.value) {
    videoRef.value.currentTime = time;
  }
};

let activeDrag = null;

const startDrag = (type, e) => {
    activeDrag = type;
    e.preventDefault();
    window.addEventListener('mousemove', onDrag);
    window.addEventListener('mouseup', stopDrag);
};

const onDrag = (e) => {
    if (!activeDrag || !timelineRef.value || duration.value <= 0) return;
    
    const rect = timelineRef.value.getBoundingClientRect();
    let x = e.clientX - rect.left;
    x = Math.max(0, Math.min(x, rect.width));
    
    let time = (x / rect.width) * duration.value;
    
    if (activeDrag === 'start') {
        const endTime = parseTimeToSeconds(clipEnd.value);
        if (time > endTime) time = endTime;
        clipStart.value = formatTime(time);
    } else {
        const startTime = parseTimeToSeconds(clipStart.value);
        if (time < startTime) time = startTime;
        clipEnd.value = formatTime(time);
    }
};

const stopDrag = () => {
    activeDrag = null;
    window.removeEventListener('mousemove', onDrag);
    window.removeEventListener('mouseup', stopDrag);
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

const createClip = () => { 
  const sSec = parseTimeToSeconds(clipStart.value);
  const eSec = parseTimeToSeconds(clipEnd.value);
  if (sSec >= eSec) return;
  savedClips.value.push({ 
      id: clipCounter++, 
      name: `Clip ${clipCounter - 1} — Custom Segment`, 
      start: clipStart.value, 
      end: clipEnd.value,
      startSec: sSec,
      endSec: eSec,
      isSaving: false,
      isSaved: false
  }); 
};
const deleteClip = (id) => { savedClips.value = savedClips.value.filter(c => c.id !== id); };

const triggerSaveToCloud = (clip) => {
    if (clip.isSaved || clip.isSaving) return;
    clipToSave.value = clip;
    renameInput.value = clip.name;
    showRenameModal.value = true;
};

const confirmSaveToCloud = async () => {
    if (!clipToSave.value || !renameInput.value.trim()) return;
    
    if (typeof SharedArrayBuffer === 'undefined') {
        alert('瀏覽器不支援實體剪輯，請確保在 localhost 執行！');
        return;
    }

    const clip = clipToSave.value;
    clip.name = renameInput.value.trim();
    showRenameModal.value = false;
    
    clip.isSaving = true;
    isExporting.value = true;
    exportProgress.value = 0;
    
    try {
        const physicalUrl = await processPhysicalClip(clip);
        clip.physicalBlobUrl = physicalUrl;
        
        exportStatus.value = '上傳伺服器...';
        await recordingsStore.saveClipToDatabase(clip);
        clip.isSaved = true;
    } catch (err) {
        console.error(err);
        alert('儲存至資料庫失敗：' + (err.message || err));
    } finally {
        clip.isSaving = false;
        isExporting.value = false;
        exportStatus.value = '';
        clipToSave.value = null;
    }
};

const loadFFmpeg = async () => {
    if (isFFmpegLoaded.value) return;
    
    ffmpeg.on('progress', ({ progress }) => {
        exportProgress.value = Math.min(progress * 100, 100);
        if (progress > 0 && progress < 1) exportStatus.value = '處理中...';
    });
    
    ffmpeg.on('log', ({ message }) => {
        console.log('[FFMPEG]', message);
    });
    
    const baseURL = 'https://unpkg.com/@ffmpeg/core@0.12.6/dist/esm';
    
    try {
        await ffmpeg.load({
            coreURL: await toBlobURL(`${baseURL}/ffmpeg-core.js`, 'text/javascript'),
            wasmURL: await toBlobURL(`${baseURL}/ffmpeg-core.wasm`, 'application/wasm'),
        });
    } catch (e) {
        console.warn('載入核心失敗，嘗試自動後備載入', e);
        await ffmpeg.load();
    }
    isFFmpegLoaded.value = true;
};

const processPhysicalClip = async (clip) => {
    exportStatus.value = '載入核心...';
    await loadFFmpeg();
    
    const videoUrl = recordingsStore.currentRecording?.videoUrl;
    if (!videoUrl) throw new Error("No video selected");
    
    exportStatus.value = '讀取影片...';
    const fileData = await fetchFile(videoUrl);
    
    exportStatus.value = '寫入暫存...';
    await ffmpeg.writeFile('input.mp4', fileData);
    
    exportStatus.value = '剪輯中...';
    
    const startSec = parseTimeToSeconds(clip.start);
    const endSec = parseTimeToSeconds(clip.end);
    const durationSec = endSec - startSec;
    
    // Execute FFmpeg to cut the video (-c copy to avoid re-encoding)
    await ffmpeg.exec([
        '-ss', String(startSec),
        '-i', 'input.mp4',
        '-t', String(durationSec),
        '-c', 'copy',
        'output.mp4'
    ]);
    
    // Read back the cut video
    exportStatus.value = '產出實體檔...';
    const data = await ffmpeg.readFile('output.mp4');
    
    const blob = new Blob([data.buffer], { type: 'video/mp4' });
    return URL.createObjectURL(blob);
};

const exportClip = async (clip) => {
    try {
        if (typeof SharedArrayBuffer === 'undefined') {
            throw new Error('瀏覽器不支援 SharedArrayBuffer。請使用 localhost 或確保伺服器已設定 COOP/COEP Headers。');
        }
        
        isExporting.value = true;
        exportProgress.value = 0;
        
        const url = await processPhysicalClip(clip);
        
        // Download logic
        const a = document.createElement('a');
        a.href = url;
        a.download = `${clip.name.replace(/\s+/g, '_')}.mp4`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        // Timeout to ensure download starts before revoking
        setTimeout(() => URL.revokeObjectURL(url), 5000);
    } catch (err) {
        console.error('Export failed:', err);
        alert('影片匯出失敗：' + (err.message || err));
    } finally {
        isExporting.value = false;
        exportProgress.value = 0;
        exportStatus.value = '';
    }
};
</script>
