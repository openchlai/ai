import { describe, it, expect, beforeEach } from 'vitest'
import { loadVitePressConfig } from './config-loader'

describe('VitePress Configuration', () => {
  let vitePressConfig: any

  beforeEach(() => {
    vitePressConfig = loadVitePressConfig()
  })

  describe('Basic Configuration', () => {
    it('should have correct title', () => {
      expect(vitePressConfig.title).toBe('OpenCHS Docs')
    })

    it('should have correct description', () => {
      expect(vitePressConfig.description).toBe('Child Helpline Case Management System')
    })

    it('should ignore dead links', () => {
      expect(vitePressConfig.ignoreDeadLinks).toBe(true)
    })

    it('should exclude aidocs directory', () => {
      expect(vitePressConfig.srcExclude).toContain('**/aidocs/**')
    })

    it('should have favicon configured in head', () => {
      expect(vitePressConfig.head).toBeDefined()
      expect(Array.isArray(vitePressConfig.head)).toBe(true)
      
      const faviconLink = vitePressConfig.head.find(
        (item: any[]) => Array.isArray(item) && item[0] === 'link' && item[1]?.rel === 'icon'
      )
      expect(faviconLink).toBeDefined()
      expect(faviconLink[1].href).toBe('/favicon.ico')
    })
  })

  describe('Navigation Configuration', () => {
    it('should have navigation items', () => {
      expect(vitePressConfig.themeConfig).toBeDefined()
      expect(vitePressConfig.themeConfig.nav).toBeDefined()
      expect(Array.isArray(vitePressConfig.themeConfig.nav)).toBe(true)
    })

    it('should have exactly 6 navigation items', () => {
      expect(vitePressConfig.themeConfig.nav).toHaveLength(6)
    })

    it('should have Home navigation item', () => {
      const homeNav = vitePressConfig.themeConfig.nav.find(
        (item: any) => item.text === 'Home'
      )
      expect(homeNav).toBeDefined()
      expect(homeNav.link).toBe('/')
    })

    it('should have Install navigation item', () => {
      const installNav = vitePressConfig.themeConfig.nav.find(
        (item: any) => item.text === 'Install'
      )
      expect(installNav).toBeDefined()
      expect(installNav.link).toBe('/install')
    })

    it('should have Features navigation item', () => {
      const featuresNav = vitePressConfig.themeConfig.nav.find(
        (item: any) => item.text === 'Features'
      )
      expect(featuresNav).toBeDefined()
      expect(featuresNav.link).toBe('/features')
    })

    it('should have Docs navigation item', () => {
      const docsNav = vitePressConfig.themeConfig.nav.find(
        (item: any) => item.text === 'Docs'
      )
      expect(docsNav).toBeDefined()
      expect(docsNav.link).toBe('/documentation')
    })

    it('should have Roadmap navigation item', () => {
      const roadmapNav = vitePressConfig.themeConfig.nav.find(
        (item: any) => item.text === 'Roadmap'
      )
      expect(roadmapNav).toBeDefined()
      expect(roadmapNav.link).toBe('/roadmap')
    })

    it('should have FAQ navigation item', () => {
      const faqNav = vitePressConfig.themeConfig.nav.find(
        (item: any) => item.text === 'FAQ'
      )
      expect(faqNav).toBeDefined()
      expect(faqNav.link).toBe('/faq')
    })

    it('should have valid links for all navigation items', () => {
      vitePressConfig.themeConfig.nav.forEach((navItem: any) => {
        expect(navItem.link).toBeDefined()
        expect(typeof navItem.link).toBe('string')
        expect(navItem.link).toMatch(/^\//)
      })
    })
  })

  describe('Sidebar Configuration', () => {
    it('should have sidebar configuration', () => {
      expect(vitePressConfig.themeConfig.sidebar).toBeDefined()
      expect(Array.isArray(vitePressConfig.themeConfig.sidebar)).toBe(true)
    })

    it('should have exactly 4 sidebar sections', () => {
      expect(vitePressConfig.themeConfig.sidebar).toHaveLength(4)
    })

    it('should have Getting Started section', () => {
      const gettingStarted = vitePressConfig.themeConfig.sidebar.find(
        (section: any) => section.text === 'Getting Started'
      )
      expect(gettingStarted).toBeDefined()
      expect(Array.isArray(gettingStarted.items)).toBe(true)
      expect(gettingStarted.items).toHaveLength(4)
    })

    it('should have Core Features section', () => {
      const coreFeatures = vitePressConfig.themeConfig.sidebar.find(
        (section: any) => section.text === 'Core Features'
      )
      expect(coreFeatures).toBeDefined()
      expect(Array.isArray(coreFeatures.items)).toBe(true)
      expect(coreFeatures.items).toHaveLength(3)
    })

    it('should have Community & Contribution section', () => {
      const community = vitePressConfig.themeConfig.sidebar.find(
        (section: any) => section.text === 'Community & Contribution'
      )
      expect(community).toBeDefined()
      expect(Array.isArray(community.items)).toBe(true)
      expect(community.items).toHaveLength(3)
    })

    it('should have Project Evolution section', () => {
      const evolution = vitePressConfig.themeConfig.sidebar.find(
        (section: any) => section.text === 'Project Evolution'
      )
      expect(evolution).toBeDefined()
      expect(Array.isArray(evolution.items)).toBe(true)
      expect(evolution.items).toHaveLength(3)
    })

    it('should have valid links in all sidebar items', () => {
      vitePressConfig.themeConfig.sidebar.forEach((section: any) => {
        section.items.forEach((item: any) => {
          expect(item.link).toBeDefined()
          expect(typeof item.link).toBe('string')
          expect(item.link).toMatch(/^\//)
        })
      })
    })

    it('should have Overview as first item in Getting Started', () => {
      const gettingStarted = vitePressConfig.themeConfig.sidebar[0]
      expect(gettingStarted.text).toBe('Getting Started')
      expect(gettingStarted.items[0].text).toBe('Overview')
      expect(gettingStarted.items[0].link).toBe('/')
    })
  })

  describe('Footer Configuration', () => {
    it('should have footer message', () => {
      expect(vitePressConfig.themeConfig.footer.message).toBe('Released under the MIT License.')
    })

    it('should have copyright information', () => {
      expect(vitePressConfig.themeConfig.footer.copyright).toBe('© 2025 BITZ IT Consulting | OpenCHS Project')
    })
  })

  describe('Social Links Configuration', () => {
    it('should have social links', () => {
      expect(vitePressConfig.themeConfig.socialLinks).toBeDefined()
      expect(Array.isArray(vitePressConfig.themeConfig.socialLinks)).toBe(true)
    })

    it('should have exactly 2 social links', () => {
      expect(vitePressConfig.themeConfig.socialLinks).toHaveLength(2)
    })

    it('should have GitHub link', () => {
      const githubLink = vitePressConfig.themeConfig.socialLinks.find(
        (link: any) => link.icon === 'github'
      )
      expect(githubLink).toBeDefined()
      expect(githubLink.link).toBe('https://github.com/openchlsystem/OpenCHS-helpline')
    })

    it('should have LinkedIn link', () => {
      const linkedinLink = vitePressConfig.themeConfig.socialLinks.find(
        (link: any) => link.icon === 'linkedin'
      )
      expect(linkedinLink).toBeDefined()
      expect(linkedinLink.link).toBe('https://www.linkedin.com/company/bitz-it-consulting/')
    })

    it('should have valid URLs for all social links', () => {
      vitePressConfig.themeConfig.socialLinks.forEach((link: any) => {
        expect(link.link).toMatch(/^https?:\/\//)
      })
    })
  })
})