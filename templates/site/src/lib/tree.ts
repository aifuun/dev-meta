export type Leaf = { slug: string; title: string; href: string }

export type TreeNode = {
  name: string
  path: string
  title?: string
  href?: string
  children: TreeNode[]
}

/**
 * 把扁平 slug 列表按 `/` 还原为目录树。
 * 有子节点者为目录，无子节点者为叶子（可点击）。
 */
export function buildTree(items: Leaf[]): TreeNode[] {
  const root: TreeNode = { name: '', path: '', children: [] }

  for (const item of items) {
    const parts = item.slug.split('/').filter(Boolean)
    let cur = root
    parts.forEach((part, i) => {
      const path = parts.slice(0, i + 1).join('/')
      let next = cur.children.find((c) => c.name === part)
      if (!next) {
        next = { name: part, path, children: [] }
        cur.children.push(next)
      }
      if (i === parts.length - 1) {
        next.title = item.title
        next.href = item.href
      }
      cur = next
    })
  }

  sortRec(root)
  return root.children
}

/** 目录在前、文件在后，同级按名称排序 */
function sortRec(node: TreeNode) {
  node.children.sort((a, b) => {
    const aDir = a.children.length > 0
    const bDir = b.children.length > 0
    if (aDir !== bDir) return aDir ? -1 : 1
    return a.name.localeCompare(b.name)
  })
  node.children.forEach(sortRec)
}
