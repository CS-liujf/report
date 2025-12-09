// AcademicReportTool.vue
<template>
  <naive-provider>
    <div class="container">
      <n-card title="学术报告记录生成工具" header-style="font-size:40px;" class="main-card" hoverable>
        <template #header-extra>
          <mode-switch size="35" />
        </template>
        <n-form label-placement="left" :rules="rules" ref="formRef">
          <!-- 学号输入 -->
          <n-form-item label="学号" path="studentId">
            <n-input v-model:value="formData.studentId" placeholder="请输入您的学号" />
          </n-form-item>

          <!-- 文件上传 -->
          <n-form-item label="上传EML文件" required>
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

        <!-- 代码显示区域 -->
        <template v-if="codeContent">
          <n-divider title="生成的代码" />
          <n-code language="javascript" :code="codeContent" word-wrap />
          <n-button type="success" size="small" class="copy-button" @click="copyToClipboard">
            复制代码
          </n-button>
        </template>
      </n-card>
    </div>
  </naive-provider>
</template>

<script setup lang="ts">
import { ArchiveOutline as ArchiveIcon } from '@vicons/ionicons5'
import NaiveProvider from '@/layout/NaiveProvider.vue';
import ModeSwitch from '@/components/ModeSwitch/ModeSwitch.vue';
import { computed, ref, useTemplateRef } from 'vue';
import { isDark } from './utils/switchMode';
import { FormInst, FormRules } from 'naive-ui';

// 定义类型接口(翻译原先的python脚本)
interface SeminarInfo {
  date: string;
  location: string;
  speaker: string;
  subject: string;
}

interface CalendarInfo {
  dateStr: string;
  location: string;
}

interface AcademicTerm {
  termStr: string;
  termCode: string;
}

interface SeminarInfoForm {
  WID: string;
  SHZT_DISPLAY: string;
  SHZT: string;
  TBLX: string;
  XH: string;
  FJ: string;
  XNXQ_DISPLAY: string;
  XNXQ: string;
  BGMC: string;
  BGSJ: string;
  BGDD: string;
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

// 文件上传相关
const fileList = ref<FileItem[]>([]);
const loading = ref<boolean>(false);
const codeContent = ref<string>('');

// 解析EML文件内容
const parseEml = (content: string): SeminarInfo => {
  const info: SeminarInfo = {
    date: '',
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
  info.date = calInfo.dateStr;
  info.location = calInfo.location;

  return info;
};

// 从日历中提取日期和地点
const extractDateAndLocationFromCalendar = (calendarStr: string): CalendarInfo => {
  const calInfo: CalendarInfo = {
    dateStr: '',
    location: '未指定地点'
  };

  if (!calendarStr) return calInfo;

  // 提取开始时间
  const dtStartMatch = calendarStr.match(/DTSTART.*?:(\d{4})(\d{2})(\d{2})/);
  if (dtStartMatch) {
    const [, year, month, day] = dtStartMatch;
    calInfo.dateStr = `${year}-${month}-${day}`;
  }

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
const getAcademicTerm = (dateStr: string): AcademicTerm => {
  try {
    const dt = new Date(dateStr);
    const year = dt.getFullYear();
    const month = dt.getMonth() + 1; // 月份从0开始

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
  } catch (e) {
    throw new Error(`日期格式错误，应为 YYYY-MM-DD: ${dateStr}`);
  }
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
        BGSJ: info.date,
        BGDD: info.location,
        ZJR: info.speaker,
        SFSYYY_DISPLAY: "是",
        SFSYYY: "1"
      };
    });

    // 生成JavaScript代码（基于index.js模板）
    const jsonStr = JSON.stringify(formList, null, 2);
    const jsCode = `// 发送 POST 请求
      try {
          // 用json中的数组替换该空数组
          const seminarInfoArr = ${jsonStr}
          const postRequest = async (seminarInfo) => {
              const paramJson = JSON.stringify(seminarInfo);
              const formData = new URLSearchParams();
              formData.append('paramJson', paramJson);
              await fetch('https://graduate.shanghaitech.edu.cn/gsapp/sys/jzxxtjapp/tbgdj/save.do', {
                  method: 'POST',
                  headers: {
                      'Content-Type': 'application/x-www-form-urlencoded'
                  },
                  body: formData
              })
          }
          const postReqArr = seminarInfoArr.map((seminarInfo) => postRequest(seminarInfo))
          Promise.all(postReqArr)
      } catch (e) {
          console.log(e)
      }`;

    codeContent.value = jsCode;
  } catch (e) {
    console.error('处理错误:', e);
  } finally {
    loading.value = false;
  }
};

// 复制到剪贴板
const copyToClipboard = () => {
  navigator.clipboard.writeText(codeContent.value)
    .then(() => {
      window.$message.success('代码已复制到剪贴板');
    })
    .catch(() => {
      window.$message.error('复制失败，请手动复制');
    });
};

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