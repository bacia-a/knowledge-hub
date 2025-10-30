<template>
  <div class="home-page">
    <div class="welcome-section">
      <h1>欢迎回来，{{ authStore.user?.username }}！</h1>
      <p>这里是你的个人知识管理中心</p>

      <div class="stats-cards">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon size="40" color="#409EFF"><Document /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ stats.articleCount }}</div>
              <div class="stat-label">文章总数</div>
            </div>
          </div>
        </el-card>

        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon size="40" color="#67C23A"><Folder /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ stats.categoryCount }}</div>
              <div class="stat-label">分类数量</div>
            </div>
          </div>
        </el-card>

        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon size="40" color="#E6A23C"><CollectionTag /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ stats.todayCount }}</div>
              <div class="stat-label">今日新增</div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <div class="recent-articles">
      <h2>最近文章</h2>
      <el-empty description="暂无文章" v-if="recentArticles.length === 0" />
      <el-card
        v-for="article in recentArticles"
        :key="article.id"
        class="article-card"
        @click="goToArticle(article.id)"
        style="cursor: pointer"
      >
        <div class="article-header">
          <h3>{{ article.title }}</h3>
          <el-tag :type="article.status === 'published' ? 'success' : 'info'">
            {{ article.status === 'published' ? '已发布' : '草稿' }}
          </el-tag>
        </div>
        <p class="article-summary">{{ article.summary || '暂无摘要' }}</p>
        <div class="article-meta">
          <span>{{ formatDate(article.created_at) }}</span>
          <span v-if="article.category_name" style="margin-left: 10px">
            分类: {{ article.category_name }}
          </span>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, Folder, CollectionTag } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { getArticles } from '@/api/articles'
import { getCategories } from '@/api/categories'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const recentArticles = ref([])
const allArticles = ref([])
const categories = ref([])

// 统计数据
const stats = reactive({
  articleCount: 0,
  categoryCount: 0,
  todayCount: 0,
})

// 计算今日新增文章数量
const calculateTodayCount = (articles) => {
  const today = new Date().toDateString()
  return articles.filter((article) => {
    const articleDate = new Date(article.created_at).toDateString()
    return articleDate === today
  }).length
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 跳转到文章详情或编辑页
const goToArticle = (articleId) => {
  router.push(`/article/${articleId}`)
}
// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    // 并行加载文章和分类数据
    const [articlesResponse, categoriesResponse] = await Promise.all([
      getArticles(),
      getCategories(),
    ])

    allArticles.value = articlesResponse
    categories.value = categoriesResponse

    // 更新统计数据
    stats.articleCount = allArticles.value.length
    stats.categoryCount = categories.value.length
    stats.todayCount = calculateTodayCount(allArticles.value)

    // 获取最近5篇文章
    recentArticles.value = allArticles.value
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, 5)
  } catch (error) {
    console.error('加载数据错误:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.home-page {
  max-width: 1200px;
}

.welcome-section {
  text-align: center;
  margin-bottom: 40px;
}

.welcome-section h1 {
  color: #333;
  margin-bottom: 10px;
}

.welcome-section p {
  color: #666;
  font-size: 16px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.stat-card {
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.recent-articles h2 {
  margin-bottom: 20px;
  color: #333;
}

.article-card {
  margin-bottom: 15px;
  transition: all 0.3s;
}

.article-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.article-header h3 {
  margin: 0;
  color: #333;
  flex: 1;
  margin-right: 15px;
}

.article-summary {
  color: #666;
  margin-bottom: 10px;
  line-height: 1.5;
  display: -webkit-box;
  /* -webkit-line-clamp: 2; */
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-meta {
  color: #999;
  font-size: 12px;
  display: flex;
  justify-content: space-between;
}
</style>
