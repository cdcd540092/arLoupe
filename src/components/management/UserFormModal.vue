<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
    <div class="bg-white dark:bg-slate-800 rounded-3xl w-full max-w-md shadow-2xl border border-slate-200 dark:border-slate-700 overflow-hidden transform transition-all">
      <div class="p-6 border-b border-slate-100 dark:border-slate-700 flex justify-between items-center bg-slate-50 dark:bg-slate-900/50">
        <h3 class="text-lg font-black text-slate-800 dark:text-white">{{ isEditing ? (langStore.isZh ? '編輯人員' : 'Edit User') : (langStore.isZh ? '邀請新使用者' : 'Invite New User') }}</h3>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
        </button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="p-6 space-y-5">
        <!-- 帳號 (Username) -->
        <div>
          <label class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">{{ langStore.isZh ? '登入帳號' : 'Username' }}</label>
          <input v-model="form.username" type="text" required :disabled="isEditing" 
                 class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-800 dark:text-white transition-all disabled:opacity-50" 
                 placeholder="e.g. jdoe123" />
        </div>

        <!-- 姓名 (Name) -->
        <div>
          <label class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">{{ langStore.isZh ? '顯示名稱' : 'Display Name' }}</label>
          <input v-model="form.name" type="text" required 
                 class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-800 dark:text-white transition-all" 
                 placeholder="e.g. John Doe" />
        </div>

        <!-- 信箱 (Email) -->
        <div>
          <label class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">{{ langStore.isZh ? '電子郵件' : 'Email Address' }}</label>
          <input v-model="form.email" type="email" required 
                 class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-800 dark:text-white transition-all" 
                 placeholder="e.g. john@clinic.local" />
        </div>

        <!-- 角色 (Role) -->
        <div>
          <label class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">{{ langStore.isZh ? '角色層級' : 'Role' }}</label>
          <select v-model="form.role" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm font-bold focus:ring-2 focus:ring-blue-500 outline-none text-slate-800 dark:text-white transition-all">
            <option value="ADMIN">ADMIN (管理員)</option>
            <option value="DOCTOR">DOCTOR (醫師)</option>
            <option value="PATIENT">PATIENT (病患)</option>
          </select>
        </div>

        <!-- 密碼 (Password) -->
        <div>
          <label class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5 flex justify-between">
            <span>{{ langStore.isZh ? '密碼' : 'Password' }}</span>
            <span v-if="isEditing" class="text-slate-400 font-medium text-[10px]">{{ langStore.isZh ? '(若不修改請留白)' : '(Leave blank to keep)' }}</span>
          </label>
          <input v-model="form.password" type="password" :required="!isEditing" 
                 class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-800 dark:text-white transition-all" 
                 placeholder="••••••••" />
        </div>
        
        <!-- 啟用狀態 (Active) -->
        <div v-if="isEditing" class="flex items-center gap-3 pt-2">
           <input type="checkbox" id="isActive" v-model="form.is_active" class="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 bg-slate-100 border-slate-300 dark:bg-slate-800 dark:border-slate-600">
           <label for="isActive" class="text-sm font-bold text-slate-700 dark:text-slate-300">{{ langStore.isZh ? '啟用此帳號' : 'Account Active' }}</label>
        </div>

        <div class="pt-4 flex gap-3">
          <button type="button" @click="$emit('close')" class="flex-1 px-4 py-2.5 rounded-xl text-sm font-bold text-slate-600 dark:text-slate-300 bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600 transition-colors">
            {{ langStore.isZh ? '取消' : 'Cancel' }}
          </button>
          <button type="submit" :disabled="loading" class="flex-1 px-4 py-2.5 rounded-xl text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-500/30 transition-all flex justify-center items-center gap-2 disabled:opacity-70">
            <svg v-if="loading" class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            {{ langStore.isZh ? '儲存設定' : 'Save User' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { useLangStore } from '@/store/langStore';

const props = defineProps({
  isOpen: Boolean,
  userToEdit: Object
});

const emit = defineEmits(['close', 'save']);
const langStore = useLangStore();
const loading = ref(false);

const isEditing = computed(() => !!props.userToEdit);

const form = ref({
  username: '',
  name: '',
  email: '',
  role: 'DOCTOR',
  password: '',
  is_active: true
});

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    if (props.userToEdit) {
      form.value = {
        username: props.userToEdit.username,
        name: props.userToEdit.name,
        email: props.userToEdit.email,
        role: props.userToEdit.role || 'DOCTOR',
        password: '',
        is_active: props.userToEdit.is_active !== false
      };
    } else {
      form.value = { username: '', name: '', email: '', role: 'DOCTOR', password: '', is_active: true };
    }
  }
});

const handleSubmit = () => {
  loading.value = true;
  const payload = { ...form.value };
  if (isEditing.value && !payload.password) {
    delete payload.password; // Don't send empty password if editing
  }
  
  emit('save', {
    id: props.userToEdit?.id,
    data: payload,
    done: () => { loading.value = false; }
  });
};
</script>
