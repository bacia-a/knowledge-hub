import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login, register, getProfile } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')
  const isAuthenticated = ref(!!token.value)

  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
    isAuthenticated.value = true
  }

  const setUser = (userData) => {
    user.value = userData
  }

  const logout = () => {
    user.value = null
    token.value = ''
    isAuthenticated.value = false
    localStorage.removeItem('token')
    // 可以调用后端退出接口
    // apiLogout()
  }

 const loginUser = async (credentials) => {
    // 1. 先获取JWT token
    const tokenResponse = await login(credentials)
    setToken(tokenResponse.access)

    // 2. 然后用token获取用户信息
    const userData = await getProfile()
    setUser(userData)

    return { access: tokenResponse.access, user: userData }
  }

  const registerUser = async (userData) => {
    const response = await register(userData)
    return response
  }

  const fetchUserProfile = async () => {
    if (token.value) {
      try {
        const userData = await getProfile()
        setUser(userData)
      } catch (error) {
        console.error('获取用户信息失败:', error)
        // 如果token失效，清除登录状态
        if (error.response?.status === 401) {
          logout()
        }
        throw error
      }
    }
  }
  return {
    user,
    token,
    isAuthenticated,
    setToken,
    setUser,
    logout,
    loginUser,
    registerUser,
    fetchUserProfile
  }
})
