<template>
  <div>
    <!-- SidePanel Component -->
    <SidePanel
      :userRole="userRole"
      :isInQueue="isInQueue"
      :isProcessingQueue="isProcessingQueue"
      :currentCall="currentCall"
      @toggle-queue="handleQueueToggle"
      @logout="handleLogout"
      @sidebar-toggle="handleSidebarToggle"
    />

    <!-- Main Content -->
    <div class="main-content">
      <div class="page-container">
        <!-- Header -->
        <div class="header">
          <div class="header-content">
            <h1>Reports</h1>
            <p>Generate and view comprehensive reports across all categories</p>
          </div>
        </div>

        <!-- Report Categories -->
        <div class="reports-bento">
          <!-- Calls Reports Card -->
          <div class="bento-card calls-card" @click="navigateToReports('calls')">
            <div class="card-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <path d="M22 16.92V19.92C22.0011 20.1985 21.9441 20.4742 21.8325 20.7294C21.7209 20.9846 21.5573 21.2136 21.3521 21.4019C21.1469 21.5902 20.9046 21.7335 20.6407 21.8227C20.3768 21.9119 20.0973 21.9452 19.82 21.92H4.18C3.90273 21.9452 3.62323 21.9119 3.35932 21.8227C3.09542 21.7335 2.85313 21.5902 2.64794 21.4019C2.44275 21.2136 2.27912 20.9846 2.16753 20.7294C2.05594 20.4742 1.99889 20.1985 2 19.92V16.92L8.9 10.02C9.2836 9.63647 9.7662 9.42969 10.27 9.42969C10.7738 9.42969 11.2564 9.63647 11.64 10.02L22 16.92Z" stroke="currentColor" stroke-width="2"/>
                <path d="M2 16.92L8.9 10.02C9.2836 9.63647 9.7662 9.42969 10.27 9.42969C10.7738 9.42969 11.2564 9.63647 11.64 10.02L22 16.92" stroke="currentColor" stroke-width="2"/>
                <path d="M22 16.92V19.92C22.0011 20.1985 21.9441 20.4742 21.8325 20.7294C21.7209 20.9846 21.5573 21.2136 21.3521 21.4019C21.1469 21.5902 20.9046 21.7335 20.6407 21.8227C20.3768 21.9119 20.0973 21.9452 19.82 21.92H4.18C3.90273 21.9452 3.62323 21.9119 3.35932 21.8227C3.09542 21.7335 2.85313 21.5902 2.64794 21.4019C2.44275 21.2136 2.27912 20.9846 2.16753 20.7294C2.05594 20.4742 1.99889 20.1985 2 19.92V16.92" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div class="card-content">
              <h3>Calls Reports</h3>
              <p>View detailed call analytics, duration, and performance metrics</p>
            </div>
            <div class="card-arrow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>

          <!-- Cases Reports Card -->
          <div class="bento-card cases-card" @click="navigateToReports('cases')">
            <div class="card-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2"/>
                <path d="M14 2V8H20" stroke="currentColor" stroke-width="2"/>
                <path d="M16 13H8" stroke="currentColor" stroke-width="2"/>
                <path d="M16 17H8" stroke="currentColor" stroke-width="2"/>
                <path d="M10 9H8" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div class="card-content">
              <h3>Cases Reports</h3>
              <p>Track case progress, resolution times, and outcome statistics</p>
            </div>
            <div class="card-arrow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>

          <!-- Counsellors Reports Card -->
          <div class="bento-card counsellors-card" @click="navigateToReports('counsellors')">
            <div class="card-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2"/>
                <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div class="card-content">
              <h3>Counsellors Reports</h3>
              <p>Monitor counsellor performance, workload, and effectiveness</p>
            </div>
            <div class="card-arrow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>

          <!-- All Reports Card -->
          <div class="bento-card all-card" @click="navigateToReports('all')">
            <div class="card-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <path d="M9 17V7H21V17H9Z" stroke="currentColor" stroke-width="2"/>
                <path d="M3 7H7" stroke="currentColor" stroke-width="2"/>
                <path d="M3 11H7" stroke="currentColor" stroke-width="2"/>
                <path d="M3 15H7" stroke="currentColor" stroke-width="2"/>
                <path d="M3 19H7" stroke="currentColor" stroke-width="2"/>
                <path d="M13 11H17" stroke="currentColor" stroke-width="2"/>
                <path d="M13 15H17" stroke="currentColor" stroke-width="2"/>
                <path d="M13 19H17" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div class="card-content">
              <h3>All Reports</h3>
              <p>Comprehensive overview of all system metrics and analytics</p>
            </div>
            <div class="card-arrow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import SidePanel from '@/components/SidePanel.vue'

const router = useRouter()

// SidePanel props and state
const userRole = ref("admin")
const isInQueue = ref(false)
const isProcessingQueue = ref(false)
const currentCall = ref(null)

// SidePanel event handlers
const handleQueueToggle = () => {
  isInQueue.value = !isInQueue.value
}

const handleLogout = () => {
  // Handle logout logic
  console.log("Logout clicked")
}

const handleSidebarToggle = () => {
  // Handle sidebar toggle
  console.log("Sidebar toggle clicked")
}

// Navigation function
const navigateToReports = (category) => {
  router.push({
    name: 'ReportsCategory',
    params: { category }
  })
}
</script>

<style scoped>
/* Reports styles moved to global components.css */
</style>

