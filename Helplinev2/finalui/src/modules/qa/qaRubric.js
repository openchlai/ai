/**
 * QA Rubric Configuration
 * Source of truth for scoring structure.
 */
export const QA_RUBRIC = [
    {
        category: 'Opening',
        maxScore: 2,
        criteria: [
            { id: 'opening_phrase', label: 'Used Standard Opening Phrase' }
        ]
    },
    {
        category: 'Listening Skills',
        maxScore: 10,
        criteria: [
            { id: 'non_interrupting', label: 'Active Listening (Non-interrupting)' },
            { id: 'empathy', label: 'Demonstrated Empathy' },
            { id: 'paraphrasing', label: 'Paraphrasing & Confirmation' },
            { id: 'courteous', label: 'Courteous Tone' },
            { id: 'nonhesitant', label: 'Confidence (Non-hesitant)' }
        ]
    },
    {
        category: 'Pro-activeness',
        maxScore: 6,
        criteria: [
            { id: 'extra_mile_willingness', label: 'Willingness to go the extra mile' },
            { id: 'confirms_client_satisfaction', label: 'Confirms Client Satisfaction' },
            { id: 'follows_up_on_case_updates', label: 'Follows up on case updates' }
        ]
    },
    {
        category: 'Resolution / Counselling',
        maxScore: 10,
        criteria: [
            { id: 'accuracy', label: 'Information Accuracy' },
            { id: 'grammar', label: 'Language & Grammar' },
            { id: 'consults', label: 'Appropriate Consultation' },
            { id: 'procedure_adherance', label: 'Procedure Adherence' },
            { id: 'educative', label: 'Educative approach' }
        ]
    },
    {
        category: 'Hold Procedures',
        maxScore: 4,
        criteria: [
            { id: 'notifies_hold', label: 'Notifies before Hold' },
            { id: 'updates_hold', label: 'Updates during Hold' }
        ]
    },
    {
        category: 'Closing',
        maxScore: 2,
        criteria: [
            { id: 'call_closing_coutesy', label: 'Standard Closing Courtesy' }
        ]
    }
]

export const SCORING_OPTIONS = [
    { value: 0, label: 'No' },
    { value: 1, label: 'Partially' },
    { value: 2, label: 'Yes' }
]
