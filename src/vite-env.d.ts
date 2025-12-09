/// <reference types="vite/client" />

// ----------- 全局 window 扩展 -----------
import type {
  MessageProviderInst,
  DialogProviderInst,
  NotificationProviderInst,
  LoadingBarProviderInst
} from 'naive-ui'

declare global {
  interface Window {
    $message: MessageProviderInst
    $dialog: DialogProviderInst
    $notification: NotificationProviderInst
    $loadingBar: LoadingBarProviderInst
  }

  interface ImportMetaEnv {
    readonly VITE_APP_TITLE: string
    readonly VITE_APP_BASEURL: string

    // 其他字符串环境变量
    readonly [key: string]: string | boolean | number | Array<string>
  }
}

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

