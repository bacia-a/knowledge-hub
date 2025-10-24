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

export const updateCategory = (id, data) => {
  return request({
    url: `/api/categories/categories/${id}/`,
    method: 'put',
    data
  })
}

export const deleteCategory = (id) => {
  return request({
    url: `/api/categories/categories/${id}/`,
    method: 'delete'
  })
}
