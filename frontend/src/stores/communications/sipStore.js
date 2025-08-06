import { defineStore } from 'pinia'

export const useSIPStore = defineStore('sip', {
    state: () => ({
        uri: '',
        password: '',
        websocketURL: ''
    }),
    actions: {
        loadFromLocalStorage() {
            this.uri = localStorage.getItem('sipConnectionDetails.uri')
            this.password = localStorage.getItem('sipConnectionDetails.password')
            this.websocketURL = localStorage.getItem('sipConnectionDetails.websocketURL')
        }
    }
})
