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
      title="DeepSeek AI写作助手"
      width="900px"
      :before-close="handleClose"
      class="ai-assistant-dialog"
      fullscreen
    >
      <div class="assistant-container">
        <!-- 顶部功能栏 -->
        <div class="assistant-header">
          <div class="function-tabs">
            <el-radio-group v-model="currentFunction" @change="handleFunctionChange">
              <el-radio-button value="chat">
                <el-icon><ChatDotRound /></el-icon>
                AI对话
              </el-radio-button>
              <el-radio-button value="outline">
                <el-icon><List /></el-icon>
                生成大纲
              </el-radio-button>
              <el-radio-button value="improve">
                <el-icon><Edit /></el-icon>
                文章优化
              </el-radio-button>
              <el-radio-button value="summary">
                <el-icon><Document /></el-icon>
                生成摘要
              </el-radio-button>
            </el-radio-group>
          </div>

          <div class="header-actions">
            <el-button @click="clearCurrentData" :disabled="loading">
              <el-icon><Refresh /></el-icon>
              清空
            </el-button>
            <el-button type="primary" @click="insertToEditor" :disabled="!canInsert">
              <el-icon><Position /></el-icon>
              插入编辑器
            </el-button>
          </div>
        </div>

        <!-- 内容区域 -->
        <div class="assistant-content">
          <!-- AI对话界面 -->
          <div v-if="currentFunction === 'chat'" class="chat-interface">
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

          <!-- 生成大纲界面 -->
          <div v-else-if="currentFunction === 'outline'" class="outline-interface">
            <div class="function-form">
              <el-form :model="outlineForm" label-width="100px">
                <el-form-item label="文章主题">
                  <el-input
                    v-model="outlineForm.topic"
                    placeholder="请输入文章主题，如：Vue3组件开发最佳实践"
                    size="large"
                  />
                </el-form-item>
                <el-form-item label="文章风格">
                  <el-select v-model="outlineForm.style">
                    <el-option label="专业严谨" value="专业" />
                    <el-option label="通俗易懂" value="通俗" />
                    <el-option label="学术论文" value="学术" />
                    <el-option label="简洁明了" value="简洁" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button
                    type="primary"
                    @click="handleGenerateOutline"
                    :loading="outlineLoading"
                    :disabled="!outlineForm.topic.trim()"
                    size="large"
                  >
                    <el-icon><Star /></el-icon>
                    {{ outlineLoading ? '生成中...' : '生成大纲' }}
                  </el-button>
                </el-form-item>
              </el-form>
            </div>

            <div v-if="generatedOutline" class="outline-result">
              <div class="result-header">
                <h3>{{ generatedOutline.title }}</h3>
                <el-button type="primary" @click="applyOutline">
                  <el-icon><Check /></el-icon>
                  应用此大纲
                </el-button>
              </div>

              <div class="outline-sections">
                <div
                  v-for="(section, index) in generatedOutline.sections"
                  :key="index"
                  class="outline-section"
                >
                  <div class="section-header">
                    <span class="section-number">{{ index + 1 }}</span>
                    <h4 class="section-title">{{ section.title }}</h4>
                    <el-button
                      size="small"
                      @click="expandSection(section, index)"
                      :loading="expandingSection === index"
                    >
                      <el-icon><Expand /></el-icon>
                      扩展此章节
                    </el-button>
                  </div>
                  <ul class="section-points">
                    <li v-for="(point, pointIndex) in section.points" :key="pointIndex">
                      {{ point }}
                    </li>
                  </ul>

                  <div v-if="section.expandedContent" class="expanded-content">
                    <div class="content-preview">
                      {{ section.expandedContent }}
                    </div>
                    <el-button size="small" @click="useContent(section.expandedContent)">
                      <el-icon><DocumentAdd /></el-icon>
                      使用此内容
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 文章优化界面 -->
          <div v-else-if="currentFunction === 'improve'" class="improve-interface">
            <div class="function-form">
              <el-form :model="improveForm" label-width="100px">
                <el-form-item label="待优化内容">
                  <el-input
                    v-model="improveForm.content"
                    type="textarea"
                    :rows="8"
                    placeholder="请输入需要优化的文章内容..."
                    show-word-limit
                    maxlength="10000"
                  />
                </el-form-item>
                <el-form-item label="优化类型">
                  <el-radio-group v-model="improveForm.improve_type">
                    <el-radio label="grammar">
                      <el-icon><Check /></el-icon>
                      语法修正
                    </el-radio>
                    <el-radio label="style">
                      <el-icon><Edit /></el-icon>
                      风格优化
                    </el-radio>
                    <el-radio label="expand">
                      <el-icon><Expand /></el-icon>
                      内容扩展
                    </el-radio>
                  </el-radio-group>
                </el-form-item>
                <el-form-item>
                  <el-button
                    type="primary"
                    @click="handleImproveArticle"
                    :loading="improveLoading"
                    :disabled="!improveForm.content.trim()"
                  >
                    <el-icon><Star /></el-icon>
                    {{ improveLoading ? '优化中...' : '开始优化' }}
                  </el-button>
                </el-form-item>
              </el-form>
            </div>

            <div v-if="improvementResult" class="improve-result">
              <el-tabs v-model="improveActiveTab">
                <el-tab-pane label="优化结果" name="improved">
                  <div class="result-content">
                    <div class="content-comparison">
                      <div class="original-content">
                        <h4>原始内容</h4>
                        <div class="content-box">
                          {{ improveForm.content }}
                        </div>
                      </div>
                      <div class="improved-content">
                        <h4>优化后内容</h4>
                        <div class="content-box improved">
                          {{ improvementResult.improved_content }}
                        </div>
                      </div>
                    </div>
                  </div>
                </el-tab-pane>
                <el-tab-pane label="修改建议" name="suggestions">
                  <div class="suggestions-list">
                    <div
                      v-for="(suggestion, index) in improvementResult.suggestions"
                      :key="index"
                      class="suggestion-item"
                    >
                      <el-icon color="#409EFF"><InfoFilled /></el-icon>
                      <span>{{ suggestion }}</span>
                    </div>
                  </div>
                </el-tab-pane>
              </el-tabs>

              <div class="result-actions">
                <el-button type="primary" @click="useImprovedContent">
                  <el-icon><Check /></el-icon>
                  使用优化内容
                </el-button>
                <el-tag type="success" size="large">
                  评分: {{ improvementResult.overall_rating }}
                </el-tag>
              </div>
            </div>
          </div>

          <!-- 生成摘要界面 -->
          <div v-else-if="currentFunction === 'summary'" class="summary-interface">
            <div class="function-form">
              <el-form :model="summaryForm" label-width="100px">
                <el-form-item label="文章内容">
                  <el-input
                    v-model="summaryForm.content"
                    type="textarea"
                    :rows="10"
                    placeholder="请输入需要生成摘要的文章内容..."
                    show-word-limit
                    maxlength="20000"
                  />
                </el-form-item>
                <el-form-item label="摘要长度">
                  <el-slider
                    v-model="summaryForm.max_length"
                    :min="50"
                    :max="500"
                    :step="50"
                    show-stops
                    show-input
                  />
                </el-form-item>
                <el-form-item>
                  <el-button
                    type="primary"
                    @click="handleGenerateSummary"
                    :loading="summaryLoading"
                    :disabled="!summaryForm.content.trim()"
                  >
                    <el-icon><Star /></el-icon>
                    {{ summaryLoading ? '生成中...' : '生成摘要' }}
                  </el-button>
                </el-form-item>
              </el-form>
            </div>

            <div v-if="generatedSummary" class="summary-result">
              <h3>文章摘要</h3>
              <div class="summary-content">
                {{ generatedSummary }}
              </div>
              <div class="result-actions">
                <el-button type="primary" @click="useSummary">
                  <el-icon><Check /></el-icon>
                  使用此摘要
                </el-button>
                <el-tag>长度: {{ generatedSummary.length }} 字</el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
