<template>
  <div class="profile-page">
    <div class="page-header">
      <h2>个人中心</h2>
    </div>

    <el-row :gutter="20">
      <!-- 左侧：基本信息 -->
      <el-col :span="16">
        <el-card class="profile-card">
          <template #header>
            <h3>基本信息</h3>
          </template>

          <el-form
            :model="profileForm"
            :rules="profileRules"
            ref="profileFormRef"
            label-width="100px"
          >
            <el-form-item label="用户名">
              <el-input v-model="authStore.user.username" disabled />
            </el-form-item>

            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" />
            </el-form-item>

            <el-form-item label="姓氏" prop="first_name">
              <el-input v-model="profileForm.first_name" />
            </el-form-item>

            <el-form-item label="名字" prop="last_name">
              <el-input v-model="profileForm.last_name" />
            </el-form-item>

            <el-form-item label="个人简介" prop="bio">
              <el-input
                v-model="profileForm.bio"
                type="textarea"
                :rows="4"
                placeholder="介绍一下自己..."
                maxlength="500"
                show-word-limit
              />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleUpdateProfile" :loading="updating">
                保存修改
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 修改密码 -->
        <el-card class="password-card">
          <template #header>
            <h3>修改密码</h3>
          </template>

          <el-form
            :model="passwordForm"
            :rules="passwordRules"
            ref="passwordFormRef"
            label-width="100px"
          >
            <el-form-item label="当前密码" prop="old_password">
              <el-input v-model="passwordForm.old_password" type="password" show-password />
            </el-form-item>

            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="passwordForm.new_password" type="password" show-password />
            </el-form-item>

            <el-form-item label="确认密码" prop="confirm_password">
              <el-input v-model="passwordForm.confirm_password" type="password" show-password />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleChangePassword" :loading="changingPassword">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧：头像上传 -->
      <el-col :span="8">
        <el-card class="avatar-card">
          <template #header>
            <h3>头像设置</h3>
          </template>

          <div class="avatar-upload">
            <div class="avatar-preview">
              <img :src="avatarUrl" alt="头像" class="avatar-image" @error="handleAvatarError" />
            </div>

            <div class="upload-actions">
              <el-upload
                action=""
                :show-file-list="false"
                :before-upload="beforeAvatarUpload"
                :http-request="handleAvatarUpload"
                accept=".jpg,.jpeg,.png,.gif,.webp"
              >
                <el-button type="primary">
                  <el-icon><Upload /></el-icon>
                  上传头像
                </el-button>
              </el-upload>

              <el-button
                v-if="authStore.user.avatar"
                @click="handleRemoveAvatar"
                :loading="removingAvatar"
                style="margin-top: 10px"
              >
                移除头像
              </el-button>
            </div>

            <div class="upload-tips">
              <p>支持 JPG、PNG、GIF、WebP 格式</p>
              <p>文件大小不超过 2MB</p>
              <p>建议尺寸 200x200 像素</p>
            </div>
          </div>
        </el-card>

        <!-- 账户信息 -->
        <el-card class="info-card">
          <template #header>
            <h3>账户信息</h3>
          </template>

          <div class="account-info">
            <div class="info-item">
              <span class="label">注册时间：</span>
              <span class="value">{{ formatDate(authStore.user.date_joined) }}</span>
            </div>
            <div class="info-item">
              <span class="label">最后登录：</span>
              <span class="value">{{ formatDate(authStore.user.last_login) }}</span>
            </div>
            <div class="info-item">
              <span class="label">用户ID：</span>
              <span class="value">{{ authStore.user.id }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
// 重命名导入的函数，避免命名冲突
import {
  updateProfile as updateProfileApi,
  uploadAvatar as uploadAvatarApi,
  changePassword as changePasswordApi,
  removeAvatar as removeAvatarApi,
} from '@/api/profile'

const authStore = useAuthStore()
const profileFormRef = ref()
const passwordFormRef = ref()

const updating = ref(false)
const changingPassword = ref(false)
const removingAvatar = ref(false)

// 基本信息表单
const profileForm = reactive({
  email: '',
  first_name: '',
  last_name: '',
  bio: '',
})

// 密码修改表单
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

// 头像URL计算属性
const avatarUrl = computed(() => {
  if (authStore.user.avatar) {
    if (authStore.user.avatar.startsWith('http')) {
      return authStore.user.avatar
    }
    return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}${authStore.user.avatar}`
  }
  // 使用简单的SVG数据URI作为默认头像，避免文件加载问题
  return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMTAwIiBjeT0iMTAwIiByPSIxMDAiIGZpbGw9IiNlNmU2ZTYiLz48Y2lyY2xlIGN4PSIxMDAiIGN5PSI4MCIgcj0iMzAiIGZpbGw9IiM5OTkiLz48cGF0aCBkPSJNNTAgMTQwIFE5MCAxODAgMTUwIDE0MCIgc3Ryb2tlPSIjOTk5IiBzdHJva2Utd2lkdGg9IjgiIGZpbGw9Im5vbmUiLz48L3N2Zz4='
})

// 表单验证规则
const profileRules = {
  email: [{ type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }],
}

const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== passwordForm.new_password) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const passwordRules = {
  old_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' },
  ],
}

// 初始化表单数据
const initFormData = () => {
  Object.assign(profileForm, {
    email: authStore.user.email || '',
    first_name: authStore.user.first_name || '',
    last_name: authStore.user.last_name || '',
    bio: authStore.user.bio || '',
  })
}

// 更新个人信息 - 修复函数名
const handleUpdateProfile = async () => {
  if (!profileFormRef.value) return

  try {
    const valid = await profileFormRef.value.validate()
    if (!valid) return

    updating.value = true
    await updateProfileApi(profileForm)

    ElMessage.success('个人信息更新成功')
    await authStore.fetchUserProfile()
  } catch (error) {
    console.error('更新个人信息失败:', error)
    ElMessage.error(error.response?.data?.error || '更新失败')
  } finally {
    updating.value = false
  }
}

// 修改密码 - 修复函数名
const handleChangePassword = async () => {
  if (!passwordFormRef.value) return

  try {
    const valid = await passwordFormRef.value.validate()
    if (!valid) return

    changingPassword.value = true

    const { ...passwordData } = passwordForm
    await changePasswordApi(passwordData)

    ElMessage.success('密码修改成功')
    passwordFormRef.value.resetFields()
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error(error.response?.data?.error || '修改失败')
  } finally {
    changingPassword.value = false
  }
}

// 头像上传前验证
const beforeAvatarUpload = (file) => {
  const isImage = /\.(jpg|jpeg|png|gif|webp)$/i.test(file.name)
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  return true
}

// 处理头像上传
const handleAvatarUpload = async (options) => {
  const { file } = options

  try {
    const formData = new FormData()
    formData.append('avatar', file)

    await uploadAvatarApi(formData)

    ElMessage.success('头像上传成功')
    await authStore.fetchUserProfile()
  } catch (error) {
    console.error('头像上传失败:', error)
    ElMessage.error(error.response?.data?.error || '上传失败')
  }
}

// 移除头像
const handleRemoveAvatar = async () => {
  try {
    await ElMessageBox.confirm('确定要移除头像吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    removingAvatar.value = true
    await removeAvatarApi()

    ElMessage.success('头像移除成功')
    await authStore.fetchUserProfile()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('移除头像失败:', error)
      ElMessage.error(error.response?.data?.error || '移除失败')
    }
  } finally {
    removingAvatar.value = false
  }
}

// 头像加载失败处理
const handleAvatarError = (e) => {
  e.target.src = '/default-avatar.png'
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(() => {
  initFormData()
})
</script>

<style scoped>
.profile-page {
  max-width: 1200px;
}

.page-header {
  margin-bottom: 20px;
}

.profile-card,
.password-card,
.avatar-card,
.info-card {
  margin-bottom: 20px;
}

.avatar-upload {
  text-align: center;
}

.avatar-preview {
  margin-bottom: 20px;
}

.avatar-image {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e6e6e6;
}

.upload-actions {
  margin-bottom: 15px;
}

.upload-tips {
  color: #666;
  font-size: 12px;
  line-height: 1.5;
}

.upload-tips p {
  margin: 5px 0;
}

.account-info {
  padding: 10px 0;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.label {
  color: #666;
}

.value {
  color: #333;
  font-weight: 500;
}
</style>
