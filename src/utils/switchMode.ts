import { ref, computed } from 'vue'
import { darkTheme } from 'naive-ui'

const STORAGE_KEY = 'theme-mode';

// 判断是否夜间
const isNightTime = () => {
  const hour = new Date().getHours();
  return hour >= 18 || hour < 9;
}

// 初始化 isDark
const initIsDark = () => {
  const prefersDark = () =>
    window.matchMedia('(prefers-color-scheme: dark)').matches;

  const stored = localStorage.getItem(STORAGE_KEY);

  if (stored === 'dark') return true;
  if (stored === 'light') return false;

  // 用户未手动设置主题
  return prefersDark() || isNightTime();
}

export const isDark = ref(initIsDark());

export const theme = computed(() => (isDark.value ? darkTheme : null));

export const switchMode = (status = !isDark.value) => {
  isDark.value = status;
  localStorage.setItem(STORAGE_KEY, status ? 'dark' : 'light');
}
