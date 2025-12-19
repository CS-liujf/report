<template>
    <n-flex vertical>
        <n-flex justify="space-between" align="center" v-show="rawFilesModel.length">
            <n-text style="font-size: 1.05rem">
                解析列表
            </n-text>
            <n-flex justify="space-around" size="medium">
                <n-button size="small" tertiary type="warning" @click="deleteAll">清空</n-button>
                <!-- <n-button size="small" tertiary type="info">查看</n-button> -->
            </n-flex>
        </n-flex>

        <!-- 放具体的列表 -->
        <EmlFileItem v-for="file in rawFilesModel" :key="file.id" :file="file" @delete="deleteFile"
            @parse="(id, newValue) => idToParsedInfo[id] = newValue" />

    </n-flex>
</template>

<script lang="ts" setup>
import { ref, watch } from 'vue';
import { type UploadedFile } from '../EmlUpload/EmlUpload.vue';
import EmlFileItem, { SeminarInfo, type ParsedInfo } from './EmlFileItem.vue';


const rawFilesModel = defineModel<UploadedFile[]>('raw-files', { required: true });
function deletRawFiles(id: string) {
    rawFilesModel.value = rawFilesModel.value?.filter(file => file.id !== id);
}



const idToParsedInfo = ref<Record<string, ParsedInfo>>({});
function deleteParsedInfo(id: string) {
    delete idToParsedInfo.value[id];
}


function deleteFile(id: string) {
    deletRawFiles(id);
    deleteParsedInfo(id);
    return;
}

interface Emits {
    (e: 'update:seminar-list', seminarInfoArr: SeminarInfo[]): void,
}
const emits = defineEmits<Emits>();
watch(idToParsedInfo, (newVal) => {
    const result: SeminarInfo[] = [];
    for (let i = 0; i < rawFilesModel.value.length; i++) {
        if (newVal[rawFilesModel.value[i].id] && newVal[rawFilesModel.value[i].id].status === 'successful') {
            result.push(newVal[rawFilesModel.value[i].id].info);
        }
    }
    emits('update:seminar-list', result);
}, { deep: true }); //将解析出来的seminarInfo数组给父组件

function deleteAll() {
    rawFilesModel.value = [];
    idToParsedInfo.value = {};
}

</script>

<style lang="css" module></style>