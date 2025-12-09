<template>
  <n-icon :color="props.color" :depth="props.depth" :size="props.size">
    <svg aria-hidden="true">
      <use :href="symbolId"/>
    </svg>
  </n-icon>
</template>

<script lang="ts" setup>
import {computed} from 'vue'

interface Props {
  name: string
  color?: string
  size?: string | number
  depth?: 1 | 2 | 3 | 4 | 5
}

const props = withDefaults(defineProps<Props>(), {})
const symbolId = computed(() => `#icon-${props.name}`)
</script>

<style scoped>
</style>
