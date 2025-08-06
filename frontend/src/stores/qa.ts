import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { QAEvaluation } from '../types/qa'

export const useQAStore = defineStore('qa', () => {
  const evaluations = ref<QAEvaluation[]>([])
  const counselors = ref<any[]>([])
  const supervisors = ref<any[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const filteredEvaluations = ref<QAEvaluation[]>([])
  const averageScore = ref(0)

  // Dummy async fetch methods
  async function fetchEvaluations() { loading.value = false }
  async function fetchCounselors() { loading.value = false }
  async function fetchSupervisors() { loading.value = false }
  async function addEvaluation(e: QAEvaluation) { evaluations.value.push(e) }
  async function updateEvaluation(id: number, e: Partial<QAEvaluation>) {}
  async function deleteEvaluation(id: number) {}
  function setFilter(filter: any) {}

  return {
    evaluations,
    counselors,
    supervisors,
    loading,
    error,
    filteredEvaluations,
    averageScore,
    fetchEvaluations,
    fetchCounselors,
    fetchSupervisors,
    addEvaluation,
    updateEvaluation,
    deleteEvaluation,
    setFilter
  }
}) 