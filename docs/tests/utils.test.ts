import { describe, it, expect } from 'vitest'
import {
  validateNavItem,
  validateSidebarSection,
  extractFrontmatter,
  generateTOC,
  validateMarkdownLinks,
  countWords,
  MARKDOWN_FILES,
  AIDOCS_FILES
} from '../utils/docs'

describe('Documentation Utilities', () => {
  describe('validateNavItem', () => {
    it('should validate correct nav item', () => {
      const validItem = { text: 'Home', link: '/' }
      expect(validateNavItem(validItem)).toBe(true)
    })

    it('should reject invalid nav item', () => {
      expect(validateNavItem(null)).toBe(false)
      expect(validateNavItem({})).toBe(false)
    })
  })

  describe('validateSidebarSection', () => {
    it('should validate correct sidebar section', () => {
      const validSection = {
        text: 'Getting Started',
        items: [{ text: 'Overview', link: '/' }]
      }
      expect(validateSidebarSection(validSection)).toBe(true)
    })
  })

  describe('extractFrontmatter', () => {
    it('should extract frontmatter', () => {
      const content = `---
title: Test
---
Content`
      const result = extractFrontmatter(content)
      expect(result.frontmatter.title).toBe('Test')
      expect(result.body.trim()).toBe('Content')
    })
  })

  describe('generateTOC', () => {
    it('should generate table of contents', () => {
      const content = '# Title\n## Section'
      const toc = generateTOC(content)
      expect(toc).toHaveLength(2)
    })
  })

  describe('validateMarkdownLinks', () => {
    it('should validate good links', () => {
      const content = '[Good Link](https://example.com)'
      const links = validateMarkdownLinks(content)
      expect(links).toHaveLength(1)
      expect(links[0].valid).toBe(true)
    })
  })

  describe('countWords', () => {
    it('should count words correctly', () => {
      const content = 'Hello world test'
      const count = countWords(content)
      expect(count).toBe(3)
    })
  })

  describe('File Lists', () => {
    it('should have markdown files list', () => {
      expect(MARKDOWN_FILES).toBeDefined()
      expect(MARKDOWN_FILES.length).toBeGreaterThan(0)
    })

    it('should have aidocs files list', () => {
      expect(AIDOCS_FILES).toBeDefined()
      expect(AIDOCS_FILES.length).toBeGreaterThan(0)
    })
  })
})
