<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-800">System Users</h1>

      <div class="flex gap-3 mb-4">
        <button
          @click="view = 'table'"
          class="px-4 py-2 rounded bg-blue-600 text-white"
        >
          Table
        </button>

        <button
          @click="view = 'timeline'"
          class="px-4 py-2 rounded bg-green-600 text-white"
        >
          Timeline
        </button>

        <button
          @click="view = 'create'"
          class="px-4 py-2 rounded bg-amber-600 text-white"
        >
          Create User
        </button>
      </div>
    </div>

    <!-- Switch Components -->
    <UsersTable v-if="view === 'table'" />
    <UsersTimeline v-else-if="view === 'timeline'" />
    <UserForm v-else @saved="handleSaved" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/stores/users';
import UsersTable from '@/components/users/Table.vue';
import UsersTimeline from '@/components/users/Timeline.vue';
import UserForm from '@/components/users/UserForm.vue';

const store = useUserStore();
const view = ref('table');

onMounted(() => {
  store.listUsers();
});

const handleSaved = () => {
  view.value = 'table';
  store.listUsers();
};
</script>
