<template>
  <div class="articles-page">
    <div class="page-header">
      <h2>我的文章</h2>
      <div class="header-actions">
        <el-button @click="showAdvancedSearch = !showAdvancedSearch">
          <el-icon><Search /></el-icon>
          高级搜索
        </el-button>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建文章
        </el-button>
      </div>
    </div>

    <!-- 高级搜索面板 -->
    <el-card v-show="showAdvancedSearch" class="search-panel">
      <el-form :model="searchForm" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="关键词">
              <el-input v-model="searchForm.keyword" placeholder="搜索标题或摘要" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="状态">
              <el-select v-model="searchForm.status" placeholder="全部状态" clearable>
                <el-option label="草稿" value="draft" />
                <el-option label="已发布" value="published" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="分类">
              <el-select v-model="searchForm.category" placeholder="全部分类" clearable>
                <el-option
                  v-for="category in categories"
                  :key="category.id"
                  :label="category.name"
                  :value="category.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item>
              <el-button @click="resetSearch">重置</el-button>
              <el-button type="primary" @click="applySearch">搜索</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 批量操作栏 -->
    <div v-if="selectedArticles.length > 0" class="batch-actions">
      <span>已选择 {{ selectedArticles.length }} 篇文章</span>
      <el-button-group style="margin-left: 15px">
        <el-button @click="batchUpdateStatus('published')">
          <el-icon><Check /></el-icon>
          批量发布
        </el-button>
        <el-button @click="batchUpdateStatus('draft')">
          <el-icon><Edit /></el-icon>
          批量转为草稿
        </el-button>
        <el-button type="danger" @click="batchDelete">
          <el-icon><Delete /></el-icon>
          批量删除
        </el-button>
        <el-button @click="clearSelection">
          <el-icon><Close /></el-icon>
          取消选择
        </el-button>
      </el-button-group>
    </div>

    <el-card>
      <el-table
        :data="filteredArticles.data"
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="title" label="标题">
          <template #default="{ row }">
            <span class="article-title" @click="goToArticleDetail(row.id)">
              {{ row.title }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="category_name" label="分类" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'published' ? 'success' : 'info'">
              {{ row.status === 'published' ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button link type="primary" @click="editArticle(row)">编辑</el-button>
            <el-button
              link
              :type="row.status === 'published' ? 'warning' : 'success'"
              @click="quickTogglePublish(row)"
            >
              {{ row.status === 'published' ? '取消发布' : '发布' }}
            </el-button>
            <el-button link type="danger" @click="deleteArticle(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="filteredArticles.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 创建/编辑文章对话框 -->
    <el-dialog
      :title="editMode ? '编辑文章' : '新建文章'"
      v-model="showCreateDialog"
      width="800px"
      @closed="resetForm"
    >
      <el-form :model="articleForm" :rules="articleRules" ref="articleFormRef">
        <el-form-item label="标题" prop="title">
          <el-input v-model="articleForm.title" placeholder="请输入文章标题" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="articleForm.category" placeholder="请选择分类" style="width: 100%">
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
            show-word-limit
            maxlength="200"
          />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="articleForm.content"
            type="textarea"
            placeholder="请输入文章内容"
            :rows="10"
            show-word-limit
            maxlength="10000"
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
          <span style="margin-left: 10px; color: #666">
            {{ articleForm.is_public ? '所有人可见' : '仅自己可见' }}
          </span>
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
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Check, Edit, Delete, Close } from '@element-plus/icons-vue'
import {
  getArticles,
  getArticle,
  createArticle,
  updateArticle,
  deleteArticle as deleteArticleApi,
} from '@/api/articles'
import { getCategories } from '@/api/categories'

const router = useRouter()
const loading = ref(false)
const showCreateDialog = ref(false)
const showAdvancedSearch = ref(false)
const submitting = ref(false)
const editMode = ref(false)
const editingId = ref(null)
const articleFormRef = ref()

const articles = ref([])
const categories = ref([])
const selectedArticles = ref([])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  status: '',
  category: '',
})

// 文章表单
const articleForm = reactive({
  title: '',
  category: null,
  summary: '',
  content: '',
  status: 'draft',
  is_public: true,
})

