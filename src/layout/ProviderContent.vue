<template>
  <slot/>
</template>
<script lang="ts" setup>
import {useLoadingBar, useDialog, useMessage, useNotification} from 'naive-ui';
window.$loadingBar = useLoadingBar();
window.$dialog = useDialog();
window.$message = useMessage();
window.$notification = useNotification();
</script>
<style scoped>
</style>
