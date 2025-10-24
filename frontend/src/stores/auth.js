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
    const response = await login(credentials)
    setToken(response.access)
    setUser(response.user)
    return response
  }

  const registerUser = async (userData) => {
    const response = await register(userData)
    return response
  }

  const fetchUserProfile = async () => {
    if (token.value) {
        const userData = await getProfile()
        setUser(userData)
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
