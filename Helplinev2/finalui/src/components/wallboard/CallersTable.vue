<template>
  <div 
    class="rounded-lg shadow-xl border"
    :class="isDarkMode 
      ? 'bg-neutral-900 border-transparent' 
      : 'bg-white border-transparent'"
  >
    <!-- Header -->
    <div 
      class="px-4 py-3 border-b flex items-center justify-between"
      :class="isDarkMode 
        ? 'bg-black/60 border-transparent' 
        : 'bg-gray-50 border-transparent'"
    >
      <h2 
        class="text-sm font-bold flex items-center gap-2"
        :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
      >
        <i-mdi-phone-incoming 
          class="w-5 h-5"
          :class="isDarkMode ? 'text-emerald-400' : 'text-emerald-600'"
        />
        Callers Online
        <span 
          class="px-2 py-0.5 rounded-full text-xs font-semibold border"
          :class="isDarkMode 
            ? 'bg-emerald-600/20 text-emerald-400 border-emerald-600/30' 
            : 'bg-emerald-100 text-emerald-700 border-emerald-300'"
        >
          {{ onlineCount }}
        </span>
      </h2>
    </div>

    <!-- Table Container with Fixed Height -->
    <div class="overflow-hidden" style="height: 280px;">
      <!-- Table Headers -->
      <div 
        class="border-b px-4 py-2"
        :class="isDarkMode 
          ? 'bg-black/40 border-transparent' 
          : 'bg-gray-50 border-transparent'"
      >
        <div 
          class="grid gap-4 text-xs font-semibold uppercase tracking-wide"
          :class="isDarkMode ? 'text-gray-400' : 'text-gray-700'"
          style="grid-template-columns: 1fr 120px 100px 140px;"
        >
          <div>Caller Number</div>
          <div>Queue</div>
          <div>Wait Time</div>
          <div>Status</div>
        </div>
      </div>

      <!-- Scrollable Content -->
      <div 
        ref="tableContainer"
        class="overflow-y-auto"
        :class="isDarkMode ? 'scrollbar-dark' : 'scrollbar-light'"
        style="height: 236px; scroll-behavior: smooth;"
      >
        <!-- Empty State -->
        <div v-if="callers.length === 0" class="flex items-center justify-center h-full">
          <div 
            class="italic text-sm"
            :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
          >
            No callers currently online
          </div>
        </div>

        <!-- Table Rows -->
        <div 
          v-for="caller in callers" 
          :key="caller.id"
          class="px-4 py-2 border-b transition-all duration-200"
          :class="isDarkMode 
            ? 'border-transparent/50 hover:bg-neutral-800' 
            : 'border-transparent hover:bg-gray-50'"
        >
          <div 
            class="grid gap-4 text-sm items-center"
            style="grid-template-columns: 1fr 120px 100px 140px;"
          >
            <div 
              class="font-medium"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-900'"
            >
              {{ caller.callerNumber || '--' }}
            </div>
            <div :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'">
              {{ caller.vector || '--' }}
            </div>
            <div :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'">
              {{ caller.waitTime || '--' }}
            </div>
            <div>
              <span :class="['text-xs font-semibold px-2 py-1 rounded-full', getStatusClass(caller.queueStatus)]">
                {{ caller.queueStatus || 'Unknown' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, watch, nextTick, inject } from 'vue'

export default {
  name: 'CallersTable',
  props: {
    callers: {
      type: Array,
      required: true,
      default: () => []
    },
    onlineCount: {
      type: Number,
      required: true,
      default: 0
    }
  },
  setup(props) {
    const isDarkMode = inject('isDarkMode')
    const tableContainer = ref(null)
    let scrollInterval = null

    const setupAutoScroll = (container, scrollSpeed = 0.5, pauseDuration = 3000) => {
      if (!container) return null
      
      let direction = 1
      let isPaused = false
      
      return setInterval(() => {
        if (isPaused || !container) return
        
        const { scrollTop, scrollHeight, clientHeight } = container
        const maxScroll = scrollHeight - clientHeight
        
        if (maxScroll <= 0) return
        
        if (scrollTop >= maxScroll - 2) {
          direction = -1
          isPaused = true
          setTimeout(() => { isPaused = false }, pauseDuration)
        } else if (scrollTop <= 2) {
          direction = 1
          isPaused = true
          setTimeout(() => { isPaused = false }, pauseDuration)
        }
        
        container.scrollBy(0, direction * scrollSpeed)
      }, 30)
    }

    const startAutoScroll = () => {
      nextTick(() => {
        if (tableContainer.value) {
          scrollInterval = setupAutoScroll(tableContainer.value)
        }
      })
    }

    const stopAutoScroll = () => {
      if (scrollInterval) {
        clearInterval(scrollInterval)
        scrollInterval = null
      }
    }

    watch(() => props.callers, () => {
      stopAutoScroll()
      setTimeout(startAutoScroll, 1000)
    })

    onMounted(() => {
      setTimeout(startAutoScroll, 2000)
    })

    onBeforeUnmount(() => {
      stopAutoScroll()
    })

    return {
      isDarkMode,
      tableContainer
    }
  },
  methods: {
    getStatusClass(status) {
      const s = (status || 'Available').toString().toLowerCase()
      
      if (s.includes('on call')) {
        return this.isDarkMode 
          ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-600/30'
          : 'bg-emerald-100 text-emerald-700 border border-emerald-300'
      }
      if (s.includes('ring')) {
        return this.isDarkMode 
          ? 'bg-amber-600/20 text-amber-400 border border-amber-600/30 animate-pulse'
          : 'bg-amber-100 text-amber-700 border border-amber-300 animate-pulse'
      }
      if (s.includes('queue')) {
        return this.isDarkMode 
          ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-600/30'
          : 'bg-amber-600/10 text-amber-600 border border-amber-600/20'
      }
      if (s.includes('available')) {
        return this.isDarkMode 
          ? 'bg-gray-600/20 text-gray-400 border border-transparent/30'
          : 'bg-gray-100 text-gray-700 border border-transparent'
      }
      if (s.includes('offline')) {
        return this.isDarkMode 
          ? 'bg-red-600/20 text-red-400 border border-red-600/30'
          : 'bg-red-100 text-red-700 border border-red-300'
      }
      
      return this.isDarkMode 
        ? 'bg-gray-600/20 text-gray-400'
        : 'bg-gray-100 text-gray-700'
    }
  }
}
</script>

<style scoped>
/* Dark mode scrollbar */
.scrollbar-dark::-webkit-scrollbar {
  width: 6px;
}

.scrollbar-dark::-webkit-scrollbar-track {
  background: rgba(31, 41, 55, 0.5);
  border-radius: 3px;
}

.scrollbar-dark::-webkit-scrollbar-thumb {
  background: rgba(75, 85, 99, 0.5);
  border-radius: 3px;
}

.scrollbar-dark::-webkit-scrollbar-thumb:hover {
  background: rgba(75, 85, 99, 0.7);
}

/* Light mode scrollbar */
.scrollbar-light::-webkit-scrollbar {
  width: 6px;
}

.scrollbar-light::-webkit-scrollbar-track {
  background: rgba(229, 231, 235, 0.5);
  border-radius: 3px;
}

.scrollbar-light::-webkit-scrollbar-thumb {
  background: rgba(156, 163, 175, 0.5);
  border-radius: 3px;
}

.scrollbar-light::-webkit-scrollbar-thumb:hover {
  background: rgba(156, 163, 175, 0.7);
}
</style>