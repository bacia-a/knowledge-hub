<!-- src/components/AIAssistant.vue -->
<template>
  <div class="ai-assistant">
    <!-- AI助手悬浮按钮 -->
    <div class="ai-floating-btn" @click="showAssistant = true">
      <el-icon size="24"><Star /></el-icon>
      <div class="ai-badge" v-if="unreadCount > 0">{{ unreadCount }}</div>
    </div>

    <!-- AI助手主界面 -->
    <el-dialog
      v-model="showAssistant"
      title="DeepSeek AI助手"
      width="900px"
      :before-close="handleClose"
      class="ai-assistant-dialog"
      fullscreen
    >
      <div class="assistant-container">
        <!-- 顶部功能栏 -->
        <div class="assistant-header">
          <div class="function-tabs">
            <el-radio-group v-model="currentFunction">
              <el-radio-button value="chat">
                <el-icon><ChatDotRound /></el-icon>
                AI对话
              </el-radio-button>
            </el-radio-group>
          </div>

          <div class="header-actions">
            <el-button @click="clearCurrentData" :disabled="loading">
              <el-icon><Refresh /></el-icon>
              清空
            </el-button>
          </div>
        </div>

        <!-- 内容区域 -->
        <div class="assistant-content">
          <!-- AI对话界面 -->
          <div class="chat-interface">
            <div class="sessions-sidebar">
              <div class="sessions-header">
                <span>会话列表</span>
                <el-button type="primary" text @click="createNewSession">
                  <el-icon><Plus /></el-icon>
                </el-button>
              </div>
              <div class="sessions-list">
                <div
                  v-for="session in sessions"
                  :key="session.id"
                  :class="['session-item', { active: currentSession?.id === session.id }]"
                  @click="selectSession(session)"
                >
                  <div class="session-title">{{ session.title }}</div>
                  <div class="session-meta">{{ session.message_count }} 条消息</div>
                </div>
                <div v-if="sessions.length === 0" class="empty-sessions">
                  <el-empty description="暂无会话" />
                </div>
              </div>
            </div>

            <div class="chat-main">
              <div class="chat-messages" ref="messagesContainer">
                <div v-if="!currentSession" class="empty-session">
                  <el-empty description="请选择或创建会话" />
                </div>
                <div v-else class="messages-list">
                  <div
                    v-for="message in currentSession.messages"
                    :key="message.id"
                    :class="['message', message.is_user ? 'user-message' : 'ai-message']"
                  >
                    <div class="message-avatar">
                      <el-avatar :size="32" :src="message.is_user ? userAvatar : aiAvatar">
                        {{ message.is_user ? '你' : 'AI' }}
                      </el-avatar>
                    </div>
                    <div class="message-content">
                      <div class="message-text" v-html="formatMessage(message.content)"></div>
                      <div class="message-time">
                        {{ formatTime(message.created_at) }}
                      </div>
                    </div>
                  </div>
                  <div v-if="chatLoading" class="message ai-message">
                    <div class="message-avatar">
                      <el-avatar :size="32" :src="aiAvatar">AI</el-avatar>
                    </div>
                    <div class="message-content">
                      <div class="message-text">
                        <el-icon class="loading-icon"><Loading /></el-icon>
                        DeepSeek AI正在思考中...
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="chat-input-area">
                <el-input
                  v-model="chatInput"
                  type="textarea"
                  :rows="3"
                  placeholder="向DeepSeek AI提问..."
                  :disabled="!currentSession || chatLoading"
                  @keydown.enter.exact.prevent="handleSendMessage"
                />
                <div class="input-actions">
                  <div class="quick-prompts">
                    <el-tag
                      v-for="prompt in quickPrompts"
                      :key="prompt.text"
                      size="small"
                      @click="useQuickPrompt(prompt.text)"
                      class="quick-prompt"
                    >
                      {{ prompt.title }}
                    </el-tag>
                  </div>
                  <el-button
                    type="primary"
                    @click="handleSendMessage"
                    :loading="chatLoading"
                    :disabled="!chatInput.trim() || !currentSession"
                  >
                    <el-icon><Promotion /></el-icon>
                    发送
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
const { Star, ChatDotRound, Refresh, Plus, Loading, Promotion } = ElementPlusIconsVue
import { useAuthStore } from '@/stores/auth'
import { getAISessions, createAISession, aiChat } from '@/api/ai'

const authStore = useAuthStore()

// 状态管理
const showAssistant = ref(false)
const currentFunction = ref('chat')
const loading = ref(false)
const unreadCount = ref(0)

// 聊天相关
const sessions = ref([])
const currentSession = ref(null)
const chatInput = ref('')
const chatLoading = ref(false)
const messagesContainer = ref()

// 计算属性
const userAvatar = computed(() => {
  if (authStore.user?.avatar) {
    return authStore.user.avatar
  }
  return ''
})

const aiAvatar = computed(() => {
  return 'https://avatars.githubusercontent.com/u/158500000?s=200&v=4' // DeepSeek logo
})

const quickPrompts = ref([
  { title: '技术文档', text: '请帮我写一份技术文档，关于' },
  { title: '代码解释', text: '请解释以下代码的功能和原理：' },
  { title: '学习指南', text: '请为我制定一个学习计划，主题是' },
  { title: '问题解决', text: '我遇到了一个技术问题：' },
  { title: '文章大纲', text: '请为以下主题生成文章大纲：' },
  { title: '内容优化', text: '请帮我优化以下内容：' },
])

// 方法
const loadSessions = async () => {
  try {
    const response = await getAISessions()
    sessions.value = response
    if (sessions.value.length > 0 && !currentSession.value) {
      currentSession.value = sessions.value[0]
    }
  } catch (error) {
    console.error('加载会话失败:', error)
    ElMessage.error('加载会话失败')
  }
}

