<template>
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

<script setup lang="ts">
import { LogoGithub as GithubIcon } from '@vicons/ionicons5';
import { ButtonProps } from 'naive-ui';

type ButtonThemeOverrides = NonNullable<ButtonProps['themeOverrides']>;
const githubButtonThemeOverides: ButtonThemeOverrides = {
  textColorTextFocus: '#FCB040FF',
  textColorTextHover: '#FCB040FF'
};
</script>