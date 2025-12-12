<template>
  <!-- 代码显示区域 -->
  <n-card>
    <!-- 手动创建header -->
    <n-flex justify="space-between" align="center" style="padding-bottom: 20px;">
      <n-badge value="已过期" color="grey" :offset="[24, 8]" :show="stale">
        <div class="card-header">生成的代码</div>
      </n-badge>

      <n-popover placement="bottom" trigger="manual" ref="copyPopRef">
        <template #trigger>
          <n-button type="success" strong secondary size="small" @click="copyToClipboard"
            :disabled="code.length === 0">
            <template #icon>
              <n-icon>
                <CopyIcon />
              </n-icon>
            </template>
            复制
          </n-button>
        </template>

        <!-- 成功复制的提示 -->
        <template v-if="copySuccess">
          <n-flex align="center" :size="4">
            <n-icon color="#36AD6AFF" size="1.2rem">
              <SuccessIcon />
            </n-icon>
            <n-text style="font-size: 0.9rem">
              代码已复制到剪贴板，
              <n-button text tag="a"
                href="https://graduate.shanghaitech.edu.cn/gsapp/sys/yjsemaphome/portal/index.do"
                target="_blank" referrerpolicy="no-referrer" type="warning">
                立刻去用
              </n-button>
              <!-- 一定要设置为no-referrer，否则无法正常跳转 -->
            </n-text>
          </n-flex>
        </template>

        <!-- 复制失败的提示 -->
        <template v-else>
          <n-flex align="center" :size="4">
            <n-icon color="#DE576DFF" size="1.2rem">
              <AlertIcon />
            </n-icon>
            <n-text style="font-size: 0.9rem">
              复制失败，请手动复制
            </n-text>
          </n-flex>
        </template>
      </n-popover>
    </n-flex>

    <!-- 代码显示 -->
    <template v-if="props.code">
      <n-code :code="props.code" language="javascript" show-line-numbers word-wrap />
    </template>

    <template v-else>
      <n-empty description="先输入学号和上传邮件" size="huge" />
    </template>
  </n-card>
</template>

<script setup lang="ts">
import { Copy as CopyIcon, CheckmarkCircle as SuccessIcon, AlertCircle as AlertIcon } from '@vicons/ionicons5'
import { ref, useTemplateRef } from 'vue';

interface Props {
  code: string,
  stale: boolean
}

const props = defineProps<Props>();

const copyPopRef = useTemplateRef('copyPopRef')
const copySuccess = ref(true);
// 复制到剪贴板
const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(props.code);
    copySuccess.value = true;
  } catch (e) {
    copySuccess.value = false;
  }
  finally {
    copyPopRef.value?.setShow(true);
    setTimeout(() => copyPopRef.value?.setShow(false), 3000);
  };
};
</script>
<style lang="css" scoped>
.card-header {
  font-size: 28px;
  font-weight: var(--n-title-font-weight);
  transition: color .3s var(--n-bezier);
  flex: 1;
  min-width: 0;
  color: var(--n-title-text-color);
}
</style>