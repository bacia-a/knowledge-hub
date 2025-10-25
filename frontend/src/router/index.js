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
  component: () => import('@/components/CLayout.vue'),  // 使用 Layout 组件
  meta: { requiresAuth: true },
  children: [
    {
      path: '',
      name: 'Home',
      component: () => import('@/views/UserHome.vue')  // 纯内容组件
    },
    {
      path: 'articles',
      name: 'Articles',
      component: () => import('@/views/UserArticles.vue')  // 纯内容组件
    },
    {
      path: '/categories',
      name: 'Categories',
      component: () => import('@/views/UserCategories.vue')
    },
    {
      path: '/article/:id',
      name: 'ArticleDetail',
      component: () => import('@/views/ArticleDetail.vue'),
    }
  ]
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
