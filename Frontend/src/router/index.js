import { createRouter, createWebHistory } from 'vue-router'
import { useStore } from '../store'
import axios from '../api/axios'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/recognize',
    name: 'Recognize',
    component: () => import('../views/Recognize.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/batch-recognize',
    name: 'BatchRecognize',
    component: () => import('../views/BatchRecognize.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/agent',
    name: 'Agent',
    component: () => import('../views/Agent.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/pets',
    name: 'Pets',
    component: () => import('../views/Pets.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/health',
    name: 'HealthRecords',
    component: () => import('../views/HealthRecords.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/schedule',
    name: 'Schedule',
    component: () => import('../views/Schedule.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('../views/Favorites.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/feedback',
    name: 'Feedback',
    component: () => import('../views/Feedback.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/announcements',
    name: 'Announcements',
    component: () => import('../views/Announcements.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/breed/:name',
    name: 'BreedDetail',
    component: () => import('../views/BreedDetail.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/Admin.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: () => import('../views/admin/Users.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/stats',
    name: 'AdminStats',
    component: () => import('../views/admin/Stats.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/feedback',
    name: 'AdminFeedback',
    component: () => import('../views/admin/Feedback.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/announcements',
    name: 'AdminAnnouncements',
    component: () => import('../views/admin/Announcements.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  let user = null
  try {
    user = JSON.parse(localStorage.getItem('user') || 'null')
  } catch (e) {
    console.error('Failed to parse user from localStorage:', e)
  }
  let isLoggedIn = !!token && user !== null
  
  if (isLoggedIn && to.meta.requiresAuth) {
    try {
      await axios.get('/auth/profile')
    } catch (error) {
      console.log('Token validation failed, clearing localStorage')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      isLoggedIn = false
    }
  }
  
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
  } else if (to.meta.requiresAdmin && user?.role !== 'admin') {
    next('/')
  } else {
    next()
  }
})

// 添加新的管理页面路由
router.addRoute('admin', {
  path: '/admin/models',
  name: 'AdminModels',
  component: () => import('../views/admin/Models.vue'),
  meta: { requiresAuth: true, requiresAdmin: true }
})

router.addRoute('admin', {
  path: '/admin/knowledge',
  name: 'AdminKnowledge',
  component: () => import('../views/admin/Knowledge.vue'),
  meta: { requiresAuth: true, requiresAdmin: true }
})

router.addRoute('admin', {
  path: '/admin/samples',
  name: 'AdminSamples',
  component: () => import('../views/admin/Samples.vue'),
  meta: { requiresAuth: true, requiresAdmin: true }
})

router.addRoute('admin', {
  path: '/admin/sensitive-words',
  name: 'AdminSensitiveWords',
  component: () => import('../views/admin/SensitiveWords.vue'),
  meta: { requiresAuth: true, requiresAdmin: true }
})

router.addRoute('admin', {
  path: '/admin/rate-limits',
  name: 'AdminRateLimits',
  component: () => import('../views/admin/RateLimits.vue'),
  meta: { requiresAuth: true, requiresAdmin: true }
})

router.addRoute('admin', {
  path: '/admin/prompts',
  name: 'AdminPrompts',
  component: () => import('../views/admin/Prompts.vue'),
  meta: { requiresAuth: true, requiresAdmin: true }
})

router.addRoute('admin', {
  path: '/admin/corrections',
  name: 'AdminCorrections',
  component: () => import('../views/admin/Corrections.vue'),
  meta: { requiresAuth: true, requiresAdmin: true }
})

router.addRoute('admin', {
  path: '/admin/logs',
  name: 'AdminLogs',
  component: () => import('../views/admin/Logs.vue'),
  meta: { requiresAuth: true, requiresAdmin: true }
})

export default router