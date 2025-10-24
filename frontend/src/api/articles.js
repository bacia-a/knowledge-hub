import request from '@/utils/request'

export const getArticles = () => {
  return request({
    url: '/api/articles/articles/',
    method: 'get'
  })
}

export const createArticle = (data) => {
  return request({
    url: '/api/articles/articles/',
    method: 'post',
    data
  })
}

export const updateArticle = (id, data) => {
  return request({
    url: `/api/articles/articles/${id}/`,
    method: 'put',
    data
  })
}

export const deleteArticle = (id) => {
  return request({
    url: `/api/articles/articles/${id}/`,
    method: 'delete'
  })
}
