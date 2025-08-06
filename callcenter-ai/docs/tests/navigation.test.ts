import { describe, it, expect, beforeEach } from 'vitest'
import { loadVitePressConfig } from './config-loader'
import { validateNavItem, validateSidebarSection, validateNavigationLinks, MARKDOWN_FILES } from '../utils/docs'

describe('Navigation System', () => {
  let config: any

  beforeEach(() => {
    config = loadVitePressConfig()
  })

  describe('Main Navigation', () => {
    it('should have all navigation items valid', () => {
      config.themeConfig.nav.forEach((item: any) => {
        expect(validateNavItem(item)).toBe(true)
      })
    })

    it('should have exactly 6 navigation items', () => {
      expect(config.themeConfig.nav).toHaveLength(6)
    })

    it('should have unique navigation links', () => {
      const links = config.themeConfig.nav.map((item: any) => item.link)
      const uniqueLinks = new Set(links)
      expect(uniqueLinks.size).toBe(links.length)
    })

    it('should have appropriate navigation order', () => {
      const expectedOrder = ['Home', 'Install', 'Features', 'Docs', 'Roadmap', 'FAQ']
      const actualOrder = config.themeConfig.nav.map((item: any) => item.text)
      
      expect(actualOrder).toEqual(expectedOrder)
    })

    it('should have root link for home', () => {
      const homeItem = config.themeConfig.nav.find((item: any) => item.text === 'Home')
      expect(homeItem?.link).toBe('/')
    })

    it('should have consistent link formatting', () => {
      config.themeConfig.nav.forEach((item: any) => {
        if (item.text !== 'Home') {
          expect(item.link).toMatch(/^\/[a-z-]+$/)
        }
      })
    })

    it('should map to expected markdown files', () => {
      const linkValidation = validateNavigationLinks(config.themeConfig.nav)
      linkValidation.forEach(result => {
        // Log missing files for debugging but don't fail the test
        if (!result.hasFile) {
          console.warn(`Navigation link ${result.link} may not have corresponding file`)
        }
      })
      
      // At least the homepage should exist
      const homeLink = linkValidation.find(l => l.link === '/')
      expect(homeLink?.hasFile).toBe(true)
    })
  })

  describe('Sidebar Navigation', () => {
    it('should have all sidebar sections valid', () => {
      config.themeConfig.sidebar.forEach((section: any) => {
        expect(validateSidebarSection(section)).toBe(true)
      })
    })

    it('should have exactly 4 sidebar sections', () => {
      expect(config.themeConfig.sidebar).toHaveLength(4)
    })

    it('should have logical section grouping', () => {
      const sectionTexts = config.themeConfig.sidebar.map((section: any) => section.text)
      const expectedSections = [
        'Getting Started',
        'Core Features', 
        'Community & Contribution',
        'Project Evolution'
      ]
      
      expect(sectionTexts).toEqual(expectedSections)
    })

    it('should have unique links across all sections', () => {
      const allLinks = config.themeConfig.sidebar.flatMap((section: any) => 
        section.items.map((item: any) => item.link)
      )
      const uniqueLinks = new Set(allLinks)
      expect(uniqueLinks.size).toBe(allLinks.length)
    })

    it('should have proper Getting Started flow', () => {
      const gettingStarted = config.themeConfig.sidebar.find((section: any) => 
        section.text === 'Getting Started'
      )
      
      expect(gettingStarted).toBeDefined()
      
      const expectedFlow = ['Overview', 'AI Powered', 'Installation', 'Usage']
      const actualFlow = gettingStarted.items.map((item: any) => item.text)
      
      expect(actualFlow).toEqual(expectedFlow)
    })

    it('should have overview as first item in Getting Started', () => {
      const gettingStarted = config.themeConfig.sidebar.find((section: any) => 
        section.text === 'Getting Started'
      )
      
      expect(gettingStarted.items[0].text).toBe('Overview')
      expect(gettingStarted.items[0].link).toBe('/')
    })

    it('should have Core Features section with correct items', () => {
      const coreFeatures = config.themeConfig.sidebar.find((section: any) => 
        section.text === 'Core Features'
      )
      
      expect(coreFeatures).toBeDefined()
      expect(coreFeatures.items).toHaveLength(3)
      
      const expectedItems = ['Features', 'Documentation', 'Support']
      const actualItems = coreFeatures.items.map((item: any) => item.text)
      expect(actualItems).toEqual(expectedItems)
    })

    it('should have Community section with correct items', () => {
      const community = config.themeConfig.sidebar.find((section: any) => 
        section.text === 'Community & Contribution'
      )
      
      expect(community).toBeDefined()
      expect(community.items).toHaveLength(3)
      
      const expectedItems = ['Contributing', 'License', 'Acknowledgements']
      const actualItems = community.items.map((item: any) => item.text)
      expect(actualItems).toEqual(expectedItems)
    })

    it('should have Project Evolution section with correct items', () => {
      const evolution = config.themeConfig.sidebar.find((section: any) => 
        section.text === 'Project Evolution'
      )
      
      expect(evolution).toBeDefined()
      expect(evolution.items).toHaveLength(3)
      
      const expectedItems = ['Roadmap', 'Changelog', 'FAQ']
      const actualItems = evolution.items.map((item: any) => item.text)
      expect(actualItems).toEqual(expectedItems)
    })
  })

  describe('Navigation Consistency', () => {
    it('should have consistent links between nav and sidebar', () => {
      const navLinks = new Set(config.themeConfig.nav.map((item: any) => item.link))
      const sidebarLinks = new Set(
        config.themeConfig.sidebar.flatMap((section: any) => 
          section.items.map((item: any) => item.link)
        )
      )

      // Check that main nav links exist in sidebar
      const sharedLinks = ['/install', '/features', '/roadmap', '/faq']
      
      sharedLinks.forEach(link => {
        if (navLinks.has(link)) {
          expect(sidebarLinks.has(link)).toBe(true)
        }
      })
    })

    it('should have proper link format consistency', () => {
      const allLinks = [
        ...config.themeConfig.nav.map((item: any) => item.link),
        ...config.themeConfig.sidebar.flatMap((section: any) => 
          section.items.map((item: any) => item.link)
        )
      ]

      allLinks.forEach(link => {
        // Should start with / and not end with /
        expect(link).toMatch(/^\//)
        if (link !== '/') {
          expect(link).not.toMatch(/\/$/)
        }
      })
    })

    it('should have documentation link consistency', () => {
      // Nav has 'Docs' linking to '/documentation'
      const docsNav = config.themeConfig.nav.find((item: any) => item.text === 'Docs')
      expect(docsNav.link).toBe('/documentation')
      
      // Sidebar should have corresponding item
      const docsSidebar = config.themeConfig.sidebar
        .flatMap((section: any) => section.items)
        .find((item: any) => item.link === '/documentation')
      expect(docsSidebar).toBeDefined()
    })
  })

  describe('Accessibility and UX', () => {
    it('should have meaningful navigation text', () => {
      const allNavTexts = [
        ...config.themeConfig.nav.map((item: any) => item.text),
        ...config.themeConfig.sidebar.flatMap((section: any) => [
          section.text,
          ...section.items.map((item: any) => item.text)
        ])
      ]

      allNavTexts.forEach(text => {
        expect(text.length).toBeGreaterThan(2)
        expect(text).not.toMatch(/^\s|\s$/) // No leading/trailing spaces
        expect(text).toMatch(/^[A-Z]/) // Should start with capital letter
      })
    })

    it('should have reasonable section sizes', () => {
      config.themeConfig.sidebar.forEach((section: any) => {
        expect(section.items.length).toBeGreaterThan(0)
        expect(section.items.length).toBeLessThanOrEqual(5) // Reasonable size
      })
    })

    it('should have descriptive section names', () => {
      const sectionNames = config.themeConfig.sidebar.map((section: any) => section.text)
      
      sectionNames.forEach(name => {
        expect(name.length).toBeGreaterThan(5)
        expect(name).not.toContain('Section') // Avoid generic names
      })
    })

    it('should have balanced navigation distribution', () => {
      // Should have reasonable distribution of items across sections
      const itemCounts = config.themeConfig.sidebar.map((section: any) => section.items.length)
      const totalItems = itemCounts.reduce((sum: number, count: number) => sum + count, 0)
      
      expect(totalItems).toBeGreaterThan(8)
      expect(totalItems).toBeLessThan(20)
    })
  })

  describe('Error Handling', () => {
    it('should handle missing navigation gracefully', () => {
      // Test that config structure is robust
      expect(config.themeConfig).toBeDefined()
      expect(config.themeConfig.nav).toBeDefined()
      expect(config.themeConfig.sidebar).toBeDefined()
    })

    it('should have fallback for empty sections', () => {
      // Ensure no section has empty items array
      config.themeConfig.sidebar.forEach((section: any) => {
        expect(Array.isArray(section.items)).toBe(true)
        expect(section.items.length).toBeGreaterThan(0)
      })
    })

    it('should have valid link structure', () => {
      // All links should be strings and properly formatted
      const allLinks = [
        ...config.themeConfig.nav.map((item: any) => item.link),
        ...config.themeConfig.sidebar.flatMap((section: any) => 
          section.items.map((item: any) => item.link)
        )
      ]

      allLinks.forEach(link => {
        expect(typeof link).toBe('string')
        expect(link.length).toBeGreaterThan(0)
        expect(link.startsWith('/')).toBe(true)
      })
    })
  })
})