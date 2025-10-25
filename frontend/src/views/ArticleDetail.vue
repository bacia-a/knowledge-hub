<template>
  <div class="article-detail" v-loading="loading">
    <div class="article-header">
      <el-button @click="$router.back()" class="back-button">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>

      <div class="article-actions">
        <el-button type="primary" @click="editArticle">编辑</el-button>
        <el-button
          @click="togglePublish"
          :type="article.status === 'published' ? 'success' : 'warning'"
        >
          {{ article.status === 'published' ? '取消发布' : '发布' }}
        </el-button>
      </div>
    </div>

    <el-card class="article-card">
      <template #header>
        <div class="article-title-section">
          <h1>{{ article.title }}</h1>
          <div class="article-meta">
            <el-tag :type="article.status === 'published' ? 'success' : 'info'">
              {{ article.status === 'published' ? '已发布' : '草稿' }}
            </el-tag>
            <span>创建时间: {{ formatDate(article.created_at) }}</span>
            <span v-if="article.published_at"
              >发布时间: {{ formatDate(article.published_at) }}</span
            >
            <span v-if="article.category_name">分类: {{ article.category_name }}</span>
          </div>
        </div>
      </template>

      <div class="article-content">
        <div v-if="article.summary" class="article-summary">
          <h3>摘要</h3>
          <p>{{ article.summary }}</p>
        </div>

        <div v-if="article.content" class="content-text">
          <h3>内容</h3>
          <div class="content-body">{{ article.content }}</div>
        </div>

        <el-empty v-else description="暂无内容" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getArticle, updateArticle } from '@/api/articles'

const route = useRoute()
const router = useRouter()
const loading = ref(false)

const article = ref({
  title: '',
  content: '',
  summary: '',
  status: 'draft',
  created_at: '',
  published_at: '',
  category_name: '',
})

const loadArticle = async () => {
  loading.value = true
  try {
    const articleId = route.params.id
    const response = await getArticle(articleId)
    article.value = response
  } catch (error) {
    console.error('加载文章错误:', error)
    ElMessage.error('加载文章失败')
  } finally {
    loading.value = false
  }
}

const editArticle = () => {
  // 跳转到文章编辑页面，或者直接在文章列表页面编辑
  router.push('/articles')
  ElMessage.info('请在文章列表页面点击编辑按钮进行编辑')
}

const togglePublish = async () => {
  try {
    const newStatus = article.value.status === 'published' ? 'draft' : 'published'
    await updateArticle(article.value.id, {
      status: newStatus,
    })

    article.value.status = newStatus
    ElMessage.success(newStatus === 'published' ? '发布成功' : '已转为草稿')
  } catch (error) {
    console.error('发布操作错误:', error)
    ElMessage.error('操作失败')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(() => {
  loadArticle()
})
</script>

<style scoped>
.article-detail {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.back-button {
  margin-right: auto;
}

.article-actions {
  display: flex;
  gap: 10px;
}

.article-card {
  margin-bottom: 20px;
}

.article-title-section h1 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 28px;
}

.article-meta {
  display: flex;
  gap: 15px;
  align-items: center;
  color: #666;
  font-size: 14px;
  flex-wrap: wrap;
}

.article-content {
  line-height: 1.8;
}

.article-summary {
  margin-bottom: 30px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
}

.article-summary h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.content-text h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.content-body {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 16px;
  line-height: 1.6;
}
</style>
