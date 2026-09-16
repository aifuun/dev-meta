/**
 * 抽取 HTML 内容：
 * - 完整文档（含 <body>）→ 只取 body 内容，丢弃 <head>
 * - 片段（无 body）→ 原样返回
 */
export function extractBody(raw: string): string {
  const m = raw.match(/<body[^>]*>([\s\S]*?)<\/body>/i)
  return m ? m[1] : raw
}
