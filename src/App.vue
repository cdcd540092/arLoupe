<template>
  <div id="app" class="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 transition-colors duration-200 font-sans">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useUserStore } from '@/store/userStore';
import { useThemeStore } from '@/store/themeStore';

const userStore = useUserStore();
const themeStore = useThemeStore();

onMounted(() => {
  themeStore.init();
});
</script>

<style>
:root {
  --primary-color: #3b82f6;
  --secondary-color: #64748b;
}

body {
  margin: 0;
  padding: 0;
}
</style>
