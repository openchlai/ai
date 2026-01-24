<template>
  <div class="space-y-6">
     <div class="w-full flex justify-center pt-10">
        <Dialpad />
     </div>
  </div>
</template>

<script setup>
import Dialpad from '@/components/softphone/Dialpad.vue'
import { inject } from 'vue'

const isDarkMode = inject('isDarkMode')
</script>
