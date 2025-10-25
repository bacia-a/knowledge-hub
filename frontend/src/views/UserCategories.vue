<template>
  <div class="categories-page">
    <div class="page-header">
      <h2>分类管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新建分类
      </el-button>
    </div>

    <el-card>
      <el-table :data="categories" v-loading="loading">
        <el-table-column prop="name" label="分类名称" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="article_count" label="文章数量" width="100" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button link type="primary" @click="editCategory(row)"> 编辑 </el-button>
            <el-button link type="danger" @click="deleteCategory(row)"> 删除 </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑分类对话框 -->
    <el-dialog :title="editMode ? '编辑分类' : '新建分类'" v-model="showCreateDialog" width="500px">
      <el-form :model="categoryForm" :rules="categoryRules" ref="categoryFormRef">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="categoryForm.description"
            type="textarea"
            placeholder="请输入分类描述"
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="颜色" prop="color">
          <el-color-picker v-model="categoryForm.color" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCategory" :loading="submitting">
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
  getCategories,
  createCategory,
  updateCategory,
  deleteCategory as deleteCategoryApi,
} from '@/api/categories'

const loading = ref(false)
const showCreateDialog = ref(false)
const submitting = ref(false)
const editMode = ref(false)
const editingId = ref(null)
const categoryFormRef = ref()

const categories = ref([])

const categoryForm = reactive({
  name: '',
  description: '',
  color: '#409EFF',
})

const categoryRules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }],
}

// 加载分类列表
const loadCategories = async () => {
  loading.value = true
  try {
    const response = await getCategories()
    categories.value = response
  } catch (error) {
    console.error(error)
    ElMessage.error('加载分类失败')
  } finally {
    loading.value = false
  }
}

const submitCategory = async () => {
  if (!categoryFormRef.value) return

  try {
    const valid = await categoryFormRef.value.validate()
    if (!valid) return

    submitting.value = true

    if (editMode.value) {
      // 更新分类
      await updateCategory(editingId.value, categoryForm)
      ElMessage.success('更新成功')
    } else {
      // 创建分类
      await createCategory(categoryForm)
      ElMessage.success('创建成功')
    }

    showCreateDialog.value = false
    resetForm()
    loadCategories()
  } catch (error) {
    console.error(error)
    ElMessage.error(editMode.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

const editCategory = (category) => {
  editMode.value = true
  editingId.value = category.id
  Object.assign(categoryForm, category)
  showCreateDialog.value = true
}

const deleteCategory = async (category) => {
  try {
    await ElMessageBox.confirm(`确定删除分类 "${category.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteCategoryApi(category.id)
    ElMessage.success('删除成功')
    loadCategories()
  } catch {
    // 用户取消
  }
}

const resetForm = () => {
  categoryFormRef.value?.resetFields()
  Object.assign(categoryForm, {
    name: '',
    description: '',
    color: '#409EFF',
  })
  editMode.value = false
  editingId.value = null
}

onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.categories-page {
  max-width: 1200px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>
