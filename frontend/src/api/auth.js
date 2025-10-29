import request from '@/utils/request'

export const login = (data) => {
  return request({
    url: '/api/token/',  // 使用JWT端点
    method: 'post',
    data
  })
}

export const register = (data) => {
  return request({
    url: '/api/auth/register/',
    method: 'post',
    data
  })
}

export const getProfile = () => {
  return request({
    url: '/api/auth/profile/',
    method: 'get'
  })
}

export const logout = () => {
  return request({
    url: '/api/auth/logout/',
    method: 'post'
  })
}