const createNewSession = async () => {
  try {
    const { value: title } = await ElMessageBox.prompt('请输入会话标题', '新建会话', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValue: `新会话 ${new Date().toLocaleDateString()}`,
      inputValidator: (value) => {
        if (!value || value.trim().length === 0) {
          return '会话标题不能为空'
        }
        return true
      },
    })

    if (title) {
      const newSession = await createAISession({ title: title.trim() })
      sessions.value.unshift(newSession)
      currentSession.value = newSession
      ElMessage.success('会话创建成功')
    }
  } catch (error) {
    // 用户取消
    console.error('创建会话失败:', error)
  }
}

const selectSession = (session) => {
  currentSession.value = session
}

const handleSendMessage = async () => {
  if (!chatInput.value.trim() || !currentSession.value) return

  chatLoading.value = true
  const message = chatInput.value
  chatInput.value = ''

  try {
    const response = await aiChat(currentSession.value.id, message)

    // 更新会话消息
    const sessionIndex = sessions.value.findIndex((s) => s.id === currentSession.value.id)
    if (sessionIndex !== -1) {
      if (!sessions.value[sessionIndex].messages) {
        sessions.value[sessionIndex].messages = []
      }
      sessions.value[sessionIndex].messages.push(response.user_message, response.ai_message)
    }

    // 滚动到底部
    nextTick(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    })
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送消息失败: ' + (error.response?.data?.error || error.message))
    chatInput.value = message // 恢复输入
  } finally {
    chatLoading.value = false
  }
}

const clearCurrentData = () => {
  chatInput.value = ''
  ElMessage.success('已清空')
}

const useQuickPrompt = (text) => {
  chatInput.value = text
  // 自动聚焦到输入框
  nextTick(() => {
    const textarea = document.querySelector('.chat-input-area textarea')
    if (textarea) {
      textarea.focus()
    }
  })
}

const formatMessage = (content) => {
  // 简单的消息格式化
  return content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
}

const formatTime = (time) => {
  return new Date(time).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

const handleClose = (done) => {
  if (chatInput.value.trim()) {
    ElMessageBox.confirm('确定要关闭AI助手吗？未发送的消息将会丢失。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
      .then(() => {
        done()
      })
      .catch(() => {
        // 取消关闭
      })
  } else {
    done()
  }
}

// 生命周期
onMounted(() => {
  loadSessions()
})
</script>

<style scoped>
.ai-assistant {
  position: relative;
}

.ai-floating-btn {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  transition: all 0.3s ease;
}

.ai-floating-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 25px rgba(0, 0, 0, 0.2);
}

.ai-floating-btn.pulse {
  animation: pulse 2s infinite;
}

.ai-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ff4d4f;
  color: white;
  border-radius: 10px;
  padding: 2px 6px;
  font-size: 12px;
  min-width: 18px;
  text-align: center;
  font-weight: bold;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.assistant-container {
  height: 80vh;
  display: flex;
  flex-direction: column;
}

.assistant-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e6e6e6;
  background: white;
}

.function-tabs {
  flex: 1;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.assistant-content {
  flex: 1;
  overflow: hidden;
}

/* 聊天界面样式 */
.chat-interface {
  display: flex;
  height: 100%;
}

.sessions-sidebar {
  width: 280px;
  border-right: 1px solid #e6e6e6;
  background: #fafafa;
  display: flex;
  flex-direction: column;
}

.sessions-header {
  padding: 15px;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  font-weight: 600;
}

.sessions-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.empty-sessions {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
}

.session-item {
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
  border: 1px solid #e6e6e6;
}

.session-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.session-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.session-title {
  font-weight: 500;
  margin-bottom: 4px;
  font-size: 14px;
}

.session-meta {
  font-size: 12px;
  color: #666;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f5f5;
}

.messages-list {
  max-width: 800px;
  margin: 0 auto;
}

.message {
  display: flex;
  margin-bottom: 20px;
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  margin: 0 12px;
}

.message-content {
  max-width: 70%;
}

.user-message .message-content {
  text-align: right;
}

.message-text {
  padding: 12px 16px;
  border-radius: 18px;
  background: white;
  border: 1px solid #e6e6e6;
  line-height: 1.5;
  word-wrap: break-word;
}

.user-message .message-text {
  background: #409eff;
  color: white;
  border-color: #409eff;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.loading-icon {
  animation: spin 1s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.chat-input-area {
  padding: 20px;
  border-top: 1px solid #e6e6e6;
  background: white;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.quick-prompts {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  flex: 1;
  margin-right: 15px;
}

.quick-prompt {
  cursor: pointer;
  transition: all 0.3s;
}

.quick-prompt:hover {
  background: #409eff;
  color: white;
}

.empty-session {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-interface {
    flex-direction: column;
  }

  .sessions-sidebar {
    width: 100%;
    height: 200px;
  }

  .ai-floating-btn {
    bottom: 20px;
    right: 20px;
    width: 50px;
    height: 50px;
  }

  .assistant-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .function-tabs {
    order: 2;
  }

  .header-actions {
    order: 1;
    justify-content: flex-end;
  }

  .input-actions {
    flex-direction: column;
    gap: 10px;
  }

  .quick-prompts {
    margin-right: 0;
    justify-content: center;
  }
}

/* 滚动条样式 */
.sessions-list::-webkit-scrollbar,
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.sessions-list::-webkit-scrollbar-track,
.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.sessions-list::-webkit-scrollbar-thumb,
.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.sessions-list::-webkit-scrollbar-thumb:hover,
.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