// 分页配置 - 使用单独的 ref 避免响应式问题
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
})

// 表单验证规则
const articleRules = {
  title: [
    { required: true, message: '请输入文章标题', trigger: 'blur' },
    { min: 2, max: 100, message: '标题长度在 2 到 100 个字符', trigger: 'blur' },
  ],
  content: [
    { required: true, message: '请输入文章内容', trigger: 'blur' },
    { min: 10, message: '内容至少需要 10 个字符', trigger: 'blur' },
  ],
}

// 计算属性：过滤和分页文章 - 返回包含数据和总数的对象
const filteredArticles = computed(() => {
  let filtered = articles.value

  // 关键词搜索
  if (searchForm.keyword) {
    const keyword = searchForm.keyword.toLowerCase()
    filtered = filtered.filter(
      (article) =>
        article.title.toLowerCase().includes(keyword) ||
        (article.summary && article.summary.toLowerCase().includes(keyword)),
    )
  }

  // 状态筛选
  if (searchForm.status) {
    filtered = filtered.filter((article) => article.status === searchForm.status)
  }

  // 分类筛选
  if (searchForm.category) {
    filtered = filtered.filter((article) => article.category == searchForm.category)
  }

  // 分页处理
  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize

  return {
    data: filtered.slice(start, end),
    total: filtered.length,
  }
})

// 选择处理
const handleSelectionChange = (selection) => {
  selectedArticles.value = selection
}

// 批量操作
const batchUpdateStatus = async (status) => {
  if (selectedArticles.value.length === 0) {
    ElMessage.warning('请先选择文章')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定将选中的 ${selectedArticles.value.length} 篇文章${status === 'published' ? '发布' : '转为草稿'}吗？`,
      '提示',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' },
    )

    loading.value = true

    const results = await Promise.allSettled(
      selectedArticles.value.map(async (article) => {
        try {
          // 为每篇文章获取完整数据
          const fullArticle = await getArticle(article.id)
          const updateData = {
            title: fullArticle.title,
            content: fullArticle.content,
            summary: fullArticle.summary || '',
            status: status,
            is_public: fullArticle.is_public,
            category: fullArticle.category,
          }
          // console.log(`更新文章 ${article.id} 的数据:`, updateData)
          return await updateArticle(article.id, updateData)
        } catch (error) {
          console.error(`获取文章 ${article.id} 详情失败:`, error)
          throw error
        }
      }),
    )

    // 检查结果
    const successful = results.filter((result) => result.status === 'fulfilled').length
    const failed = results.filter((result) => result.status === 'rejected').length

    if (failed > 0) {
      const failedDetails = results
        .filter((result) => result.status === 'rejected')
        .map(
          (result, index) =>
            `文章${index + 1}: ${result.reason.response?.data?.detail || result.reason.message}`,
        )
        .join('; ')

      ElMessage.warning(`成功更新 ${successful} 篇，失败 ${failed} 篇。失败原因: ${failedDetails}`)
    } else {
      ElMessage.success(`成功更新 ${successful} 篇文章`)
    }

    clearSelection()
    await loadArticles()
  } catch (error) {
    // 用户取消操作
    console.log('用户取消批量操作', error)
  } finally {
    loading.value = false
  }
}

const batchDelete = async () => {
  if (selectedArticles.value.length === 0) {
    ElMessage.warning('请先选择文章')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定删除选中的 ${selectedArticles.value.length} 篇文章吗？此操作不可恢复。`,
      '警告',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' },
    )

    loading.value = true

    const results = await Promise.allSettled(
      selectedArticles.value.map((article) => deleteArticleApi(article.id)),
    )

    const successful = results.filter((result) => result.status === 'fulfilled').length
    const failed = results.filter((result) => result.status === 'rejected').length

    if (failed > 0) {
      ElMessage.warning(`成功删除 ${successful} 篇，失败 ${failed} 篇`)
    } else {
      ElMessage.success(`成功删除 ${successful} 篇文章`)
    }

    clearSelection()
    await loadArticles()
  } catch {
    // 用户取消
  } finally {
    loading.value = false
  }
}

