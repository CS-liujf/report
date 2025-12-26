<template>
    <n-flex :wrap="false" vertical justify="center" class="item-container" @click="showModal = true">
        <n-flex :wrap="false" justify="space-between" align="center">
            <n-flex :wrap="false" align="center" :size="[6, 0]">
                <n-icon size="1.2rem" :class="{ 'errorFile': parsedInfoModel.status === 'failed' }">
                    <MailIcon />
                </n-icon>
                <n-text style="font-size: 0.9rem;"
                    :style="{ color: showColor, transition: 'color 0.1s cubic-bezier(.4, 0, .2, 1)' }">
                    {{ props.file.file.name }}
                </n-text>
            </n-flex>

            <!-- 操作按钮 -->
            <template v-if="parsedInfoModel.status === 'failed'">
                <n-flex justify="center" align="center">
                    <n-icon class="close" size="1.6rem">
                        <CloseOutIcon @click.prevent="handleDelete" />
                    </n-icon>
                    <n-icon class="reload" size="1.2rem">
                        <RefreshIcon @click.prevent.stop="reParseEml" />
                    </n-icon>
                </n-flex>
            </template>
            <template v-else>
                <n-icon size="1.2rem" class="trashBin">
                    <TrashBinIcon @click.prevent="handleDelete" />
                </n-icon>
            </template>
        </n-flex>

        <!-- 进度条 -->
        <n-progress v-if="parsedInfoModel.status === 'parsing'" type="line" processing :percentage="percentage"
            :show-indicator="false" color="skyblue" :height='4' style="margin-top: -6px;">
        </n-progress>
    </n-flex>

    <!-- 详情弹窗 -->
    <n-modal v-model:show="showModal" preset="card" title="详情" :bordered="false" size="medium" style="max-width: 30rem"
        draggable>
        <n-form ref="formRef" :model="formValue" :rules="rules" label-placement="left" :label-width="80">
            <n-form-item label="会议名" path="subject">
                <n-input v-model:value="formValue.subject" placeholder="输入会议名" type="textarea"
                    :autosize="{ minRows: 1 }" />
            </n-form-item>

            <n-form-item label="演讲者" path="speaker">
                <n-input v-model:value="formValue.speaker" placeholder="输入演讲者名字" />
            </n-form-item>

            <n-form-item label="时间" path="date" required>
                <n-date-picker style="width: 100%;" v-model:value="formValue.date" type="date" placeholder="请选择会议时间" />
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
    </n-modal>
</template>

<script setup lang="ts">
import { MailOutline as MailIcon, TrashBinOutline as TrashBinIcon, CloseOutline as CloseOutIcon, Refresh as RefreshIcon } from '@vicons/ionicons5';
import { type UploadedFile } from "../EmlUpload/EmlUpload.vue";
import type { Attachment, ReadedEmlJson } from 'eml-parse-js';
import { useTemplateRef, ref, watchEffect, computed, onMounted } from 'vue';
import { FormRules } from 'naive-ui';
import { isDark } from '@/utils/switchMode';
import { useThemeVars } from 'naive-ui';

// Props and Emits
interface Props {
    file: UploadedFile;
}
const props = defineProps<Props>();

interface Emits {
    (e: 'delete', id: string): void
}
const emit = defineEmits<Emits>();

// Types
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

// Refs
const formRef = useTemplateRef('formRef');
const showModal = ref(false);
const showColor = ref('');
const percentage = ref(0);

// Form
const formValue = ref({
    speaker: '',
    location: '',
    date: Date.now(),
    subject: '',
    isEnglish: true
});

const rules: FormRules = {
    subject: { required: true, message: '请输入会议名', trigger: 'blur' },
    speaker: { required: true, message: '请输入演讲者', trigger: 'blur' },
    location: { required: true, message: '请输入会议地点' },
    isEnglish: { required: true, message: '请选择是否使用英语' }
};

// Computed
const themeVars = useThemeVars();
const fileColor = computed(() => (isDark.value ? '#e88080' : '#d03050'));
const listColor = computed(() => {
    if (parsedInfoModel.value.status === 'failed') {
        return isDark.value ? '#2e2c2c' : '#faeded';
    } else {
        return isDark.value ? 'rgba(255, 255, 255, 0.09)' : 'rgb(243, 243, 245)';
    }
});
const trashBinColor = computed(() => (isDark.value ? 'rgba(255, 255, 255, .12)' : 'rgba(194, 194, 194, 1)'));
const isParsing = computed(() => parsedInfoModel.value.status === 'parsing');

// Helper functions
const getRandomInt = (min: number, max: number): number => {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
};

const resetColors = () => {
    showColor.value = '';
};

const updateFormValue = () => {
    const { info } = parsedInfoModel.value;
    formValue.value = { ...info, date: info.date.getTime() };
};

const handleDelete = () => {
    emit('delete', props.file.id);
};


