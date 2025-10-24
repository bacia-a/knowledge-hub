import request from '@/utils/request'

export const getCategories = () => {
  return request({
    url: '/api/categories/categories/',
    method: 'get'
  })
}

export const createCategory = (data) => {
  return request({
    url: '/api/categories/categories/',
    method: 'post',
    data
  })
}
