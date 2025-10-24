import { createRouter, createWebHistory} from 'vue-router'
import { useAuthStore } from '@/stores/auth'
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/UserLogin.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/UserRegister.vue')
  },
  {
    path: '/',
    name: 'UserHome',
    component: () => import('@/views/UserHome.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/articles',
    name: 'UserArticles',
    component: () => import('@/views/UserArticles.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
