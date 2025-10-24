<!-- src/views/Articles.vue -->
<template>
  <div class="articles-container">
    <div class="articles-header">
      <h1>文章管理</h1>
      <el-button type="primary" @click="handleCreateArticle">
        <el-icon><Plus /></el-icon>
        新建文章
      </el-button>
    </div>

    <div class="articles-content">
      <el-table :data="articles" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="category" label="分类" />
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getArticles, deleteArticle } from '@/api/articles'

const articles = ref([])

onMounted(() => {
  fetchArticles()
})

const fetchArticles = async () => {
  const response = await getArticles()
  articles.value = response
}

const handleCreateArticle = () => {
  // 跳转到创建文章页面或打开弹窗
  ElMessage.info('创建文章功能待实现')
}

const handleEdit = (article) => {
  // 跳转到编辑页面或打开弹窗
  ElMessage.info(`编辑文章: ${article.title}`)
}

const handleDelete = async (article) => {
  try {
    await ElMessageBox.confirm(`确定要删除文章 "${article.title}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await deleteArticle(article.id)
    ElMessage.success('删除成功')
    fetchArticles() // 重新加载列表
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style scoped>
.articles-container {
  padding: 20px;
}

.articles-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.articles-header h1 {
  margin: 0;
  color: #333;
}

.articles-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>
