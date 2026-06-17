<template>
  <div class="lesson-records-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>上课记录</span>
          <div class="header-right">
            <el-select v-model="filterChild" placeholder="选择孩子" @change="loadData" style="width: 120px;">
              <el-option :label="c.name" :value="c.id" v-for="c in children" :key="c.id" />
              <el-option label="全部" :value="null" />
            </el-select>
            <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" @change="loadData" />
          </div>
        </div>
      </template>

      <el-table :data="records" border :header-cell-style="{ background: '#f8f9fa' }" @row-click="viewRecord">
        <el-table-column prop="lesson_date" label="上课日期" width="120" />
        <el-table-column prop="course_name" label="课程名称" width="150" />
        <el-table-column prop="teacher_name" label="授课老师" width="100" />
        <el-table-column prop="status" label="上课状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="上课内容" min-width="200" />
        <el-table-column prop="homework" label="作业" min-width="200" />
      </el-table>

      <div v-if="records.length === 0" class="empty-hint">暂无上课记录</div>
    </el-card>

    <el-dialog title="上课详情" v-model="showDetail" width="500px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="日期">{{ selectedRecord?.lesson_date }}</el-descriptions-item>
        <el-descriptions-item label="课程">{{ selectedRecord?.course_name }}</el-descriptions-item>
        <el-descriptions-item label="老师">{{ selectedRecord?.teacher_name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(selectedRecord?.status)">{{ getStatusText(selectedRecord?.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="上课内容">
          <p>{{ selectedRecord?.content || '无' }}</p>
        </el-descriptions-item>
        <el-descriptions-item label="作业">
          <p>{{ selectedRecord?.homework || '无' }}</p>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { getLessonRecords, getChildren } from '../api/parent.js'

const records = ref([])
const children = ref([])
const filterChild = ref(null)
const dateRange = ref([])
const showDetail = ref(false)
const selectedRecord = ref(null)

function getStatusType(status) {
  const map = { attended: 'success', absent: 'danger', pending: 'warning' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { attended: '已上课', absent: '缺席', pending: '待上课' }
  return map[status] || status
}

function viewRecord(row) {
  selectedRecord.value = row
  showDetail.value = true
}

async function loadData() {
  try {
    const start = dateRange.value[0] ? dateRange.value[0].toISOString().split('T')[0] : null
    const end = dateRange.value[1] ? dateRange.value[1].toISOString().split('T')[0] : null
    records.value = await getLessonRecords(filterChild.value, start, end)
  } catch (e) {
    console.error('加载上课记录失败', e)
  }
}

async function loadChildren() {
  try {
    children.value = await getChildren()
  } catch (e) {
    console.error('加载孩子列表失败', e)
  }
}

onMounted(() => {
  loadChildren()
  loadData()
})

watch([filterChild, dateRange], () => {
  loadData()
})
</script>

<style scoped>
.lesson-records-page { padding: 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-right { display: flex; align-items: center; gap: 12px; }
.empty-hint { text-align: center; padding: 40px; color: #999; }
</style>