const parseEml = async (emlFile: File): Promise<void> => {
    // EML Parsing Logic
    const parseEmlContent = async (text: string): Promise<ReadedEmlJson> => {
        const { readEml } = await import('eml-parse-js');
        return new Promise((resolve, reject) => {
            readEml(text, (err, data) => {
                if (err) {
                    reject(err instanceof Error ? err : new Error(String(err)));
                } else {
                    resolve(data!);
                }
            });
        });
    };

    const extractSpeaker = (text: string): string | null => {
        if (!text) return null;
        const regexList = [
            /speaker\s*[:：]\s*(.+)/i,
            /演讲者\s*[:：]\s*(.+)/i
        ];
        for (const r of regexList) {
            const m = text.match(r);
            if (m && m[1]) {
                return m[1].trim().replace(/[。．\.；;，,]+$/, '');
            }
        }
        return null;
    };

    const extractLocation = (text: string): string | null => {
        if (!text) return null;
        const regexList = [
            /location\s*[:：]\s*(.+)/i,
            /地点\s*[:：]\s*(.+)/i,
        ];
        for (const r of regexList) {
            const m = text.match(r);
            if (m?.[1]) {
                return m[1].trim().replace(/[。．\.；;，,]+$/, '');
            }
        }
        return null;
    };

    const getCalendarAttachment = (attachments?: Attachment[]): Attachment | null => {
        if (!attachments?.length) return null;
        return attachments.find(att => att.contentType?.startsWith('text/calendar')) ?? null;
    };

    const hasChinese = (str: string): boolean => {
        const chineseReg = /[\u4e00-\u9fa5]/;
        return chineseReg.test(str);
    };

    const parseByContent = (emlFile: ReadedEmlJson, info: SeminarInfo) => {
        info.date = emlFile.date instanceof Date ? emlFile.date : new Date(emlFile.date);
        info.subject = emlFile.subject;
        const location = extractLocation(emlFile.text!);
        info.location = location || '';
    };

    const parseByAttachment = async (calendarAttachment: Attachment, info: SeminarInfo) => {
        const { default: ICAL } = await import('ical.js');
        const icsText = calendarAttachment.data as string;
        const jcal = ICAL.parse(icsText);
        const component = new ICAL.Component(jcal);
        const event = new ICAL.Event(component.getFirstSubcomponent('vevent')!);

        info.subject = event.summary;
        info.location = event.location;
        info.date = event.startDate.toJSDate();
    };

    const info: SeminarInfo = {
        date: new Date(),
        location: '',
        speaker: '',
        subject: '',
        isEnglish: true
    };

    try {
        const text = await emlFile.text();
        const data = await parseEmlContent(text);

        if (!data?.text) {
            throw new Error('邮件解析失败：正文缺失');
        }

        const speaker = extractSpeaker(data.text);
        if (!speaker) {
            throw new Error('邮件解析失败：未找到演讲者');
        }
        info.speaker = speaker;

        const calendarAttachment = getCalendarAttachment(data.attachments);
        if (calendarAttachment) {
            await parseByAttachment(calendarAttachment, info);
        } else {
            parseByContent(data, info);
        }

        info.isEnglish = !hasChinese(info.subject);

        parsedInfoModel.value.status = 'successful';
        parsedInfoModel.value.info = info;
    } catch (error) {
        console.error('EML解析失败:', error);
        parsedInfoModel.value.status = 'failed';
        throw error; // Re-throw to be caught by caller
    }
};

const reParseEml = async () => {
    if (isParsing.value) return; // Prevent concurrent parsing
    await startParsing();
};

const startParsing = async () => {
    parsedInfoModel.value.status = 'parsing';
    percentage.value = getRandomInt(10, 80);
    const delay = getRandomInt(180, 500);
    //使用延迟，避免文件列表显示卡住
    setTimeout(() => { }, delay);
    try {
        await parseEml(props.file.file);
        percentage.value = 100;
        showColor.value = themeVars.value.successColorHover;
        setTimeout(resetColors, 2000);
    } catch (err) {
        percentage.value = 0;
        showColor.value = themeVars.value.errorColor;
    }
};

// Form Actions
const confirm = async () => {
    await formRef.value?.validate();
    parsedInfoModel.value.info = { ...formValue.value, date: new Date(formValue.value.date) };
    showModal.value = false;
};

// Watchers & Lifecycle
watchEffect(() => {
    updateFormValue();
});

onMounted(() => {
    // Trigger initial parsing only if status is pending
    if (parsedInfoModel.value.status === 'pending') {
        startParsing();
    }
});
</script>

<style lang="css" scoped>
.item-container {
    cursor: pointer;
    padding-top: 0.4rem;
    padding-bottom: 0.4rem;
    padding-left: 0.4rem;
    padding-right: 1.2rem;
    border-radius: 3px;
}

.item-container .trashBin {
    padding: 3px 3px;
    border-radius: 3px;
}

.item-container .close {
    padding: 2px 2px;
    border-radius: 3px;
    color: v-bind(fileColor);
}

.item-container .reload {
    padding: 4px 4px;
    border-radius: 3px;
    color: v-bind(fileColor);
}

.item-container:hover {
    background-color: v-bind(listColor);
}

.item-container .trashBin:hover {
    background-color: v-bind(trashBinColor);
}

.item-container .close:hover {
    background-color: v-bind(trashBinColor);
}

.item-container .reload:hover {
    background-color: v-bind(trashBinColor);
}

.errorFile {
    color: v-bind(showColor);
}
</style>