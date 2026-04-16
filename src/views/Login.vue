<template>
  <div class="login-page flex min-h-screen items-center justify-center bg-slate-50 dark:bg-slate-950 font-sans p-6 overflow-hidden relative">
    <div class="absolute inset-0 z-0">
      <div class="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] bg-blue-600/10 blur-[120px] rounded-full animate-pulse"></div>
      <div class="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-indigo-600/10 blur-[100px] rounded-full animate-pulse"></div>
    </div>
    
    <div class="relative z-10 w-full max-w-lg">
      <div class="bg-white dark:bg-slate-900 rounded-[3rem] p-10 md:p-16 shadow-2xl shadow-blue-500/10 border border-slate-200/50 dark:border-slate-800/50 backdrop-blur-xl">
        <!-- Top-right: Language & Theme toggles -->
        <div class="flex justify-end gap-2 mb-6">
          <button @click="themeStore.toggle()" class="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all" :title="themeStore.isDark ? t.lightMode : t.darkMode">
            <svg v-if="themeStore.isDark" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
          </button>
          <button @click="langStore.toggle()" class="px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all text-xs font-black text-slate-600 dark:text-slate-300">
            {{ langStore.isZh ? 'EN' : '中' }}
          </button>
        </div>

        <div class="text-center mb-12">
            <div class="w-full h-24 mx-auto flex items-center justify-center mb-10 overflow-hidden">
               <div class="relative h-20 w-56 flex items-center">
                  <img src="@/assets/logo_user.png" alt="arLoupe" class="h-full w-full object-contain transition-all duration-300" :style="themeStore.isDark ? 'mix-blend-mode: screen; filter: invert(1) hue-rotate(180deg) brightness(3);' : 'mix-blend-mode: multiply;'" />
               </div>
            </div>
           <h1 class="hidden text-4xl font-black text-slate-900 dark:text-white tracking-tighter">{{ t.appName.split(' ')[0] }} <span class="text-blue-600">{{ t.appName.split(' ')[1] }}</span></h1>
           <p class="text-sm font-bold text-slate-400 mt-2 uppercase tracking-widest">{{ t.appSubtitle }}</p>
        </div>

        <div class="space-y-4">
           <p class="text-center text-xs font-black text-slate-400 uppercase tracking-[4px] mb-8">{{ t.login.selectPortal }}</p>
           
           <div class="grid grid-cols-1 gap-4">
              <button @click="login('admin')" class="group p-6 bg-slate-50 dark:bg-slate-800 rounded-3xl border-2 border-transparent hover:border-blue-600 hover:bg-white dark:hover:bg-slate-800 transition-all flex items-center gap-5">
                 <div class="text-blue-600 group-hover:scale-110 transition-transform">
                    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/><path d="m9 12 2 2 4-4"/></svg>
                 </div>
                 <div class="text-left">
                    <p class="font-black text-slate-900 dark:text-white text-sm">{{ t.login.adminAccess }}</p>
                    <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-0.5">{{ t.login.adminDesc }}</p>
                 </div>
              </button>
              
              <button @click="login('staff')" class="group p-6 bg-slate-50 dark:bg-slate-800 rounded-3xl border-2 border-transparent hover:border-indigo-500 hover:bg-white dark:hover:bg-slate-800 transition-all flex items-center gap-5">
                 <div class="text-indigo-500 group-hover:scale-110 transition-transform">
                    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 20a6 6 0 0 0-12 0"/><circle cx="12" cy="10" r="4"/><circle cx="12" cy="12" r="10"/></svg>
                 </div>
                 <div class="text-left">
                    <p class="font-black text-slate-900 dark:text-white text-sm">{{ t.login.clinicalStaff }}</p>
                    <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-0.5">{{ t.login.staffDesc }}</p>
                 </div>
              </button>
              
              <button @click="login('patient')" class="group p-6 bg-slate-50 dark:bg-slate-800 rounded-3xl border-2 border-transparent hover:border-emerald-500 hover:bg-white dark:hover:bg-slate-800 transition-all flex items-center gap-5">
                 <div class="text-emerald-500 group-hover:scale-110 transition-transform">
                    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                 </div>
                 <div class="text-left">
                    <p class="font-black text-slate-900 dark:text-white text-sm">{{ t.login.patientPortal }}</p>
                    <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-0.5">{{ t.login.patientDesc }}</p>
                 </div>
              </button>
           </div>
        </div>

        <p class="text-center text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-16 leading-relaxed">
          {{ t.login.footer }}<br/>{{ t.login.footerHipaa }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/store/userStore';
import { useLangStore } from '@/store/langStore';
import { useThemeStore } from '@/store/themeStore';

const router = useRouter();
const userStore = useUserStore();
const langStore = useLangStore();
const themeStore = useThemeStore();
const t = computed(() => langStore.t);

const login = (role) => {
  if (role === 'admin') {
    userStore.setUser({ name: 'Clinic Manager', role: 'admin' });
    router.push('/');
  } else if (role === 'staff') {
    userStore.setUser({ name: 'Dr. Chen', role: 'staff' });
    router.push('/');
  } else {
    userStore.setUser({ name: 'Dwayne Johnson', role: 'patient' });
    router.push('/portal');
  }
};
</script>
