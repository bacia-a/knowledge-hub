import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const request = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 10000
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    console.log('请求:', config.method?.toUpperCase(), config.url)
    console.log('请求数据:', config.data)

    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    console.log('响应:', response.config.url, response.data)
    return response.data
  },
  (error) => {
    console.error('请求错误:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)
export default request
