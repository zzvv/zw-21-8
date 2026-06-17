<template>
  <el-container class="parent-layout">
    <el-aside width="200px" class="aside">
      <div class="logo">
        <el-icon :size="22"><Headset /></el-icon>
        <span>家长端</span>
      </div>
      <el-menu :default-active="route.path" router class="menu" background-color="#2c3e50" text-color="#ecf0f1" active-text-color="#3498db">
        <el-menu-item index="/parent/dashboard"><el-icon><Odometer /></el-icon><span>首页</span></el-menu-item>
        <el-menu-item index="/parent/schedules"><el-icon><Calendar /></el-icon><span>课表</span></el-menu-item>
        <el-menu-item index="/parent/lesson-records"><el-icon><Document /></el-icon><span>上课记录</span></el-menu-item>
        <el-menu-item index="/parent/exams"><el-icon><Medal /></el-icon><span>考级进度</span></el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span class="header-title">{{ pageTitle }}</span>
        <div class="header-right">
          <el-select v-model="selectedChild" placeholder="选择孩子" class="child-select" @change="handleChildChange">
            <el-option v-for="child in children" :key="child.id" :label="child.name" :value="child.id" />
          </el-select>
          <el-tag size="small" effect="plain">{{ userStore.userInfo?.real_name || userStore.userInfo?.username }}</el-tag>
          <el-button size="small" @click="logout" text><el-icon><SwitchButton /></el-icon> 退出</el-button>
        </div>
      </el-header>
      <el-main class="main"><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user.js'
import { getChildren } from '../api/parent.js'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const children = ref([])
const selectedChild = ref(null)

const pageTitle = computed(() => {
  const map = {
    '/parent/dashboard': '家长首页',
    '/parent/schedules': '课表',
    '/parent/lesson-records': '上课记录',
    '/parent/exams': '考级进度',
  }
  return map[route.path] || '家长端'
})

async function loadChildren() {
  try {
    children.value = await getChildren()
    if (children.value.length > 0) {
      const saved = localStorage.getItem('selectedChild')
      selectedChild.value = saved ? parseInt(saved) : children.value[0].id
    }
  } catch (e) {
    console.error('加载孩子列表失败', e)
  }
}

function handleChildChange(val) {
  localStorage.setItem('selectedChild', val)
}

function logout() {
  localStorage.removeItem('selectedChild')
  userStore.logout()
  router.push('/login')
}

onMounted(() => {
  loadChildren()
})

defineExpose({ children, selectedChild })
</script>

<style scoped>
.parent-layout { height: 100vh; background: #f8f9fa; }
.aside { background: #2c3e50; }
.logo { height: 56px; display: flex; align-items: center; gap: 10px; padding: 0 18px; color: #fff; font-size: 16px; font-weight: 600; border-bottom: 1px solid #34495e; }
.menu { border-right: none; }
.header { display: flex; align-items: center; justify-content: space-between; background: #fff; border-bottom: 1px solid #e9ecef; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
.header-title { font-size: 16px; font-weight: 600; color: #333; }
.header-right { display: flex; align-items: center; gap: 12px; }
.child-select { width: 140px; }
.main { padding: 20px; overflow: auto; }
</style>