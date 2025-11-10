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
        { text: 'Getting Started', link: '/getting-started/introduction' },
        { text: 'User Guides', link: '/user-guides/for-helpline-operators/daily-workflow-guide' },
        { text: 'Deployment & Administration', link: '/deployment-administration/installation/system-requirements' },
        { text: 'Developer Documentation', link: '/developer-documentation/api-reference/authentication' },
        { text: 'AI Services', link: '/ai-services/overview' },
        { text: 'Governance & Legal', link: '/governance-legal/project-governance' },
        { text: 'Case Studies & Impact', link: '/case-studies-impact/success-stories' },
        { text: 'Resources', link: '/resources/faqs' }
    ],

    sidebar: {
        '/getting-started/': [
            {
                text: 'Getting Started',
                items: [
                    { text: 'Introduction to OpenCHS', link: '/getting-started/introduction' },
                    { text: 'Quick Start for Helpline Operators', link: '/getting-started/quick-start-helpline-operators' },
                    { text: 'Quick Start for System Administrators', link: '/getting-started/quick-start-system-administrators' },
                    { text: 'Quick Start for Developers', link: '/getting-started/quick-start-developers' }
                ]
            }
        ],

        '/user-guides/': [
    {
        text: 'User Guides',
        items: [
            {
                text: 'For Helpline Operators',
                items: [
                    { text: 'Daily Workflow Guide', link: '/user-guides/for-helpline-operators/daily-workflow-guide' },
                    { text: 'Case Management Guide', link: '/user-guides/for-helpline-operators/case-management-guide' },
                    { text: 'Using AI Features', link: '/user-guides/for-helpline-operators/using-ai-features' }
                ]
            },
            {
                text: 'For Supervisors & Managers',
                items: [
                    { text: 'Quality Assurance Monitoring', link: '/user-guides/for-supervisors-managers/quality-assurance-monitoring' },
                    { text: 'Team Workflow Management', link: '/user-guides/for-supervisors-managers/team-workflow-management' },
                    { text: 'Reporting Dashboards', link: '/user-guides/for-supervisors-managers/reporting-dashboards' }
                ]
            },
            {
                text: 'For Reporting Users',
                items: [
                    { text: 'Accessing & Interpreting Reports', link: '/user-guides/for-reporting-users/accessing-interpreting-reports' },
                    { text: 'Custom Report Generation', link: '/user-guides/for-reporting-users/custom-report-generation' },
                    { text: 'Data Export', link: '/user-guides/for-reporting-users/data-export' }
                            ]
                    }
                ]
            }
        ],


        '/deployment-administration/': [
            {
                text: 'Deployment & Administration',
                items: [
                    {
                        text: 'Installation',
                        items: [
                            { text: 'System Requirements', link: '/deployment-administration/installation/system-requirements' },
                            { text: 'On-Premise Installation Guide', link: '/deployment-administration/installation/on-premise-installation-guide' },
                            //{ text: 'Cloud Deployment', link: '/deployment-administration/installation/cloud-deployment' },
                            { text: 'Docker & Kubernetes Setup', link: '/deployment-administration/installation/docker-kubernetes-setup' }
                        ]
                    },
                    {
                        text: 'Configuration',
                        items: [
                            { text: 'System Settings', link: '/deployment-administration/configuration/system-settings' },
                            { text: 'User & Role Management', link: '/deployment-administration/configuration/user-role-management' },
                            { text: 'Configuring Communication Channels', link: '/deployment-administration/configuration/configuring-communication-channels' },
                            { text: 'Backup & Recovery', link: '/deployment-administration/configuration/backup-recovery' }
                        ]
                    },
                    {
                        text: 'Maintenance & Monitoring',
                        items: [
                            { text: 'System Health Checks', link: '/deployment-administration/maintenance-monitoring/system-health-checks' },
                            { text: 'Performance Tuning', link: '/deployment-administration/maintenance-monitoring/performance-tuning' },
                            { text: 'Logging & Auditing', link: '/deployment-administration/maintenance-monitoring/logging-auditing' },
                           // { text: 'Upgrading OpenCHS', link: '/deployment-administration/maintenance-monitoring/upgrading-openchs' }
                        ]
                    }
                ]
            }
        ],

        '/developer-documentation/': [
            {
                text: 'Developer Documentation',
                items: [
                    {
                        text: 'API Reference',
                        items: [
                            { text: 'Authentication', link: '/developer-documentation/api-reference/authentication' },
                            { text: 'Helpline API Endpoints', link: '/developer-documentation/api-reference/helpline-api-endpoints' },
                            { text: 'AI Service API Endpoints', link: '/developer-documentation/api-reference/ai-service-api-endpoints' },
                            { text: 'API Rate Limiting & Throttling', link: '/developer-documentation/api-reference/api-rate-limiting-throttling' },
                            { text: 'Overview', link: '/developer-documentation/api-reference/overview' },
                            { text: 'Testing Strategy', link: '/developer-documentation/api-reference/testing-strategy.md' }
                        ]
                    },
                    {
                        text: 'Data Models',
                        items: [
                            { text: 'Case Data Schema', link: '/developer-documentation/data-models/case-data-schema' },
                            { text: 'User Data Schema', link: '/developer-documentation/data-models/user-data-schema' },
                            { text: 'Reporting Data Warehouse', link: '/developer-documentation/data-models/reporting-data-warehouse' }
                        ]
                    },
                    {
                        text: 'Integrations & Extensions',
                        items: [
                            { text: 'Integrating with External Systems', link: '/developer-documentation/integrations-extensions/integrating-with-external-systems' },
                            { text: 'Building Custom Extensions', link: '/developer-documentation/integrations-extensions/building-custom-extensions' },
                            { text: 'Webhook & Event Reference', link: '/developer-documentation/integrations-extensions/webhook-event-reference' }
                        ]
                    },
                    {
                        text: 'Contribution Guide',
                        items: [
                            { text: 'Contribution Guide', link: '/developer-documentation/contribution-guide' },
                            { text: 'API', link: '/developer-documentation/api.md' }
                        ]
                    }
                ]
            }
        ],

        '/ai-services/': [
            {
                text: 'AI Services',
                items: [
                    { text: 'Overview', link: '/ai-services/overview' },
                    { text: 'Ethics', link: '/ai-services/ethics.md' },
                    {
                        text: 'Features',
                        items: [
                            { text: 'Classifier Model', link: '/ai-services/features/classifier_model.md' },
                            { text: 'Data Science Analytics', link: '/ai-services/features/data_sciaence_analytics.md' },
                            { text: 'Insights', link: '/ai-services/features/insights.md' },
                            { text: 'NER Model', link: '/ai-services/features/ner_model.md' },
                            { text: 'QA Model', link: '/ai-services/features/qa_model.md' },
                            { text: 'Summarizer Model', link: '/ai-services/features/summarizer_model.md' },
                            { text: 'Translator Model', link: '/ai-services/features/translator_model.md' },
                            { text: 'Whisper Model', link: '/ai-services/features/whisper_model.md' }
                        ]
                    },
                    {
                        text: 'Speech-to-Text',
                        items: [
                            { text: 'How it Works', link: '/ai-services/speech-to-text/how-it-works' },
                            { text: 'Accuracy & Language Support', link: '/ai-services/speech-to-text/accuracy-language-support' }
                        ]
                    },
                    {
                        text: 'Translation',
                        items: [
                            { text: 'Supported Languages', link: '/ai-services/translation/supported-languages' },
                            { text: 'Usage & Limitations', link: '/ai-services/translation/usage-limitations' }
                        ]
                    },
                    {
                        text: 'NLP',
                        items: [
                            { text: 'Named Entity Recognition', link: '/ai-services/nlp/named-entity-recognition' },
                            { text: 'Case Classification & Prediction', link: '/ai-services/nlp/case-classification-prediction' },
                            { text: 'Summarization & Insights', link: '/ai-services/nlp/summarization-insights' }
                        ]
                    }
                ]
            }
        ],

        '/governance-legal/': [
    {
        text: 'Governance & Legal',
        items: [
            { text: 'Open Source License', link: '/governance-legal/open-source-license' },
            { text: 'Project Governance', link: '/governance-legal/project-governance' },
            { text: 'Project Charter', link: '/governance-legal/project-charter' },
            { text: 'Data Privacy & Compliance', link: '/governance-legal/data-privacy-compliance' },
            { text: 'Privacy Policy', link: '/governance-legal/privacy-policy' },
            { text: 'Terms of Service', link: '/governance-legal/terms-of-service' },
            { text: 'Accessibility & CRPD', link: '/governance-legal/accessibility-crpd' }
        ]
    }
],

        '/case-studies-impact/': [
            {
                text: 'Case Studies & Impact',
                items: [
                    { text: 'Success Stories', link: '/case-studies-impact/success-stories' },
                    { text: 'Impact Reports', link: '/case-studies-impact/impact-reports' },
                    { text: 'Testimonials', link: '/case-studies-impact/testimonials' }
                ]
            }
        ],

        '/resources/': [
            {
                text: 'Resources',
                items: [
                    { text: 'FAQs', link: '/resources/faqs' },
                    { text: 'Glossary', link: '/resources/glossary' },
                    { text: 'Training Materials', link: '/resources/training-materials' },
                    { text: 'Community Forum', link: '/resources/community-forum' },
                    { text: 'Overview', link: '/resources/overview.md' }
                    // Note: training-materials.md removed - content consolidated in user-guides
                ]
            }
        ]
    },

    socialLinks: [
        { icon: 'github', link: 'https://github.com/openchlai' }
    ]
}
})
