import '@testing-library/jest-dom'

// Mock VitePress specific globals
global.VITEPRESS = true

// Mock process.env if needed
process.env.NODE_ENV = 'test'

// Setup any global test utilities here
export const mockMarkdownFile = (content: string, frontmatter: Record<string, any> = {}) => {
  return {
    frontmatter,
    content,
    excerpt: content.slice(0, 100)
  }
}