const clearSelection = () => {
  selectedArticles.value = []
}

// 搜索功能
const applySearch = () => {
  pagination.currentPage = 1
}

const resetSearch = () => {
  Object.assign(searchForm, {
    keyword: '',
    status: '',
    category: '',
  })
  pagination.currentPage = 1
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
}

// 日期格式化
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 跳转到文章详情页
const goToArticleDetail = (articleId) => {
  router.push(`/article/${articleId}`)
}

// 快速发布/取消发布
const quickTogglePublish = async (article) => {
  try {
    const newStatus = article.status === 'published' ? 'draft' : 'published'
    // 重新获取文章完整数据，确保有所有必需字段
    const fullArticle = await getArticle(article.id)

    // 使用完整数据更新
    const updateData = {
      title: fullArticle.title,
      content: fullArticle.content,
      summary: fullArticle.summary || '',
      status: newStatus,
      is_public: fullArticle.is_public,
      category: fullArticle.category,
    }

    await updateArticle(article.id, updateData)
    ElMessage.success(newStatus === 'published' ? '发布成功' : '已转为草稿')
    await loadArticles()
  } catch (error) {
    console.error('快速操作错误详情:', error)
    console.error('错误响应数据:', error.response?.data)

    if (error.response?.data) {
      const fieldErrors = Object.entries(error.response.data)
        .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`)
        .join('; ')
      ElMessage.error(`操作失败: ${fieldErrors || error.response.data.detail || '未知错误'}`)
    } else {
      ElMessage.error('操作失败: ' + error.message)
    }
  }
}

// 加载文章列表
const loadArticles = async () => {
  loading.value = true
  try {
    const response = await getArticles()
    // console.log('API响应数据:', response)
    articles.value = response
    // console.log('处理后文章列表:', articles.value)

    // 确保数据正确设置
    if (articles.value && articles.value.length > 0) {
      // console.log('第一篇文章数据:', articles.value[0])
    }
  } catch (error) {
    console.error('加载文章错误:', error)
    ElMessage.error('加载文章失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 加载分类列表
const loadCategories = async () => {
  try {
    const response = await getCategories()
    categories.value = response
  } catch (error) {
    console.error('加载分类错误:', error)
    ElMessage.error('加载分类失败')
  }
}

// 编辑文章
const editArticle = (article) => {
  editMode.value = true
  editingId.value = article.id
  Object.assign(articleForm, {
    title: article.title,
    category: article.category,
    summary: article.summary || '',
    content: article.content,
    status: article.status,
    is_public: article.is_public,
  })
  showCreateDialog.value = true
}

// 删除单篇文章
const deleteArticle = async (article) => {
  try {
    await ElMessageBox.confirm(`确定删除文章 "${article.title}" 吗？此操作不可恢复。`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteArticleApi(article.id)
    ElMessage.success('删除成功')
    await loadArticles()
  } catch {
    // 用户取消
  }
}

// 提交文章（创建或更新）
const submitArticle = async () => {
  if (!articleFormRef.value) return

  try {
    const valid = await articleFormRef.value.validate()
    if (!valid) return

    submitting.value = true

    if (editMode.value) {
      await updateArticle(editingId.value, articleForm)
      ElMessage.success('更新成功')
    } else {
      await createArticle(articleForm)
      ElMessage.success('创建成功')
    }

    showCreateDialog.value = false
    resetForm()
    await loadArticles()
  } catch (error) {
    console.error('操作文章错误:', error)
    ElMessage.error(
      editMode.value ? '更新失败' : '创建失败: ' + (error.response?.data?.detail || error.message),
    )
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  if (articleFormRef.value) {
    articleFormRef.value.resetFields()
  }
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

// 初始化加载
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-panel {
  margin-bottom: 20px;
}

.batch-actions {
  background: #f0f9ff;
  padding: 12px 16px;
  border: 1px solid #bae0ff;
  border-radius: 4px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.article-title {
  color: #409eff;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.3s;
}

.article-title:hover {
  color: #67a8ff;
  text-decoration: underline;
}
</style>
