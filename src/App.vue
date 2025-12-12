// AcademicReportTool.vue
<template>
  <naive-provider>
    <div class="container">
      <n-card title="学术报告记录生成工具" header-style="font-size:42px;" footer-style="display: flex; justify-content: center;"
        class="main-card" hoverable>
        <template #header-extra>
          <mode-switch size="36" />
        </template>
        <n-form label-placement="left" :rules="rules" ref="formRef" :model="formData">
          <!-- 学号输入 -->
          <n-form-item label="学号" path="studentId" label-style="font-size: 1.1rem">
            <n-input v-model:value="formData.studentId" placeholder="请输入您的学号" />
          </n-form-item>

          <!-- 文件上传 -->
          <n-form-item label="解析EML文件" path="emlFiles" label-style="font-size: 1.1rem">
            <n-upload multiple v-model:file-list="formData.emlFiles" :custom-request="customRequest"
              @before-upload="beforeUpload">
              <n-upload-dragger>
                <div style="margin-bottom: 12px">
                  <n-icon size="48" :depth="3">
                    <ArchiveIcon />
                  </n-icon>
                </div>
                <n-text style="font-size: 1rem">
                  点击上传或拖放邮件文件到该区域解析
                </n-text>
                <n-p depth="3" style="margin: 4px 0 0 0; font-size: 0.9rem">
                  支持上传多个.eml格式的邮件文件
                </n-p>
              </n-upload-dragger>
            </n-upload>
          </n-form-item>

          <n-form-item label="是否提交" label-style="font-size: 1.1rem">
            <n-radio-group v-model:value="formData.reviewStatus">
              <n-radio value="0" size="large">
                <n-text style="font-size: 1rem">
                  仅存草稿
                </n-text>
              </n-radio>
              <n-radio value="10" size="large">
                <n-text style="font-size: 1rem">
                  提交导师审核
                </n-text>
              </n-radio>
            </n-radio-group>
          </n-form-item>

          <!-- 确定按钮 -->
          <n-form-item content-style="display: flex; justify-content: center;">
            <n-button type="info" @click="handleSubmit" :loading="loading" style="width: 60%;">
              生成
            </n-button>
          </n-form-item>
        </n-form>


        <n-divider />

        <!-- 代码显示区 -->
        <CodeCard :code="codeContent" :stale="false" />


        <template #footer>
          <Footer />
        </template>
      </n-card>
    </div>
  </naive-provider>
</template>

<script setup lang="ts">
import { ArchiveOutline as ArchiveIcon } from '@vicons/ionicons5'
import NaiveProvider from '@/layout/NaiveProvider.vue';
import ModeSwitch from '@/components/ModeSwitch/ModeSwitch.vue';
import CodeCard from '@/components/CodeCard/CodeCard.vue';
import Footer from '@/components/Footer/Footer.vue';
import { computed, onMounted, ref, useTemplateRef } from 'vue';
import { isDark } from './utils/switchMode';
import { FormRules, UploadFileInfo, FormValidationError, UploadCustomRequestOptions } from 'naive-ui';
import scriptTemplate from '@/scriptTemplate.js?raw';

import type { Attachment } from 'eml-parse-js'

//预热加载
onMounted(() => {
  import('ical.js');
  import("eml-parse-js");
});

// 定义类型接口(翻译原先的python脚本)
interface SeminarInfo {
  date: Date;
  location: string;
  speaker: string;
  subject: string;
}


interface AcademicTerm {
  termStr: string;
  termCode: string;
}

/**
 * 学术报告信息表单接口
 * @description 用于描述学术报告提交/展示的核心字段
 */
interface SeminarInfoForm {
  /** 唯一标识 ID */
  WID: string;
  /** 审核状态显示值 */
  SHZT_DISPLAY: string;
  /** 审核状态编码 (10表示提交给导师审核，0表示存草稿) */
  SHZT: '10' | '0';

  TBLX: string;

  /** 学号（学生唯一标识） */
  XH: string;
  /** 附件 */
  FJ: string;
  /** 学年学期显示值 */
  XNXQ_DISPLAY: string;
  /** 学年学期编码（如：202401） */
  XNXQ: string;
  /** 报告名称（学术报告的标题） */
  BGMC: string;
  /** 报告时间（格式：YYYY-MM-DD HH:mm:ss） */
  BGSJ: string;
  /** 报告地点 */
  BGDD: string;
  /** 主讲人名字 */
  ZJR: string;

