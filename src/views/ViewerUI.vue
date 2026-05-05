<template>
  <div class="viewer-ui flex min-h-screen bg-slate-50 dark:bg-slate-900 overflow-hidden font-sans">
    <Sidebar />
    <main class="flex-1 flex flex-col p-4 md:p-8 h-screen overflow-y-auto">
      <header class="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4 pb-6 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h1 class="text-3xl font-black text-slate-900 dark:text-white tracking-tighter">{{ t.viewer.title }}</h1>
          <p class="text-xs font-bold text-slate-400 mt-1 uppercase tracking-widest">{{ t.viewer.subtitle }}</p>
        </div>
        <div class="flex items-center gap-3 bg-white dark:bg-slate-800 p-1.5 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 w-full md:w-96 transition-all focus-within:ring-2 focus-within:ring-blue-500/20">
          <div class="pl-3 text-slate-400">
            <svg v-if="!recordingsStore.loading" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            <div v-else class="w-4 h-4 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
          </div>
          <input v-model="recordingsStore.searchQuery" type="text" :placeholder="t.viewer.searchPlaceholder" class="flex-1 bg-transparent border-none focus:ring-0 text-sm font-medium" />
        </div>
      </header>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 flex-1">
        <div class="lg:col-span-8 flex flex-col gap-6">
          <VideoPlayer />
          <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700">
            <h2 class="text-lg font-bold mb-4 flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/><path d="M8 11h8"/><path d="M12 7v8"/></svg>
              {{ t.viewer.hipaaTitle }}
            </h2>
            <div class="space-y-4">
              <div v-if="complianceResult" class="p-4 bg-slate-50 dark:bg-slate-900 rounded-xl text-sm border-l-4 border-blue-500 whitespace-pre-wrap">{{ complianceResult }}</div>
              <button @click="performAIVerification" :disabled="loadingCompliance" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-black py-4 rounded-xl shadow-xl shadow-blue-500/20 active:scale-[0.98] transition-all flex items-center justify-center gap-3">
                <span v-if="loadingCompliance" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                {{ t.viewer.runScan }}
              </button>
            </div>
          </div>
        </div>

        <div class="lg:col-span-4 space-y-6">
          <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700">
            <h3 class="text-xs font-black text-slate-400 uppercase tracking-[2px] mb-6 flex items-center justify-between">
              {{ t.viewer.searchFilters }}
              <button @click="recordingsStore.resetFilters" class="text-blue-500 hover:underline capitalize">{{ t.viewer.clear }}</button>
            </h3>
            <div class="space-y-5">
              <div>
                <label class="text-[10px] font-black text-slate-500 uppercase block mb-2">{{ t.viewer.treatmentType }}</label>
                <select v-model="recordingsStore.selectedType" class="w-full bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-700 rounded-xl text-sm font-bold p-3">
                  <option value="All">{{ t.viewer.allTreatments }}</option>
                  <option value="Cleaning">{{ t.viewer.cleaning }}</option>
                  <option value="Extraction">{{ t.viewer.extraction }}</option>
                  <option value="Implant">{{ t.viewer.implant }}</option>
                </select>
              </div>
              <div>
                <label class="text-[10px] font-black text-slate-500 uppercase block mb-2">{{ t.viewer.dateRange }}</label>
                <input type="date" v-model="recordingsStore.selectedDate" class="w-full bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-700 rounded-xl text-sm font-bold p-3" />
              </div>
            </div>
          </div>

          <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 flex-1 min-h-[300px] relative">
             <div v-if="recordingsStore.loading" class="absolute inset-0 bg-white/50 dark:bg-slate-800/50 backdrop-blur-[2px] z-10 flex items-center justify-center rounded-2xl">
                <div class="w-8 h-8 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
             </div>
             <h3 class="text-xs font-black text-slate-400 uppercase tracking-[2px] mb-5">{{ t.viewer.patientRecordings }}</h3>
             <div class="space-y-3">
                <div v-for="item in recordingsStore.filteredRecordings" :key="item.id" @click="recordingsStore.selectedId = item.id" :class="recordingsStore.selectedId === item.id ? 'bg-blue-600 shadow-lg shadow-blue-600/30' : 'hover:bg-slate-50 dark:hover:bg-slate-700 border-transparent'" class="group p-4 rounded-2xl border transition-all cursor-pointer">
                   <div class="flex items-center gap-4">
                      <div :class="recordingsStore.selectedId === item.id ? 'bg-white/20' : 'bg-slate-100 dark:bg-slate-900'" class="p-3 rounded-xl transition-colors">
                         <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" :class="recordingsStore.selectedId === item.id ? 'text-white' : ''"><circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/></svg>
                      </div>
                      <div class="flex-1 overflow-hidden">
                         <p :class="recordingsStore.selectedId === item.id ? 'text-white' : 'text-slate-900 dark:text-white'" class="font-bold text-sm truncate">{{ item.patientName }}</p>
                         <div class="flex items-center gap-2 mt-1">
                            <span :class="recordingsStore.selectedId === item.id ? 'text-blue-100' : 'text-slate-500'" class="text-[10px] font-bold uppercase tracking-tighter">{{ item.type }}</span>
                            <span :class="recordingsStore.selectedId === item.id ? 'bg-white/20' : 'bg-slate-100 dark:bg-slate-900'" class="w-1 h-1 rounded-full"></span>
                            <span :class="recordingsStore.selectedId === item.id ? 'text-blue-100' : 'text-slate-500'" class="text-[10px] font-medium">{{ item.date }}</span>
                         </div>
                      </div>
                   </div>
                </div>
                <div v-if="recordingsStore.filteredRecordings.length === 0 && !recordingsStore.loading" class="text-center py-10">
                   <p class="text-sm text-slate-400 font-bold">{{ t.viewer.noRecords }}</p>
                </div>
             </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import Sidebar from '@/components/Sidebar.vue';
import VideoPlayer from '@/components/VideoPlayer.vue';
import { verifyHIPAACompliance } from '@/api/imaging';
import { useLangStore } from '@/store/langStore';
import { useRecordingsStore } from '@/store/recordingsStore';

const langStore = useLangStore();
const recordingsStore = useRecordingsStore();
const t = computed(() => langStore.t);

const loadingCompliance = ref(false);
const complianceResult = ref('');

// 當篩選條件改變時，執行 fetch (模擬 API)
watch([() => recordingsStore.selectedType, () => recordingsStore.selectedDate], () => {
  recordingsStore.fetchRecordings();
});

onMounted(() => {
  recordingsStore.fetchRecordings();
});

const performAIVerification = async () => {
  loadingCompliance.value = true;
  const current = recordingsStore.currentRecording;
  try {
    complianceResult.value = await verifyHIPAACompliance(`Patient: ${current.patientName}\nTreatment: ${current.type}\nDate: ${current.date}`);
  } finally { loadingCompliance.value = false; }
};
</script>
