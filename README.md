# Knowledge Hub - 个人知识管理系统

## 项目简介

Knowledge Hub 是一个现代化的个人知识管理系统，集成了 AI 助手功能，帮助用户高效地组织、管理和创作技术文档与知识内容。系统采用 Django + Vue3 全栈开发，提供丰富的文章管理、分类组织和 AI 辅助写作功能。

## 主要特性

### 🚀 核心功能
- **文章管理**：完整的文章 CRUD 操作，支持富文本编辑
- **分类管理**：自定义文章分类，支持颜色标记
- **用户系统**：完整的用户注册、登录和个人资料管理
- **响应式设计**：适配桌面和移动设备

### 🤖 AI 智能助手
- **AI 对话**：基于 DeepSeek API 的智能对话
- **大纲生成**：一键生成文章结构大纲
- **内容优化**：语法修正、风格优化、内容扩展
- **智能摘要**：自动生成文章摘要
- **标签生成**：智能提取文章关键词标签
- **自动补全**：AI 辅助内容创作

### 🎨 用户体验
- **现代化 UI**：基于 Element Plus 的优雅界面
- **富文本编辑器**：集成 WangEditor，支持图片上传
- **实时预览**：文章内容实时渲染
- **批量操作**：支持文章的批量发布、删除
- **会话管理**：AI 对话历史记录

## 技术栈

### 后端技术
- **框架**：Django 4.2.7 + Django REST Framework
- **数据库**：MySQL
- **认证**：JWT (djangorestframework-simplejwt)
- **AI 服务**：DeepSeek API 集成
- **文件存储**：本地文件系统
- **跨域**：django-cors-headers

### 前端技术
- **框架**：Vue 3 + Composition API
- **构建工具**：Vite
- **UI 组件**：Element Plus
- **路由**：Vue Router 4
- **状态管理**：Pinia
- **HTTP 客户端**：Axios
- **富文本编辑器**：WangEditor

## 项目结构
```bash
knowledge-hub/
├── backend/ # Django 后端
│ ├── apps/
│ │ ├── users/ # 用户管理
│ │ ├── articles/ # 文章管理
│ │ ├── categories/ # 分类管理
│ │ └── ai/ # AI 助手功能
│ ├── config/ # Django 配置
│ └── requirements.txt # Python 依赖
└── frontend/ # Vue 前端
├── src/
│ ├── api/ # API 接口
│ ├── components/ # 公共组件
│ ├── views/ # 页面视图
│ ├── stores/ # 状态管理
│ └── router/ # 路由配置
├── package.json
└── vite.config.js
```
## 快速开始

### 环境要求
- Python 3.8+
- Node.js 20.19.0+ 或 22.12.0+
- MySQL 5.7+

### 后端部署

1. **克隆项目**
```bash
git clone https://github.com/bacia-a/knowledge-hub.git
cd knowledge-hub/backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 前端部署
```bash
cd frontend
npm install
npm run dev
```