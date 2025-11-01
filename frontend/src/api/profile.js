import request from '@/utils/request'

export const updateProfile = (data) => {
  return request({
    url: '/api/auth/profile/update/',
    method: 'put',
    data
  })
}

export const uploadAvatar = (data) => {
  return request({
    url: '/api/auth/profile/upload-avatar/',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const changePassword = (data) => {
  return request({
    url: '/api/auth/profile/change-password/',
    method: 'post',
    data
  })
}

export const removeAvatar = () => {
  return request({
    url: '/api/auth/profile/remove-avatar/',
    method: 'delete'
  })
}
