<template>
  <div class="management-ui flex min-h-screen bg-slate-50 dark:bg-slate-900 font-sans overflow-hidden">
    <Sidebar />
    <main class="flex-1 p-8 h-screen overflow-y-auto">
      <header class="mb-12 flex justify-between items-center">
        <div>
          <h1 class="text-4xl font-black text-slate-900 dark:text-white tracking-tighter">{{ t.management.title }}</h1>
          <p class="text-sm font-bold text-slate-400 mt-1 uppercase tracking-widest">{{ t.management.subtitle }}</p>
        </div>
      </header>
      
      <!-- Tabs -->
      <div class="mb-8 flex gap-2 border-b border-slate-200 dark:border-slate-700">
        <button @click="activeTab = 'Overview'" class="px-6 py-3 font-bold text-sm border-b-2 transition-colors uppercase tracking-wider" :class="activeTab === 'Overview' ? 'border-blue-600 text-blue-600 dark:text-blue-400' : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-300'">
          {{ langStore.isZh ? '數據總覽與人員' : 'Overview & Users' }}
        </button>
        <button @click="activeTab = 'Audit'" class="px-6 py-3 font-bold text-sm border-b-2 transition-colors uppercase tracking-wider" :class="activeTab === 'Audit' ? 'border-blue-600 text-blue-600 dark:text-blue-400' : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-300'">
          {{ langStore.isZh ? '稽核紀錄' : 'Audit Logs' }}
        </button>
        <button @click="activeTab = 'Settings'" class="px-6 py-3 font-bold text-sm border-b-2 transition-colors uppercase tracking-wider" :class="activeTab === 'Settings' ? 'border-blue-600 text-blue-600 dark:text-blue-400' : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-300'">
          {{ langStore.isZh ? '系統設定' : 'System Settings' }}
        </button>
      </div>
      
      <!-- Overview Tab -->
      <div v-show="activeTab === 'Overview'" class="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <div class="xl:col-span-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-4">
          <div v-for="stat in statsDisplay" :key="stat.label" class="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 group hover:border-blue-500 transition-all">
             <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">{{ stat.label }}</p>
             <h3 class="text-3xl font-black text-slate-900 dark:text-white">{{ stat.value }}</h3>
             <p class="text-xs font-bold text-emerald-500 mt-2 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
                +{{ stat.change }}%
             </p>
          </div>
        </div>

        <div class="xl:col-span-2 space-y-8">
          <UserManagementTable />
        </div>

        <div class="xl:col-span-1 space-y-8">
          <div class="bg-slate-900 text-white p-8 rounded-3xl shadow-2xl relative overflow-hidden group">
            <div class="absolute -right-10 -top-10 w-40 h-40 bg-blue-600/20 blur-3xl rounded-full"></div>
            <h3 class="text-xs font-black text-blue-400 uppercase tracking-widest mb-6 relative z-10">{{ t.management.securityHealth }}</h3>
            <div class="flex items-center gap-6 relative z-10">
               <div class="w-16 h-16 rounded-full border-[6px] border-blue-600/20 flex items-center justify-center relative">
                  <span class="text-lg font-black tracking-tighter">94%</span>
                  <div class="absolute inset-0 border-[6px] border-blue-500 border-t-transparent rounded-full transform -rotate-12"></div>
               </div>
               <div>
                  <p class="font-black text-lg">{{ t.management.hipaaCompliance }}</p>
                  <p class="text-xs text-slate-400 font-bold uppercase tracking-wider">{{ t.management.strongProtection }}</p>
               </div>
            </div>
          </div>

          <div class="bg-white dark:bg-slate-800 p-8 rounded-3xl shadow-sm border border-slate-200 dark:border-slate-700">
             <h3 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-6">{{ t.management.securityPolicies }}</h3>
             <div class="space-y-6">
                <div v-for="policy in policiesDisplay" :key="policy.name" class="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-900 rounded-2xl border border-slate-100 dark:border-slate-700">
                   <div>
                      <p class="font-black text-sm text-slate-800 dark:text-white">{{ policy.name }}</p>
                      <p class="text-[10px] text-slate-400 font-bold uppercase tracking-wider mt-0.5">{{ policy.desc }}</p>
                   </div>
                   <button class="w-10 h-6 bg-blue-600 rounded-full relative transition-all shadow-lg active:scale-90">
                      <div class="absolute right-1 top-1 bg-white w-4 h-4 rounded-full shadow-sm"></div>
                   </button>
                </div>
             </div>
          </div>
        </div>
      </div>

      <!-- Audit Tab -->
      <div v-show="activeTab === 'Audit'" class="bg-white dark:bg-slate-800 rounded-3xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="p-8 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
          <div>
            <h2 class="text-xl font-black text-slate-800 dark:text-white">{{ langStore.isZh ? '系統操作稽核紀錄' : 'System Audit Logs' }}</h2>
            <p class="text-xs font-bold text-slate-400 mt-1 uppercase tracking-widest">HIPAA Compliance Tracking</p>
          </div>
          <button class="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 p-2 rounded-xl text-slate-500 hover:bg-slate-100 transition-all font-bold text-xs px-4">{{ langStore.isZh ? '匯出 CSV' : 'Export CSV' }}</button>
        </div>
        <AuditTable />
      </div>

      <!-- Settings Tab -->
      <div v-show="activeTab === 'Settings'" class="space-y-6">
        <SystemSettings />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import Sidebar from '@/components/Sidebar.vue';
import AuditTable from '@/components/AuditTable.vue';
import UserManagementTable from '@/components/management/UserManagementTable.vue';
import SystemSettings from '@/components/management/SystemSettings.vue';
import { useLangStore } from '@/store/langStore';
import api from '@/api';

const activeTab = ref('Overview');

const langStore = useLangStore();
const t = computed(() => langStore.t);

const dashboardStats = ref({
  total_videos: 0,
  total_users: 0,
  storage_used_gb: 0
});

const fetchStats = async () => {
  try {
    const res = await api.get('/dashboard/stats/');
    dashboardStats.value = res.data;
  } catch (err) {
    console.error("Failed to fetch dashboard stats", err);
  }
};

onMounted(() => {
  fetchStats();
});

const policiesState = ref([true, true, true, false]);

const statsDisplay = computed(() => [
  { label: langStore.isZh ? '系統影片總數' : 'Total Videos', value: dashboardStats.value.total_videos, change: 0 },
  { label: langStore.isZh ? '儲存空間使用' : 'Storage Used', value: dashboardStats.value.storage_used_gb + ' GB', change: 0 },
  { label: langStore.isZh ? '註冊帳號總數' : 'Total Users', value: dashboardStats.value.total_users, change: 0 },
  { label: t.value.management.securityThreats, value: '0', change: 0 }
]);

const policiesDisplay = computed(() => [
  { name: t.value.management.twoFA, desc: t.value.management.twoFADesc },
  { name: t.value.management.encryption, desc: t.value.management.encryptionDesc },
  { name: t.value.management.timeout, desc: t.value.management.timeoutDesc },
  { name: t.value.management.ipWhitelist, desc: t.value.management.ipWhitelistDesc }
]);
</script>
