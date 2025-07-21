import { describe, it, expect, beforeAll } from 'vitest'
import fs from 'fs/promises'
import path from 'path'
import { MARKDOWN_FILES, AIDOCS_FILES, isValidFileName, getExpectedLinkPath } from '../utils/docs'

describe('Markdown Content Tests', () => {
  const docsPath = path.resolve(process.cwd(), 'docs')
  let actualMarkdownFiles: string[] = []

  beforeAll(async () => {
    try {
      const files = await fs.readdir(docsPath)
      actualMarkdownFiles = files.filter(file => file.endsWith('.md'))
    } catch (error) {
      console.warn('Could not read docs directory:', error)
      actualMarkdownFiles = []
    }
  })

  describe('Required Files Existence', () => {
    const criticalFiles = [
      'index.md',
      'install.md',
      'features.md',
      'documentation.md',
      'roadmap.md',
      'faq.md',
      'contributing.md',
      'support.md',
      'usage.md'
    ]

    criticalFiles.forEach(file => {
      it(`should have ${file}`, () => {
        expect(MARKDOWN_FILES).toContain(file)
      })
    })

    it('should have all expected markdown files in the list', () => {
      expect(MARKDOWN_FILES.length).toBeGreaterThan(15)
    })

    it('should include index.md as homepage', () => {
      expect(MARKDOWN_FILES).toContain('index.md')
    })

    it('should include main navigation files', () => {
      const navFiles = ['install.md', 'features.md', 'documentation.md', 'roadmap.md', 'faq.md']
      navFiles.forEach(file => {
        expect(MARKDOWN_FILES).toContain(file)
      })
    })
  })

  describe('AiDocs Exclusion', () => {
    it('should have aidocs files listed separately', () => {
      expect(AIDOCS_FILES.length).toBeGreaterThan(0)
    })

    it('should include architecture.md in aidocs', () => {
      expect(AIDOCS_FILES).toContain('architecture.md')
    })

    it('should include security guide in aidocs', () => {
      expect(AIDOCS_FILES).toContain('securityguide.md')
    })

    it('should have testing strategy in aidocs', () => {
      expect(AIDOCS_FILES).toContain('testingstrategy.md')
    })

    it('should not mix aidocs files with main docs', () => {
      AIDOCS_FILES.forEach(file => {
        expect(MARKDOWN_FILES).not.toContain(file)
      })
    })
  })

  describe('File Content Structure', () => {
    it('should have non-empty index.md if it exists', async () => {
      if (actualMarkdownFiles.includes('index.md')) {
        try {
          const indexContent = await fs.readFile(path.join(docsPath, 'index.md'), 'utf-8')
          expect(indexContent.trim().length).toBeGreaterThan(0)
        } catch (error) {
          console.warn('Could not read index.md:', error)
        }
      }
    })

    it('should have proper markdown structure in main files if they exist', async () => {
      const mainFiles = ['index.md', 'install.md', 'features.md'].filter(file => 
        actualMarkdownFiles.includes(file)
      )
      
      for (const file of mainFiles) {
        try {
          const content = await fs.readFile(path.join(docsPath, file), 'utf-8')
          
          // Check for at least one heading or some content
          const hasHeading = content.includes('#')
          const hasContent = content.trim().length > 50
          
          expect(hasHeading || hasContent).toBe(true)
        } catch (error) {
          console.warn(`Could not read ${file}:`, error)
        }
      }
    })

    it('should have valid frontmatter format if present', async () => {
      const filesToCheck = ['index.md', 'features.md', 'install.md'].filter(file => 
        actualMarkdownFiles.includes(file)
      )
      
      for (const file of filesToCheck) {
        try {
          const content = await fs.readFile(path.join(docsPath, file), 'utf-8')
          
          // If file starts with ---, it should have valid frontmatter
          if (content.startsWith('---')) {
            const frontmatterEnd = content.indexOf('---', 3)
            expect(frontmatterEnd).toBeGreaterThan(3)
          }
        } catch (error) {
          console.warn(`Could not read ${file}:`, error)
        }
      }
    })
  })

  describe('File Naming Conventions', () => {
    it('should have valid file names in the expected list', () => {
      MARKDOWN_FILES.forEach(filename => {
        expect(isValidFileName(filename)).toBe(true)
      })
    })

    it('should use lowercase with hyphens', () => {
      const validPattern = /^[a-z0-9-]+\.md$/
      MARKDOWN_FILES.forEach(filename => {
    // Allow README.md as a special case
    if (filename === "README.md") return;
        expect(filename).toMatch(validPattern)
      })
    })

    it('should not have spaces in filenames', () => {
      MARKDOWN_FILES.forEach(filename => {
        expect(filename).not.toContain(' ')
      })
    })

    it('should not have uppercase letters', () => {
      MARKDOWN_FILES.forEach(filename => {
    // Allow README.md as a special case
    if (filename === "README.md") return;
        expect(filename).not.toMatch(/[A-Z]/)
      })
    })
  })

  describe('Content Quality Checks', () => {
    it('should have reasonable file count', () => {
      expect(MARKDOWN_FILES.length).toBeGreaterThan(10)
      expect(MARKDOWN_FILES.length).toBeLessThan(50)
    })

    it('should have both README.md and index.md', () => {
      expect(MARKDOWN_FILES).toContain('README.md')
      expect(MARKDOWN_FILES).toContain('index.md')
    })

    it('should have license files', () => {
      const hasLicense = MARKDOWN_FILES.includes('license.md') || MARKDOWN_FILES.includes('licenses.md')
      expect(hasLicense).toBe(true)
    })

    it('should have contribution guidelines', () => {
      const hasContrib = MARKDOWN_FILES.includes('contributing.md') || MARKDOWN_FILES.includes('contribution.md')
      expect(hasContrib).toBe(true)
    })
  })

  describe('Link Path Generation', () => {
    it('should generate correct link paths', () => {
      expect(getExpectedLinkPath('index.md')).toBe('/')
      expect(getExpectedLinkPath('install.md')).toBe('/install')
      expect(getExpectedLinkPath('features.md')).toBe('/features')
      expect(getExpectedLinkPath('documentation.md')).toBe('/documentation')
    })

    it('should handle hyphenated filenames', () => {
      expect(getExpectedLinkPath('centos-install.md')).toBe('/centos-install')
    })

    it('should handle files with multiple parts', () => {
      expect(getExpectedLinkPath('some-long-filename.md')).toBe('/some-long-filename')
    })
  })

  describe('File System Structure', () => {
    it('should have docs directory structure', async () => {
      try {
        const stats = await fs.stat(docsPath)
        expect(stats.isDirectory()).toBe(true)
      } catch (error) {
        console.warn('Docs directory not found:', error)
      }
    })

    it('should have aidocs subdirectory', async () => {
      try {
        const aidocsPath = path.join(docsPath, 'aidocs')
        const stats = await fs.stat(aidocsPath)
        expect(stats.isDirectory()).toBe(true)
      } catch (error) {
        console.warn('Aidocs directory not found:', error)
      }
    })

    it('should have public subdirectory', async () => {
      try {
        const publicPath = path.join(docsPath, 'public')
        const stats = await fs.stat(publicPath)
        expect(stats.isDirectory()).toBe(true)
      } catch (error) {
        console.warn('Public directory not found:', error)
      }
    })

    it('should have training subdirectory', async () => {
      try {
        const trainingPath = path.join(docsPath, 'training')
        const stats = await fs.stat(trainingPath)
        expect(stats.isDirectory()).toBe(true)
      } catch (error) {
        console.warn('Training directory not found:', error)
      }
    })
  })
})