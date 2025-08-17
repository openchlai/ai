export interface Category {
  id: number
  title: string
  description: string
  count: number
  lastUpdated: Date
}

export interface CategoryForm {
  title: string
  description: string
} 