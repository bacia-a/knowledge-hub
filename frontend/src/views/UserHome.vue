<!-- src/views/Home.vue -->
<template>
  <div class="home-container">
    <div class="welcome-section">
      <h1>欢迎来到 Knowledge Hub</h1>
      <p>个人知识管理系统</p>
    </div>

    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="stat-card">
            <template #header>
              <div class="card-header">
                <span>文章数量</span>
              </div>
            </template>
            <div class="stat-content">
              <h2>0</h2>
              <p>篇知识文章</p>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="stat-card">
            <template #header>
              <div class="card-header">
                <span>分类数量</span>
              </div>
            </template>
            <div class="stat-content">
              <h2>0</h2>
              <p>个知识分类</p>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="stat-card">
            <template #header>
              <div class="card-header">
                <span>最近更新</span>
              </div>
            </template>
            <div class="stat-content">
              <h2>-</h2>
              <p>暂无更新</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="quick-actions">
      <el-button type="primary" @click="$router.push('/articles')">管理文章</el-button>
      <el-button>管理分类</el-button>
    </div>
  </div>
</template>

<script setup></script>

<style scoped>
.home-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-section {
  text-align: center;
  margin-bottom: 40px;
}

.welcome-section h1 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 10px;
}

.welcome-section p {
  font-size: 1.2rem;
  color: #666;
}

.stats-section {
  margin-bottom: 40px;
}

.stat-card {
  text-align: center;
}

.card-header {
  font-weight: bold;
  color: #333;
}

.stat-content h2 {
  font-size: 2rem;
  color: #409eff;
  margin: 10px 0;
}

.stat-content p {
  color: #666;
  margin: 0;
}

.quick-actions {
  text-align: center;
}
</style>
