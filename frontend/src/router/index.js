import { createRouter, createWebHistory } from 'vue-router'

import Login from '../pages/Login.vue'
import Dashboard from '../pages/Dashboard.vue'
import Calls from '../pages/Calls.vue'
import Cases from '../pages/Cases.vue'
import Chats from '../pages/Chats.vue'
import QAStatistics from '../pages/QAStatistics.vue'
import Wallboard from '../pages/Wallboard.vue'
import Settings from '../pages/Settings.vue'
import EditProfile from '../pages/EditProfile.vue'
import CaseCreation from '../pages/CaseCreation.vue'
import superadmin from '../pages/SuperAdminDashboard.vue'
import TestCall from '../pages/TestCall.vue'
import Reports from '../pages/Reports.vue'
import ReportsCategory from '../pages/ReportsCategory.vue'
import TranscriptionReviews from '../pages/TranscriptionReviews.vue'

// Admin Components
import AdminLayout from '../pages/admin/AdminLayout.vue'
import AdminDashboard from '../pages/admin/AdminDashboard.vue'
import AdminCases from '../pages/admin/AdminCases.vue'
import AdminUsers from '../pages/admin/AdminUsers.vue'
import AdminReports from '../pages/admin/AdminReports.vue'
import AdminAIAssistant from '../pages/admin/AdminAIAssistant.vue'
import AdminCategories from '../pages/admin/AdminCategories.vue'
import AdminWorkflows from '../pages/admin/AdminWorkflows.vue'
import AdminSettings from '../pages/admin/AdminSettings.vue'
import Demo from '../pages/Demo.vue'


const routes = [
  { path: '/', component: Login },
  { path: '/dashboard', component: Dashboard, name: 'Dashboard' },
  { path: '/calls', component: Calls, name: 'Calls' },
  { path: '/cases', component: Cases, name: 'Cases' },
  { path: '/chats', component: Chats, name: 'Chats' },
  { path: '/qa-statistics', component: QAStatistics, name: 'QAStatistics' },
  { path: '/wallboard', component: Wallboard, name: 'Wallboard' },
  { path: '/settings', component: Settings, name: 'Settings' },
  { path: '/edit-profile', component: EditProfile, name: 'EditProfile' },
  { path: '/case-creation', component: CaseCreation, name: 'CaseCreation' },
  { path: '/superadmin', component: superadmin, name: 'SuperAdmin' },
  { path: '/test-call', component: TestCall, name: 'TestCall' },
  { path: '/reports', component: Reports, name: 'Reports' },
  { path: '/reports/:category', component: ReportsCategory, name: 'ReportsCategory' },
  { path: '/reviews', component: TranscriptionReviews, name: 'TranscriptionReviews' },
  { path: '/demo', component: Demo, name: 'Demo' },
  
  // Admin Routes
  {
    path: '/admin',
    component: AdminLayout,
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', component: AdminDashboard, name: 'AdminDashboard' },
      { path: 'cases', component: AdminCases, name: 'AdminCases' },
      { path: 'users', component: AdminUsers, name: 'AdminUsers' },
      { path: 'reports', component: AdminReports, name: 'AdminReports' },
      { path: 'ai-assistant', component: AdminAIAssistant, name: 'AdminAIAssistant' },
      { path: 'categories', component: AdminCategories, name: 'AdminCategories' },
      { path: 'workflows', component: AdminWorkflows, name: 'AdminWorkflows' },
      { path: 'settings', component: AdminSettings, name: 'AdminSettings' }
    ]
  }
]

export const router = createRouter({
  history: createWebHistory(),
  routes
})