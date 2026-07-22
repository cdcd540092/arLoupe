<template>
  <div class="bg-white dark:bg-slate-800 rounded-3xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
    <div class="p-8 border-b border-slate-100 dark:border-slate-700 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h2 class="text-xl font-black text-slate-800 dark:text-white">{{ langStore.isZh ? '人員與權限管理' : 'Staff & Role Management' }}</h2>
        <p class="text-xs font-bold text-slate-400 mt-1 uppercase tracking-widest">{{ langStore.isZh ? '管理診所內所有具備系統存取權限的帳號' : 'Manage all accounts with system access' }}</p>
      </div>
      <button @click="openModal()" class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl text-sm font-bold shadow-lg shadow-blue-500/20 transition-all flex items-center gap-2 w-fit">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        {{ langStore.isZh ? '邀請新使用者' : 'Invite User' }}
      </button>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-100 dark:border-slate-700">
            <th class="p-4 pl-8 text-[10px] font-black uppercase tracking-widest text-slate-400 w-1/3">{{ langStore.isZh ? '使用者' : 'User' }}</th>
            <th class="p-4 text-[10px] font-black uppercase tracking-widest text-slate-400 w-1/6">{{ langStore.isZh ? '角色層級' : 'Role' }}</th>
            <th class="p-4 text-[10px] font-black uppercase tracking-widest text-slate-400 w-1/4">{{ langStore.isZh ? '最後登入' : 'Last Login' }}</th>
            <th class="p-4 text-[10px] font-black uppercase tracking-widest text-slate-400 w-1/6 text-right pr-8">{{ langStore.isZh ? '操作' : 'Actions' }}</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 dark:divide-slate-700/50 text-sm">
          <tr v-for="user in users" :key="user.id" class="hover:bg-slate-50/50 dark:hover:bg-slate-900/20 transition-colors group">
            <td class="p-4 pl-8">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full flex items-center justify-center font-bold text-white shadow-inner uppercase" :class="user.avatarBg">
                  {{ user.name.charAt(0) }}
                </div>
                <div>
                  <p class="font-bold text-slate-800 dark:text-slate-100">{{ user.name }}</p>
                  <p class="text-xs text-slate-500">{{ user.email }}</p>
                </div>
              </div>
            </td>
            <td class="p-4">
              <span class="px-2.5 py-1 rounded-lg text-xs font-bold border flex w-fit items-center gap-1.5" :class="roleClasses(user.role)">
                <div class="w-1.5 h-1.5 rounded-full" :class="roleDotClasses(user.role)"></div>
                {{ user.role }}
              </span>
            </td>
            <td class="p-4 text-slate-500 font-medium text-xs">
              {{ user.lastLogin }}
            </td>
            <td class="p-4 pr-8 text-right">
              <div class="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button @click="openModal(user)" class="p-2 text-slate-400 hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-colors" :title="langStore.isZh ? '編輯' : 'Edit'">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
                </button>
                <button v-if="user.role !== 'ADMIN'" @click="deleteUser(user.id)" class="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors" :title="langStore.isZh ? '刪除' : 'Delete'">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 彈出式表單 -->
    <UserFormModal 
      :isOpen="isModalOpen" 
      :userToEdit="editingUser" 
      @close="closeModal" 
      @save="handleSaveUser" 
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useLangStore } from '@/store/langStore';
import api from '@/api';
import UserFormModal from './UserFormModal.vue';

const langStore = useLangStore();
const users = ref([]);
const isModalOpen = ref(false);
const editingUser = ref(null);

const bgColors = [
  'bg-gradient-to-br from-blue-500 to-indigo-600',
  'bg-gradient-to-br from-emerald-400 to-teal-500',
  'bg-gradient-to-br from-amber-400 to-orange-500',
  'bg-gradient-to-br from-rose-400 to-pink-500'
];

const fetchUsers = async () => {
  try {
    const response = await api.get('/users/');
    users.value = response.data.map((user, idx) => ({
      ...user,
      avatarBg: bgColors[idx % bgColors.length],
      lastLogin: user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'
    }));
  } catch (error) {
    console.error("Failed to fetch users:", error);
  }
};

const openModal = (user = null) => {
  editingUser.value = user;
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
  editingUser.value = null;
};

const handleSaveUser = async ({ id, data, done }) => {
  try {
    if (id) {
      await api.put(`/users/${id}/`, data);
    } else {
      await api.post('/users/', data);
    }
    await fetchUsers();
    closeModal();
  } catch (error) {
    console.error("Failed to save user:", error);
    alert('儲存失敗，請確認資料格式或帳號是否重複。');
  } finally {
    done();
  }
};

const deleteUser = async (id) => {
  if (confirm(langStore.isZh ? '確定要刪除此使用者嗎？' : 'Are you sure you want to delete this user?')) {
    try {
      await api.delete(`/users/${id}/`);
      await fetchUsers();
    } catch (error) {
      console.error("Failed to delete user:", error);
    }
  }
};

onMounted(() => {
  fetchUsers();
});

const roleClasses = (role) => {
  switch (role) {
    case 'ADMIN': return 'bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-indigo-900/30 dark:text-indigo-400 dark:border-indigo-800';
    case 'DOCTOR': return 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-400 dark:border-emerald-800';
    case 'PATIENT': return 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800';
    default: return 'bg-slate-50 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700';
  }
};

const roleDotClasses = (role) => {
  switch (role) {
    case 'ADMIN': return 'bg-indigo-500';
    case 'DOCTOR': return 'bg-emerald-500';
    case 'PATIENT': return 'bg-blue-500';
    default: return 'bg-slate-500';
  }
};
</script>
