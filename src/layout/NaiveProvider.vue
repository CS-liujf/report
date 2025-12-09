<template>
  <n-config-provider
      :theme="theme"
      :theme-overrides="themeOverrides"
  >
    <n-loading-bar-provider>
      <n-message-provider>
        <n-dialog-provider>
          <n-notification-provider>
            <provider-content>
              <slot />
            </provider-content>
          </n-notification-provider>
        </n-dialog-provider>
      </n-message-provider>
    </n-loading-bar-provider>
  </n-config-provider>
</template>
<script lang="ts" setup>
import { GlobalThemeOverrides } from 'naive-ui'
import { theme } from '@/utils/switchMode'
import ProviderContent from './ProviderContent.vue'
const themeOverrides: GlobalThemeOverrides = {
  LoadingBar: {
    colorLoading: '#1a91ff'
  },
  Breadcrumb: {
    itemTextColorHover: '#1a91ff',
    itemTextColorPressed: '#1a91ff'
  }
}
</script>
<style scoped>
</style>
