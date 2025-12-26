<template>
  <n-flex vertical style="width: 100%;">
    <EmlUpload :accept="beforeUpload" @select="onFilesSelected" />
    <EmlList v-model:raw-files="uploadedFiles" @update:seminar-list="(arr) => emit('update:seminar-list', arr)" />
  </n-flex>
</template>

<script setup lang="ts">
import EmlUpload, { type UploadedFile } from './components/EmlUpload/EmlUpload.vue';
import EmlList from './components/EmlList/EmlList.vue';
import { ref, onMounted } from 'vue';

//预热加载
onMounted(() => {
  import('ical.js');
  import("eml-parse-js");
});

/* ===== 类型 ===== */
export interface SeminarInfo {
  date: Date;
  location: string;
  speaker: string;
  subject: string;
  isEnglish: boolean;
}

/* ===== emits 定义 ===== */
// 向父组件传递解析出来的seminarInfo数组
const emit = defineEmits<{
  (e: 'update:seminar-list', value: SeminarInfo[]): void
}>();

/* ===== 校验 ===== */
const beforeUpload = (file: File) =>
  file.name.toLowerCase().endsWith('.eml') ?? false;

const uploadedFiles = ref<UploadedFile[]>([]);
function onFilesSelected(files: UploadedFile[]) {
  uploadedFiles.value.push(...files);
}
</script>