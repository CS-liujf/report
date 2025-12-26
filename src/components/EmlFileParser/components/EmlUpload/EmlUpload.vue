<template>
    <div class="upload" @click="triggerInput" @dragover.prevent="handleDragOver" @dragenter.prevent="handleDragEnter"
        @dragleave.prevent="handleDragLeave" @drop.prevent="handleDrop">
        <input ref="fileInputRef" @change="handleChange" type="file" class="upload-file-input" multiple></input>

        <div class="upload-dragger" :class="{ 'dragenter': isDragOver }">
            <div style="margin-bottom: 0.75rem">
                <n-icon size="48" :depth="3">
                    <ArchiveIcon />
                </n-icon>
            </div>
            <n-text style="font-size: 1rem">
                点击上传或拖放邮件文件到该区域解析
            </n-text>
            <n-p depth="3" style="margin: 0.25rem 0 0 0; font-size: 0.9rem">
                支持上传多个.eml格式的邮件文件
            </n-p>
        </div>

    </div>
</template>

<script setup lang="ts">
import { ref, useTemplateRef, computed } from 'vue';
import { ArchiveOutline as ArchiveIcon } from '@vicons/ionicons5';
import { isDark } from '@/utils/switchMode';

interface Props {
    accept: (file: File) => boolean
}
const props = defineProps<Props>();

// Emits
// 定义包装后的文件类型
export interface UploadedFile {
    id: string
    file: File
}
const emit = defineEmits<{
    (e: 'select', files: UploadedFile[]): void
}>()

const fileInputRef = useTemplateRef('fileInputRef');
function triggerInput() {
    fileInputRef.value?.click();
}

// 校验并 emit 包装后的文件
function generateId(): string {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        return crypto.randomUUID()
    }
    // fallback for older browsers
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = (Math.random() * 16) | 0
        const v = c === 'x' ? r : (r & 0x3) | 0x8
        return v.toString(16)
    })
}
function validateAndEmit(files: File[]) {
    const validFiles: UploadedFile[] = []

    for (const file of files) {
        if (props.accept(file)) {
            validFiles.push({
                id: generateId(),
                file
            })
        }
    }

    if (validFiles.length > 0) {
        emit('select', validFiles)
    }
}

function handleChange(event: Event) {
    const input = event.target as HTMLInputElement
    const files = Array.from(input.files || [])
    validateAndEmit(files)
    input.value = ''
}

// 拖拽处理
const isDragOver = ref(false);
function handleDragOver() {
    isDragOver.value = true
}
function handleDragEnter() {
    isDragOver.value = true
}
function handleDragLeave() {
    isDragOver.value = false
}
function handleDrop(event: DragEvent) {
    isDragOver.value = false
    const files = Array.from(event.dataTransfer?.files || [])
    validateAndEmit(files)
}
// 边框样式
const borderColor = computed(() => (isDark.value ? 'rgba(255, 255, 255, 0.24)' : 'rgb(224, 224, 230)'))
const borderHoverColor = computed(() => isDark.value ? '#63e2b7' : '#18a058')
const backgroundColor = computed(() => (isDark.value ? 'rgba(255, 255, 255, 0.06)' : 'rgb(250, 250, 252)'))
</script>

<style lang="css" scoped>
.upload {
    width: 100%;
    --n-bezier: cubic-bezier(.4, 0, .2, 1);
    --n-border-radius: 3px;
    --n-dragger-border: 1px dashed v-bind(borderColor);
    --n-dragger-color: v-bind(backgroundColor);
}

.upload-file-input {
    display: none;
    width: 0;
    height: 0;
    opacity: 0;
}

.upload-dragger {
    cursor: pointer;
    box-sizing: border-box;
    width: 100%;
    text-align: center;
    border-radius: var(--n-border-radius);
    padding: 24px;
    opacity: 1;
    transition: opacity .3s var(--n-bezier), border-color .3s var(--n-bezier), background-color .3s var(--n-bezier);
    background-color: var(--n-dragger-color);
    border: var(--n-dragger-border);
}

.upload-dragger:hover {
    border-color: v-bind(borderHoverColor);
}

.dragenter {
    border-color: v-bind(borderHoverColor);
}
</style>