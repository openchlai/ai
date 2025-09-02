<template>
  <div class="page-container">
    <div class="header">
      <div class="left">
        <h1>Transcription Reviews</h1>
        <p>Items marked as incorrect during case creation.</p>
      </div>
      <router-link to="/cases" class="back-btn">Back to Menu</router-link>
    </div>

    <div v-if="pending.length === 0" class="empty">No items pending review.</div>

    <div class="list">
      <div v-for="item in pending" :key="item.id" class="card">
        <div class="card-header">
          <div class="meta">
            <div class="row"><span class="k">Uploaded</span> <span class="v">{{ formatDate(item.uploadedAt) }}</span></div>
            <div class="row"><span class="k">Counsellor</span> <span class="v">{{ item.counsellor }}</span></div>
          </div>
        </div>

        <div class="media">
          <template v-if="item.audioUrl">
            <audio :src="item.audioUrl" controls class="audio"></audio>
          </template>
          <template v-else>
            <div class="audio-empty">No audio attached</div>
          </template>
        </div>

        <div class="editor">
          <label>Transcription</label>
          <textarea
            v-model="draft[item.id]"
            rows="6"
            :readonly="!editing[item.id]"
            :class="{ readonly: !editing[item.id] }"
          ></textarea>
        </div>
        <div class="actions">
          <button class="btn" :disabled="editing[item.id]" @click="review(item)">Review</button>
          <button class="btn primary" :disabled="!editing[item.id]" @click="submit(item)">Submit</button>
        </div>
      </div>
    </div>
  </div>
 </template>

<script setup>
import { reactive, computed } from 'vue'
import { useTranscriptionsStore } from '@/stores/transcriptionsStore'

const transStore = useTranscriptionsStore()
const pending = computed(() => transStore.pending)
const draft = reactive({})
const editing = reactive({})

const review = (item) => {
  if (draft[item.id] == null) draft[item.id] = item.transcription
  editing[item.id] = true
}

const submit = (item) => {
  const text = draft[item.id] != null ? draft[item.id] : item.transcription
  transStore.updateTranscription(item.id, text)
  transStore.markReviewed(item.id)
  editing[item.id] = false
}

const formatDate = (ts) => new Date(ts).toLocaleString()
</script>

<style scoped>
.page-container { padding: 20px; }
.page-container { min-height: 0; overflow: auto; }
.header { margin-bottom: 16px; display:flex; align-items:center; justify-content:space-between; }
.header .left h1 { margin:0; font-size: 22px; }
.header .left p { margin:4px 0 0 0; color: var(--text-muted,#666); font-size: 13px; }
.back-btn { border:1px solid var(--border-color,rgba(0,0,0,0.12)); padding:8px 12px; border-radius:10px; text-decoration:none; color:inherit; background: var(--surface,#f8f8f8); }
.empty { padding: 20px; color: #666; }
.list { display: flex; flex-direction: column; gap: 16px; }
.card { background: var(--card-bg, #fff); border: 1px solid var(--border-color, rgba(0,0,0,0.08)); border-radius: 14px; padding: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.02); }
.card-header { padding-bottom: 10px; border-bottom: 1px dashed var(--border-color,rgba(0,0,0,0.08)); }
.meta { font-size: 13px; color: var(--text-muted, #666); display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap: 6px; }
.meta .k { font-weight: 600; margin-right: 6px; }
.media { margin: 12px 0; }
.audio { width: 100%; }
.audio-empty { padding: 10px; background: var(--surface-muted, rgba(0,0,0,0.03)); border: 1px dashed var(--border-color, rgba(0,0,0,0.12)); border-radius: 10px; color: var(--text-muted,#666); text-align:center; }
.editor label { font-weight: 600; display: block; margin-bottom: 6px; }
.editor textarea { width: 100%; border: 1px solid var(--border-color, rgba(0,0,0,0.12)); border-radius: 10px; padding: 10px; font-family: inherit; font-size: 14px; background: var(--surface,#fff); }
.editor textarea.readonly { background: var(--surface-muted, rgba(0,0,0,0.02)); }
.actions { display: flex; gap: 10px; margin-top: 12px; justify-content: flex-end; }
.btn { border: 1px solid var(--border-color, rgba(0,0,0,0.12)); background: var(--surface, #f8f8f8); padding: 8px 14px; border-radius: 10px; cursor: pointer; font-weight: 600; }
.btn.primary { background: #964B00; color: #fff; border-color: #964B00; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
</style>


