<template>
  <div class="login-page flex min-h-screen items-center justify-center bg-slate-50 dark:bg-slate-950 font-sans p-6 overflow-hidden relative">
    <div class="absolute inset-0 z-0">
      <div class="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] bg-blue-600/10 blur-[120px] rounded-full animate-pulse"></div>
      <div class="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-indigo-600/10 blur-[100px] rounded-full animate-pulse"></div>
    </div>
    
    <div class="relative z-10 w-full max-w-md">
      <div class="bg-white dark:bg-slate-900 rounded-[3rem] p-8 md:p-12 shadow-2xl shadow-blue-500/10 border border-slate-200/50 dark:border-slate-800/50 backdrop-blur-xl">
        <!-- Top-right: Language & Theme toggles -->
        <div class="flex justify-end gap-2 mb-4">
          <button @click="themeStore.toggle()" class="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all" :title="themeStore.isDark ? t.lightMode : t.darkMode">
            <svg v-if="themeStore.isDark" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
          </button>
          <button @click="langStore.toggle()" class="px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all text-xs font-black text-slate-600 dark:text-slate-300">
            {{ langStore.isZh ? 'EN' : '中' }}
          </button>
        </div>

        <div class="text-center mb-8">
          <div class="w-full h-20 mx-auto flex items-center justify-center mb-4 overflow-hidden">
             <div class="relative h-16 w-48 flex items-center">
                <img src="@/assets/logo_user.png" alt="arLoupe" class="h-full w-full object-contain transition-all duration-300" :style="themeStore.isDark ? 'mix-blend-mode: screen; filter: invert(1) hue-rotate(180deg) brightness(3);' : 'mix-blend-mode: multiply;'" />
             </div>
          </div>
          <p class="text-xs font-bold text-slate-400 uppercase tracking-widest">{{ t.appSubtitle }}</p>
        </div>

        <!-- Single Unified Login Form -->
        <form @submit.prevent="handleLogin" class="space-y-5">
           <div v-if="userStore.error" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/50 rounded-2xl">
              <p class="text-xs font-bold text-red-600 dark:text-red-400">{{ userStore.error }}</p>
           </div>
           
           <div>
              <label class="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5">{{ t.login.username || 'Username' }}</label>
              <div class="relative">
                 <input v-model="credentials.username" type="text" class="w-full bg-slate-50 dark:bg-slate-800 border-2 border-slate-200 dark:border-slate-700 rounded-2xl px-5 py-3.5 pl-12 text-sm font-bold text-slate-900 dark:text-white focus:border-blue-500 focus:ring-0 transition-all placeholder:text-slate-400/50" placeholder="admin" required />
                 <svg class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              </div>
           </div>
           <div>
              <label class="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5">{{ t.login.password || 'Password' }}</label>
              <div class="relative">
                 <input v-model="credentials.password" type="password" class="w-full bg-slate-50 dark:bg-slate-800 border-2 border-slate-200 dark:border-slate-700 rounded-2xl px-5 py-3.5 pl-12 text-sm font-bold text-slate-900 dark:text-white focus:border-blue-500 focus:ring-0 transition-all placeholder:text-slate-400/50" placeholder="••••••••" required />
                 <svg class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
              </div>
           </div>
           
           <button type="submit" :disabled="userStore.loading" class="w-full mt-2 bg-blue-600 hover:bg-blue-700 text-white font-black py-4 px-8 rounded-2xl shadow-xl shadow-blue-500/20 active:scale-95 transition-all text-sm tracking-widest uppercase flex justify-center items-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed">
              <span v-if="userStore.loading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              {{ userStore.loading ? (t.login.signIning || 'Signing in...') : (t.login.signIn || 'Sign In') }}
           </button>
        </form>

        <p class="text-center text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-10 leading-relaxed">
          {{ t.login.footer }}<br/>{{ t.login.footerHipaa }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/store/userStore';
import { useLangStore } from '@/store/langStore';
import { useThemeStore } from '@/store/themeStore';

const router = useRouter();
const userStore = useUserStore();
const langStore = useLangStore();
const themeStore = useThemeStore();
const t = computed(() => langStore.t);

const credentials = ref({
   username: '',
   password: ''
});

const handleLogin = async () => {
   const success = await userStore.login(credentials.value);
   if (success) {
      if (userStore.role === 'patient') {
         router.push('/portal');
      } else {
         router.push('/');
      }
   }
};
</script>

