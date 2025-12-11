import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import Components from 'unplugin-vue-components/vite'
import { NaiveUiResolver } from 'unplugin-vue-components/resolvers'
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'
import { createHtmlPlugin } from 'vite-plugin-html'
import { visualizer } from 'rollup-plugin-visualizer'
import path from 'node:path'

//启用tsx
import vueJsx from '@vitejs/plugin-vue-jsx';

// 路径工具
const pathResolve = (dir: string) => path.resolve(process.cwd(), dir)

// Vite 5 推荐显式传入 mode（config 中可直接使用 env）
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [
      vue(),
      vueJsx(),

      // 自动按需引入naiveui组件
      Components({
        dts: 'src/components.d.ts',
        resolvers: [NaiveUiResolver()]
      }),

      // SVG 图标
      createSvgIconsPlugin({
        iconDirs: [pathResolve('src/assets/icons')],
        symbolId: 'icon-[name]'
      }),

      // 注入 index.html里的title
      createHtmlPlugin({
        inject: {
          data: {
            title: env.VITE_APP_TITLE
          }
        }
      }),

      // 包体积分析
      visualizer({
        filename: 'dist/analysis.html',
        open: false,
        gzipSize: true,
        brotliSize: true
      })
    ],

    resolve: {
      alias: {
        '@': pathResolve('src')
      }
    },

    server: {
      open: true
      // proxy: { ... }
    },

    // 相对路径部署
    base: '/report/',
  }
})
