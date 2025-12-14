<template>
  <n-upload multiple v-model:file-list="fileList" :custom-request="customRequest" @before-upload="beforeUpload">
    <n-upload-dragger>
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
    </n-upload-dragger>
  </n-upload>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { UploadFileInfo, UploadCustomRequestOptions } from 'naive-ui';
import type { Attachment } from 'eml-parse-js';
import { ArchiveOutline as ArchiveIcon } from '@vicons/ionicons5';

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

/* ===== 状态 ===== */
const fileList = ref<UploadFileInfo[]>([]);
const idSeminarInfoMap = new Map<string, SeminarInfo>();

/* ===== 计算结果 ===== */
const seminarInfoArr = computed(() =>
  fileList.value
    .filter(f => f.status === 'finished')
    .map(f => idSeminarInfoMap.get(f.id)!)
);

/* ===== emits 定义 ===== */
const emit = defineEmits<{
  (e: 'update:seminar-list', value: SeminarInfo[]): void
}>();
/* 向父组件推送 */
watch(
  seminarInfoArr,
  (val) => {
    emit('update:seminar-list', val);
  },
  { immediate: true }
);

/* ===== 校验 ===== */
const beforeUpload = (data: { file: UploadFileInfo }) =>
  data.file.file?.name.toLowerCase().endsWith('.eml') ?? false;

const parseEml = async (emlFile: File): Promise<SeminarInfo> => {
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
        return m[1].trim();
      }
    }

    return null;
  }

  function hasChinese(str: string): boolean {
    // 正则匹配基本中文字符
    const chineseReg = /[\u4e00-\u9fa5]/;
    return chineseReg.test(str);
  }

  const info: SeminarInfo = {
    date: new Date(),
    location: '',
    speaker: '',
    subject: '',
    isEnglish: true
  };

  const { readEml } = await import('eml-parse-js');
  const { default: ICAL } = await import('ical.js');

  // 解析日历，提取主题、时间和地点
  const text = await emlFile.text();
  readEml(text, (err, data) => {
    if (!err && data && data.text && data.attachments) {
      // 从正文提取演讲者
      const speaker = extractSpeaker(data.text);
      if (speaker) {
        info.speaker = speaker;
      } else {
        throw Error('邮件解析失败');
      }

      const calendarPart = data.attachments.find(
        (att: Attachment) => att.contentType.startsWith("text/calendar")
      );

      if (calendarPart) {
        const icsText = calendarPart.data as string;
        // 用 ical.js 解析 icsText
        const jcal = ICAL.parse(icsText);
        const component = new ICAL.Component(jcal);
        const event = new ICAL.Event(component.getFirstSubcomponent('vevent')!);

        info.subject = event.summary;
        info.location = event.location;
        info.date = event.startDate.toJSDate();
        info.isEnglish = !hasChinese(info.subject);

        // console.log("演讲会名字", event.summary);
        // console.log("开始时间", event.startDate.toJSDate());
        // console.log("结束时间", event.endDate.toJSDate());
      } else {
        throw Error('邮件解析失败');
      }
    } else {
      throw Error('邮件解析失败');
    }
  });
  return info;
};

const customRequest = (uploadFileOpts: UploadCustomRequestOptions) => {
  const getRandomInt = (min: number, max: number): number => {
    // 处理边界：确保 min <= max
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
  };

  const {
    onError, onFinish, onProgress,
    file: fileInfo,
  } = uploadFileOpts;

  const delay = getRandomInt(180, 500);
  //使用延迟，避免文件列表显示卡住
  setTimeout(async () => {
    onProgress({ percent: getRandomInt(10, 80) });
    try {
      const seminarInfo = await parseEml(fileInfo.file!);
      idSeminarInfoMap.set(fileInfo.id, seminarInfo);
      onFinish();
    } catch {
      onError();
    }
  }, delay);
};
</script>