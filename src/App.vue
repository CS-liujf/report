// AcademicReportTool.vue
<template>
  <naive-provider>
    <div class="container">
      <n-card title="学术报告记录生成工具" header-style="font-size:42px;" footer-style="display: flex; justify-content: center;"
        class="main-card" hoverable>
        <template #header-extra>
          <mode-switch size="36" />
        </template>
        <n-form label-placement="left" :rules="rules" ref="formRef">
          <!-- 学号输入 -->
          <n-form-item label="学号" path="studentId">
            <n-input v-model:value="formData.studentId" placeholder="请输入您的学号" />
          </n-form-item>

          <!-- 文件上传 -->
          <n-form-item label="解析EML文件" required>
            <n-upload multiple directory-dnd>
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

          <!-- 确定按钮 -->
          <n-form-item content-style="display: flex; justify-content: center;">
            <n-button type="info" @click="handleSubmit" :loading="loading" style="width: 60%;">
              确定
            </n-button>
          </n-form-item>
        </n-form>


        <n-divider />

        <!-- 代码显示区域 -->
        <n-card title="生成的代码" header-style="font-size:28px">

          <!-- 复制按钮 -->
          <template #header-extra>
            <n-popover placement="bottom" trigger="click" ref="copyPopRef">
              <template #trigger>
                <n-button type="success" strong secondary size="small" @click="copyToClipboard"
                  :disabled="codeContent.length === 0">
                  <template #icon>
                    <n-icon>
                      <CopyIcon />
                    </n-icon>
                  </template>
                  复制
                </n-button>
              </template>

              <n-flex align="center" :size="4">
                <n-icon color="#36AD6AFF" size="1.2rem">
                  <SuccessIcon />
                </n-icon>
                <n-text style="font-size: 0.9rem">
                  代码已复制到剪贴板
                </n-text>
              </n-flex>
            </n-popover>
          </template>

          <template v-if="codeContent">
            <n-code code="
function sleep (ms = 1000) {
  return new Promise(resolve => setTimeout(resolve, ms))
}" language="javascript" show-line-numbers />
          </template>

          <template v-else>
            <n-empty description="先输入学号和上传邮件" size="huge" />
          </template>
        </n-card>


        <template #footer>
          <n-button text size="small" type="default" tag="a" href="https://github.com/CS-liujf/report" target="_blank"
            :theme-overrides="githubButtonThemeOverides">
            fly
            <template #icon>
              <NIcon>
                <GithubIcon />
              </NIcon>
            </template>
          </n-button>
        </template>
      </n-card>
    </div>
  </naive-provider>
</template>

<script setup lang="ts">
import { ArchiveOutline as ArchiveIcon, Copy as CopyIcon, LogoGithub as GithubIcon, CheckmarkCircle as SuccessIcon } from '@vicons/ionicons5'
import NaiveProvider from '@/layout/NaiveProvider.vue';
import ModeSwitch from '@/components/ModeSwitch/ModeSwitch.vue';
import { computed, ref, useTemplateRef } from 'vue';
import { isDark } from './utils/switchMode';
import { FormInst, FormRules, ButtonProps } from 'naive-ui';
import scriptTemplate from '@/scriptTemplate.js?raw';

type ButtonThemeOverrides = NonNullable<ButtonProps['themeOverrides']>
const githubButtonThemeOverides: ButtonThemeOverrides = {
  textColorTextFocus: '#FCB040FF',
  textColorTextHover: '#FCB040FF'
}


// 定义类型接口(翻译原先的python脚本)
interface SeminarInfo {
  date: Date;
  location: string;
  speaker: string;
  subject: string;
}

interface CalendarInfo {
  date: Date;
  location: string;
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
  /** 审核状态编码 */
  SHZT: string;

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
  emlFiles: File[];
}

interface FileItem {
  id: string;
  name: string;
  file: File;
}

const formRef = useTemplateRef('formRef')
// 表单数据
const formData = ref<FormData>({
  studentId: '',
  emlFiles: []
});


const rules: FormRules = {
  studentId: {
    required: true,
    message: '请输入学号',
    trigger: ['input', 'blur']
  }
}

const validateForm = async () => {
  await formRef.value?.validate((errors) => {
    if (errors) {
      window.$message.error(errors[0][0].message!);
    }
  })
}

// 处理文件上传前验证
const beforeUpload = (file: File) => {
  const isEml = file.name.toLowerCase().endsWith('.eml');
  if (!isEml) {
    window.$message.error('请上传.eml格式的文件');
    return false;
  }

  // 添加文件到列表
  fileList.value.push({
    id: Date.now().toString(),
    name: file.name,
    file: file
  });
  return false; // 阻止自动上传，我们只需要文件内容
};

// 移除文件
const handleRemove = (id: string) => {
  fileList.value = fileList.value.filter(item => item.id !== id);
};