// import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
// import {
//   Magic,
//   ChatDotRound,
//   List,
//   Edit,
//   Document,
//   Refresh,
//   Position,
//   Plus,
//   Loading,
//   Promotion,
//   Check,
//   Expand,
//   DocumentAdd,
//   InfoFilled,
// } from '@element-plus/icons-vue'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
const {
  Star,
  ChatDotRound,
  List,
  Edit,
  Document,
  Refresh,
  Position,
  Plus,
  Loading,
  Promotion,
  Check,
  Expand,
  DocumentAdd,
  InfoFilled,
} = ElementPlusIconsVue
import { useAuthStore } from '@/stores/auth'
import {
  getAISessions,
  createAISession,
  aiChat,
  aiCreateOutline,
  aiImproveWriting,
  aiCreateSummary,
} from '@/api/ai'

// const router = useRouter()
const authStore = useAuthStore()

// 状态管理
const showAssistant = ref(false)
const currentFunction = ref('chat')
const loading = ref(false)
// const hasNewFeature = ref(true)
const unreadCount = ref(0)

// 聊天相关
const sessions = ref([])
const currentSession = ref(null)
const chatInput = ref('')
const chatLoading = ref(false)
const messagesContainer = ref()

// 大纲相关
const outlineForm = reactive({
  topic: '',
  style: '专业',
})
const outlineLoading = ref(false)
const generatedOutline = ref(null)
const expandingSection = ref(null)

