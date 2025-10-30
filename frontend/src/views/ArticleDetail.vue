<template>
  <div class="article-detail" v-loading="loading">
    <div class="article-header">
      <el-button @click="$router.back()" class="back-button">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>

      <div class="article-actions">
        <!-- 修改按钮点击事件 -->
        <el-button type="primary" @click="toggleEditMode">
          {{ editMode ? '取消编辑' : '编辑' }}
        </el-button>
        <el-button
          @click="quickTogglePublish(article)"
          :type="article.status === 'published' ? 'warning' : 'success'"
          :disabled="editMode"
        >
          {{ article.status === 'published' ? '取消发布' : '发布' }}
        </el-button>
        <el-button v-if="editMode" type="success" @click="saveArticle" :loading="saving">
          保存
        </el-button>
      </div>
    </div>

    <!-- 编辑模式 -->
    <el-card v-if="editMode" class="edit-card">
      <template #header>
        <div class="edit-header">
          <h3>编辑文章</h3>
          <el-alert title="编辑模式" type="info" :closable="false" show-icon />
        </div>
      </template>

      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="editForm.title" placeholder="请输入文章标题" />
        </el-form-item>

        <el-form-item label="分类" prop="category">
          <el-select v-model="editForm.category" placeholder="请选择分类" style="width: 100%">
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
            v-model="editForm.summary"
            type="textarea"
            placeholder="请输入文章摘要"
            :rows="3"
            show-word-limit
            maxlength="500"
          />
        </el-form-item>

        <el-form-item label="内容" prop="content">
          <!-- 添加编辑器创建事件 -->
          <RichTextEditor
            v-model="editForm.content"
            :height="'500px'"
            @onCreated="handleEditorCreated"
          />
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="editForm.status">
            <el-radio label="draft">草稿</el-radio>
            <el-radio label="published">发布</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="公开" prop="is_public">
          <el-switch v-model="editForm.is_public" />
          <span style="margin-left: 10px; color: #666">
            {{ editForm.is_public ? '所有人可见' : '仅自己可见' }}
          </span>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 阅读模式 -->
    <el-card v-else class="article-card">
      <template #header>
        <div class="article-title-section">
          <h1>{{ article.title }}</h1>
          <div class="article-meta">
            <el-tag :type="article.status === 'published' ? 'success' : 'info'">
              {{ article.status === 'published' ? '已发布' : '草稿' }}
            </el-tag>
            <span>创建时间: {{ formatDate(article.created_at) }}</span>
            <span v-if="article.published_at">
              发布时间: {{ formatDate(article.published_at) }}
            </span>
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
          <div class="content-body" v-html="article.content"></div>
        </div>

        <el-empty v-else description="暂无内容" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getArticle, updateArticle } from '@/api/articles'
import { getCategories } from '@/api/categories'
import RichTextEditor from '@/components/RichTextEditor.vue'

const route = useRoute()

const loading = ref(false)
const saving = ref(false)
const editMode = ref(false)
const editFormRef = ref()
const categories = ref([])
const editorRef = ref() // 添加编辑器引用

const article = ref({
  title: '',
  content: '',
  summary: '',
  status: 'draft',
  created_at: '',
  published_at: '',
  category_name: '',
  category: null,
  is_public: true,
})

// 编辑表单
const editForm = reactive({
  title: '',
  content: '',
  summary: '',
  status: 'draft',
  category: null,
  is_public: true,
})

// 表单验证规则
const editRules = {
  title: [
    { required: true, message: '请输入文章标题', trigger: 'blur' },
    { min: 2, max: 200, message: '标题长度在 2 到 200 个字符', trigger: 'blur' },
  ],
  content: [
    { required: true, message: '请输入文章内容', trigger: 'blur' },
    { min: 10, message: '内容至少需要 10 个字符', trigger: 'blur' },
  ],
}

