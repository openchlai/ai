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
import AdminPanel from '../pages/AdminPanel.vue'
import TestCall from '../pages/TestCall.vue'

const routes = [
  { path: '/', component: Login },
  { path: '/dashboard', component: Dashboard },
  { path: '/calls', component: Calls },
  { path: '/cases', component: Cases },
  { path: '/chats', component: Chats },
  { path: '/qa-statistics', component: QAStatistics },
  { path: '/wallboard', component: Wallboard },
  { path: '/settings', component: Settings },
  { path: '/edit-profile', component: EditProfile },
  { path: '/case-creation', component: CaseCreation },
  { path: '/superadmin', component: superadmin },
  { path: '/admin', component: AdminPanel },
  { path: '/test-call', component: TestCall }
]

export const router = createRouter({
  history: createWebHistory(),
  routes
})