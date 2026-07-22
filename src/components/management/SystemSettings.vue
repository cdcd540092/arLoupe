<template>
  <div class="space-y-8">
    <!-- Device Management -->
    <div class="bg-white dark:bg-slate-800 rounded-3xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-8 border-b border-slate-100 dark:border-slate-700">
        <h2 class="text-xl font-black text-slate-800 dark:text-white">{{ langStore.isZh ? '雲端設備管理' : 'Cloud Device Management' }}</h2>
        <p class="text-xs font-bold text-slate-400 mt-1 uppercase tracking-widest">{{ langStore.isZh ? '管理連線的樹莓派與即時狀態' : 'Manage connected Raspberry Pi devices and status' }}</p>
      </div>
      <div class="p-8">
        <div v-if="devices.length === 0" class="text-slate-500 font-bold text-sm">
          {{ langStore.isZh ? '載入中或無可用設備...' : 'Loading or no devices available...' }}
        </div>
        <div class="space-y-4">
          <div v-for="device in devices" :key="device.device_id" class="flex flex-col md:flex-row md:items-center justify-between p-4 bg-slate-50 dark:bg-slate-900 rounded-2xl border border-slate-100 dark:border-slate-700 gap-4">
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center font-bold" :class="device.status === 'active' ? 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-slate-200 text-slate-500 dark:bg-slate-800 dark:text-slate-400'">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 4h.01"/><path d="M12 4h.01"/><path d="M9 4h.01"/></svg>
              </div>
              <div>
                <p class="font-bold text-slate-800 dark:text-slate-100">{{ device.name }}</p>
                <p class="text-xs font-medium text-slate-500">ID: {{ device.device_id }} • Version: {{ device.config_version }}</p>
              </div>
            </div>
            <div class="flex items-center gap-4">
              <span class="text-xs font-bold" :class="device.apply_status === 'pending' ? 'text-amber-500' : 'text-emerald-500'">
                {{ device.apply_status === 'pending' ? (langStore.isZh ? '套用中...' : 'Applying...') : (langStore.isZh ? '已同步' : 'Synced') }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Storage & Recording Policies -->
    <div v-if="primaryDevice" class="bg-white dark:bg-slate-800 rounded-3xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-8 border-b border-slate-100 dark:border-slate-700 flex justify-between items-center">
        <div>
          <h2 class="text-xl font-black text-slate-800 dark:text-white">{{ langStore.isZh ? '錄影與儲存策略' : 'Recording & Storage Policies' }}</h2>
          <p class="text-xs font-bold text-slate-400 mt-1 uppercase tracking-widest">{{ langStore.isZh ? '遠端控制相機的保留天數與畫質' : 'Remote control retention and video quality' }}</p>
        </div>
        <button @click="saveConfig" :disabled="isSaving" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl text-sm font-bold shadow-lg shadow-blue-500/20 transition-all flex items-center gap-2 disabled:opacity-50">
          <div v-if="isSaving" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          {{ langStore.isZh ? '儲存並同步至設備' : 'Save & Sync to Device' }}
        </button>
      </div>
      <div class="p-8 grid grid-cols-1 md:grid-cols-2 gap-8">
        
        <!-- Local Retention -->
        <div class="space-y-6">
          <h3 class="text-sm font-black text-slate-800 dark:text-white">{{ langStore.isZh ? '本地檔案保留 (Retention)' : 'Local Retention' }}</h3>
          <div class="flex items-center gap-4">
            <label class="text-sm font-bold text-slate-600 dark:text-slate-400 w-32">{{ langStore.isZh ? '保留天數' : 'Retention Days' }}</label>
            <input type="number" v-model="primaryDevice.desired_config.retention.retention_days" class="w-24 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2 text-sm font-bold focus:ring-2 focus:ring-blue-500 outline-none text-slate-800 dark:text-white" />
          </div>
          <div class="flex items-center gap-4">
            <label class="text-sm font-bold text-slate-600 dark:text-slate-400 w-32">{{ langStore.isZh ? '低容量警告 (GB)' : 'Low Free (GB)' }}</label>
            <input type="number" v-model="primaryDevice.desired_config.retention.low_free_gb" class="w-24 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2 text-sm font-bold focus:ring-2 focus:ring-blue-500 outline-none text-slate-800 dark:text-white" />
          </div>
        </div>
        
        <!-- Recording Parameters -->
        <div class="space-y-6">
          <h3 class="text-sm font-black text-slate-800 dark:text-white">{{ langStore.isZh ? '錄影畫質設定 (Recording)' : 'Recording Config' }}</h3>
          <div class="flex items-center gap-4">
            <label class="text-sm font-bold text-slate-600 dark:text-slate-400 w-32">{{ langStore.isZh ? '幀率 (FPS)' : 'FPS' }}</label>
            <select v-model="primaryDevice.desired_config.recording.fps" class="w-32 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2 text-sm font-bold focus:ring-2 focus:ring-blue-500 outline-none text-slate-800 dark:text-white">
              <option :value="30">30 FPS</option>
              <option :value="60">60 FPS</option>
            </select>
          </div>
          <div class="flex items-center gap-4">
            <label class="text-sm font-bold text-slate-600 dark:text-slate-400 w-32">{{ langStore.isZh ? '畫質 (kbps)' : 'Bitrate (kbps)' }}</label>
            <input type="number" v-model="primaryDevice.desired_config.recording.bitrate_kbps" step="500" class="w-32 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2 text-sm font-bold focus:ring-2 focus:ring-blue-500 outline-none text-slate-800 dark:text-white" />
          </div>
        </div>
        
      </div>
      <div v-if="saveStatus" class="px-8 pb-6 text-sm font-bold" :class="saveStatus.includes('Error') ? 'text-red-500' : 'text-emerald-500'">
        {{ saveStatus }}
      </div>
    </div>

    <!-- PMS Integration (Mocked) -->
    <div class="bg-white dark:bg-slate-800 rounded-3xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden opacity-60">
      <div class="p-8 border-b border-slate-100 dark:border-slate-700">
        <h2 class="text-xl font-black text-slate-800 dark:text-white">{{ langStore.isZh ? '醫療系統 (PMS) 介接' : 'PMS Integration' }}</h2>
        <p class="text-xs font-bold text-slate-400 mt-1 uppercase tracking-widest">{{ langStore.isZh ? '設定診所現有醫療系統的連線資訊' : 'Configure connection to clinic EMR/PMS' }}</p>
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
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useLangStore } from '@/store/langStore';
import axios from 'axios';

