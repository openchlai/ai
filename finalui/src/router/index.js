import { createRouter, createWebHistory } from 'vue-router'

// Pages
import Login from '@/pages/Login.vue'
import Dashboard from '@/pages/Dashboard.vue'
import Reports from '@/pages/Reports.vue'
import Calls from '@/pages/Calls.vue'
import Cases from '@/pages/Cases.vue'
import Wallboard from '@/pages/Wallboard.vue'
import Qa from '@/pages/Qa.vue'
import Demo from '@/pages/Demo.vue'
import Messages from '@/pages/Messages.vue'
import Users from '@/pages/Users.vue'
import CaseCreation from '@/pages/CaseCreation.vue'
import QaCreation from '@/pages/QaCreation.vue'

const routes = [
  { path: '/login', name: 'Login', component: Login, meta: { layout: 'none' } },

  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/reports', name: 'Reports', component: Reports },
  { path: '/calls', name: 'Calls', component: Calls },
  { path: '/cases', name: 'Cases', component: Cases },
  { path: '/messages', name: 'Messages', component: Messages },
  { path: '/wallboard', name: 'Wallboard', component: Wallboard },
  { path: '/qa', name: 'Qa', component: Qa },
  { path: '/users', name: 'Users', component: Users },
  { path: '/case-creation', name: 'CaseCreation', component: CaseCreation },
  { path: '/qa-creation', name: 'QaCreation', component: QaCreation },

  { path: '/demo', name: 'Demo', component: Demo },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// ✅ Remove authentication enforcement
router.beforeEach((to, from, next) => {
  next()
})

export default router
