<template>
  <div class="flex space-x-2 mb-4">
    <button
      v-for="platform in channelFilters"
      :key="platform.id"
      :class="['px-4 py-2 rounded-full border', activePlatform === platform.id ? 'bg-blue-500 text-white' : 'bg-white text-gray-700 border-gray-300']"
      @click="$emit('update:activePlatform', platform.id)"
    >
      {{ platform.name }}
    </button>
  </div>
</template>

<script setup>
const props = defineProps({
  channelFilters: Array,
  activePlatform: String,
});
</script>
