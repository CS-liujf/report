// AcademicReportTool.vue
<template>
  <naive-provider>
    <div class="container">
      <n-card title="学术报告记录生成工具" header-style="font-size:2.7rem;" footer-style="display: flex; justify-content: center;"
        class="main-card" hoverable>
        <template #header-extra>
          <mode-switch size="36" />
        </template>
        <n-form :label-placement="labelPlacement" :rules="rules" ref="formRef" :model="formData">
          <!-- 学号输入 -->
          <n-form-item label="学号" path="studentId" label-style="font-size: 1.1rem">
            <n-input v-model:value="formData.studentId" placeholder="请输入您的学号" />
          </n-form-item>

          <!-- 文件上传 -->
          <n-form-item label="解析EML文件" path="emlFiles" label-style="font-size: 1.1rem">
            <EmlFileParser @update:seminar-list="handleSeminarListChange" />
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
import NaiveProvider from '@/layout/NaiveProvider.vue';
import ModeSwitch from '@/components/ModeSwitch/ModeSwitch.vue';
import EmlFileParser, { type SeminarInfo } from '@/components/EmlFileParser/EmlFileParser.vue';
import CodeCard from '@/components/CodeCard/CodeCard.vue';
import Footer from '@/components/Footer/Footer.vue';
import { computed, ref, useTemplateRef } from 'vue';
import { isDark } from './utils/switchMode';
import { FormRules, FormValidationError } from 'naive-ui';
import scriptTemplate from '@/scriptTemplate.js?raw';
import { useWindowSize } from '@vueuse/core'


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

interface FormDataModel {
  studentId: string;
  seminarInfoArr: SeminarInfo[];
  reviewStatus: '0' | '10';
}

const formRef = useTemplateRef('formRef');
// 表单数据
const formData = ref<FormDataModel>({
  studentId: '',
  seminarInfoArr: [],
  reviewStatus: '0',
});

const rules: FormRules = {
  studentId: {
    required: true,
    message: '请输入学号',
    trigger: ['input', 'blur']
  },
  emlFiles: {
    required: true,
    validator() {
      if (formData.value.seminarInfoArr.length == 0) {
        return new Error('请上传邮件');
      }
      return true
    },
    // trigger: ['input', 'blur'] 必须注释，否则会议详情弹窗里的switch会触发此校验
  }
}

const validateForm = async () => {
  await formRef.value?.validate((errors: FormValidationError[] | undefined) => {
    if (errors) {
      window.$message.error(errors[0][0].message!);
    }
  })
}

// 接收解析的seminarInfo[]
const handleSeminarListChange = (list: SeminarInfo[]) => {
  formData.value.seminarInfoArr = list;
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
    const formList: SeminarInfoForm[] = formData.value.seminarInfoArr.map(info => {
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
        SFSYYY_DISPLAY: info.isEnglish ? "是" : "否",
        SFSYYY: info.isEnglish ? "1" : "0",
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

// 样式相关的设置
const backgroundColor = computed(() => (isDark.value ? '#101014' : '#f6f9f8'));
const { width } = useWindowSize();
const labelPlacement = computed(() => {
  return width.value >= 768 ? 'left' : 'top'
});
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
  max-width: 55rem;
  padding: 0rem 1.5rem;
}
</style>