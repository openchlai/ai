<template>
  <div class="overflow-x-auto bg-white rounded-lg shadow">
    <table class="min-w-full text-sm text-left text-gray-700">
      <thead class="bg-gray-100 text-gray-700 font-semibold">
        <tr>
          <th class="px-4 py-3">Username</th>
          <th class="px-4 py-3">First Name</th>
          
          <th class="px-4 py-3">Role</th>
          <th class="px-4 py-3">Created On</th>
          <th class="px-4 py-3">Created By</th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="user in store.users"
          :key="getValue(user, 'id')"
          class="border-b hover:bg-amber-50 transition"
        >
          <td class="px-4 py-3">{{ getValue(user, 'usn') }}</td>
          <td class="px-4 py-3">{{ getValue(user, 'contact_fname') }}</td>
          
          <td class="px-4 py-3">{{ getValue(user, 'role') }}</td>
          <td class="px-4 py-3">{{ formatDate(getValue(user, 'created_on')) }}</td>
          <td class="px-4 py-3">{{ getValue(user, 'created_by') || 'N/A' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { useUserStore } from "@/stores/users";
const store = useUserStore();

const getValue = (user, key) => {
  if (!store.users_k?.[key]) return null;
  return user[store.users_k[key][0]];
};

const formatDate = (timestamp) => {
  if (!timestamp) return 'N/A';
  const ms = timestamp < 10000000000 ? timestamp * 1000 : timestamp * 3600 * 1000;
  return new Date(ms).toLocaleString();
};
</script>