const loadArticle = async () => {
  loading.value = true
  try {
    const articleId = route.params.id
    const response = await getArticle(articleId)
    article.value = response

    // 初始化编辑表单
    Object.assign(editForm, {
      title: response.title,
      content: response.content,
      summary: response.summary || '',
      status: response.status,
      category: response.category,
      is_public: response.is_public,
    })
  } catch (error) {
    console.error('加载文章错误:', error)
    ElMessage.error('加载文章失败')
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const response = await getCategories()
    categories.value = response
  } catch (error) {
    console.error('加载分类错误:', error)
    ElMessage.error('加载分类失败')
  }
}

// 切换编辑模式
const toggleEditMode = async () => {
  loadArticle()
  if (editMode.value) {
    // 退出编辑模式
    const hasChanges =
      editForm.title !== article.value.title ||
      editForm.content !== article.value.content ||
      editForm.summary !== article.value.summary ||
      editForm.status !== article.value.status ||
      editForm.category !== article.value.category ||
      editForm.is_public !== article.value.is_public

    if (hasChanges) {
      try {
        await ElMessageBox.confirm('有未保存的更改，确定要取消编辑吗？', '确认', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        })
        editMode.value = false
        // 重置表单到原始数据
        resetEditForm()
      } catch {
        // 用户取消操作
        return
      }
    } else {
      editMode.value = false
    }
  } else {
    // 进入编辑模式
    editMode.value = true
    // 确保表单数据正确同步
    nextTick(() => {
      // 如果有编辑器实例，手动设置内容
    })
  }
}

// 重置编辑表单到文章当前数据
const resetEditForm = () => {
  Object.assign(editForm, {
    title: article.value.title,
    content: article.value.content,
    summary: article.value.summary || '',
    status: article.value.status,
    category: article.value.category,
    is_public: article.value.is_public,
  })
}

// 保存文章
const saveArticle = async () => {
  if (!editFormRef.value) return

  try {
    const valid = await editFormRef.value.validate()
    if (!valid) return

    saving.value = true

    await updateArticle(article.value.id, editForm)

    ElMessage.success('保存成功')

    // 重新加载文章数据
    await loadArticle()

    // 退出编辑模式
    editMode.value = false
  } catch (error) {
    console.error('保存文章错误:', error)
    console.error('错误详情:', error.response?.data)
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

// 切换发布状态
const quickTogglePublish = async () => {
  try {
    const newStatus = article.value.status === 'published' ? 'draft' : 'published'

    const updateData = {
      title: article.value.title,
      content: article.value.content,
      summary: article.value.summary || '',
      status: newStatus,
      is_public: article.value.is_public,
      category: article.value.category,
    }

    await updateArticle(article.value.id, updateData)
    ElMessage.success(newStatus === 'published' ? '发布成功' : '已转为草稿')
    await loadArticle()
  } catch (error) {
    console.error('发布操作错误:', error)
    ElMessage.error('操作失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 监听编辑模式变化
watch(editMode, (newVal) => {
  if (newVal) {
    // 进入编辑模式时，确保数据正确
  }
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

// 获取编辑器实例的方法
const handleEditorCreated = (editor) => {
  editorRef.value = editor
  console.log('编辑器创建完成')
}

onMounted(() => {
  loadArticle()
  loadCategories()
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

.edit-card,
.article-card {
  margin-bottom: 20px;
}

.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  word-break: break-word;
  font-size: 16px;
  line-height: 1.6;
}

/* 富文本编辑器内容的样式 */
.content-body :deep(p) {
  margin-bottom: 1em;
}

.content-body :deep(img) {
  max-width: 100%;
  height: auto;
}

.content-body :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 1em;
}

.content-body :deep(table th),
.content-body :deep(table td) {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.content-body :deep(blockquote) {
  border-left: 4px solid #ddd;
  padding-left: 1em;
  margin-left: 0;
  color: #666;
}

.content-body :deep(pre) {
  background: #f5f5f5;
  padding: 1em;
  border-radius: 4px;
  overflow-x: auto;
}

.content-body :deep(code) {
  background: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}
</style>
