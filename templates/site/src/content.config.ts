import { defineCollection, z } from 'astro:content'
import { glob } from 'astro/loaders'

// 内容根 = ./content（模板实例化后的 site/content）。
// md / mdx 走内容集合；html 由页面侧 import.meta.glob 读取（见 src/pages）。
const docs = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './content' }),
  schema: z.object({
    title: z.string().optional(),
    description: z.string().optional(),
  }),
})

export const collections = { docs }
