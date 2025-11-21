// src/api/ai.js - 修复版本
import request from '@/utils/request'

// AI助手会话管理
export const getAISessions = () => {
  return request({
    url: '/api/ai/sessions/',
    method: 'get'
  })
}

export const createAISession = (data) => {
  return request({
    url: '/api/ai/sessions/',
    method: 'post',
    data
  })
}

export const deleteAISession = (id) => {
  return request({
    url: `/api/ai/sessions/${id}/`,
    method: 'delete'
  })
}

// AI对话 - 修复路径
export const aiChat = (sessionId, message) => {
  return request({
    url: `/api/ai/sessions/${sessionId}/chat/`,
    method: 'post',
    data: { message },
    timeout: 120000 // 增加超时时间到120秒
  })
}

// 文章AI功能 - 修复路径
export const aiCreateOutline = (data) => {
  return request({
    url: '/api/ai/generate_outline/',
    method: 'post',
    data,
    timeout: 60000
  })
}

export const aiImproveWriting = (data) => {
  return request({
    url: '/api/ai/improve_article/',
    method: 'post',
    data,
    timeout: 60000
  })
}

export const aiCreateSummary = (data) => {
  return request({
    url: '/api/ai/generate_summary/',
    method: 'post',
    data,
    timeout: 60000
  })
}

export const aiCreateTags = (data) => {
  return request({
    url: '/api/ai/generate_tags/',
    method: 'post',
    data,
    timeout: 30000
  })
}

export const aiAutoComplete = (data) => {
  return request({
    url: '/api/ai/articles/auto_complete/',
    method: 'post',
    data,
    timeout: 30000
  })
}
