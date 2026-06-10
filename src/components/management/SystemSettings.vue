<template>
  <div class="space-y-8">
    <!-- Device Management -->
    <div class="bg-white dark:bg-slate-800 rounded-3xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-8 border-b border-slate-100 dark:border-slate-700">
        <h2 class="text-xl font-black text-slate-800 dark:text-white">{{ langStore.isZh ? '設備與診間綁定' : 'Device Management' }}</h2>
        <p class="text-xs font-bold text-slate-400 mt-1 uppercase tracking-widest">{{ langStore.isZh ? '管理連線的樹莓派與其對應的診間位置' : 'Manage connected Raspberry Pi devices and their locations' }}</p>
      </div>
      <div class="p-8">
        <div class="space-y-4">
          <div v-for="device in devices" :key="device.id" class="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-900 rounded-2xl border border-slate-100 dark:border-slate-700">
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center font-bold" :class="device.status === 'online' ? 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-slate-200 text-slate-500 dark:bg-slate-800 dark:text-slate-400'">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 4h.01"/><path d="M12 4h.01"/><path d="M9 4h.01"/></svg>
              </div>
              <div>
                <p class="font-bold text-slate-800 dark:text-slate-100">{{ device.name }}</p>
                <p class="text-xs font-medium text-slate-500">{{ device.ip }}</p>
              </div>
            </div>
            <div class="flex items-center gap-4">
              <select class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-1.5 text-sm font-bold text-slate-700 dark:text-slate-300 outline-none focus:ring-2 focus:ring-blue-500">
                <option v-for="op in ['Op 1', 'Op 2', 'Op 3', 'Unassigned']" :key="op" :selected="device.location === op">{{ op }}</option>
              </select>
              <button class="text-blue-600 dark:text-blue-400 font-bold text-sm hover:underline">{{ langStore.isZh ? '測試連線' : 'Test Ping' }}</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Storage Policies -->
    <div class="bg-white dark:bg-slate-800 rounded-3xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-8 border-b border-slate-100 dark:border-slate-700">
        <h2 class="text-xl font-black text-slate-800 dark:text-white">{{ langStore.isZh ? '儲存與備份策略' : 'Storage Policies' }}</h2>
        <p class="text-xs font-bold text-slate-400 mt-1 uppercase tracking-widest">{{ langStore.isZh ? '設定本地硬碟保留時間與 AWS 雲端備份金鑰' : 'Configure local retention rules and AWS backup credentials' }}</p>
      </div>
      <div class="p-8 grid grid-cols-1 md:grid-cols-2 gap-8">
        <div class="space-y-6">
          <h3 class="text-sm font-black text-slate-800 dark:text-white">{{ langStore.isZh ? '本地檔案保留' : 'Local Retention' }}</h3>
          <div class="flex items-center justify-between">
            <div>
              <p class="font-bold text-sm text-slate-800 dark:text-white">{{ langStore.isZh ? '自動刪除已同步檔案' : 'Auto-delete synced files' }}</p>
              <p class="text-xs text-slate-500">{{ langStore.isZh ? '影片成功上傳雲端後，經過指定天數將從本地硬碟抹除。' : 'Delete local copy after X days if successfully synced to cloud.' }}</p>
            </div>
            <div class="w-12 h-6 bg-blue-600 rounded-full relative shadow-inner cursor-pointer transition-all">
              <div class="absolute right-1 top-1 bg-white w-4 h-4 rounded-full shadow-sm transition-transform"></div>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <label class="text-sm font-bold text-slate-600 dark:text-slate-400">{{ langStore.isZh ? '保留天數' : 'Retention Days' }}</label>
            <input type="number" value="30" class="w-24 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2 text-sm font-bold focus:ring-2 focus:ring-blue-500 outline-none text-slate-800 dark:text-white" />
          </div>
        </div>
        
        <div class="space-y-6">
          <h3 class="text-sm font-black text-slate-800 dark:text-white">{{ langStore.isZh ? 'AWS S3 雲端設定' : 'AWS S3 Configuration' }}</h3>
          <div class="space-y-3">
            <input type="text" placeholder="AWS Access Key ID" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-800 dark:text-white" />
            <input type="password" placeholder="AWS Secret Access Key" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-800 dark:text-white" />
            <input type="text" placeholder="Bucket Name (e.g. arloupe-clinic-a)" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-800 dark:text-white" />
          </div>
          <button class="bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-300 px-4 py-2 rounded-xl text-xs font-bold transition-colors">
            {{ langStore.isZh ? '驗證連線' : 'Verify Connection' }}
          </button>
        </div>
      </div>
    </div>

    <!-- PMS Integration -->
    <div class="bg-white dark:bg-slate-800 rounded-3xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-8 border-b border-slate-100 dark:border-slate-700">
        <h2 class="text-xl font-black text-slate-800 dark:text-white">{{ langStore.isZh ? '醫療系統 (PMS) 介接' : 'PMS Integration' }}</h2>
        <p class="text-xs font-bold text-slate-400 mt-1 uppercase tracking-widest">{{ langStore.isZh ? '設定診所現有醫療系統的連線資訊，以啟用自動綁定病歷功能' : 'Configure connection to clinic EMR/PMS for auto-binding features' }}</p>
      </div>
      <div class="p-8 space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">API Endpoint URL</label>
            <input type="text" value="https://api.clinic-pms.local/v1/active-patients" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-800 dark:text-white transition-all" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">Authentication Token</label>
            <input type="password" value="************************" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-800 dark:text-white transition-all" />
          </div>
        </div>
        <div class="flex items-center gap-4 pt-2">
          <button class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl text-sm font-bold shadow-lg shadow-blue-500/20 transition-all">
            {{ langStore.isZh ? '儲存介接設定' : 'Save Integration Settings' }}
          </button>
          <span class="text-xs font-bold text-emerald-500 flex items-center gap-1">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            {{ langStore.isZh ? '連線成功 (2 分鐘前)' : 'Connected (2 mins ago)' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useLangStore } from '@/store/langStore';

const langStore = useLangStore();

const devices = ref([
  { id: 1, name: 'arLoupe Pi-01', ip: '192.168.1.150', status: 'online', location: 'Op 1' },
  { id: 2, name: 'arLoupe Pi-02', ip: '192.168.1.151', status: 'offline', location: 'Op 2' }
]);
</script>
