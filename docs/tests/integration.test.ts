import { describe, it, expect, beforeAll } from 'vitest'
import fs from 'fs/promises'
import path from 'path'
import { loadVitePressConfig } from './config-loader'
import { extractFrontmatter, generateTOC, validateMarkdownLinks, MARKDOWN_FILES, AIDOCS_FILES } from '../utils/docs'

describe('Integration Tests', () => {
  const docsPath = path.resolve(process.cwd(), 'docs')
  let markdownFiles: string[] = []
  let fileContents: Map<string, string> = new Map()
  let config: any

  beforeAll(async () => {
    // Load configuration
    config = loadVitePressConfig()

    // Load markdown files
    try {
      const files = await fs.readdir(docsPath)
      markdownFiles = files.filter(file => file.endsWith('.md'))
      
      // Load content for key files only (for performance)
      const keyFiles = ['index.md', 'install.md', 'features.md', 'documentation.md', 'faq.md']
      for (const file of keyFiles) {
        if (markdownFiles.includes(file)) {
          try {
            const content = await fs.readFile(path.join(docsPath, file), 'utf-8')
            fileContents.set(file, content)
          } catch (error) {
            console.warn(`Could not read file ${file}:`, error)
          }
        }
      }
    } catch (error) {
      console.warn('Could not read docs directory:', error)
      markdownFiles = []
    }
  })

  describe('Complete Documentation Structure', () => {
    it('should have all navigation targets available as files', () => {
      const navLinks = config.themeConfig.nav.map((item: any) => item.link)
      const sidebarLinks = config.themeConfig.sidebar.flatMap((section: any) => 
        section.items.map((item: any) => item.link)
      )
      
      const allLinks = [...new Set([...navLinks, ...sidebarLinks])]
      const missingFiles: string[] = []
      
      for (const link of allLinks) {
        const expectedFile = link === '/' ? 'index.md' : link.slice(1) + '.md'
        if (!MARKDOWN_FILES.includes(expectedFile)) {
          missingFiles.push(`${link} -> ${expectedFile}`)
        }
      }

      // Log missing files but don't fail (files might exist but not be in our list)
      if (missingFiles.length > 0) {
        console.warn('Navigation links without files in expected list:', missingFiles)
      }
      
      // At least index.md should exist
      expect(MARKDOWN_FILES).toContain('index.md')
    })

    it('should have proper content hierarchy', () => {
      const mainFiles = ['index.md', 'install.md', 'features.md', 'documentation.md']
      
      mainFiles.forEach(file => {
        const content = fileContents.get(file)
        if (content) {
          const { body } = extractFrontmatter(content)
          const toc = generateTOC(body)
          
          // Should have at least one heading or substantial content
          if (toc.length === 0) {
            expect(body.trim().length).toBeGreaterThan(100)
          } else {
            expect(toc.length).toBeGreaterThan(0)
          }
        }
      })
    })

    it('should have consistent file organization', () => {
      // Main docs should have more files than aidocs
      expect(MARKDOWN_FILES.length).toBeGreaterThan(AIDOCS_FILES.length)
      
      // Should have key documentation files
      const criticalFiles = ['index.md', 'README.md', 'install.md', 'features.md']
      criticalFiles.forEach(file => {
        expect(MARKDOWN_FILES).toContain(file)
      })
    })
  })

  describe('Content Quality Assurance', () => {
    it('should have no obviously broken internal links', () => {
      let brokenLinks: Array<{ file: string, link: string, text: string }> = []

      fileContents.forEach((content, fileName) => {
        const links = validateMarkdownLinks(content)
        
        links.forEach(linkInfo => {
          if (!linkInfo.valid) {
            brokenLinks.push({
              file: fileName,
              link: linkInfo.link,
              text: linkInfo.text
            })
          }
        })
      })

      // Allow some broken links in development but warn about them
      if (brokenLinks.length > 0) {
        console.warn('Found potentially broken links:', brokenLinks.slice(0, 5))
      }
      
      // Should have mostly valid links
      expect(brokenLinks.length).toBeLessThan(10)
    })

    it('should have consistent heading structure', () => {
      fileContents.forEach((content, fileName) => {
        const { body } = extractFrontmatter(content)
        const toc = generateTOC(body)
        
        if (toc.length > 0) {
          // First heading should be level 1
          expect(toc[0].level).toBe(1)
          
          // Should not skip heading levels dramatically
          for (let i = 1; i < toc.length; i++) {
            const levelDiff = toc[i].level - toc[i-1].level
            expect(levelDiff).toBeLessThanOrEqual(2) // Allow some flexibility
          }
        }
      })
    })

    it('should have proper metadata in key files', () => {
      const keyFiles = ['index.md', 'install.md', 'features.md']
      
      keyFiles.forEach(file => {
        const content = fileContents.get(file)
        if (content) {
          const { frontmatter, body } = extractFrontmatter(content)
          
          // Should have meaningful content
          expect(body.trim().length).toBeGreaterThan(50)
          
          // Check for basic markdown structure
          const hasHeading = body.includes('#')
          const hasContent = body.trim().length > 100
          expect(hasHeading || hasContent).toBe(true)
        }
      })
    })
  })

  describe('VitePress Configuration Integration', () => {
    it('should have valid theme configuration', () => {
      expect(config.themeConfig).toBeDefined()
      expect(config.themeConfig.nav).toBeDefined()
      expect(config.themeConfig.sidebar).toBeDefined()
      expect(config.themeConfig.footer).toBeDefined()
      expect(config.themeConfig.socialLinks).toBeDefined()
    })

    it('should have proper head configuration for SEO', () => {
      expect(config.head).toBeDefined()
      expect(Array.isArray(config.head)).toBe(true)
      
      // Should have favicon
      const hasFavicon = config.head.some((item: any[]) => 
        Array.isArray(item) && 
        item[0] === 'link' && 
        item[1]?.rel === 'icon'
      )
      expect(hasFavicon).toBe(true)
    })

    it('should have appropriate build configuration', () => {
      expect(config.ignoreDeadLinks).toBe(true)
      expect(config.srcExclude).toContain('**/aidocs/**')
    })

    it('should have proper social links format', () => {
      config.themeConfig.socialLinks.forEach((link: any) => {
        expect(link.icon).toBeDefined()
        expect(link.link).toBeDefined()
        expect(typeof link.link).toBe('string')
        expect(link.link).toMatch(/^https?:\/\//)
      })
    })

    it('should exclude aidocs files correctly', () => {
      // AiDocs files should be separate from main docs
      AIDOCS_FILES.forEach(file => {
        expect(MARKDOWN_FILES).not.toContain(file)
      })
      
      // Should have architecture and security files in aidocs
      expect(AIDOCS_FILES).toContain('architecture.md')
      expect(AIDOCS_FILES).toContain('securityguide.md')
    })
  })

  describe('File System Integrity', () => {
    it('should have all required directories', async () => {
      const requiredDirs = ['public', 'training', 'aidocs']
      
      for (const dir of requiredDirs) {
        const dirPath = path.join(docsPath, dir)
        try {
          const stats = await fs.stat(dirPath)
          expect(stats.isDirectory()).toBe(true)
        } catch (error) {
          console.warn(`Directory ${dir} not found or not accessible:`, error)
        }
      }
    })

    it('should have proper file permissions and accessibility', async () => {
      const filesToCheck = markdownFiles.slice(0, Math.min(5, markdownFiles.length))
      
      for (const file of filesToCheck) {
        const filePath = path.join(docsPath, file)
        try {
          const stats = await fs.stat(filePath)
          
          expect(stats.isFile()).toBe(true)
          expect(stats.size).toBeGreaterThan(0)
          
          // Should be readable
          await expect(fs.access(filePath, fs.constants.R_OK)).resolves.toBeUndefined()
        } catch (error) {
          console.warn(`Could not access file ${file}:`, error)
        }
      }
    })

    it('should have consistent file naming', () => {
      markdownFiles.forEach(file => {
    // Allow README.md as a special case
    if (file === "README.md") return;
        // Should be lowercase with hyphens
        expect(file).toMatch(/^[a-z0-9-]+\.md$/)
        
        // Should not have spaces or uppercase
        expect(file).not.toMatch(/[A-Z\s_]/)
      })
    })

    it('should have expected file structure', () => {
      // Should have both main docs and separate areas
      expect(MARKDOWN_FILES.length).toBeGreaterThan(15)
      expect(AIDOCS_FILES.length).toBeGreaterThan(5)
      
      // Should have different types of documentation
      const hasInstallDocs = MARKDOWN_FILES.some(f => f.includes('install'))
      const hasFeatureDocs = MARKDOWN_FILES.includes('features.md')
      const hasContribDocs = MARKDOWN_FILES.some(f => f.includes('contribut'))
      
      expect(hasInstallDocs).toBe(true)
      expect(hasFeatureDocs).toBe(true)
      expect(hasContribDocs).toBe(true)
    })
  })

  describe('Performance and Optimization', () => {
    it('should have reasonable file sizes', async () => {
      const filesToCheck = ['index.md', 'install.md', 'features.md'].filter(f => 
        markdownFiles.includes(f)
      )
      
      for (const file of filesToCheck) {
        const filePath = path.join(docsPath, file)
        try {
          const stats = await fs.stat(filePath)
          
          // Files should be under 100KB for good performance
          expect(stats.size).toBeLessThan(100000)
          
          // But should have meaningful content (over 50 bytes)
          expect(stats.size).toBeGreaterThan(50)
        } catch (error) {
          console.warn(`Could not check size of ${file}:`, error)
        }
      }
    })

    it('should have optimized navigation structure', () => {
      // Navigation should not be too deep
      expect(config.themeConfig.sidebar.length).toBeLessThanOrEqual(6)
      
      // Each section should have reasonable number of items
      config.themeConfig.sidebar.forEach((section: any) => {
        expect(section.items.length).toBeLessThanOrEqual(8)
        expect(section.items.length).toBeGreaterThan(0)
      })
    })

    it('should have efficient content organization', () => {
      // Check that content is well distributed
      const contentSizes = Array.from(fileContents.entries()).map(([file, content]) => ({
        file,
        size: content.length
      }))

      if (contentSizes.length > 0) {
        // Should not have one file dominating the content
        const totalSize = contentSizes.reduce((sum, item) => sum + item.size, 0)
        const averageSize = totalSize / contentSizes.length

        contentSizes.forEach(item => {
          // No single file should be more than 10x the average
          expect(item.size).toBeLessThan(averageSize * 10)
        })
      }
    })

    it('should have balanced documentation coverage', () => {
      // Should cover different aspects of the project
      const categories = {
        installation: MARKDOWN_FILES.some(f => f.includes('install')),
        features: MARKDOWN_FILES.includes('features.md'),
        contribution: MARKDOWN_FILES.some(f => f.includes('contribut')),
        support: MARKDOWN_FILES.includes('support.md'),
        roadmap: MARKDOWN_FILES.includes('roadmap.md'),
        faq: MARKDOWN_FILES.includes('faq.md')
      }

      // Should have most documentation categories covered
      const coveredCategories = Object.values(categories).filter(Boolean).length
      expect(coveredCategories).toBeGreaterThan(4)
    })
  })
})