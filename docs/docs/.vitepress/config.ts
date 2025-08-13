import { defineConfig } from 'vitepress'


export default defineConfig({
  title: 'OpenCHS Docs',
  description: 'Child Helpline Case Management System',
  head: [
    ['link', { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }]
  ], 
  ignoreDeadLinks: true, 
  srcExclude: ['**/aidocs/**'],
  
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Install', link: '/install' },
      { text: 'Features', link: '/features' },
      { text: 'Docs', link: '/documentation' },
      { text: 'Roadmap', link: '/roadmap' },
      { text: 'FAQ', link: '/faq' }
    ],
    sidebar: [
      {
        text: 'Getting Started',
        items: [
          { text: 'Overview', link: '/' },
          { text: 'AI Powered', link: '/aipowered' },
          { text: 'Installation', link: '/install' },
          { text: 'Usage', link: '/usage' }
        ]
      },
      {
        text: 'Core Features',
        items: [
          { text: 'Features', link: '/features' },
          { text: 'Documentation', link: '/documentation' },
          { text: 'Support', link: '/support' }
        ]
      },
      {
        text: 'Community & Contribution',
        items: [
          { text: 'Contributing', link: '/contributing' },
          { text: 'License', link: '/license' },
          { text: 'Acknowledgements', link: '/acknowledgements' }
        ]
      },
      
      {
  text: 'Developer Tools',
  items: [
    { text: 'Test Coverage', link: '/coverage-html/' }
  ]
},
      {
        text: 'Project Evolution',
        items: [
          { text: 'Roadmap', link: '/roadmap' },
          { text: 'Changelog', link: '/changelog' },
          { text: 'FAQ', link: '/faq' }
        ]
      }
    ],
    footer: {
      message: 'Released under the MIT License.',
      copyright: '© 2025 BITZ IT Consulting | OpenCHS Project'
    },
    
    socialLinks: [
      { icon: 'github', link: 'https://github.com/openchlsystem/OpenCHS-helpline' },
      { icon: 'linkedin', link: 'https://www.linkedin.com/company/bitz-it-consulting/' }
    ]
  },
 
})
