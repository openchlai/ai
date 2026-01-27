<template>
    <Transition enter-active-class="transform transition ease-out duration-300"
        enter-from-class="translate-y-4 opacity-0 scale-95" enter-to-class="translate-y-0 opacity-100 scale-100"
        leave-active-class="transform transition ease-in duration-200"
        leave-from-class="translate-y-0 opacity-100 scale-100" leave-to-class="translate-y-4 opacity-0 scale-95">

        <div v-if="activeCallStore.callState === 'ringing'" class="fixed bottom-6 right-6 z-[100]">
            <div
                class="bg-white dark:bg-neutral-900 rounded-3xl shadow-2xl overflow-hidden border border-gray-100 dark:border-neutral-800 w-80">

                <!-- Header / Caller Info -->
                <div
                    class="p-6 text-center bg-gradient-to-b from-gray-50 to-white dark:from-neutral-800 dark:to-neutral-900 border-b border-gray-100 dark:border-neutral-800">
                    <div
                        class="w-16 h-16 mx-auto mb-4 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center animate-bounce">
                        <i-mdi-phone class="w-8 h-8 text-amber-600 dark:text-amber-500" />
                    </div>
                    <h3 class="text-sm font-black uppercase tracking-widest text-amber-600 dark:text-amber-500 mb-1">
                        Incoming Call
                    </h3>
                    <p class="text-2xl font-black tracking-tight" :class="isDarkMode ? 'text-white' : 'text-gray-900'">
                        {{ activeCallStore.callerNumber }}
                    </p>
                    <p class="text-xs mt-2 opacity-50 font-mono">
                        ID: {{ activeCallStore.ssid }}
                    </p>
                </div>

                <!-- Actions -->
                <div class="grid grid-cols-2">
                    <button @click="activeCallStore.hangupCall"
                        class="p-4 flex flex-col items-center justify-center gap-1 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors group border-r border-gray-100 dark:border-neutral-800">
                        <i-mdi-phone-hangup class="w-6 h-6 text-red-500 group-hover:scale-110 transition-transform" />
                        <span class="text-[10px] font-bold uppercase tracking-widest text-red-500">Reject</span>
                    </button>
                    <button @click="activeCallStore.answerCall"
                        class="p-4 flex flex-col items-center justify-center gap-1 hover:bg-emerald-50 dark:hover:bg-emerald-900/20 transition-colors group">
                        <i-mdi-phone class="w-6 h-6 text-emerald-500 group-hover:scale-110 transition-transform" />
                        <span class="text-[10px] font-bold uppercase tracking-widest text-emerald-500">Answer</span>
                    </button>
                </div>

            </div>
        </div>

    </Transition>
</template>

<script setup>
    import { inject } from 'vue'
    import { useActiveCallStore } from '@/stores/activeCall'

    const activeCallStore = useActiveCallStore()
    const isDarkMode = inject('isDarkMode')

    import { watch } from 'vue'
    watch(() => activeCallStore.callState, (newState) => {
        console.log('[IncomingCallPopup] callState changed to:', newState)
    })
</script>
