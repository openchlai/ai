import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'OpenChS',
  description: 'Automated Feature Engineering',
  themeConfig: {
    logo: '/logo.png', // place your logo in public folder
    nav: [
      { text: 'Install', link: '/install' },
      { text: 'Getting Started', link: '/getting-started' },
      { text: 'Guides', link: '/guides' },
      { text: 'Resources', link: '/resources' },
      { text: 'API Reference', link: '/api-reference' },
      { text: 'Release Notes', link: '/release-notes' },
    ],
    sidebar: {
      '/': [
        {
          text: 'Install',
          items: [
            { text: 'Add-ons', link: '/install#add-ons' },
            { text: 'Installing Graphviz', link: '/install#installing-graphviz' },
            { text: 'Source', link: '/install#source' },
            { text: 'Docker', link: '/install#docker' },
          ]
        },
        {
          text: 'Development',
          items: []
        },
      ]
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/openchlsystem/OpenCHS-helpline' },
      { icon: 'linkedin', link: 'https://www.linkedin.com/company/bitz-it-consulting/' }
    ]
  }
})