// 文件上传相关
const fileList = ref<FileItem[]>([]);
const loading = ref<boolean>(false);
const codeContent = ref<string>('');

// 解析EML文件内容
const parseEml = (content: string): SeminarInfo => {
  const info: SeminarInfo = {
    date: new Date(),
    location: '',
    speaker: '',
    subject: ''
  };

  // 提取主题
  const subjectMatch = content.match(/Subject: (.*?)\r?\n/m);
  if (subjectMatch) {
    info.subject = subjectMatch[1].replace(/^\[[^\]]*\]\s*/, '');
  }

  // 提取邮件正文和日历信息
  let body = '';
  let calendarStr = '';
  const parts = content.split(/\r?\n--/);

  parts.forEach(part => {
    if (part.includes('Content-Type: text/calendar') || part.includes('Content-Type: application/ics')) {
      const calendarContent = part.split(/\r?\n\r?\n/)[1] || '';
      calendarStr = calendarContent.replace(/\r?\n--.*/s, '');
    } else if (part.includes('Content-Type: text/plain') && !part.includes('attachment')) {
      const textContent = part.split(/\r?\n\r?\n/)[1] || '';
      body = textContent.replace(/\r?\n--.*/s, '');
    }
  });

  // 提取演讲者
  const speakerMatch = body.match(/^(?:Speaker|演讲者):\s*(.+)$/im);
  if (speakerMatch) {
    info.speaker = speakerMatch[1].trim();
  }

  // 解析日历信息
  const calInfo = extractDateAndLocationFromCalendar(calendarStr);
  info.date = calInfo.date;
  info.location = calInfo.location;

  return info;
};

// 从日历中提取日期和地点
const extractDateAndLocationFromCalendar = (calendarStr: string): CalendarInfo => {
  const calInfo: CalendarInfo = {
    date: new Date(),
    location: '未指定地点'
  };

  if (!calendarStr) return calInfo;

  // 提取开始时间


  // 提取地点
  const locationMatch = calendarStr.match(/LOCATION.*?:(.*?)(?:\r?\n|$)/i);
  if (locationMatch) {
    calInfo.location = decodeURIComponent(
      locationMatch[1].replace(/=([0-9A-Fa-f]{2})/g, (_, hex) =>
        String.fromCharCode(parseInt(hex, 16))
      )
    );
  }

  return calInfo;
};

// 获取学年学期信息
const getAcademicTerm = (date: Date): AcademicTerm => {
  const year = date.getFullYear();
  const month = date.getMonth();

  let termStr: string, termCode: string;

  if (month >= 9 || month < 2) {
    // 9月到12月：第一学期
    termStr = `${year}-${year + 1}学年 第一学期`;
    termCode = (year * 10 + 1).toString();
  } else if (month === 7 || month === 8) {
    // 7月和8月：第三学期
    termStr = `${year - 1}-${year}学年 第三学期`;
    termCode = ((year - 1) * 10 + 3).toString();
  } else {
    // 2月到6月：第二学期
    termStr = `${year - 1}-${year}学年 第二学期`;
    termCode = ((year - 1) * 10 + 2).toString();
  }

  return { termStr, termCode };

};

// 读取文件内容
const readFileContent = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      if (typeof e.target?.result === 'string') {
        resolve(e.target.result);
      } else {
        reject(new Error('无法读取文件内容'));
      }
    };
    reader.onerror = () => reject(new Error('文件读取失败'));
    reader.readAsText(file);
  });
};

// 处理表单提交
const handleSubmit = async () => {
  loading.value = true;
  try {
    await validateForm();
    codeContent.value = '';
    // 解析所有上传的eml文件
    const infoList: SeminarInfo[] = [];
    for (const fileItem of fileList.value) {
      const content = await readFileContent(fileItem.file);
      const seminarInfo = parseEml(content);
      infoList.push(seminarInfo);
    }

    // 生成表单数据
    const formList: SeminarInfoForm[] = infoList.map(info => {
      const academicTerm = getAcademicTerm(info.date);
      return {
        WID: "",
        SHZT_DISPLAY: "",
        SHZT: "0",
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


const copyPopRef = useTemplateRef('copyPopRef')
// 复制到剪贴板
const copyToClipboard = () => {
  navigator.clipboard.writeText(codeContent.value)
    .then(() => {

    })
    .catch(() => {

    }).finally(() => {
      setTimeout(() => copyPopRef.value?.setShow(false), 3000);
    });
};


const backgroundColor = computed(() => (isDark.value ? '#101014' : '#f6f9f8'));
</script>

<style scoped>
.container {
  min-height: 100vh;
  background-color: v-bind(backgroundColor);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.main-card {
  max-width: 800px;
  padding: 1.5rem;
  margin-top: 6rem;
}

.copy-button {
  margin-top: 1rem;
}

.error-message {
  margin-top: 1rem;
}
</style>