import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Category, CategoryForm } from '../types/category'

export const useCategoryStore = defineStore('category', () => {
  const categories = ref<Category[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchCategories() {
    loading.value = true
    error.value = null
    // Dummy fetch: replace with real API call
    categories.value = [
      { id: 1, title: 'Sample', description: 'Sample category', count: 5, lastUpdated: new Date() }
    ]
    loading.value = false
  }

  async function createCategory(form: CategoryForm) {
    // Dummy create: replace with real API call
    const newCategory: Category = {
      id: Date.now(),
      title: form.title,
      description: form.description,
      count: 0,
      lastUpdated: new Date()
    }
    categories.value.push(newCategory)
  }

  async function updateCategory(id: number, form: CategoryForm) {
    // Dummy update: replace with real API call
    const cat = categories.value.find(c => c.id === id)
    if (cat) {
      cat.title = form.title
      cat.description = form.description
      cat.lastUpdated = new Date()
    }
  }

  async function deleteCategory(id: number) {
    // Dummy delete: replace with real API call
    categories.value = categories.value.filter(c => c.id !== id)
  }

  return {
    categories,
    loading,
    error,
    fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory
  }
}) 