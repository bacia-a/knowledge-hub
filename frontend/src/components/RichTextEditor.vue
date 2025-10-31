<!-- RichTextEditor.vue -->
<template>
  <div class="rich-text-editor">
    <Toolbar
      :editor="editorRef"
      :defaultConfig="toolbarConfig"
      :mode="mode"
      class="editor-toolbar"
    />
    <Editor
      :defaultConfig="editorConfig"
      :mode="mode"
      v-model="editorValue"
      @onCreated="handleCreated"
      @onChange="handleChange"
      @onDestroyed="handleDestroyed"
      class="editor-content"
    />
  </div>
</template>

<script setup>
import { ref, shallowRef, watch, onBeforeUnmount, nextTick, computed } from 'vue'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import '@wangeditor/editor/dist/css/style.css'
import { ElMessage } from 'element-plus'

// 编辑器实例
const editorRef = shallowRef()
const isDestroyed = ref(false)
const isInitialized = ref(false)

// 编辑器模式
const mode = ref('default')

// 组件属性
const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  height: {
    type: String,
    default: '500px',
  },
  minHeight: {
    type: String,
    default: '400px',
  },
})

// 计算属性
const computedMinHeight = computed(() => props.minHeight)

// 工具栏配置
const toolbarConfig = {
  excludeKeys: ['group-video', 'fullScreen'],
}

// 修复的编辑器配置
const editorConfig = ref({
  placeholder: '请输入内容...',
  scroll: true,
  MENU_CONF: {
    uploadImage: {
      server: `${
        import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      }/api/articles/upload/image/`,
      fieldName: 'image',
      maxFileSize: 2 * 1024 * 1024,
      allowedFileTypes: ['image/*'],
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
      },
      // 自定义上传处理
      customUpload: async (file, insertFn) => {
        try {
          const formData = new FormData()
          formData.append('image', file)

          const response = await fetch(
            `${
              import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
            }/api/articles/upload/image/`,
            {
              method: 'POST',
              headers: {
                Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
              },
              body: formData,
            },
          )

          const result = await response.json()

          if (result.errno !== 0) {
            throw new Error(result.message || '上传失败')
          }

          // 使用Django返回的URL
          insertFn(result.data.url, result.data.alt, result.data.href)
        } catch (error) {
          console.error('图片上传失败:', error)
          ElMessage.error('图片上传失败: ' + error.message)
        }
      },
      // 自定义插入
      customInsert: (res, insertFn) => {
        insertFn(res.data.url, res.data.alt, res.data.href)
      },
    },
  },
})

// 编辑器内容
const editorValue = ref('')

// 组件事件
const emit = defineEmits(['update:modelValue', 'change', 'created', 'destroyed'])

// 安全设置HTML内容
const safeSetHtml = (html) => {
  if (!editorRef.value || isDestroyed.value || !editorRef.value.setHtml) {
    console.warn('编辑器未就绪，无法设置内容')
    return false
  }

  try {
    // 延迟设置确保编辑器完全初始化
    setTimeout(() => {
      if (editorRef.value && !isDestroyed.value) {
        editorRef.value.setHtml(html || '')
        editorValue.value = html || ''
      }
    }, 100)
    return true
  } catch (error) {
    console.error('设置编辑器内容失败:', error)
    return false
  }
}

// 监听外部值变化
watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal !== editorValue.value && !isDestroyed.value && isInitialized.value) {
      safeSetHtml(newVal)
    }
  },
  { immediate: true },
)

// 监听编辑器内容变化
watch(editorValue, (newVal) => {
  if (!isDestroyed.value && isInitialized.value) {
    emit('update:modelValue', newVal)
  }
})

// 编辑器变化回调
const handleChange = (editor) => {
  if (!isDestroyed.value) {
    emit('change', editor)
  }
}

// 编辑器创建回调
const handleCreated = (editor) => {
  editorRef.value = editor
  isDestroyed.value = false
  isInitialized.value = true

  // 安全设置初始内容
  if (props.modelValue) {
    nextTick(() => {
      safeSetHtml(props.modelValue)
    })
  }

  // 设置编辑器高度
  nextTick(() => {
    setTimeout(() => {
      const textContainer = document.querySelector('.w-e-text-container')
      const scrollEl = document.querySelector('.w-e-scroll')

      if (textContainer && scrollEl) {
        textContainer.style.height = props.height
        textContainer.style.minHeight = props.minHeight
        scrollEl.style.height = props.height
        scrollEl.style.minHeight = props.minHeight
      }
    }, 200)
  })

  emit('created', editor)
}

// 编辑器销毁回调
const handleDestroyed = () => {
  isDestroyed.value = true
  isInitialized.value = false
  emit('destroyed')
}

// 获取纯文本内容
const getText = () => {
  return editorRef.value && !isDestroyed.value ? editorRef.value.getText() : ''
}

// 获取HTML内容
const getHtml = () => {
  return editorRef.value && !isDestroyed.value ? editorRef.value.getHtml() : ''
}

// 设置内容
const setHtml = (html) => {
  return safeSetHtml(html)
}

// 清空内容
const clearContent = () => {
  if (editorRef.value && !isDestroyed.value) {
    try {
      editorRef.value.clear()
      editorValue.value = ''
    } catch (error) {
      console.error('清空编辑器内容失败:', error)
    }
  }
}

// 销毁编辑器
const destroyEditor = () => {
  if (editorRef.value && !isDestroyed.value) {
    try {
      editorRef.value.destroy()
      editorRef.value = null
      isDestroyed.value = true
      isInitialized.value = false
    } catch (error) {
      console.error('销毁编辑器失败:', error)
    }
  }
}

// 组件卸载时销毁编辑器
onBeforeUnmount(() => {
  destroyEditor()
})

// 暴露方法给父组件
defineExpose({
  getText,
  getHtml,
  setHtml,
  clearContent,
  destroyEditor,
  isDestroyed,
  isInitialized,
})
</script>

<style scoped>
.rich-text-editor {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  min-height: v-bind(computedMinHeight);
}

.editor-toolbar {
  border-bottom: 1px solid #dcdfe6;
  background: #fff;
}

/* 深度选择器修改编辑器内部样式 */
:deep(.w-e-text-container) {
  min-height: v-bind(computedMinHeight);
}

:deep(.w-e-scroll) {
  min-height: v-bind(computedMinHeight) !important;
}

:deep(.w-e-bar) {
  position: relative !important;
  z-index: 10;
}

:deep(.w-e-menu-tooltip) {
  z-index: 1000 !important;
}

:deep(.w-e-modal) {
  z-index: 1000 !important;
}

:deep(.w-e-bar-divider) {
  margin: 0 8px !important;
}
</style>
