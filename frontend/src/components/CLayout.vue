<template>
  <div class="layout-container">
    <!-- 全局加载遮罩 -->
    <div v-if="globalLoading" class="global-loading">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <span>加载中...</span>
    </div>
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-left">
        <!-- 折叠按钮 -->
        <el-button
          @click="toggleSidebar"
          :icon="isCollapsed ? Expand : Fold"
          text
          class="collapse-btn"
        />
        <h2 class="logo" :class="{ 'logo-collapsed': isCollapsed }">
          {{ isCollapsed ? 'KH' : 'Knowledge Hub' }}
        </h2>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <!-- 显示用户头像 -->
            <el-avatar :size="32" :src="userAvatarUrl" class="user-avatar">
              {{ authStore.user?.username?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <span class="username">{{ authStore.user?.username }}</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人中心
              </el-dropdown-item>
              <el-dropdown-item command="logout" divided>
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <!-- 主体内容 -->
    <div class="main-content">
      <!-- 侧边栏 -->
      <el-aside class="sidebar" :width="sidebarWidth">
        <el-menu
          :default-active="activeMenu"
          router
          class="sidebar-menu"
          :collapse="isCollapsed"
          :collapse-transition="false"
          :unique-opened="true"
        >
          <el-menu-item index="/">
            <el-icon><House /></el-icon>
            <template #title>首页</template>
          </el-menu-item>
          <el-menu-item index="/articles">
            <el-icon><Document /></el-icon>
            <template #title>我的文章</template>
          </el-menu-item>
          <el-menu-item index="/categories">
            <el-icon><Folder /></el-icon>
            <template #title>分类管理</template>
          </el-menu-item>
          <el-menu-item index="/profile">
            <el-icon><User /></el-icon>
            <template #title>个人中心</template>
          </el-menu-item>
        </el-menu>

        <!-- 底部折叠按钮 -->
        <!-- <div class="sidebar-footer" @click="toggleSidebar">
          <el-icon class="collapse-icon">
            {{ isCollapsed ? Expand : Fold }}
          </el-icon>
          <span v-if="!isCollapsed">收起菜单</span>
        </div> -->
      </el-aside>

      <!-- 内容区域 -->
      <main class="content" :class="{ 'content-collapsed': isCollapsed }">
        <div class="content-wrapper">
          <router-view />
        </div>
      </main>
    </div>
    <AIAssistant />
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  House,
  Document,
  Folder,
  User,
  ArrowDown,
  Loading,
  SwitchButton,
  Fold,
  Expand,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import AIAssistant from '@/components/AIAssistant.vue'
const globalLoading = ref(false)
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 侧边栏折叠状态
const isCollapsed = ref(false)

// 计算侧边栏宽度
const sidebarWidth = computed(() => {
  return isCollapsed.value ? '64px' : '200px'
})

const activeMenu = computed(() => route.path)

// 计算用户头像URL
const userAvatarUrl = computed(() => {
  const user = authStore.user
  if (!user || !user.avatar) {
    return ''
  }

  let avatarPath = user.avatar

  // 如果已经是完整URL，直接返回
  if (avatarPath.startsWith('http')) {
    return avatarPath
  }

  // 如果是相对路径，确保以/开头
  if (!avatarPath.startsWith('/')) {
    avatarPath = '/' + avatarPath
  }

  // 拼接完整URL
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  return `${baseUrl}${avatarPath}`
})

// 切换侧边栏折叠状态
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

const handleCommand = async (command) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      })
      authStore.logout()
      ElMessage.success('退出成功')
      router.push('/login')
    } catch {
      // 用户取消
    }
  } else if (command === 'profile') {
    // 跳转到个人中心页面
    router.push('/profile')
  }
}

const setGlobalLoading = (loading) => {
  globalLoading.value = loading
}

// 监听用户信息变化，确保头像及时更新
watch(
  () => authStore.user,
  () => {
    // 用户信息更新时，可以在这里处理
  },
  { deep: true },
)

defineExpose({
  setGlobalLoading,
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
  z-index: 1000;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.collapse-btn {
  padding: 8px;
  border: none;
  background: transparent;
  color: #606266;
  transition: all 0.3s ease;
}

.collapse-btn:hover {
  color: #409eff;
  background: #f5f7fa;
  border-radius: 4px;
}

.logo {
  color: #409eff;
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.logo-collapsed {
  font-size: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.user-info:hover {
  background: #f5f7fa;
}

.user-avatar {
  border: 2px solid #e6e6e6;
  transition: border-color 0.3s ease;
}

.user-info:hover .user-avatar {
  border-color: #409eff;
}

.username {
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar {
  background: #fff;
  border-right: 1px solid #e6e6e6;
  box-shadow: 1px 0 3px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  overflow: hidden;
  flex-shrink: 0;
  z-index: 999;
}

.sidebar-menu {
  border: none;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 自定义滚动条样式 */
.sidebar-menu::-webkit-scrollbar {
  width: 4px;
}

.sidebar-menu::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.sidebar-menu::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.sidebar-menu::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 200px;
}

.sidebar-menu .el-menu-item {
  height: 50px;
  line-height: 50px;
  margin: 4px 8px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.sidebar-menu .el-menu-item.is-active {
  background-color: #ecf5ff;
  color: #409eff;
}

.sidebar-menu .el-menu-item:not(.is-active):hover {
  background-color: #f5f7fa;
}

/* 折叠状态下菜单项样式 */
.sidebar-menu.el-menu--collapse .el-menu-item {
  margin: 4px 8px;
  padding: 0 16px !important;
}

.sidebar-menu.el-menu--collapse .el-menu-item .el-tooltip__trigger {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 内容区域 - 主要修改部分 */
.content {
  flex: 1;
  padding: 20px;
  background: #f8f9fa;
  overflow-y: auto;
  overflow-x: hidden;
  transition: all 0.3s ease;
  display: flex;
  justify-content: center;
}

/* 内容包装器，控制最大宽度 */
.content-wrapper {
  width: 100%;
  max-width: 1200px;
  transition: all 0.3s ease;
}

/* 侧边栏收起时的内容区域样式 */
.content-collapsed .content-wrapper {
  max-width: 1400px; /* 收起时允许更宽的内容 */
}

/* 自定义内容区域滚动条 */
.content::-webkit-scrollbar {
  width: 6px;
}

.content::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.global-loading {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loading-icon {
  font-size: 40px;
  margin-bottom: 10px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header {
    padding: 0 15px;
  }

  .logo {
    font-size: 18px;
  }

  .username {
    display: none;
  }

  .sidebar {
    position: fixed;
    top: 60px;
    left: 0;
    bottom: 0;
    z-index: 1000;
    transform: translateX(0);
    transition: transform 0.3s ease;
  }

  .sidebar.collapsed-mobile {
    transform: translateX(-100%);
  }

  .content {
    margin-left: 0;
    padding: 15px;
  }

  .content-wrapper {
    max-width: 100% !important;
  }
}

/* 大屏幕优化 */
@media (min-width: 1600px) {
  .content-wrapper {
    max-width: 1400px;
  }

  .content-collapsed .content-wrapper {
    max-width: 1600px;
  }
}
</style>

<style>
/* 全局样式：修复 Element Plus 折叠菜单的工具提示问题 */
.el-menu--collapse .el-tooltip__trigger {
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
}

.el-menu--collapse .el-tooltip__trigger .el-menu-tooltip__trigger {
  display: none;
}

.el-popper {
  max-width: 200px;
}

.el-popper .el-popper__title {
  font-size: 14px;
  color: #333;
}
</style>
