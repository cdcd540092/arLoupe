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
            <button class="text-blue-500 hover:text-blue-600 font-bold text-xs uppercase tracking-tighter opacity-0 group-hover:opacity-100 transition-all">{{ t.management.inspectLog }}</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useLangStore } from '@/store/langStore';

const langStore = useLangStore();
const t = computed(() => langStore.t);

const logs = ref([
  { id: 1, timestamp: '2026-04-07 15:32:11', username: 'admin_alpha', action: 'EXPORT_IMAGE', status: 'Success' },
  { id: 2, timestamp: '2026-04-07 14:21:45', username: 'dr_chen', action: 'VIEW_PATIENT', status: 'Success' },
  { id: 3, timestamp: '2026-04-07 12:05:30', username: 'system_core', action: 'BACKUP_DB', status: 'Success' },
  { id: 4, timestamp: '2026-04-07 11:45:12', username: 'nurse_joy', action: 'UPDATE_VITAL', status: 'Success' },
  { id: 5, timestamp: '2026-04-07 10:12:55', username: 'hacker_007', action: 'LOGIN_FAILURE', status: 'Failure' }
]);
</script>