// 优化相关
const improveForm = reactive({
  content: '',
  improve_type: 'style',
})
const improveLoading = ref(false)
const improvementResult = ref(null)
const improveActiveTab = ref('improved')

// 摘要相关
const summaryForm = reactive({
  content: '',
  max_length: 200,
})
const summaryLoading = ref(false)
const generatedSummary = ref(null)

// 计算属性
const canInsert = computed(() => {
  switch (currentFunction.value) {
    case 'outline':
      return !!generatedOutline.value
    case 'improve':
      return !!improvementResult.value
    case 'summary':
      return !!generatedSummary.value
    default:
      return false
  }
})

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

const handleGenerateOutline = async () => {
  if (!outlineForm.topic.trim()) {
    ElMessage.warning('请输入文章主题')
    return
  }

  outlineLoading.value = true
  try {
    const response = await aiCreateOutline(outlineForm)
    generatedOutline.value = response
    ElMessage.success('大纲生成成功')
  } catch (error) {
    console.error('生成大纲失败:', error)
    ElMessage.error('生成大纲失败: ' + (error.response?.data?.error || error.message))
  } finally {
    outlineLoading.value = false
  }
}

const expandSection = async (section, index) => {
  expandingSection.value = index
  try {
    // 模拟扩展章节内容
    await new Promise((resolve) => setTimeout(resolve, 2000))
    section.expandedContent = `这是关于"${section.title}"的详细内容。这部分内容可以根据实际需求进行扩展，包括具体的技术细节、实现步骤、注意事项等。DeepSeek AI能够帮助您生成更加详细和专业的章节内容。`
    ElMessage.success('章节扩展完成')
  } catch (error) {
    ElMessage.error('扩展章节失败')
    console.error('扩展章节失败:', error)
  } finally {
    expandingSection.value = null
  }
}

const handleImproveArticle = async () => {
  if (!improveForm.content.trim()) {
    ElMessage.warning('请输入需要优化的内容')
    return
  }

  improveLoading.value = true
  try {
    const response = await aiImproveWriting(improveForm)
    improvementResult.value = response
    ElMessage.success('文章优化完成')
  } catch (error) {
    console.error('文章优化失败:', error)
    ElMessage.error('文章优化失败: ' + (error.response?.data?.error || error.message))
  } finally {
    improveLoading.value = false
  }
}

const handleGenerateSummary = async () => {
  if (!summaryForm.content.trim()) {
    ElMessage.warning('请输入文章内容')
    return
  }

  summaryLoading.value = true
  try {
    const response = await aiCreateSummary(summaryForm)
    generatedSummary.value = response.summary
    ElMessage.success('摘要生成成功')
  } catch (error) {
    console.error('生成摘要失败:', error)
    ElMessage.error('生成摘要失败: ' + (error.response?.data?.error || error.message))
  } finally {
    summaryLoading.value = false
  }
}

const handleFunctionChange = () => {
  // 切换功能时清空数据
  generatedOutline.value = null
  improvementResult.value = null
  generatedSummary.value = null
  improveActiveTab.value = 'improved'
}

