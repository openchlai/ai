<template>
  <div class="main-scroll-content">
    <!-- Settings Grid -->
    <div class="settings-grid">
      <!-- Organization Settings -->
      <div class="settings-group glass-card fine-border">
        <div class="group-title">Organization Settings</div>
        <div class="settings-items">
          <div class="setting-item">
            <label class="setting-label">Organization Name</label>
            <input
              class="setting-input"
              type="text"
              v-model="settings.organizationName"
              placeholder="Enter organization name"
            />
          </div>
          <div class="setting-item">
            <label class="setting-label">Location</label>
            <input
              class="setting-input"
              type="text"
              v-model="settings.location"
              placeholder="Enter location"
            />
          </div>
          <div class="setting-item">
            <label class="setting-label">Contact Email</label>
            <input
              class="setting-input"
              type="email"
              v-model="settings.contactEmail"
              placeholder="Enter contact email"
            />
          </div>
          <div class="setting-item">
            <label class="setting-label">Phone Number</label>
            <input
              class="setting-input"
              type="tel"
              v-model="settings.phoneNumber"
              placeholder="Enter phone number"
            />
          </div>
        </div>
      </div>

      <!-- Case Management Settings -->
      <div class="settings-group glass-card fine-border">
        <div class="group-title">Case Management</div>
        <div class="settings-items">
          <div class="setting-item">
            <label class="setting-label">Case Number Prefix</label>
            <input
              class="setting-input"
              type="text"
              v-model="settings.casePrefix"
              placeholder="Enter case prefix"
            />
          </div>
          <div class="setting-item">
            <label class="setting-label">Default Priority</label>
            <select class="setting-select" v-model="settings.defaultPriority">
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
              <option value="Critical">Critical</option>
            </select>
          </div>
          <div class="setting-item">
            <label class="setting-label">Auto-assign Cases</label>
            <label class="toggle-switch">
              <input type="checkbox" v-model="settings.autoAssign" />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>
      </div>

      <!-- Notification Settings -->
      <div class="settings-group glass-card fine-border">
        <div class="group-title">Notifications</div>
        <div class="settings-items">
          <div class="setting-item">
            <label class="setting-label">Email Notifications</label>
            <label class="toggle-switch">
              <input type="checkbox" v-model="settings.emailNotifications" />
              <span class="toggle-slider"></span>
            </label>
          </div>
          <div class="setting-item">
            <label class="setting-label">Assignment Alerts</label>
            <label class="toggle-switch">
              <input type="checkbox" v-model="settings.assignmentAlerts" />
              <span class="toggle-slider"></span>
            </label>
          </div>
          <div class="setting-item">
            <label class="setting-label">Deadline Reminders</label>
            <label class="toggle-switch">
              <input type="checkbox" v-model="settings.deadlineReminders" />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>
      </div>

      <!-- Security Settings -->
      <div class="settings-group glass-card fine-border">
        <div class="group-title">Security</div>
        <div class="settings-items">
          <div class="setting-item">
            <label class="setting-label">Two-Factor Authentication</label>
            <label class="toggle-switch">
              <input type="checkbox" v-model="settings.twoFactorAuth" />
              <span class="toggle-slider"></span>
            </label>
          </div>
          <div class="setting-item">
            <label class="setting-label">Session Timeout (minutes)</label>
            <input
              class="setting-input"
              type="number"
              v-model="settings.sessionTimeout"
              min="15"
              max="480"
            />
          </div>
          <div class="setting-item">
            <label class="setting-label">Password Strength</label>
            <select class="setting-select" v-model="settings.passwordStrength">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Save Settings Button -->
    <div style="text-align: center; margin-top: 30px;">
      <button class="save-settings-btn" @click="saveSettings">
        Save Settings
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Reactive data
const settings = ref({
  organizationName: "Children First Kenya",
  location: "Nairobi, Kenya",
  contactEmail: "admin@cfk.org",
  phoneNumber: "+254 700 123 456",
  casePrefix: "CASE",
  autoAssign: true,
  defaultPriority: "Medium",
  emailNotifications: true,
  assignmentAlerts: true,
  deadlineReminders: true,
  twoFactorAuth: false,
  sessionTimeout: 60,
  passwordStrength: "medium"
})

// Methods
const saveSettings = () => {
  console.log('Saving settings:', settings.value)
  alert('Settings saved successfully!')
}
</script>

<style scoped>
/* Settings specific styles are inherited from global components.css */
</style>
