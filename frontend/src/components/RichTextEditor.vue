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
import { ref, shallowRef, watch, onBeforeUnmount, nextTick } from 'vue'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import '@wangeditor/editor/dist/css/style.css'

// 编辑器实例
const editorRef = shallowRef()
const isDestroyed = ref(false)

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
})

// 工具栏配置
const toolbarConfig = {
  excludeKeys: ['group-video', 'fullScreen'],
}

// 编辑器配置
const editorConfig = ref({
  placeholder: '请输入内容...',
  scroll: true,
  MENU_CONF: {
    uploadImage: {
      server: '/api/articles/upload/image/',
      fieldName: 'image',
      maxFileSize: 2 * 1024 * 1024,
      allowedFileTypes: ['image/*'],
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
      },
    },
  },
})

// 编辑器内容
const editorValue = ref('')

// 组件事件
const emit = defineEmits(['update:modelValue', 'change', 'created', 'destroyed'])

// 监听外部值变化 - 修复：只在编辑器存在时更新
watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal !== editorValue.value && !isDestroyed.value) {
      editorValue.value = newVal
      // 如果编辑器已经创建，手动设置内容
      if (editorRef.value && editorRef.value.setHtml) {
        editorRef.value.setHtml(newVal)
      }
    }
  },
  { immediate: true },
)

// 监听编辑器内容变化
watch(editorValue, (newVal) => {
  if (!isDestroyed.value) {
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

  // 设置初始内容
  if (props.modelValue) {
    editor.setHtml(props.modelValue)
  }

  // 设置编辑器高度
  nextTick(() => {
    setTimeout(() => {
      const textContainer = document.querySelector('.w-e-text-container')
      const scrollEl = document.querySelector('.w-e-scroll')

      if (textContainer && scrollEl) {
        textContainer.style.height = props.height
        textContainer.style.minHeight = props.height
        scrollEl.style.height = props.height
        scrollEl.style.minHeight = props.height
      }
    }, 100)
  })

  emit('created', editor)
}

// 编辑器销毁回调
const handleDestroyed = () => {
  isDestroyed.value = true
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

// 设置内容 - 确保安全设置
const setHtml = (html) => {
  if (editorRef.value && !isDestroyed.value && editorRef.value.setHtml) {
    editorRef.value.setHtml(html)
    editorValue.value = html
  }
}

// 清空内容
const clearContent = () => {
  if (editorRef.value && !isDestroyed.value) {
    editorRef.value.clear()
    editorValue.value = ''
  }
}

// 销毁编辑器
const destroyEditor = () => {
  if (editorRef.value && !isDestroyed.value) {
    editorRef.value.destroy()
    editorRef.value = null
    isDestroyed.value = true
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
})
</script>

<style scoped>
.rich-text-editor {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  min-height: v-bind(computedMinHeight); /* 使用计算属性 */
}

.editor-toolbar {
  border-bottom: 1px solid #dcdfe6;
  background: #fff;
}

/* 深度选择器修改编辑器内部样式 */
:deep(.w-e-text-container) {
  min-height: 100%;
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
