<template>
  <div class="max-w-xl bg-white p-6 rounded-lg shadow">
    <h2 class="text-xl font-bold mb-4 text-gray-800">Create User</h2>

    <form @submit.prevent="submitForm" class="space-y-4">

      <!-- Username -->
      <div>
        <label class="block text-gray-700 mb-1">Username *</label>
        <input v-model="form.usn" type="text" required class="w-full border px-3 py-2 rounded" />
      </div>

      <!-- First Name -->
      <div>
        <label class="block text-gray-700 mb-1">First Name *</label>
        <input v-model="form.fname" type="text" required class="w-full border px-3 py-2 rounded" />
      </div>

      <!-- Last Name -->
      <div>
        <label class="block text-gray-700 mb-1">Last Name *</label>
        <input v-model="form.lname" type="text" required class="w-full border px-3 py-2 rounded" />
      </div>

      <!-- Role (Dropdown) -->
      <div>
        <label class="block text-gray-700 mb-1">Role *</label>
        <select v-model="form.role" required class="w-full border px-3 py-2 rounded">
          <option disabled value="">Select Role</option>
          <option v-for="r in roles" :key="r.id" :value="r.id">
            {{ r.name }}
          </option>
        </select>
      </div>

      <!-- Phone -->
      <div>
        <label class="block text-gray-700 mb-1">Phone</label>
        <input v-model="form.phone" type="text" class="w-full border px-3 py-2 rounded" />
      </div>

      <!-- Email -->
      <div>
        <label class="block text-gray-700 mb-1">Email</label>
        <input v-model="form.email" type="email" class="w-full border px-3 py-2 rounded" />
      </div>

      <!-- Is Active -->
      <div class="flex items-center gap-2">
        <input type="checkbox" v-model="isActive" class="h-4 w-4" />
        <label class="text-gray-700">Active User</label>
      </div>

      <button
        type="submit"
        class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
      >
        Save User
      </button>

    </form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useUserStore } from '@/stores/users';

const emit = defineEmits(["saved"]);
const store = useUserStore();

// Backend Role Mapping
const roles = [
  { id: "1", name: "Counsellor" },
  { id: "2", name: "Supervisor" },
  { id: "3", name: "Case Manager" },
  { id: "4", name: "Case Worker" },
  { id: "5", name: "Partner" },
  { id: "6", name: "Media Account" },
  { id: "99", name: "Administrator" },
];

const form = reactive({
  usn: "",
  fname: "",
  lname: "",
  role: "",
  phone: "",
  email: ""
});

// Boolean toggle for active state
const isActive = ref(true);

const submitForm = async () => {
  const payload = {
    ...form,
    is_active: isActive.value ? 1 : 0,   // convert to integer
  };

  await store.createUser(payload);
  emit("saved");
};
</script>
