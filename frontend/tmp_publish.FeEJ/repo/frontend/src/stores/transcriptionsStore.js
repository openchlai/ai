import { defineStore } from 'pinia'

let nextId = 1

export const useTranscriptionsStore = defineStore('transcriptions', {
  state: () => ({
    items: [
      {
        id: nextId++,
        audioFile: null,
        audioUrl: null,
        transcription: 'Caller reported a disturbance near the market around 7pm. No injuries reported.',
        counsellor: 'Jane Doe',
        uploadedAt: Date.now() - 3600 * 1000,
        reviewed: false
      },
      {
        id: nextId++,
        audioFile: null,
        audioUrl: null,
        transcription: 'Follow-up call regarding previous incident; caller requested legal aid referral.',
        counsellor: 'John Smith',
        uploadedAt: Date.now() - 2 * 3600 * 1000,
        reviewed: false
      }
    ]
  }),
  getters: {
    pending: (state) => state.items.filter(i => !i.reviewed)
  },
  actions: {
    addItem({ audioFile, audioUrl, transcription, counsellor, uploadedAt }) {
      const item = {
        id: nextId++,
        audioFile: audioFile || null,
        audioUrl: audioUrl || null,
        transcription: transcription || '',
        counsellor: counsellor || 'Unknown',
        uploadedAt: uploadedAt || Date.now(),
        reviewed: false
      }
      this.items.unshift(item)
      return item
    },
    updateTranscription(id, text) {
      const item = this.items.find(i => i.id === id)
      if (item) item.transcription = text
    },
    markReviewed(id) {
      const item = this.items.find(i => i.id === id)
      if (item) item.reviewed = true
    }
  }
})


