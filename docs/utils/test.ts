import { describe, it, expect } from 'vitest'
import {
  validateNavItem,
  validateSidebarSection,
  extractFrontmatter,
  generateTOC,
  validateMarkdownLinks,
  countWords,
  isExpectedFile,
  isAidocsFile,
  isValidFileName,
  getExpectedLinkPath,
  validateNavigationLinks,
  MARKDOWN_FILES,
  AIDOCS_FILES
} from './docs'

describe('Documentation Utilities', () => {
  describe('validateNavItem', () => {
    it('should validate correct nav item', () => {
      const validItem = { text: 'Home', link: '/' }
      expect(validateNavItem(validItem)).toBe(true)
    })

    it('should reject nav item without text', () => {
      const invalidItem = { link: '/' }
      expect(validateNavItem(invalidItem)).toBe(false)
    })

    it('should reject nav item without link', () => {
      const invalidItem = { text: 'Home' }
      expect(validateNavItem(invalidItem)).toBe(false)
    })

    it('should reject nav item with empty text', () => {
      const invalidItem = { text: '', link: '/' }
      expect(validateNavItem(invalidItem)).toBe(false)
    })

    it('should reject nav item with empty link', () => {
      const invalidItem = { text: 'Home', link: '' }
      expect(validateNavItem(invalidItem)).toBe(false)
    })

    it('should reject non-object input', () => {
      expect(validateNavItem('invalid')).toBe(false)
      expect(validateNavItem(null)).toBe(false)
      expect(validateNavItem(undefined)).toBe(false)
    })
  })

  describe('validateSidebarSection', () => {
    it('should validate correct sidebar section', () => {
      const validSection = {
        text: 'Getting Started',
        items: [
          { text: 'Overview', link: '/' },
          { text: 'Installation', link: '/install' }
        ]
      }
      expect(validateSidebarSection(validSection)).toBe(true)
    })

    it('should reject section without text', () => {
      const invalidSection = {
        items: [{ text: 'Overview', link: '/' }]
      }
      expect(validateSidebarSection(invalidSection)).toBe(false)
    })

    it('should reject section without items', () => {
      const invalidSection = {
        text: 'Getting Started'
      }
      expect(validateSidebarSection(invalidSection)).toBe(false)
    })

    it('should reject section with invalid items', () => {
      const invalidSection = {
        text: 'Getting Started',
        items: [
          { text: 'Overview', link: '/' },
          { text: '', link: '/invalid' } // Invalid item
        ]
      }
      expect(validateSidebarSection(invalidSection)).toBe(false)
    })

    it('should reject section with empty text', () => {
      const invalidSection = {
        text: '',
        items: [{ text: 'Overview', link: '/' }]
      }
      expect(validateSidebarSection(invalidSection)).toBe(false)
    })
  })

  describe('extractFrontmatter', () => {
    it('should extract frontmatter from markdown', () => {
      const content = `---
title: Test Page
description: A test page
---

# Hello World

This is content.`

      const result = extractFrontmatter(content)
      
      expect(result.frontmatter.title).toBe('Test Page')
      expect(result.frontmatter.description).toBe('A test page')
      expect(result.body).toBe('\n# Hello World\n\nThis is content.')
    })

    it('should handle content without frontmatter', () => {
      const content = '# Hello World\n\nThis is content.'
      const result = extractFrontmatter(content)
      
      expect(result.frontmatter).toEqual({})
      expect(result.body).toBe(content)
    })

    it('should handle malformed frontmatter', () => {
      const content = `---
invalid yaml content
---

# Hello World`

      const result = extractFrontmatter(content)
      expect(result.frontmatter).toEqual({})
      expect(result.body).toBe(content)
    })

    it('should handle frontmatter with quotes', () => {
      const content = `---
title: "Quoted Title"
description: 'Single Quoted'
---

Content here`

      const result = extractFrontmatter(content)
      expect(result.frontmatter.title).toBe('Quoted Title')
      expect(result.frontmatter.description).toBe('Single Quoted')
    })

    it('should handle empty or null content', () => {
      expect(extractFrontmatter('')).toEqual({ frontmatter: {}, body: '' })
      expect(extractFrontmatter('   ')).toEqual({ frontmatter: {}, body: '   ' })
    })
  })

  describe('generateTOC', () => {
    it('should generate table of contents from headings', () => {
      const content = `# Main Title

## Section 1

### Subsection 1.1

## Section 2

# Another Main Title`

      const toc = generateTOC(content)
      
      expect(toc).toHaveLength(5)
      expect(toc[0]).toEqual({ level: 1, text: 'Main Title', anchor: 'main-title' })
      expect(toc[1]).toEqual({ level: 2, text: 'Section 1', anchor: 'section-1' })
      expect(toc[2]).toEqual({ level: 3, text: 'Subsection 1.1', anchor: 'subsection-11' })
    })

    it('should handle content without headings', () => {
      const content = 'This is just regular text without any headings.'
      const toc = generateTOC(content)
      
      expect(toc).toHaveLength(0)
    })

    it('should sanitize anchor names', () => {
      const content = '# Special Characters! @#$%'
      const toc = generateTOC(content)
      
      expect(toc[0].anchor).toBe('special-characters')
    })

    it('should handle various heading levels', () => {
      const content = `# H1
## H2
### H3
#### H4
##### H5
###### H6`

      const toc = generateTOC(content)
      
      expect(toc).toHaveLength(6)
      expect(toc.map(t => t.level)).toEqual([1, 2, 3, 4, 5, 6])
    })
  })

  describe('validateMarkdownLinks', () => {
    it('should validate correct markdown links', () => {
      const content = `
[Valid Link](https://example.com)
[Internal Link](/page)
[Anchor Link](#section)
[Email Link](mailto:test@example.com)
`

      const results = validateMarkdownLinks(content)
      
      expect(results).toHaveLength(4)
      results.forEach(result => {
        expect(result.valid).toBe(true)
      })
    })

    it('should identify invalid links', () => {
      const content = `
[Empty Link]()
[](https://example.com)
[Invalid Link](invalid-url)
`

      const results = validateMarkdownLinks(content)
      
      expect(results).toHaveLength(3)
      expect(results[0].valid).toBe(false) // Empty link
      expect(results[1].valid).toBe(false) // Empty text
      expect(results[2].valid).toBe(false) // Invalid URL format
    })

    it('should handle content without links', () => {
      const content = 'This content has no links at all.'
      const results = validateMarkdownLinks(content)
      
      expect(results).toHaveLength(0)
    })

    it('should handle relative links', () => {
      const content = '[Relative Link](./relative-page)'
      const results = validateMarkdownLinks(content)
      
      expect(results).toHaveLength(1)
      expect(results[0].valid).toBe(false) // Our validator requires /, #, http, or mailto
    })
  })

  describe('countWords', () => {
    it('should count words in plain text', () => {
      const content = 'This is a simple test with seven words.'
      const count = countWords(content)
      
      expect(count).toBe(9)
    })

    it('should exclude frontmatter from word count', () => {
      const content = `---
title: Test Page
description: A test page
---

This is the actual content with six words.`

      const count = countWords(content)
      expect(count).toBe(9)
    })

    it('should handle markdown syntax', () => {
      const content = `
# Heading

This is **bold** text and *italic* text.
Here is a [link](https://example.com) and \`inline code\`.

\`\`\`
This code block should be ignored
\`\`\`

More content here.
`

      const count = countWords(content)
      // Should count: "This is bold text and italic text Here is a link and inline code More content here"
      expect(count).toBeGreaterThan(10)
    })

    it('should handle empty content', () => {
      const count = countWords('')
      expect(count).toBe(0)
    })

    it('should handle content with only frontmatter', () => {
      const content = `---
title: Test Page
description: A test page
---`

      const count = countWords(content)
      expect(count).toBe(0)
    })

    it('should normalize whitespace', () => {
      const content = 'Word1    Word2\n\nWord3\t\tWord4'
      const count = countWords(content)
      expect(count).toBe(4)
    })
  })

  describe('File Classification Functions', () => {
    describe('isExpectedFile', () => {
      it('should identify expected markdown files', () => {
        expect(isExpectedFile('index.md')).toBe(true)
        expect(isExpectedFile('install.md')).toBe(true)
        expect(isExpectedFile('features.md')).toBe(true)
      })

      it('should reject non-expected files', () => {
        expect(isExpectedFile('random-file.md')).toBe(false)
        expect(isExpectedFile('not-in-list.md')).toBe(false)
      })
    })

    describe('isAidocsFile', () => {
      it('should identify aidocs files', () => {
        expect(isAidocsFile('architecture.md')).toBe(true)
        expect(isAidocsFile('securityguide.md')).toBe(true)
        expect(isAidocsFile('testingstrategy.md')).toBe(true)
      })

      it('should reject non-aidocs files', () => {
        expect(isAidocsFile('index.md')).toBe(false)
        expect(isAidocsFile('install.md')).toBe(false)
      })
    })

    describe('isValidFileName', () => {
      it('should validate correct filenames', () => {
        expect(isValidFileName('index.md')).toBe(true)
        expect(isValidFileName('install-guide.md')).toBe(true)
        expect(isValidFileName('some-file-123.md')).toBe(true)
      })

      it('should reject invalid filenames', () => {
        expect(isValidFileName('Invalid.md')).toBe(false) // Uppercase
        expect(isValidFileName('file with spaces.md')).toBe(false) // Spaces
        expect(isValidFileName('file_underscore.md')).toBe(false) // Underscore
        expect(isValidFileName('file.txt')).toBe(false) // Wrong extension
      })
    })
  })

  describe('Link Path Functions', () => {
    describe('getExpectedLinkPath', () => {
      it('should generate correct link paths', () => {
        expect(getExpectedLinkPath('index.md')).toBe('/')
        expect(getExpectedLinkPath('install.md')).toBe('/install')
        expect(getExpectedLinkPath('features.md')).toBe('/features')
        expect(getExpectedLinkPath('documentation.md')).toBe('/documentation')
      })

      it('should handle hyphenated filenames', () => {
        expect(getExpectedLinkPath('centos-install.md')).toBe('/centos-install')
        expect(getExpectedLinkPath('some-long-name.md')).toBe('/some-long-name')
      })
    })

    describe('validateNavigationLinks', () => {
      it('should validate navigation links against file list', () => {
        const navItems = [
          { text: 'Home', link: '/' },
          { text: 'Install', link: '/install' },
          { text: 'Features', link: '/features' }
        ]

        const results = validateNavigationLinks(navItems)
        
        expect(results).toHaveLength(3)
        expect(results[0]).toEqual({ link: '/', hasFile: true })
        expect(results[1]).toEqual({ link: '/install', hasFile: true })
        expect(results[2]).toEqual({ link: '/features', hasFile: true })
      })

      it('should identify missing files', () => {
        const navItems = [
          { text: 'Home', link: '/' },
          { text: 'Missing', link: '/nonexistent' }
        ]

        const results = validateNavigationLinks(navItems)
        
        expect(results).toHaveLength(2)
        expect(results[0].hasFile).toBe(true)
        expect(results[1].hasFile).toBe(false)
      })
    })
  })

  describe('File Lists', () => {
    describe('MARKDOWN_FILES', () => {
      it('should contain expected critical files', () => {
        const criticalFiles = [
          'index.md',
          'install.md',
          'features.md',
          'documentation.md',
          'faq.md',
          'README.md'
        ]

        criticalFiles.forEach(file => {
          expect(MARKDOWN_FILES).toContain(file)
        })
      })

      it('should have reasonable number of files', () => {
        expect(MARKDOWN_FILES.length).toBeGreaterThan(15)
        expect(MARKDOWN_FILES.length).toBeLessThan(50)
      })

      it('should contain only valid filenames', () => {
        MARKDOWN_FILES.forEach(file => {
          expect(isValidFileName(file)).toBe(true)
        })
      })
    })

    describe('AIDOCS_FILES', () => {
      it('should contain expected aidocs files', () => {
        const expectedAidocsFiles = [
          'architecture.md',
          'securityguide.md',
          'testingstrategy.md',
          'deploymentguide.md'
        ]

        expectedAidocsFiles.forEach(file => {
          expect(AIDOCS_FILES).toContain(file)
        })
      })

      it('should have reasonable number of files', () => {
        expect(AIDOCS_FILES.length).toBeGreaterThan(5)
        expect(AIDOCS_FILES.length).toBeLessThan(20)
      })

      it('should not overlap with main markdown files', () => {
        AIDOCS_FILES.forEach(file => {
          expect(MARKDOWN_FILES).not.toContain(file)
        })
      })
    })
  })

  describe('Integration with File Lists', () => {
    it('should have consistent file organization', () => {
      // Main docs should be larger than aidocs
      expect(MARKDOWN_FILES.length).toBeGreaterThan(AIDOCS_FILES.length)
    })

    it('should cover different documentation types', () => {
      // Should have installation docs
      const hasInstallDocs = MARKDOWN_FILES.some(f => f.includes('install'))
      expect(hasInstallDocs).toBe(true)

      // Should have feature docs
      expect(MARKDOWN_FILES).toContain('features.md')

      // Should have contribution docs
      const hasContribDocs = MARKDOWN_FILES.some(f => f.includes('contribut'))
      expect(hasContribDocs).toBe(true)
    })

    it('should have proper separation of concerns', () => {
      // Security and architecture should be in aidocs
      expect(AIDOCS_FILES).toContain('architecture.md')
      expect(AIDOCS_FILES).toContain('securityguide.md')

      // User-facing docs should be in main docs
      expect(MARKDOWN_FILES).toContain('index.md')
      expect(MARKDOWN_FILES).toContain('install.md')
      expect(MARKDOWN_FILES).toContain('usage.md')
    })
  })
})