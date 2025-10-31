import { createRouter, createWebHistory } from 'vue-router'

// Pages
import Login from '@/pages/Login.vue'
import Dashboard from '@/pages/Dashboard.vue'
import Reports from '@/pages/Reports.vue'
import Calls from '@/pages/Calls.vue'
import Cases from '@/pages/Cases.vue'
import Transcribe from '@/pages/Transcribe.vue'
import Wallboard from '@/pages/Wallboard.vue'
import Qa from '@/pages/Qa.vue'
import Demo from '../pages/Demo.vue'
import Messages from '../pages/Messages.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { layout: 'none' } // hide sidebar
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  { path: '/reports', name: 'Reports', component: Reports, meta: { requiresAuth: true } },
  { path: '/calls', name: 'Calls', component: Calls, meta: { requiresAuth: true } },
  { path: '/cases', name: 'Cases', component: Cases, meta: { requiresAuth: true } },
  { path: '/messages', name: 'messages', component: Messages, meta: { requiresAuth: true } },
  { path: '/transcribe', name: 'Transcribe', component: Transcribe, meta: { requiresAuth: true } },
  { path: '/wallboard', name: 'Wallboard', component: Wallboard, meta: { requiresAuth: true } },
  { path: '/qa', name: 'Qa', component: Qa, meta: { requiresAuth: true } },
  { path: '/demo', name: 'Demo', component: Demo, meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const sessionId = localStorage.getItem('session-id')
  if (to.meta.requiresAuth && !sessionId) {
    next('/login')
  } else {
    next()
  }
})



export default router
