<!-- src/views/UsersView.vue -->
<script setup>
import { ref, onMounted } from 'vue';
import { useReporterStore } from "@/stores/reporters" 

const reporterStore = useReporterStore();

// Filters for list, CSV, and pivot
const filters = ref({
  _a: '',
  _c: 20,
  phone: '',
  email: ''
});

// Pivot report data
const pivotData = ref([]);
const pivotColumns = ref([]);

// Load initial user list
onMounted(() => {
  reporterStore.listReporters({ _c: filters.value._c });
});

// View User details
const handleViewUser = async (userId) => {
  try {
    const details = await reporterStore.viewUser(userId);
    alert(JSON.stringify(details, null, 2));
  } catch (err) {
    console.error('Failed to view user:', err.message);
  }
};

// Create a new user (mock data for demo)
const handleCreateUser = async () => {
  const payload = {
    usn: 'newuser',
    exten: '8123',
    photo: '123244554556',
    fname: 'Jane',
    lname: 'Doe',
    phone: '0700000000',
    email: 'jane.doe@example.com'
  };
  try {
    const created = await reporterStore.createUser(payload);
    alert('User Created: ' + JSON.stringify(created, null, 2));
    reporterStore.listReporters({ _c: filters.value._c });
  } catch (err) {
    console.error('Create failed:', err.message);
  }
};

// Edit a user (mock data for demo)
const handleEditUser = async (userId) => {
  const payload = { fname: 'UpdatedName' };
  try {
    const updated = await reporterStore.editUser(userId, payload);
    alert('User Updated: ' + JSON.stringify(updated, null, 2));
    reporterStore.listReporters({ _c: filters.value._c });
  } catch (err) {
    console.error('Edit failed:', err.message);
  }
};

// Download CSV
const handleDownloadCSV = async () => {
  try {
    const blob = await reporterStore.downloadCSV(filters.value);
    const url = window.URL.createObjectURL(new Blob([blob], { type: 'text/csv' }));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'users.csv');
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    console.error('CSV Download failed:', err.message);
  }
};

// Get Pivot Report
const handlePivotReport = async () => {
  try {
    const data = await reporterStore.getPivotReport({
      ...filters.value,
      xaxis: 'role',
      yaxis: 'enabled'
    });
    if (Array.isArray(data) && data.length > 0) {
      pivotColumns.value = Object.keys(data[0]);
      pivotData.value = data;
    } else {
      pivotColumns.value = [];
      pivotData.value = [];
    }
  } catch (err) {
    console.error('Pivot report fetch failed:', err.message);
  }
};
</script>

<template>
  <section class="users-view">
    <h2>Users List</h2>

    <!-- Filters -->
    <div class="filters">
      <input v-model="filters._a" placeholder="Start position (_a)" />
      <input v-model.number="filters._c" type="number" placeholder="Count (_c)" />
      <input v-model="filters.phone" placeholder="Phone" />
      <input v-model="filters.email" placeholder="Email" />
      <button @click="reporterStore.listReporters(filters)">Apply Filters</button>
      <button @click="handleDownloadCSV">Download CSV</button>
      <button @click="handlePivotReport">Get Pivot Report</button>
    </div>

    <!-- Error and Loading states -->
    <p v-if="reporterStore.loading">Loading…</p>
    <p v-else-if="reporterStore.error" class="error">{{ reporterStore.error }}</p>

    <!-- Users Table -->
    <div v-else>
      <h3>Total Users: {{ reporterStore.users.length }}</h3>

      <table v-if="reporterStore.users.length">
        <thead>
          <tr>
            <th v-for="(meta, key) in reporterStore.users_k" :key="key">
              {{ meta[3] || key }}
            </th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in reporterStore.users" :key="user[0]">
            <td v-for="(meta, key) in reporterStore.users_k" :key="key">
              {{ user[parseInt(meta[0])] }}
            </td>
            <td>
              <button @click="handleViewUser(user[0])">View</button>
              <button @click="handleEditUser(user[0])">Edit</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else>
        <p>No users available.</p>
      </div>

      <!-- Pivot Table -->
      <div v-if="pivotData.length" class="pivot-section">
        <h3>Pivot Report</h3>
        <table>
          <thead>
            <tr>
              <th v-for="col in pivotColumns" :key="col">{{ col }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in pivotData" :key="idx">
              <td v-for="col in pivotColumns" :key="col">{{ row[col] }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<style scoped>
.users-view {
  padding: 1rem;
}
.filters {
  margin-bottom: 1rem;
}
.filters input {
  margin-right: 8px;
}
.filters button {
  margin-right: 8px;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
}
th, td {
  border: 1px solid #ccc;
  padding: 6px 8px;
  text-align: left;
}
button {
  margin-right: 5px;
  padding: 4px 8px;
  cursor: pointer;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
}
button:hover {
  background: #45a049;
}
.error {
  color: #e74c3c;
}
</style>
