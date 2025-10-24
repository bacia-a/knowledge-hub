<template>
  <div class="articles-page">
    <div class="page-header">
      <h2>我的文章</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新建文章
      </el-button>
    </div>

    <el-card>
      <el-table :data="articles" v-loading="loading">
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="category_name" label="分类" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'published' ? 'success' : 'info'">
              {{ row.status === 'published' ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button link type="primary" @click="editArticle(row)">编辑</el-button>
            <el-button link type="danger" @click="deleteArticle(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建文章对话框 -->
    <el-dialog :title="editMode ? '编辑文章' : '新建文章'" v-model="showCreateDialog" width="800px">
      <el-form :model="articleForm" :rules="articleRules" ref="articleFormRef">
        <el-form-item label="标题" prop="title">
          <el-input v-model="articleForm.title" placeholder="请输入文章标题" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="articleForm.category" placeholder="请选择分类">
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="摘要" prop="summary">
          <el-input
            v-model="articleForm.summary"
            type="textarea"
            placeholder="请输入文章摘要"
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="articleForm.content"
            type="textarea"
            placeholder="请输入文章内容"
            :rows="10"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="articleForm.status">
            <el-radio label="draft">草稿</el-radio>
            <el-radio label="published">发布</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="公开" prop="is_public">
          <el-switch v-model="articleForm.is_public" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitArticle" :loading="submitting">
          {{ editMode ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getArticles,
  createArticle,
  updateArticle,
  deleteArticle as deleteArticleApi,
} from '@/api/articles'
import { getCategories } from '@/api/categories'

const loading = ref(false)
const showCreateDialog = ref(false)
const submitting = ref(false)
const editMode = ref(false)
const editingId = ref(null)
const articleFormRef = ref()

const articles = ref([])
const categories = ref([])

const articleForm = reactive({
  title: '',
  category: null,
  summary: '',
  content: '',
  status: 'draft',
  is_public: true,
})

const articleRules = {
  title: [{ required: true, message: '请输入文章标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入文章内容', trigger: 'blur' }],
}

// 加载文章列表
const loadArticles = async () => {
  loading.value = true
  try {
    const response = await getArticles()
    articles.value = response
    console.log('文章列表:', response)
  } catch (error) {
    console.error('加载文章错误:', error)
    ElMessage.error('加载文章失败')
  } finally {
    loading.value = false
  }
}

// 加载分类列表
const loadCategories = async () => {
  try {
    const response = await getCategories()
    categories.value = response
  } catch {
    ElMessage.error('加载分类失败')
  }
}

// 编辑文章函数 - 添加这个函数
const editArticle = (article) => {
  editMode.value = true
  editingId.value = article.id
  Object.assign(articleForm, {
    title: article.title,
    category: article.category,
    summary: article.summary,
    content: article.content,
    status: article.status,
    is_public: article.is_public,
  })
  showCreateDialog.value = true
}

// 删除文章函数
const deleteArticle = async (article) => {
  try {
    await ElMessageBox.confirm(`确定删除文章 "${article.title}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteArticleApi(article.id)
    ElMessage.success('删除成功')
    loadArticles()
  } catch {
    // 用户取消
  }
}

const submitArticle = async () => {
  if (!articleFormRef.value) return

  try {
    const valid = await articleFormRef.value.validate()
    if (!valid) return

    submitting.value = true

    if (editMode.value) {
      // 更新文章
      await updateArticle(editingId.value, articleForm)
      ElMessage.success('更新成功')
    } else {
      // 创建文章
      await createArticle(articleForm)
      ElMessage.success('创建成功')
    }

    showCreateDialog.value = false
    resetForm()
    loadArticles()
  } catch (error) {
    console.error('操作文章错误:', error)
    ElMessage.error(editMode.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  articleFormRef.value?.resetFields()
  Object.assign(articleForm, {
    title: '',
    category: null,
    summary: '',
    content: '',
    status: 'draft',
    is_public: true,
  })
  editMode.value = false
  editingId.value = null
}

onMounted(() => {
  loadArticles()
  loadCategories()
})
</script>

<style scoped>
.articles-page {
  max-width: 1200px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>
