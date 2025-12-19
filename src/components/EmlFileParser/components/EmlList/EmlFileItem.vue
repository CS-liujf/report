<template>
    <n-flex :wrap="false" justify="space-between" align="center" class="item-container" @click="showModal = true">
        <n-flex :wrap="false" align="center" :size="[6, 0]">
            <n-icon size="1.2rem">
                <MailIcon />
            </n-icon>
            <n-text style="font-size: 0.9rem;">{{ props.file.file.name }}</n-text>
        </n-flex>

        <n-icon size="1.2rem">
            <TrashBinIcon @click.prevent="emit('delete', props.file.id)" />
        </n-icon>
    </n-flex>

    <!-- 弹窗 -->
    <n-modal v-model:show="showModal">
        <n-card style="max-width: 600px" title="详情" :bordered="false" size="medium">
            <n-form ref="formRef" :model="formValue" :rules="rules" label-placement="left" :label-width="80">
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

            <template #footer>
                <n-flex justify="end" align="center">
                    <n-button size="small" tertiary @click="showModal = false">取消</n-button>
                    <n-button size="small" secondary type="warning" @click="confirm">确认</n-button>
                </n-flex>
            </template>
        </n-card>
    </n-modal>
</template>
<script setup lang="ts">
import { MailOutline as MailIcon, TrashBinOutline as TrashBinIcon } from '@vicons/ionicons5';
import { type UploadedFile } from "../EmlUpload/EmlUpload.vue";
import type { Attachment, ReadedEmlJson } from 'eml-parse-js';
import { useTemplateRef, ref, watchEffect } from 'vue';
import { FormRules } from 'naive-ui';


// 用于接收原始文件
interface Props {
    file: UploadedFile;
}
const props = defineProps<Props>();

export interface SeminarInfo {
    date: Date;
    location: string;
    speaker: string;
    subject: string;
    isEnglish: boolean;
}

export interface ParsedInfo {
    info: SeminarInfo;
    status: 'pending' | 'parsing' | 'successful' | 'failed';
}

const parsedInfoModel = defineModel<ParsedInfo>('parsed-info', { required: true });

export interface ParsedFile {
    id: string
    info: SeminarInfo
}


interface Emits {
    (e: 'delete', id: string): void
}
const emit = defineEmits<Emits>();


const parseEml = async (emlFile: File): Promise<void> => {
    async function readEmlAsync(text: string): Promise<ReadedEmlJson | undefined> {
        const { readEml } = await import('eml-parse-js');

        return new Promise((resolve, reject) => {
            readEml(text, (err, data) => {
                if (err) {
                    reject(err instanceof Error ? err : new Error(String(err)));
                } else {
                    resolve(data);
                }
            });
        });
    }

    function extractSpeaker(text: string): string | null {
        if (!text) return null;

        // 两种格式：
        // 1) Speaker: xxx
        // 2) 演讲者：xxx
        // - 忽略大小写 (i)
        // - 匹配各种半角/全角冒号
        // - 提取冒号后面的内容直到换行
        const regexList = [
            /speaker\s*[:：]\s*(.+)/i,
            /演讲者\s*[:：]\s*(.+)/i
        ];

        for (const r of regexList) {
            const m = text.match(r);
            if (m && m[1]) {
                return m[1].trim().replace(/[。．\.；;，,]+$/, ''); //去掉句末的标点
            }
        }

        return null;
    }

    function extractLocation(text: string): string | null {
        if (!text) return null;

        // 两种格式：
        // 1) Location: xxx
        // 2) 地点：xxx
        // - 忽略大小写 (i)
        // - 匹配半角 / 全角冒号
        // - 提取冒号后直到换行
        const regexList = [
            /location\s*[:：]\s*(.+)/i,
            /地点\s*[:：]\s*(.+)/i,
        ];

        for (const r of regexList) {
            const m = text.match(r);
            if (m?.[1]) {
                return m[1].trim().replace(/[。．\.；;，,]+$/, ''); //去掉句末的标点
            }
        }

        return null;
    }


    function getCalendarAttachment(
        attachments?: Attachment[]
    ): Attachment | null {
        if (!attachments?.length) return null;

        return (
            attachments.find(att =>
                att.contentType?.startsWith('text/calendar')
            ) ?? null
        );
    }

    function hasChinese(str: string): boolean {
        // 正则匹配基本中文字符
        const chineseReg = /[\u4e00-\u9fa5]/;
        return chineseReg.test(str);
    }

    function parseByContent(emlFile: ReadedEmlJson, info: SeminarInfo) {
        if (emlFile.date instanceof Date) {
            info.date = emlFile.date;
        } else {
            info.date = new Date(emlFile.date);
        }

        info.subject = emlFile.subject;
        const location = extractLocation(emlFile.text!);
        info.location = location ? location : '';
    }
    async function parseByAttachment(calendarAttachment: Attachment, info: SeminarInfo) {
        // 用 ical.js 解析 icsText
        const { default: ICAL } = await import('ical.js');
        const icsText = calendarAttachment.data as string;
        const jcal = ICAL.parse(icsText);
        const component = new ICAL.Component(jcal);
        const event = new ICAL.Event(component.getFirstSubcomponent('vevent')!);

        info.subject = event.summary;
        info.location = event.location;
        info.date = event.startDate.toJSDate();
    }

    const info: SeminarInfo = {
        date: new Date(),
        location: '',
        speaker: '',
        subject: '',
        isEnglish: true
    };

    // 解析日历，提取主题、时间和地点
    const text = await emlFile.text();
    const data = await readEmlAsync(text);
    // 正文必须存在
    if (!data?.text) {
        throw new Error('邮件解析失败：正文缺失');
    }

    const speaker = extractSpeaker(data.text);
    if (!speaker) {
        throw new Error('邮件解析失败：未找到演讲者');
    }
    info.speaker = speaker;

    //解析时间、地点和主题
    const calendarAttachment = getCalendarAttachment(data.attachments);
    if (calendarAttachment) {
        await parseByAttachment(calendarAttachment, info);
    } else {
        parseByContent(data, info);
    }

    info.isEnglish = !hasChinese(info.subject);

    parsedInfoModel.value.status = 'successful';
    parsedInfoModel.value.info = info;

    return;
};


//表单处理
const formRef = useTemplateRef('formRef');
const formValue = ref({
    speaker: '',
    location: '',
    date: Date.now(),
    subject: '',
    isEnglish: true
})
watchEffect(() => {
    const newValue = parsedInfoModel.value;
    formValue.value = { ...(newValue.info), date: newValue.info.date.getTime() };
})

const rules: FormRules = {
    subject: { required: true, message: '请输入会议名', trigger: 'blur' },
    speaker: { required: true, message: '请输入演讲者', trigger: 'blur' },
    location: { required: true, message: '请输入会议地点' },
    isEnglish: { required: true, message: '请选择是否使用英语' }
}



async function confirm() {
    await formRef.value?.validate();
    parsedInfoModel.value.info = { ...formValue.value, date: new Date(formValue.value.date) };
    showModal.value = false;
}

const showModal = ref(false);


// watcheffect自动同步formValue的变化
parseEml(props.file.file);

</script>

<style lang="css" scoped>
.item-container {
    cursor: pointer;
    padding-top: 0.4rem;
    padding-bottom: 0.4rem;
    padding-left: 0.4rem;
    padding-right: 1.2rem;
}
</style>