import { defineConfig } from 'vitepress'

// Determine if we are in production mode
const isProd = process.env.NODE_ENV === 'production'

export default defineConfig({
    base: '/',  // Use root path to avoid CSS loading issues
    title: "openCHS",
    description: "A Child Helpline System",
    ignoreDeadLinks: true,
    themeConfig: {
        nav: [
            { text: 'Home', link: '/' },
            { text: 'Getting Started', link: '/getting-started/overview' },
            { text: 'Helpline', link: '/helpline-service/overview' },
            { text: 'AI Service', link: '/ai-service/overview' },
            { text: 'Ecosystem', link: '/ecosystem/overview' },
            { text: 'API Docs', link: '/api/overview' },
            { text: 'User Guides', link: '/user-guides/operators' },
            { text: 'About', link: '/about/privacy' }
        ],

        sidebar: {
            '/getting-started/': [
                {
                    text: 'Getting Started',
                    items: [
                        { text: 'Overview', link: '/getting-started/overview' },
                        { text: 'Helpline Setup', link: '/getting-started/helpline-setup' },
                        { text: 'AI Service Setup', link: '/getting-started/ai-service-setup' }
                    ]
                }
            ],

            '/helpline-service/': [
                {
                    text: 'Helpline Service',
                    items: [
                        { text: 'Overview', link: '/helpline-service/overview' },
                        { text: 'Compliance', link: '/helpline-service/compliance' },
                        {
                            text: 'Operations',
                            items: [
                                { text: 'Call Flow', link: '/helpline-service/operations/call-flow' }
                            ]
                        },
                        {
                            text: 'Training',
                            items: [
                                { text: 'Training Materials', link: '/helpline-service/training/training-materials' }
                            ]
                        },
                        { text: 'API', link: '/api/helpline-service' }
                    ]
                }
            ],

            '/ai-service/': [
                {
                    text: 'AI Service',
                    items: [
                        { text: 'Overview', link: '/ai-service/overview' },
                        {
                            text: 'Features',
                            items: [
                                { text: 'Transcription', link: '/ai-service/features/whisper_model' },
                                { text: 'Translation', link: '/ai-service/features/translator_model' },
                                { text: 'Quality Assurance', link: '/ai-service/features/qa_model' },
                                { text: 'Named Entity Extraction', link: '/ai-service/features/ner_model' },
                                { text: 'Classification', link: '/ai-service/features/classifier_model' },
                                { text: 'Summarization', link: '/ai-service/features/summarizer_model' },
                                { text: 'Insights', link: '/ai-service/features/insights' },
                                { text: 'Data Science & Analytics', link: '/ai-service/features/data_sciaence_analytics' }
                            ]
                        },
                        { text: 'Ethics', link: '/ai-service/ethics' }
                    ]
                }
            ],

            '/ecosystem/': [
                {
                    text: 'Ecosystem',
                    items: [
                        { text: 'Overview', link: '/ecosystem/overview' },
                        { text: 'OpenCHS Ecosystem', link: '/ecosystem/openchs-ecosystem' },
                        { text: 'OpenCHS Community', link: '/ecosystem/openchs-community' }
                    ]
                }
            ],

            '/api/': [
                {
                    text: 'API Documentation',
                    items: [
                        { text: 'Overview', link: '/api/overview' },
                        { text: 'Helpline Service API', link: '/api/helpline-service' },
                        { text: 'AI Service API', link: '/api/ai-service' },
                        { text: 'Testing Strategy', link: '/api/testing-strategy' }
                    ]
                }
            ],

            '/user-guides/': [
                {
                    text: 'User Guides',
                    items: [
                        { text: 'Operators', link: '/user-guides/operators' }
                    ]
                }
            ],

            '/about/': [
                {
                    text: 'About',
                    items: [
                        { text: 'Overview', link: '/about/overview' },
                        { text: 'Governance', link: '/about/project-governance' },
                        { text: 'Project Charter', link: '/about/project-charter' },
                        { text: 'Privacy', link: '/about/privacy' }
                    ]
                }
            ]
        },

        socialLinks: [
            { icon: 'github', link: 'https://github.com/openchlai' }
        ]
    }
})
