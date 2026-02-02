import { defineStore } from 'pinia'

export const useSearchStore = defineStore('search', {
    state: () => ({
        query: '',
        isFocused: false
    }),
    actions: {
        setQuery(q) {
            this.query = q
        },
        clearQuery() {
            this.query = ''
        }
    }
})
