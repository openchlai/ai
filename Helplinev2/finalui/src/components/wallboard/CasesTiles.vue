<template>
  <div 
    class="rounded-lg shadow-xl border p-4"
    :class="isDarkMode 
      ? 'bg-neutral-900 border-transparent' 
      : 'bg-white border-transparent'"
  >
    <h3 
      class="text-lg font-bold mb-4 flex items-center gap-2"
      :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
    >
      <i-mdi-chart-box 
        class="w-5 h-5"
        :class="isDarkMode ? 'text-amber-500' : 'text-amber-600'"
      />
      Cases Overview
    </h3>
    
    <div 
      v-if="!tiles || tiles.length === 0" 
      class="flex items-center justify-center py-12"
    >
      <div 
        class="text-sm"
        :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
      >
        No case data available
      </div>
    </div>
    
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3">
      <div
        v-for="tile in tiles"
        :key="tile.id"
        :class="[
          'rounded-lg p-4 relative overflow-hidden transition-all duration-200 hover:scale-[1.02] border',
          getBgClass(tile.variant)
        ]"
      >
        <!-- Gradient Overlay -->
        <div :class="['absolute inset-0 opacity-10', getGradientClass(tile.variant)]"></div>
        
        <!-- Content -->
        <div class="relative z-10">
          <div class="flex items-start justify-between mb-2">
            <div :class="['text-3xl font-bold', getTextClass(tile.variant)]">
              {{ tile.value }}
            </div>
            <div :class="['w-10 h-10 rounded-lg flex items-center justify-center', getIconBgClass(tile.variant)]">
              <i-mdi-phone v-if="tile.icon === 'phone'" class="w-6 h-6" />
              <i-mdi-folder v-else-if="tile.icon === 'folder'" class="w-6 h-6" />
              <i-mdi-alert v-else-if="tile.icon === 'alert'" class="w-6 h-6" />
              <i-mdi-check v-else-if="tile.icon === 'check'" class="w-6 h-6" />
              <i-mdi-chart-line v-else-if="tile.icon === 'chart'" class="w-6 h-6" />
              <i-mdi-database v-else-if="tile.icon === 'database'" class="w-6 h-6" />
            </div>
          </div>
          <div 
            class="text-xs font-semibold uppercase tracking-wide"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            {{ tile.label }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { inject } from 'vue'

export default {
  name: 'CasesTiles',
  props: {
    tiles: {
      type: Array,
      required: true,
      default: () => []
    }
  },
  setup() {
    const isDarkMode = inject('isDarkMode')
    
    return {
      isDarkMode
    }
  },
  methods: {
    getBgClass(variant) {
      const darkBgMap = {
        'blue': 'bg-amber-600/10 border-amber-600/20',
        'amber': 'bg-amber-600/10 border-amber-600/20',
        'red': 'bg-red-600/10 border-red-600/20',
        'green': 'bg-emerald-600/10 border-emerald-600/20',
        'purple': 'bg-purple-600/10 border-purple-600/20',
        'indigo': 'bg-indigo-600/10 border-indigo-600/20'
      }
      
      const lightBgMap = {
        'blue': 'bg-blue-50 border-blue-200',
        'amber': 'bg-amber-50 border-amber-200',
        'red': 'bg-red-50 border-red-200',
        'green': 'bg-emerald-50 border-emerald-200',
        'purple': 'bg-purple-50 border-purple-200',
        'indigo': 'bg-indigo-50 border-indigo-200'
      }
      
      return this.isDarkMode 
        ? (darkBgMap[variant] || 'bg-gray-700/30')
        : (lightBgMap[variant] || 'bg-gray-100')
    },
    getTextClass(variant) {
      const darkTextMap = {
        'blue': 'text-amber-500',
        'amber': 'text-amber-400',
        'red': 'text-red-400',
        'green': 'text-emerald-400',
        'purple': 'text-purple-400',
        'indigo': 'text-indigo-400'
      }
      
      const lightTextMap = {
        'blue': 'text-amber-600',
        'amber': 'text-amber-600',
        'red': 'text-red-600',
        'green': 'text-emerald-600',
        'purple': 'text-purple-600',
        'indigo': 'text-indigo-600'
      }
      
      return this.isDarkMode 
        ? (darkTextMap[variant] || 'text-gray-100')
        : (lightTextMap[variant] || 'text-gray-900')
    },
    getGradientClass(variant) {
      const gradientMap = {
        'blue': 'bg-gradient-to-br from-blue-500 to-blue-600',
        'amber': 'bg-gradient-to-br from-amber-500 to-amber-600',
        'red': 'bg-gradient-to-br from-red-500 to-red-600',
        'green': 'bg-gradient-to-br from-emerald-500 to-emerald-600',
        'purple': 'bg-gradient-to-br from-purple-500 to-purple-600',
        'indigo': 'bg-gradient-to-br from-indigo-500 to-indigo-600'
      }
      return gradientMap[variant] || 'bg-gray-700'
    },
    getIconBgClass(variant) {
      const darkIconBgMap = {
        'blue': 'bg-amber-600/20 text-amber-500',
        'amber': 'bg-amber-600/20 text-amber-400',
        'red': 'bg-red-600/20 text-red-400',
        'green': 'bg-emerald-600/20 text-emerald-400',
        'purple': 'bg-purple-600/20 text-purple-400',
        'indigo': 'bg-indigo-600/20 text-indigo-400'
      }
      
      const lightIconBgMap = {
        'blue': 'bg-amber-600/10 text-amber-600',
        'amber': 'bg-amber-600/10 text-amber-600',
        'red': 'bg-red-600/10 text-red-600',
        'green': 'bg-emerald-600/10 text-emerald-600',
        'purple': 'bg-purple-600/10 text-purple-600',
        'indigo': 'bg-indigo-600/10 text-indigo-600'
      }
      
      return this.isDarkMode 
        ? (darkIconBgMap[variant] || 'bg-gray-700 text-gray-400')
        : (lightIconBgMap[variant] || 'bg-gray-200 text-gray-700')
    }
  }
}
</script>