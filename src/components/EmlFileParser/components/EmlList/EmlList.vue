<template>
    <n-flex vertical>
        <n-flex justify="space-between" align="center" v-show="rawFilesModel.length">
            <n-text style="font-size: 1.05rem">
                解析列表
            </n-text>
            <n-flex justify="space-around" size="medium">
                <n-button size="small" tertiary type="warning" @click="deleteAll">清空</n-button>
                <n-button size="small" tertiary type="info" @click="openModal">总览</n-button>
            </n-flex>
        </n-flex>

        <!-- 放具体的列表 -->
        <EmlFileItem v-for="file in rawFilesModel" :key="file.id" v-model:parsed-info="idToParsedInfo[file.id]"
            :file="file" @delete="deleteFile" />

    </n-flex>


    <n-modal v-model:show="showModal" title="总览" preset="card" :bordered="true" size="medium" style="width: 30rem">
        <n-scrollbar style=" max-height: 80vh; min-height: 100px;">
            <template v-for="({ info: formValue }, index) in formSeminarInfoArr">
                <n-form ref="formRefs" :model="formValue" :rules="rules" label-placement="left" :label-width="80"
                    style="width: 96%;">
                    <n-form-item label="会议名" path="subject">
                        <n-input v-model:value="formValue.subject" placeholder="输入会议名" type="textarea"
                            :autosize="{ minRows: 1 }" />
                    </n-form-item>

                    <n-form-item label="演讲者" path="speaker">
                        <n-input v-model:value="formValue.speaker" placeholder="输入演讲者名字" />
                    </n-form-item>

                    <n-form-item label="时间" path="date" required>
                        <n-date-picker style="width: 100%;" v-model:value="formValue.date" type="date"
                            placeholder="请选择会议时间" />
                    </n-form-item>

                    <n-form-item label="地点" path="location">
                        <n-input v-model:value="formValue.location" placeholder="输入会议地点" />
                    </n-form-item>

                    <n-form-item label="使用英语" path="isEnglish">
                        <n-radio-group v-model:value="formValue.isEnglish">
                            <n-radio :value="true">是</n-radio>
                            <n-radio :value="false">否</n-radio>
                        </n-radio-group>
                    </n-form-item>
                </n-form>
                <n-divider v-if="index !== formSeminarInfoArr.length - 1" />
            </template>
        </n-scrollbar>
        <template #footer>
            <n-flex justify="end" align="center">
                <n-button size="small" tertiary @click="showModal = false">取消</n-button>
                <n-button size="small" secondary type="warning" @click="confirm">确认</n-button>
            </n-flex>
        </template>
    </n-modal>
</template>

<script lang="ts" setup>
import { computed, ref, useTemplateRef, watch, watchEffect } from 'vue';
import { type UploadedFile } from '../EmlUpload/EmlUpload.vue';
import EmlFileItem, { SeminarInfo, type ParsedInfo } from './EmlFileItem.vue';
import { FormRules, FormInst } from 'naive-ui';


const rawFilesModel = defineModel<UploadedFile[]>('raw-files', { required: true });
function deletRawFiles(id: string) {
    rawFilesModel.value = rawFilesModel.value?.filter(file => file.id !== id);
}


// 定义初始 ParsedInfo 工厂函数（可复用）
const createInitialParsedInfo = (): ParsedInfo => ({
    info: {
        speaker: '',
        location: '',
        date: new Date(),
        subject: '',
        isEnglish: true
    },
    status: 'pending'
});
const idToParsedInfo = ref<Record<string, ParsedInfo>>({});

// 响应 rawFilesModel 的变化，自动同步 idToParsedInfo
watchEffect(() => {
    const currentIds = new Set(rawFilesModel.value.map(f => f.id))
    const existingIds = new Set(Object.keys(idToParsedInfo.value))

    // 1. 为新增的 id 添加初始状态
    for (const id of currentIds) {
        if (!existingIds.has(id)) {
            idToParsedInfo.value[id] = createInitialParsedInfo()
        }
    }
})

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


const showModal = ref(false);

interface FormSemniarInfo {
    id: string,
    info: {
        speaker: string,
        location: string,
        date: number,
        subject: string,
        isEnglish: boolean
    }
}
const formSeminarInfoArr = ref<FormSemniarInfo[]>([]);
//根据idToParsedInfo创建表单数组
function openModal() {
    formSeminarInfoArr.value = rawFilesModel.value
        .map(file => {
            const parsed = idToParsedInfo.value[file.id];
            return { id: file.id, parsed };
        })
        .filter((item): item is { id: string; parsed: ParsedInfo } =>
            item.parsed?.status === 'successful'
        )
        .map(({ id, parsed }) => ({
            id,
            info: {
                ...parsed.info,
                date: parsed.info.date.getTime(), // Date → number
            },
        }));
    showModal.value = true;
}

const rules: FormRules = {
    subject: { required: true, message: '请输入会议名', trigger: 'blur' },
    speaker: { required: true, message: '请输入演讲者', trigger: 'blur' },
    location: { required: true, message: '请输入会议地点' },
    isEnglish: { required: true, message: '请选择是否使用英语' }
}

const formRefs = useTemplateRef('formRefs');
function validateForm(form: FormInst): Promise<void> {
    return new Promise((resolve, reject) => {
        form.validate((errors) => {
            if (errors) {
                reject(errors);
            } else {
                resolve();
            }
        });
    });
}
async function confirm() {
    await Promise.all(
        formRefs.value!.map(form => validateForm(form!))
    );
    // 对idToParsedInfo进行了watch，会自动向父组件传递最新的seminarInfo数组
    formSeminarInfoArr.value.forEach(({ id, info: formValue }) => {
        idToParsedInfo.value[id] = {
            info: {
                ...formValue,
                date: new Date(formValue.date) // number → Date
            }, status: 'successful'
        };
    });

    showModal.value = false;
}
</script>

<style lang="css" scoped></style>