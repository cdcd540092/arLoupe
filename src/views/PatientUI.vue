<template>
  <div class="patient-portal flex min-h-screen bg-slate-100 dark:bg-slate-950 font-sans p-6 md:p-12 overflow-y-auto">
    <div class="max-w-6xl mx-auto w-full space-y-12">
      <header class="flex flex-col md:flex-row md:items-end justify-between gap-8 pb-10 border-b border-slate-200 dark:border-slate-800">
        <div>
          <div class="logo flex items-center gap-3 mb-6 overflow-hidden">
            <div class="relative h-10 w-28 flex items-center">
               <img src="@/assets/logo_user.png" alt="arLoupe" class="h-full w-full object-contain transition-all duration-300" :style="themeStore.isDark ? 'mix-blend-mode: screen; filter: invert(1) hue-rotate(180deg) brightness(3);' : 'mix-blend-mode: multiply;'" />
            </div>
            <h1 class="hidden text-3xl font-black text-slate-900 dark:text-white tracking-tighter">MyArloupe <span class="text-blue-600 text-sm align-top tracking-widest uppercase ml-1">Portal</span></h1>
          </div>
          <h2 class="text-5xl font-black text-slate-800 dark:text-slate-100 leading-tight">{{ t.patient.welcomeBack }}<br/><span class="text-blue-500">{{ userStore.user?.name }}</span></h2>
        </div>
        <div class="flex items-center gap-4">
           <button @click="themeStore.toggle()" class="p-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 transition-all">
             <svg v-if="themeStore.isDark" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
             <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
           </button>
           <button @click="langStore.toggle()" class="px-3 py-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 transition-all text-xs font-black text-slate-600 dark:text-slate-300">{{ langStore.isZh ? 'EN' : '中' }}</button>
           <button @click="userStore.logout(); $router.push('/login')" class="text-sm font-black text-slate-400 hover:text-red-500 uppercase tracking-widest transition-colors flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>
              {{ t.logout }}
           </button>
        </div>
      </header>

      <div class="space-y-10">
        <section>
          <h3 class="text-xs font-black text-slate-400 uppercase tracking-[3px] mb-8 flex items-center gap-3">
            <span class="w-10 h-[2px] bg-blue-500"></span>
            {{ t.patient.approvedContent }}
          </h3>
          <div v-show="selectedVideo" class="video-container bg-slate-900 rounded-[2.5rem] overflow-hidden shadow-2xl relative group mb-12">
             <div class="aspect-video bg-black flex items-center justify-center relative group/video">
                <video 
                   ref="patientVideoRef" 
                   :src="selectedVideo?.url" 
                   class="absolute inset-0 w-full h-full object-contain z-10" 
                   controls
                   @pause="isPlaying = false"
                   @play="isPlaying = true"
                ></video>

                <!-- Overlay -->
                <div v-show="!isPlaying" class="absolute inset-0 z-20 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center transition-opacity" @click="playVideo">
                  <div class="z-30 text-center">
                    <button class="w-24 h-24 bg-white/10 hover:bg-white/20 rounded-full border border-white/30 backdrop-blur-xl flex items-center justify-center transition-all hover:scale-110 active:scale-95 mx-auto">
                       <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="white" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="6 3 20 12 6 21 6 3"/></svg>
                    </button>
                    <p class="text-white font-bold mt-4 tracking-widest uppercase text-xs opacity-60">{{ t.patient.readyToPlay }}</p>
                  </div>
                </div>
             </div>
             <div class="p-8 bg-slate-900 border-t border-white/5 flex items-center justify-between">
               <div>
                  <h4 class="text-xl font-black text-white">{{ selectedVideo?.title }}</h4>
                  <p class="text-xs font-bold text-slate-500 uppercase mt-1 tracking-widest">{{ selectedVideo?.date }} • {{ selectedVideo?.type }}</p>
               </div>
               <button @click="downloadFile" class="bg-blue-600 hover:bg-blue-700 text-white font-black py-3 px-6 rounded-2xl shadow-xl shadow-blue-500/30 transition-all flex items-center gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
                  {{ t.patient.saveFile }}
               </button>
             </div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div v-for="v in approvedVideos" :key="v.id" @click="selectedVideoId = v.id" :class="selectedVideoId === v.id ? 'border-blue-500 bg-white dark:bg-slate-800 ring-8 ring-blue-500/5' : 'border-transparent bg-white/50 dark:bg-slate-800/50 hover:bg-white dark:hover:bg-slate-800'" class="p-6 rounded-[2rem] border-2 transition-all cursor-pointer group shadow-sm">
               <div class="w-12 h-12 bg-slate-100 dark:bg-slate-700 rounded-2xl flex items-center justify-center mb-6 border border-slate-200 dark:border-slate-600 group-hover:scale-110 transition-transform">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.834a.5.5 0 0 0-.777-.416L16 11"/><rect width="14" height="12" x="2" y="6" rx="2"/></svg>
               </div>
               <h5 class="text-lg font-black text-slate-800 dark:text-white">{{ v.title }}</h5>
               <p class="text-xs font-bold text-slate-400 mt-1">{{ v.date }}</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useUserStore } from '@/store/userStore';
import { useLangStore } from '@/store/langStore';
import { useThemeStore } from '@/store/themeStore';

const userStore = useUserStore();
const langStore = useLangStore();
const themeStore = useThemeStore();
const t = computed(() => langStore.t);
const selectedVideoId = ref(1);
const patientVideoRef = ref(null);
const isPlaying = ref(false);

const approvedVideos = ref([
  { id: 1, title: 'Dental Scaler Procedure (Full Record)', date: 'April 07, 2026', type: 'Clinical Video', url: '/procedure_demo.mp4' },
  { id: 2, title: 'Final Assessment Clip', date: 'April 07, 2026', type: 'Educational', url: '/procedure_demo.mp4#t=5,15' }
]);

const selectedVideo = computed(() => approvedVideos.value.find(v => v.id === selectedVideoId.value));

const playVideo = () => {
    if (patientVideoRef.value) {
        patientVideoRef.value.play();
        isPlaying.value = true;
    }
};

// Reset video state when switching selection
watch(selectedVideoId, () => {
    isPlaying.value = false;
    if (patientVideoRef.value) {
        patientVideoRef.value.pause();
        patientVideoRef.value.currentTime = 0;
        patientVideoRef.value.load();
    }
});

const downloadFile = () => {
    if (!selectedVideo.value) return;
    
    // Create an invisible anchor element
    const link = document.createElement('a');
    
    // Remove the time fragment (#t=...) from the URL to get the actual file path
    const url = selectedVideo.value.url.split('#')[0];
    
    link.href = url;
    // Format the title into a valid filename
    const filename = selectedVideo.value.title.replace(/[\s\(\)]+/g, '_').toLowerCase();
    link.download = `${filename}.mp4`;
    
    // Append, click, and remove the element
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};
</script>
