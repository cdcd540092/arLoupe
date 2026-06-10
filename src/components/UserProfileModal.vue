<template>
  <div class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
    <div class="bg-white dark:bg-slate-800 w-full max-w-md rounded-3xl shadow-2xl overflow-hidden border border-slate-200 dark:border-slate-700 animate-in fade-in zoom-in duration-200">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between bg-slate-50 dark:bg-slate-800/50">
        <h2 class="text-lg font-black text-slate-800 dark:text-white">{{ langStore.isZh ? '個人資訊與設定' : 'Profile Settings' }}</h2>
        <button @click="$emit('close')" class="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>

      <!-- Form Content -->
      <div class="p-6 space-y-6">
        <!-- Avatar Section -->
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center font-bold text-white text-2xl p-1 shadow-inner">
            <div class="w-full h-full rounded-full bg-slate-800 flex items-center justify-center uppercase">
              {{ formData.name?.charAt(0) || 'U' }}
            </div>
          </div>
          <div>
            <button class="px-4 py-2 bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-bold hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors">
              {{ langStore.isZh ? '更換大頭貼' : 'Change Avatar' }}
            </button>
          </div>
        </div>

        <form @submit.prevent="saveProfile" class="space-y-4">
          <!-- Name -->
          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">{{ langStore.isZh ? '顯示名稱' : 'Display Name' }}</label>
            <input v-model="formData.name" type="text" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-slate-800 dark:text-white transition-all" />
          </div>
          
          <!-- Email -->
          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">{{ langStore.isZh ? '電子郵件' : 'Email Address' }}</label>
            <input v-model="formData.email" type="email" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-slate-800 dark:text-white transition-all" />
          </div>

          <!-- Password (Mock) -->
          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">{{ langStore.isZh ? '新密碼' : 'New Password' }}</label>
            <input v-model="formData.password" type="password" :placeholder="langStore.isZh ? '留白表示不更改' : 'Leave empty to keep current'" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-slate-800 dark:text-white transition-all" />
          </div>

          <!-- Actions -->
          <div class="pt-4 flex gap-3">
            <button type="button" @click="$emit('close')" class="flex-1 px-4 py-3 bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-xl text-sm font-bold hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors">
              {{ langStore.isZh ? '取消' : 'Cancel' }}
            </button>
            <button type="submit" class="flex-1 px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-bold shadow-lg shadow-blue-500/20 transition-all flex items-center justify-center gap-2">
              <svg v-if="saving" class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              {{ langStore.isZh ? '儲存變更' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useUserStore } from '@/store/userStore';
import { useLangStore } from '@/store/langStore';

const emit = defineEmits(['close']);
const userStore = useUserStore();
const langStore = useLangStore();

const saving = ref(false);

const formData = reactive({
  name: userStore.user?.name || '',
  email: userStore.user?.email || 'admin@clinic.local',
  password: ''
});

const saveProfile = async () => {
  saving.value = true;
  // Mock API call
  setTimeout(() => {
    if(formData.name) {
       userStore.user.name = formData.name;
    }
    saving.value = false;
    emit('close');
  }, 600);
};
</script>
