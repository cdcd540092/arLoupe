<template>
  <aside class="sidebar w-72 bg-gradient-to-b from-slate-900 to-slate-800 text-white min-h-screen px-6 py-10 flex flex-col shadow-2xl border-r border-slate-700">
      <div class="logo-area flex items-center mb-12 group cursor-pointer transition-transform hover:scale-105 active:scale-95 overflow-hidden">
        <div class="relative h-12 w-32 flex items-center">
          <img 
            src="@/assets/logo_user.png" 
            alt="arLoupe" 
            class="h-full w-full object-contain"
            style="mix-blend-mode: screen; filter: invert(1) hue-rotate(180deg) brightness(3);"
          />
        </div>
      </div>
    
    <!-- Navigation -->
    <nav class="flex-1 space-y-3">
      <router-link to="/" class="nav-item flex items-center gap-3 px-4 py-3 rounded-xl transition-all hover:bg-slate-700/50 group" :class="{ 'bg-blue-600/20 text-blue-400 border border-blue-500/30': $route.name === 'ClinicalViewer' }">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/></svg>
        <span class="font-semibold text-[15px]">{{ t.sidebar.medicalViewer }}</span>
        <div v-show="$route.name === 'ClinicalViewer'" class="ml-auto w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.8)]"></div>
      </router-link>

      <router-link to="/live" class="nav-item flex items-center gap-3 px-4 py-3 rounded-xl transition-all hover:bg-slate-700/50 group" :class="{ 'bg-blue-600/20 text-blue-400 border border-blue-500/30': $route.name === 'LiveStream' }">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15.6 11.6L22 7v10l-6.4-4.5v-1z"/><circle cx="6" cy="12" r="3"/><circle cx="6" cy="12" r="6" class="opacity-30"/><circle cx="6" cy="12" r="9" class="opacity-10"/></svg>
        <span class="font-semibold text-[15px]">{{ t.sidebar.liveStream }}</span>
        <div v-show="$route.name === 'LiveStream'" class="ml-auto w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.8)]"></div>
      </router-link>
      
      <router-link v-if="userStore.isAdmin" to="/management" class="nav-item flex items-center gap-3 px-4 py-3 rounded-xl transition-all hover:bg-slate-700/50 group" :class="{ 'bg-blue-600/20 text-blue-400 border border-blue-500/30': $route.name === 'Management' }">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.5 3.8 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></svg>
        <span class="font-semibold text-[15px]">{{ t.sidebar.managementConsole }}</span>
        <div v-show="$route.name === 'Management'" class="ml-auto w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.8)]"></div>
      </router-link>
    </nav>

    <!-- Settings: Theme & Language -->
    <div class="space-y-3 mb-6">
      <!-- Dark/Light Toggle -->
      <button @click="themeStore.toggle()" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-700/50 transition-all text-left">
        <svg v-if="themeStore.isDark" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
        <span class="text-sm font-semibold">{{ themeStore.isDark ? t.lightMode : t.darkMode }}</span>
      </button>
      
      <!-- Language Toggle -->
      <button @click="langStore.toggle()" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-700/50 transition-all text-left">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>
        <span class="text-sm font-semibold">{{ langStore.isZh ? 'English' : '中文' }}</span>
        <span class="ml-auto text-[10px] font-black tracking-widest text-slate-400 bg-slate-800 px-2 py-1 rounded-lg">{{ langStore.isZh ? 'ZH' : 'EN' }}</span>
      </button>
    </div>

    <!-- User Profile -->
    <div class="relative">
      <div @click="isProfileMenuOpen = !isProfileMenuOpen" class="user-profile p-4 bg-slate-800/40 rounded-2xl border border-slate-700/50 flex items-center gap-4 group cursor-pointer hover:bg-slate-800/60 transition-all">
        <div class="avatar w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center font-bold text-shadow p-0.5">
          <div class="w-full h-full rounded-full bg-slate-800 flex items-center justify-center uppercase">
            {{ userStore.user?.name?.charAt(0) || 'U' }}
          </div>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-bold truncate">{{ userStore.user?.name || 'Guest' }}</p>
          <p class="text-[11px] text-slate-400 font-medium uppercase tracking-wider">{{ userStore.role || 'Visitor' }}</p>
        </div>
        <div class="text-slate-400 group-hover:text-white transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="{'rotate-180': isProfileMenuOpen}" class="transition-transform duration-300"><polyline points="18 15 12 9 6 15"/></svg>
        </div>
      </div>

      <!-- Profile Menu Dropdown -->
      <div v-if="isProfileMenuOpen" class="absolute bottom-full left-0 mb-3 w-full bg-slate-800 border border-slate-700 rounded-2xl shadow-2xl py-2 z-50 overflow-hidden">
        <button @click="openProfileModal" class="w-full px-4 py-3 text-left text-sm font-semibold text-slate-200 hover:bg-slate-700 hover:text-white flex items-center gap-3 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          {{ langStore.isZh ? '個人資訊設定' : 'Profile Settings' }}
        </button>
        <div class="h-px bg-slate-700 my-1"></div>
        <button @click="userStore.logout(); $router.push('/login')" class="w-full px-4 py-3 text-left text-sm font-semibold text-red-400 hover:bg-red-500/10 hover:text-red-300 flex items-center gap-3 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>
          {{ t.logout }}
        </button>
      </div>
    </div>

    <!-- User Profile Modal Component -->
    <UserProfileModal v-if="isProfileModalOpen" @close="isProfileModalOpen = false" />
  </aside>
</template>

<script setup>
import { useUserStore } from '@/store/userStore';
import { useLangStore } from '@/store/langStore';
import { useThemeStore } from '@/store/themeStore';
import { computed, ref, onMounted, onUnmounted } from 'vue';
import UserProfileModal from '@/components/UserProfileModal.vue';

const userStore = useUserStore();
const langStore = useLangStore();
const themeStore = useThemeStore();
const t = computed(() => langStore.t);

const isProfileMenuOpen = ref(false);
const isProfileModalOpen = ref(false);

const openProfileModal = () => {
  isProfileMenuOpen.value = false;
  isProfileModalOpen.value = true;
};

// 點擊其他地方關閉選單
const closeMenu = (e) => {
  if (!e.target.closest('.user-profile') && !e.target.closest('.absolute')) {
    isProfileMenuOpen.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', closeMenu);
});
onUnmounted(() => {
  document.removeEventListener('click', closeMenu);
});
</script>
