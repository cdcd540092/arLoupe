<template>
  <div class="management-ui flex min-h-screen bg-slate-50 dark:bg-slate-900 font-sans overflow-hidden">
    <Sidebar />
    <main class="flex-1 p-8 h-screen overflow-y-auto">
      <header class="mb-12 flex justify-between items-center">
        <div>
          <h1 class="text-4xl font-black text-slate-900 dark:text-white tracking-tighter">{{ t.management.title }}</h1>
          <p class="text-sm font-bold text-slate-400 mt-1 uppercase tracking-widest">{{ t.management.subtitle }}</p>
        </div>
        <div class="flex gap-4">
           <button class="bg-white dark:bg-slate-800 p-3 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 hover:bg-slate-50 transition-all">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.1a2 2 0 0 1-1-1.72v-.51a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
           </button>
           <button v-if="false" class="bg-blue-600 hover:bg-blue-700 text-white font-black py-3 px-8 rounded-2xl shadow-xl shadow-blue-500/20 active:scale-95 transition-all">{{ t.management.createPolicy }}</button>
        </div>
      </header>
      
      <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
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
          <div class="bg-white dark:bg-slate-800 rounded-3xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
            <div class="p-8 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
              <div>
                <h2 class="text-xl font-black text-slate-800 dark:text-white">{{ t.management.activeUsers }}</h2>
                <p class="text-xs font-bold text-slate-400 mt-1 uppercase tracking-widest">{{ t.management.activeUsersDesc }}</p>
              </div>
              <button class="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 p-2 rounded-xl text-slate-500 hover:bg-slate-100 transition-all font-bold text-xs px-4">{{ t.management.viewAll }}</button>
            </div>
            <AuditTable />
          </div>
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
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import Sidebar from '@/components/Sidebar.vue';
import AuditTable from '@/components/AuditTable.vue';
import { useLangStore } from '@/store/langStore';

const langStore = useLangStore();
const t = computed(() => langStore.t);

const statsDisplay = computed(() => [
  { label: t.value.management.totalPatients, value: '1,284', change: 12 },
  { label: t.value.management.cloudStorage, value: '84.2 GB', change: 5 },
  { label: t.value.management.dailyScans, value: '52', change: 24 },
  { label: t.value.management.securityThreats, value: '0', change: 0 }
]);

const policiesDisplay = computed(() => [
  { name: t.value.management.twoFA, desc: t.value.management.twoFADesc },
  { name: t.value.management.encryption, desc: t.value.management.encryptionDesc },
  { name: t.value.management.timeout, desc: t.value.management.timeoutDesc },
  { name: t.value.management.ipWhitelist, desc: t.value.management.ipWhitelistDesc }
]);
</script>