  SFSYYY_DISPLAY: string;
  SFSYYY: string;
}

interface FormData {
  studentId: string;
  emlFiles: UploadFileInfo[];
  reviewStatus: '0' | '10';
}

const formRef = useTemplateRef('formRef');
// 表单数据
const formData = ref<FormData>({
  studentId: '',
  emlFiles: [],
  reviewStatus: '0',
});

async function beforeUpload(data: {
  file: UploadFileInfo
}) {
  if (!data.file.file?.name.toLowerCase().endsWith('.eml')) {
    return false;
  }
  return true;
}


const rules: FormRules = {
  studentId: {
    required: true,
    message: '请输入学号',
    trigger: ['input', 'blur']
  },
  emlFiles: {
    required: true,
    validator() {
      if (seminarInfoArr.value.length == 0) {
        return new Error('请上传邮件');
      }
      return true
    },
    trigger: ['input', 'blur']
  }
}

const validateForm = async () => {
  await formRef.value?.validate((errors: FormValidationError[] | undefined) => {
    if (errors) {
      window.$message.error(errors[0][0].message!);
    }
  })
}

const idSeminarInfoMap = new Map<string, SeminarInfo>();
const seminarInfoArr = computed(() => {
  return formData.value.emlFiles.filter(file => file.status === 'finished') // 筛选状态为finished的文件
    .map(file => {
      return idSeminarInfoMap.get(file.id)!; //使用!否则会返回undefined
    })
})

// 解析EML文件内容
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

  const info: SeminarInfo = {
    date: new Date(),
    location: '',
    speaker: '',
    subject: ''
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
  }

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
}


// 生成发送请求的代码
const loading = ref<boolean>(false);
const codeContent = ref<string>('');

// 获取学年学期信息
const getAcademicTerm = (date: Date): AcademicTerm => {
  const year = date.getFullYear();
  const month = date.getMonth();

  let termStr: string, termCode: string;

  if (month >= 9 || month < 2) {
    // 9月到来年1月：第一学期
    termStr = `${year}-${year + 1}学年 第一学期`;
    termCode = `${year * 10 + 1}`; // y1
  } else if (month === 7 || month === 8) {
    // 7月和8月：第三学期
    termStr = `${year - 1}-${year}学年 第三学期`;
    termCode = `${(year - 1) * 10 + 3}`; // (y-1)3
  } else {
    // 2月到6月：第二学期
    termStr = `${year - 1}-${year}学年 第二学期`;
    termCode = `${(year - 1) * 10 + 2}`; // (y-1)2
  }

  return { termStr, termCode };
};

const handleSubmit = async () => {
  try {
    await validateForm();
  } catch (e) {
    return;
  }

  loading.value = true;
  try {
    // 生成表单数据
    const formList: SeminarInfoForm[] = seminarInfoArr.value.map(info => {
      const academicTerm = getAcademicTerm(info.date);
      return {
        WID: "",
        SHZT_DISPLAY: "",
        SHZT: `${formData.value.reviewStatus}`,
        TBLX: "",
        XH: formData.value.studentId,
        FJ: "",
        XNXQ_DISPLAY: academicTerm.termStr,
        XNXQ: academicTerm.termCode,
        BGMC: info.subject,
        BGSJ: info.date.toISOString().slice(0, 10),
        BGDD: info.location,
        ZJR: info.speaker,
        SFSYYY_DISPLAY: "是",
        SFSYYY: "1"
      };
    });

    // 生成JavaScript代码（基于index.js模板）
    const formListJsonStr = JSON.stringify(formList, null, 2);
    // 核心：匹配 "const seminarInfoArr = [];" 整行，替换为带动态数据的代码
    const jsCode = scriptTemplate.replace(
      /const seminarInfoArr = \[\];/, // 正则匹配空数组占位行
      `const seminarInfoArr = ${formListJsonStr};` // 替换为动态数据
    );

    codeContent.value = jsCode;
  } catch (e) {
    console.error('处理错误:', e);
  } finally {
    loading.value = false;
  }
};


const backgroundColor = computed(() => (isDark.value ? '#101014' : '#f6f9f8'));
</script>

<style scoped>
.container {
  min-height: 100vh;
  box-sizing: border-box;
  background-color: v-bind(backgroundColor);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 6em;
  padding-bottom: 4em;
}

.main-card {
  max-width: 880px;
  padding: 0rem 1.5rem;
}
</style>