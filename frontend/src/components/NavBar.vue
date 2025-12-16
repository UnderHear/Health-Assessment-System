<template>
  <el-header class="top-header">
    <div class="logo">
      <h1>体质健康测试分析与运动处方推荐系统</h1>
    </div>

    <el-menu
      :default-active="activeIndex"
      class="nav-menu"
      mode="horizontal"
      :ellipsis="false"
      router
    >
      <el-menu-item index="/">开始测试</el-menu-item>
      <el-menu-item index="/history">测试记录</el-menu-item>
      <el-menu-item index="/health">健康管理</el-menu-item>
      <el-menu-item index="/plan">我的计划</el-menu-item>
      <el-menu-item index="/profile">个人信息</el-menu-item>
    </el-menu>

    <div class="user-info">
      <span>欢迎，{{ userInfo?.realName || userInfo?.username }}</span>
      <el-button @click="handleLogout">退出登录</el-button>
    </div>
  </el-header>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userInfo = ref(null)

const activeIndex = computed(() => route.path)

onMounted(() => {
  const storedUserInfo = localStorage.getItem('userInfo')
  if (storedUserInfo) {
    userInfo.value = JSON.parse(storedUserInfo)
  }
})

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 0 20px;
  margin: -20px -20px 20px -20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: 60px;
}

.logo h1 {
  margin: 0;
  font-size: 20px;
  color: #303133;
  white-space: nowrap;
}

.nav-menu {
  flex: 1;
  justify-content: center;
  border-bottom: none !important;
  background: transparent !important;
  margin: 0 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #606266;
  white-space: nowrap;
}
</style>
