<template>
  <div
    class="svg-container"
    @click.stop="switchMode()"
  >
    <SvgIcon
      v-if="isDark"
      name="太阳"
      :size="sunSize"
    />
    <SvgIcon
      v-else
      name="月亮"
      :size="size"
    />
  </div>
</template>

<script lang="ts" setup>
import { isDark, switchMode } from '@/utils/switchMode';
import SvgIcon from '@/components/SvgIcon/SvgIcon.vue';
import { computed } from 'vue';

interface Props {
  size?: string | number //必须设置为可选属性，否则会有ts类型错误
}

// 设置默认值
const props = withDefaults(defineProps<Props>(), {
  size: 28 
});

// 计算太阳图标尺寸：保持 26:28 的比例
const sunSize = computed(() => {
  const baseSize = Number(props.size);
  return Math.round((baseSize * 26) / 28);
});
</script>

<style scoped>
.svg-container {
  cursor: pointer;
  height: 100%;
  display: flex;
  align-items: center;
}
</style>