const clearCurrentData = () => {
  switch (currentFunction.value) {
    case 'outline':
      outlineForm.topic = ''
      generatedOutline.value = null
      break
    case 'improve':
      improveForm.content = ''
      improvementResult.value = null
      break
    case 'summary':
      summaryForm.content = ''
      generatedSummary.value = null
      break
    case 'chat':
      chatInput.value = ''
      break
  }
  ElMessage.success('已清空')
}

const insertToEditor = () => {
  let content = ''
  switch (currentFunction.value) {
    case 'outline':
      content = generatedOutline.value
        ? `# ${generatedOutline.value.title}\n\n` +
          generatedOutline.value.sections
            .map(
              (section) =>
                `## ${section.title}\n\n${section.points.map((point) => `- ${point}`).join('\n')}`,
            )
            .join('\n\n')
        : ''
      break
    case 'improve':
      content = improvementResult.value?.improved_content || ''
      break
    case 'summary':
      content = generatedSummary.value || ''
      break
  }

  // 触发全局事件，让编辑器接收内容
  const event = new CustomEvent('ai-content-insert', {
    detail: { content, type: currentFunction.value },
  })
  window.dispatchEvent(event)

  ElMessage.success('内容已准备插入编辑器')
  showAssistant.value = false
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

const applyOutline = () => {
  if (!generatedOutline.value) return
  insertToEditor()
}

const useContent = (content) => {
  const event = new CustomEvent('ai-content-insert', {
    detail: { content, type: 'section' },
  })
  window.dispatchEvent(event)
  ElMessage.success('章节内容已准备插入编辑器')
}

const useImprovedContent = () => {
  if (!improvementResult.value) return
  insertToEditor()
}

const useSummary = () => {
  if (!generatedSummary.value) return
  insertToEditor()
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
  if (
    chatInput.value.trim() ||
    generatedOutline.value ||
    improvementResult.value ||
    generatedSummary.value
  ) {
    ElMessageBox.confirm('确定要关闭AI助手吗？未保存的内容将会丢失。', '提示', {
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

// 监听编辑器内容插入事件
const setupEditorListener = () => {
  window.addEventListener('ai-content-insert', (event) => {
    console.log('AI内容准备插入:', event.detail)
    // 这里可以添加更多的插入逻辑
  })
}

// 生命周期
onMounted(() => {
  loadSessions()
  setupEditorListener()
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

/* 其他功能界面样式 */
.function-form {
  padding: 30px;
  max-width: 800px;
  margin: 0 auto;
}

.outline-result,
.improve-result,
.summary-result {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #409eff;
}

.outline-sections {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.outline-section {
  padding: 20px;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  background: white;
  transition: all 0.3s;
}

.outline-section:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.section-number {
  width: 30px;
  height: 30px;
  background: #409eff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-weight: bold;
  flex-shrink: 0;
}

.section-title {
  flex: 1;
  margin: 0;
  color: #333;
  font-size: 16px;
}

.section-points {
  margin: 0;
  padding-left: 20px;
  color: #666;
}

.section-points li {
  margin-bottom: 8px;
  line-height: 1.5;
}

.expanded-content {
  margin-top: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

.content-preview {
  margin-bottom: 10px;
  line-height: 1.6;
  color: #333;
}

.content-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.original-content,
.improved-content {
  padding: 15px;
}

.original-content h4,
.improved-content h4 {
  margin-bottom: 10px;
  color: #333;
  font-size: 14px;
}

.content-box {
  padding: 15px;
  border: 1px solid #e6e6e6;
  border-radius: 6px;
  background: white;
  min-height: 200px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.content-box.improved {
  border-color: #67c23a;
  background: #f0f9ff;
}

.suggestions-list {
  padding: 15px;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  padding: 10px;
  margin-bottom: 8px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.suggestion-item .el-icon {
  margin-right: 8px;
  margin-top: 2px;
  flex-shrink: 0;
}

.result-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #e6e6e6;
}

.summary-content {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
  line-height: 1.8;
  font-size: 15px;
  white-space: pre-wrap;
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

  .content-comparison {
    grid-template-columns: 1fr;
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
