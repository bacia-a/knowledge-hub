<template>
  <div class="home-page">
    <div class="welcome-section">
      <h1>欢迎回来！</h1>
      <p>这里是你的个人知识管理中心</p>

      <div class="stats-cards">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon size="40" color="#409EFF"><Document /></el-icon>
            <div class="stat-info">
              <div class="stat-number">0</div>
              <div class="stat-label">文章总数</div>
            </div>
          </div>
        </el-card>

        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon size="40" color="#67C23A"><Folder /></el-icon>
            <div class="stat-info">
              <div class="stat-number">0</div>
              <div class="stat-label">分类数量</div>
            </div>
          </div>
        </el-card>

        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon size="40" color="#E6A23C"><CollectionTag /></el-icon>
            <div class="stat-info">
              <div class="stat-number">0</div>
              <div class="stat-label">今日新增</div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <div class="recent-articles">
      <h2>最近文章</h2>
      <el-empty description="暂无文章" v-if="recentArticles.length === 0" />
      <el-card v-for="article in recentArticles" :key="article.id" class="article-card">
        <div class="article-header">
          <h3>{{ article.title }}</h3>
          <el-tag :type="article.status === 'published' ? 'success' : 'info'">
            {{ article.status === 'published' ? '已发布' : '草稿' }}
          </el-tag>
        </div>
        <p class="article-summary">{{ article.summary }}</p>
        <div class="article-meta">
          <span>{{ article.created_at }}</span>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Document, Folder, CollectionTag } from '@element-plus/icons-vue'

const recentArticles = ref([])
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
}

.article-meta {
  color: #999;
  font-size: 12px;
}
</style>
