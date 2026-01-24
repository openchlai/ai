import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

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
import Activities from '../pages/Activities.vue'
import FAQs from '@/pages/FAQs.vue'
import AiPredictions from '@/pages/AiPredictions.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { auth: false }
  },

  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { auth: true, permission: 'dashboard' }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: Reports,
    meta: { auth: true, permission: 'reports' }
  },
  {
    path: '/calls',
    name: 'Calls',
    component: Calls,
    meta: { auth: true, permission: 'calls' }
  },
  {
    path: '/cases',
    name: 'Cases',
    component: Cases,
    meta: { auth: true, permission: 'cases' }
  },
  {
    path: '/messages',
    name: 'Messages',
    component: Messages,
    meta: { auth: true, permission: 'messages' }
  },
  {
    path: '/ai-predictions',
    name: 'AiPredictions',
    component: AiPredictions,
    meta: { auth: true, permission: 'messages' }
  },
  {
    path: '/wallboard',
    name: 'Wallboard',
    component: Wallboard,
    meta: { auth: true, permission: 'wallboard' }
  },
  {
    path: '/qa',
    name: 'Qa',
    component: Qa,
    meta: { auth: true, permission: 'qa' }
  },
  {
    path: '/users',
    name: 'Users',
    component: Users,
    meta: { auth: true, permission: 'users' }
  },
  {
    path: '/case-creation',
    name: 'CaseCreation',
    component: CaseCreation,
    meta: { auth: true, permission: 'cases' }
  },
  {
    path: '/qa-creation',
    name: 'QaCreation',
    component: QaCreation,
    meta: { auth: true, permission: 'qa' }
  },
  {
    path: '/activities',
    name: 'Activities',
    component: Activities,
    meta: { auth: true, permission: 'activities' }
  },
  {
    path: '/faqs',
    name: 'FAQs',
    component: FAQs,
    meta: { auth: true, permission: 'faqs' }
  },
  // { 
  //   path: '/categories', 
  //   name: 'Categories', 
  //   component: Categories,
  //   meta: { requiresAuth: true, permission: 'categories' }
  // },

  {
    path: '/demo',
    name: 'Demo',
    component: Demo,
    meta: { requiresAuth: false }
  },
  { path: '/:pathMatch(.*)*', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Route guard for authentication and permissions
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // Allow access to routes that don't require auth
  if (to.meta.auth === false) {
    if (to.name === 'Login' && authStore.isAuthenticated) {
      next('/')
    } else {
      next()
    }
    return
  }

  // Check authentication via sessionId existence
  if (!authStore.sessionId) {
    console.warn('🔒 No session ID found, redirecting to login')
    next('/login')
    return
  }

  // Check permissions
  if (to.meta.permission) {
    if (authStore.hasPermission(to.meta.permission)) {
      next()
    } else {
      console.warn(`⚠️ Access denied to ${to.path} for role ${authStore.userRole}`)
      next('/')
    }
    return
  }

  next()
})

export default router