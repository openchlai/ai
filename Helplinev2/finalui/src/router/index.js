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
// import Categories from '../pages/Categories.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },

  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true, permission: 'dashboard' }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: Reports,
    meta: { requiresAuth: true, permission: 'reports' }
  },
  {
    path: '/calls',
    name: 'Calls',
    component: Calls,
    meta: { requiresAuth: true, permission: 'calls' }
  },
  {
    path: '/cases',
    name: 'Cases',
    component: Cases,
    meta: { requiresAuth: true, permission: 'cases' }
  },
  {
    path: '/messages',
    name: 'Messages',
    component: Messages,
    meta: { requiresAuth: true, permission: 'messages' }
  },
  {
    path: '/wallboard',
    name: 'Wallboard',
    component: Wallboard,
    meta: { requiresAuth: true, permission: 'wallboard' }
  },
  {
    path: '/qa',
    name: 'Qa',
    component: Qa,
    meta: { requiresAuth: true, permission: 'qa' }
  },
  {
    path: '/users',
    name: 'Users',
    component: Users,
    meta: { requiresAuth: true, permission: 'users' }
  },
  {
    path: '/case-creation',
    name: 'CaseCreation',
    component: CaseCreation,
    meta: { requiresAuth: true, permission: 'cases' }
  },
  {
    path: '/qa-creation',
    name: 'QaCreation',
    component: QaCreation,
    meta: { requiresAuth: true, permission: 'qa' }
  },
  {
    path: '/activities',
    name: 'Activities',
    component: Activities,
    meta: { requiresAuth: true, permission: 'activities' }
  },
  {
    path: '/faqs',
    name: 'FAQs',
    component: FAQs,
    meta: { requiresAuth: true, permission: 'faqs' }
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

  console.log('🔄 Navigation Guard:', {
    to: to.path,
    isAuthenticated: authStore.isAuthenticated,
    hasSession: !!authStore.sessionId,
    hasRole: !!authStore.userRole
  })

  // Allow access to routes that don't require auth
  if (to.meta.requiresAuth === false) {
    if (to.name === 'Login' && authStore.isAuthenticated) {
      console.log('✅ Already authenticated, redirecting to dashboard')
      next('/')
    } else {
      next()
    }
    return
  }

  // Check authentication - ALL fields required
  if (!authStore.isAuthenticated) {
    console.warn('🔒 Not properly authenticated, redirecting to login')
    console.warn('Session ID:', authStore.sessionId)
    console.warn('User Role:', authStore.userRole)

    // Clear any partial data
    authStore.clearAuthData()
    next('/login')
    return
  }

  // Check permissions
  if (to.meta.permission) {
    if (authStore.hasPermission(to.meta.permission)) {
      console.log('✅ Permission granted for', to.meta.permission)
      next()
    } else {
      console.warn(`⚠️ Access denied to ${to.path} for role ${authStore.roleDisplayName}`)

      if (to.path === '/') {
        next(false)
      } else {
        next('/')
      }
    }
    return
  }

  next()
})

export default router