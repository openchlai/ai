<template>
  <div class="relative border-l-2 border-gray-200 pl-6 space-y-6">

    <div
      v-for="user in store.users"
      :key="getValue(user, 'id')"
      class="relative bg-white shadow rounded-lg p-4"
    >
      <!-- Timeline Dot -->
      <div class="absolute -left-3 top-4 w-6 h-6 bg-amber-600 rounded-full border-4 border-white"></div>

      <!-- User Info -->
      <h3 class="text-lg font-semibold text-gray-800">
        {{ getValue(user, 'first_name') }} {{ getValue(user, 'last_name') }}
      </h3>

      <p class="text-sm text-gray-500">
        Username: <span class="font-medium text-gray-700">{{ getValue(user, 'usn') }}</span>
      </p>

      <p class="text-sm text-gray-600 mt-1">
        Created By: {{ getValue(user, 'created_by') || 'N/A' }}
      </p>

      <p class="text-sm text-gray-500">
        Created On: {{ formatDate(getValue(user, 'created_on')) }}
      </p>

      <!-- Role Badge -->
      <span
        class="inline-block mt-3 px-3 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-700"
      >
        {{ getValue(user, 'role') }}
      </span>
    </div>

  </div>
</template>

<script setup>
import { useUserStore } from "@/stores/users";

const store = useUserStore();

// helper to extract field values based on users_k (array index mapping)
const getValue = (userItem, key) => {
  if (!store.users_k?.[key]) return null;
  return userItem[store.users_k[key][0]];
};

// convert timestamp or hour-ts formats correctly
const formatDate = (timestamp) => {
  if (!timestamp) return 'N/A';

  const ms = timestamp < 10000000000 
    ? timestamp * 1000 
    : timestamp * 3600 * 1000;

  return new Date(ms).toLocaleString();
};
</script>