const langStore = useLangStore();

// Cloud API Config
const CLOUD_API = 'http://127.0.0.1:8002/api';

const devices = ref([]);
const primaryDevice = computed(() => devices.value.length > 0 ? devices.value[0] : null);

const isSaving = ref(false);
const saveStatus = ref('');

const authenticateCloud = async () => {
  try {
    const res = await axios.post(`${CLOUD_API}/auth/login`, {
      username: 'admin@example.com',
      password: '123456'
    }, { withCredentials: true });
    return true; 
  } catch (error) {
    console.error("Cloud Auth Error", error);
    return false;
  }
};

const fetchDevices = async () => {
  try {
    const res = await axios.get(`${CLOUD_API}/devices`, { withCredentials: true });
    if (res.data.ok) {
      devices.value = res.data.devices;
    }
  } catch (error) {
    console.error("Fetch Devices Error", error);
  }
};

const saveConfig = async () => {
  if (!primaryDevice.value) return;
  isSaving.value = true;
  saveStatus.value = '';
  try {
    const res = await axios.put(`${CLOUD_API}/devices/${primaryDevice.value.device_id}/config`, {
      recording: primaryDevice.value.desired_config.recording,
      retention: primaryDevice.value.desired_config.retention
    }, { withCredentials: true });
    
    saveStatus.value = langStore.isZh ? '✅ 設備參數已成功同步至雲端！' : '✅ Configuration synced to cloud successfully!';
    
    // Refresh to get updated version numbers
    await fetchDevices();
  } catch (error) {
    console.error("Save Config Error", error);
    saveStatus.value = langStore.isZh ? '❌ 儲存失敗，請重試' : '❌ Error saving config';
  } finally {
    isSaving.value = false;
    setTimeout(() => saveStatus.value = '', 5000);
  }
};

onMounted(async () => {
  await authenticateCloud();
  await fetchDevices();
});
</script>
