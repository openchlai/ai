<template>
  <div class="edit-profile-page">
    <router-link class="back-button" to="/dashboard">
      <svg fill="none" height="16" viewbox="0 0 24 24" width="16" xmlns="http://www.w3.org/2000/svg">
        <path d="M19 12H5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
        <path d="M12 19L5 12L12 5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
      </svg>
      Back
    </router-link>

    <div class="profile-container">
      <div class="profile-header">
        <h1>Edit Profile</h1>
      </div>

      <form class="profile-form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="username">Username</label>
          <input 
            v-model="formData.username"
            class="form-control" 
            disabled 
            id="username" 
            type="text"
          />
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <input 
            v-model="formData.email"
            class="form-control" 
            id="email" 
            placeholder="Enter your email" 
            type="email"
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input 
            v-model="formData.password"
            class="form-control" 
            id="password" 
            placeholder="Enter new password" 
            type="password"
          />
        </div>

        <div class="form-group">
          <label for="gender">Gender</label>
          <select 
            v-model="formData.gender"
            class="form-control" 
            id="gender"
          >
            <option value="">Select gender</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
            <option value="prefer-not-to-say">Prefer not to say</option>
          </select>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="birth-month">Birth month</label>
            <select 
              v-model="formData.birthMonth"
              class="form-control" 
              id="birth-month"
            >
              <option value="">Select month</option>
              <option v-for="month in months" :key="month.value" :value="month.value">
                {{ month.label }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="birth-date">Birth date</label>
            <input 
              v-model="formData.birthDate"
              class="form-control" 
              id="birth-date" 
              max="31" 
              min="1" 
              placeholder="Day" 
              type="number"
            />
          </div>

          <div class="form-group">
            <label for="birth-year">Birth year</label>
            <input 
              v-model="formData.birthYear"
              class="form-control" 
              id="birth-year" 
              max="2023" 
              min="1900" 
              placeholder="Year" 
              type="number"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="country">Country or Region</label>
          <select 
            v-model="formData.country"
            class="form-control" 
            id="country"
          >
            <option value="">Select country</option>
            <option v-for="country in countries" :key="country.value" :value="country.value">
              {{ country.label }}
            </option>
          </select>
        </div>

        <div class="form-check">
          <input 
            v-model="formData.marketingConsent"
            id="marketing-consent" 
            type="checkbox"
          />
          <label for="marketing-consent">
            Share my registration data with OpenCHS content providers for marketing purposes
          </label>
        </div>

        <div class="form-actions">
          <router-link to="/dashboard" class="btn btn-cancel">
            Cancel
          </router-link>
          <button class="glass-btn filled">
            Update Profile
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const formData = ref({
  username: '2783162984',
  email: '',
  password: '',
  gender: '',
  birthMonth: '07',
  birthDate: '',
  birthYear: '',
  country: '',
  marketingConsent: true
})

const months = [
  { value: '01', label: 'January' },
  { value: '02', label: 'February' },
  { value: '03', label: 'March' },
  { value: '04', label: 'April' },
  { value: '05', label: 'May' },
  { value: '06', label: 'June' },
  { value: '07', label: 'July' },
  { value: '08', label: 'August' },
  { value: '09', label: 'September' },
  { value: '10', label: 'October' },
  { value: '11', label: 'November' },
  { value: '12', label: 'December' }
]

const countries = [
  { value: 'us', label: 'United States' },
  { value: 'ca', label: 'Canada' },
  { value: 'uk', label: 'United Kingdom' },
  { value: 'au', label: 'Australia' },
  { value: 'other', label: 'Other' }
]

const handleSubmit = async () => {
  try {
    // TODO: Implement actual profile update logic
    console.log('Form submitted:', formData.value)
    await router.push('/dashboard')
  } catch (error) {
    console.error('Profile update failed:', error)
  }
}
</script>

<style scoped>
.edit-profile-page {
  background-color: var(--background-color);
  color: var(--text-color);
  min-height: 100vh;
  padding: 20px;
}

.back-button {
  background-color: var(--content-bg);
  color: var(--text-color);
  border: none;
  border-radius: 30px;
  padding: 8px 15px;
  font-size: 14px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  margin-bottom: 20px;
}

.profile-container {
  background-color: var(--content-bg);
  border-radius: 24px;
  padding: 30px;
  max-width: 600px;
  margin: 0 auto;
}

.profile-header {
  margin-bottom: 30px;
}

.profile-header h1 {
  font-size: 24px;
  font-weight: 600;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: var(--text-color);
}

.form-control {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background-color: var(--input-bg);
  color: var(--text-color);
  font-size: 14px;
}

.form-control:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.form-check {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 30px;
}

.form-check input[type="checkbox"] {
  width: 18px;
  height: 18px;
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
}

.btn {
  padding: 12px 24px;
  border-radius: 30px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
}

.btn-cancel {
  background-color: var(--content-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.btn-save {
  background-color: var(--accent-color);
  color: white;
  border: none;
}

.btn-save:hover {
  background-color: var(--accent-hover);
}

.glass-btn {
  padding: 12px 24px;
  border-radius: 30px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.glass-btn.filled {
  background-color: var(--accent-color);
  color: white;
  border: none;
}

.glass-btn.filled:hover {
  background-color: var(--accent-hover);
}
</style>
