import { defineConfig } from 'astro/config'
import mdx from '@astrojs/mdx'

// base 由 dm-pub-site skill 在实例化时从 git remote 推导并改写（如 '/my-repo'）。
// 项目站点（https://<user>.github.io/<repo>/）必须设置 base，否则资源路径 404。
export default defineConfig({
  site: 'https://example.github.io',
  base: '/CHANGE-ME',
  integrations: [mdx()],
})
