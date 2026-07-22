<template>
  <div class="audit-table-container">
    <table class="w-full text-left text-sm border-collapse">
      <thead>
        <tr class="bg-slate-50 dark:bg-slate-900 text-slate-500 uppercase tracking-wider font-bold text-[11px] border-b border-slate-200 dark:border-slate-800">
          <th class="px-6 py-5">{{ t.audit.timestamp }}</th>
          <th class="px-6 py-5">{{ t.audit.user }}</th>
          <th class="px-6 py-5">{{ t.audit.action }}</th>
          <th class="px-6 py-5">{{ t.audit.status }}</th>
          <th class="px-6 py-5 text-right">{{ t.audit.details }}</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-100 dark:divide-slate-800/60">
        <tr v-for="log in logs" :key="log.id" class="group hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-all duration-300">
          <td class="px-6 py-5 whitespace-nowrap">
            <div class="flex items-center gap-3">
              <div class="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.6)]"></div>
              <span class="font-medium text-slate-600 dark:text-slate-400 font-mono">{{ log.timestamp }}</span>
            </div>
          </td>
          <td class="px-6 py-5 font-bold text-slate-800 dark:text-slate-100 tracking-tight">{{ log.username }}</td>
          <td class="px-6 py-5">
            <span class="px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-700 font-bold text-[11px] text-slate-500 dark:text-slate-400 tracking-widest border border-slate-200/50 dark:border-slate-600/50">{{ log.action }}</span>
          </td>
          <td class="px-6 py-5">
            <div class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 rounded-full" :class="log.status === 'Success' ? 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.8)]' : 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.8)]'"></span>
              <span class="font-bold text-[12px]" :class="log.status === 'Success' ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-500'">{{ log.status }}</span>
            </div>
          </td>
          <td class="px-6 py-5 text-right">
            <span class="text-xs font-medium text-slate-500">{{ log.details }}</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useLangStore } from '@/store/langStore';
import api from '@/api';

const langStore = useLangStore();
const t = computed(() => langStore.t);

const logs = ref([]);

const fetchLogs = async () => {
  try {
    const res = await api.get('/audit-logs/');
    const data = res.data.results || res.data;
    logs.value = data.map(log => ({
      id: log.id,
      timestamp: new Date(log.created_at).toLocaleString('zh-TW', { hour12: false }),
      username: log.operator_name || log.operator_username || 'System',
      action: log.action,
      details: log.details,
      status: 'Success'
    }));
  } catch (err) {
    console.error('Failed to fetch audit logs', err);
  }
};

onMounted(() => {
  fetchLogs();
});
</script>
