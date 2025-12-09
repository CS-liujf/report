import { ref, computed } from 'vue'
import { darkTheme } from 'naive-ui'

export const isDark = ref(false)
export const theme = computed(() => (isDark.value ? darkTheme : null))

export const switchMode = (status = !isDark.value) => {
  isDark.value = status
  if (isDark.value) document.documentElement.classList.add('dark')
  else document.documentElement.classList.remove('dark')
}
