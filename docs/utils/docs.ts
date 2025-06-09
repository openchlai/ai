export interface NavItem {
  text: string
  link: string
}

export interface SidebarSection {
  text: string
  items: NavItem[]
}

export interface DocsMetadata {
  title: string
  description: string
  lastUpdated?: string
}

export interface MarkdownFile {
  name: string
  path: string
  size: number
  exists: boolean
}

/**
 * List of all markdown files in the docs directory
 */
export const MARKDOWN_FILES = [
  'acknowledgements.md',
  'aipowered.md',
  'asterisk.md',
  'centos-install.md',
  'changelog.md',
  'contributing.md',
  'contribution.md',
  'documentation.md',
  'faq.md',
  'features.md',
  'guides.md',
  'index.md',
  'install.md',
  'license.md',
  'licenses.md',
  'mysql.md',
  'nginx.md',
  'php.md',
  'README.md',
  'roadmap.md',
  'support.md',
  'usage.md'
]

/**
 * Files in the aidocs directory (excluded from build)
 */
export const AIDOCS_FILES = [
  'architecture.md',
  'datapipeline.md',
  'deploymentguide.md',
  'governance.md',
  'projectcharter.md',
  'securityguide.md',
  'testingstrategy.md'
]

/**
 * Validates if a navigation item has required properties
 */
export function validateNavItem(item: any): item is NavItem {
  return (
    typeof item === 'object' &&
    item !== null &&
    typeof item.text === 'string' &&
    typeof item.link === 'string' &&
    item.text.length > 0 &&
    item.link.length > 0
  )
}

/**
 * Validates if a sidebar section has required structure
 */
export function validateSidebarSection(section: any): section is SidebarSection {
  return (
    typeof section === 'object' &&
    section !== null &&
    typeof section.text === 'string' &&
    Array.isArray(section.items) &&
    section.text.length > 0 &&
    section.items.every(validateNavItem)
  )
}

/**
 * Extracts frontmatter from markdown content
 */
export function extractFrontmatter(content: string): { frontmatter: Record<string, any>, body: string } {
  if (!content || !content.startsWith('---\n')) {
    return { frontmatter: {}, body: content || '' }
  }

  const endIndex = content.indexOf('\n---\n', 4)
  if (endIndex === -1) {
    return { frontmatter: {}, body: content }
  }

  const frontmatterString = content.slice(4, endIndex)
  const body = content.slice(endIndex + 5)

  try {
    // Simple YAML-like parsing for basic frontmatter
    const frontmatter: Record<string, any> = {}
    const lines = frontmatterString.split('\n')
    
    for (const line of lines) {
      const colonIndex = line.indexOf(':')
      if (colonIndex > 0) {
        const key = line.slice(0, colonIndex).trim()
        const value = line.slice(colonIndex + 1).trim()
        frontmatter[key] = value.replace(/^["']|["']$/g, '') // Remove quotes
      }
    }

    return { frontmatter, body }
  } catch {
    return { frontmatter: {}, body: content }
  }
}

/**
 * Generates table of contents from markdown content
 */
export function generateTOC(content: string): Array<{ level: number, text: string, anchor: string }> {
  const headingRegex = /^(#{1,6})\s+(.+)$/gm
  const toc: Array<{ level: number, text: string, anchor: string }> = []
  let match

  while ((match = headingRegex.exec(content)) !== null) {
    const level = match[1].length
    const text = match[2].trim()
    const anchor = text
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')

    toc.push({ level, text, anchor })
  }

  return toc
}

/**
 * Validates markdown link syntax
 */
export function validateMarkdownLinks(content: string): Array<{ valid: boolean, link: string, text: string }> {
  const linkRegex = /\[([^\]]*)\]\(([^)]+)\)/g
  const results: Array<{ valid: boolean, link: string, text: string }> = []
  let match

  while ((match = linkRegex.exec(content)) !== null) {
    const text = match[1] || ''
    const link = match[2] || ''
    
    const valid = !!(
      text.length > 0 &&
      link.length > 0 &&
      (link.startsWith('http') || link.startsWith('/') || link.startsWith('#') || link.startsWith('mailto:'))
    )

    results.push({ valid, link, text })
  }

  return results
}

/**
 * Counts words in markdown content (excluding frontmatter)
 */
export function countWords(content: string): number {
  const { body } = extractFrontmatter(content)
  
  if (!body) return 0
  
  // Remove markdown syntax and count words
  const plainText = body
    .replace(/```[\s\S]*?```/g, '') // Remove code blocks
    .replace(/`[^`]+`/g, '') // Remove inline code
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Convert links to text
    .replace(/[#*_~`]/g, '') // Remove markdown symbols
    .replace(/\s+/g, ' ') // Normalize whitespace
    .trim()

  return plainText ? plainText.split(' ').length : 0
}

/**
 * Checks if a markdown file exists in the expected files list
 */
export function isExpectedFile(filename: string): boolean {
  return MARKDOWN_FILES.includes(filename)
}

/**
 * Checks if a file is in the excluded aidocs directory
 */
export function isAidocsFile(filename: string): boolean {
  return AIDOCS_FILES.includes(filename)
}

/**
 * Validates file naming convention (relaxed for README.md)
 */
export function isValidFileName(filename: string): boolean {
  // Allow README.md as a special case
  if (filename === "README.md") return true

  // Allow README.md as a special case
  if (filename === 'README.md') return true
  
  // Should be lowercase with hyphens, end with .md
  return /^[a-z0-9-]+\.md$/.test(filename)
}

/**
 * Gets the expected link path for a markdown file
 */
export function getExpectedLinkPath(filename: string): string {
  if (filename === 'index.md') return '/'
  return '/' + filename.replace('.md', '')
}

/**
 * Validates that all navigation links point to existing files
 */
export function validateNavigationLinks(nav: NavItem[]): Array<{ link: string, hasFile: boolean }> {
  return nav.map(item => {
    const expectedFile = item.link === '/' ? 'index.md' : item.link.slice(1) + '.md'
    return {
      link: item.link,
      hasFile: MARKDOWN_FILES.includes(expectedFile)
    }
  })
}
// Coverage debugging - remove after testing
if (typeof global !== 'undefined' && global.process?.env?.NODE_ENV === 'test') {
  console.log('utils/docs.ts module loaded and executed')
}
