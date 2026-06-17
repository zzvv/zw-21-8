<template>
  <div class="exams-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>考级进度</span>
          <div class="header-right">
            <el-select v-model="filterChild" placeholder="选择孩子" @change="loadData" style="width: 120px;">
              <el-option :label="c.name" :value="c.id" v-for="c in children" :key="c.id" />
              <el-option label="全部" :value="null" />
            </el-select>
          </div>
        </div>
      </template>

      <div class="progress-section">
        <div class="progress-card" v-for="exam in exams" :key="exam.id">
          <div class="exam-header">
            <div class="exam-info">
              <h3 class="exam-name">{{ exam.exam_name }}</h3>
              <div class="exam-meta">
                <span class="exam-instrument">{{ exam.instrument }}</span>
                <span class="exam-level">{{ exam.level }}</span>
              </div>
            </div>
            <el-tag :type="getResultType(exam.result)" size="large">
              {{ getResultText(exam.result) }}
            </el-tag>
          </div>

          <div class="exam-detail">
            <div class="detail-item">
              <span class="detail-label">考试日期</span>
              <span class="detail-value">{{ exam.exam_date || '待定' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">成绩</span>
              <span class="detail-value">{{ exam.score || '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">证书编号</span>
              <span class="detail-value">{{ exam.certificate_no || '-' }}</span>
            </div>
            <div class="detail-item" v-if="exam.remark">
              <span class="detail-label">备注</span>
              <span class="detail-value">{{ exam.remark }}</span>
            </div>
          </div>

          <div class="progress-bar">
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: getProgressWidth(exam.result) }" :class="getResultType(exam.result)"></div>
            </div>
            <div class="progress-text">{{ getProgressText(exam.result) }}</div>
          </div>
        </div>

        <div v-if="exams.length === 0" class="empty-hint">
          <el-empty description="暂无考级记录" />
        </div>
      </div>

      <el-table :data="exams" border :header-cell-style="{ background: '#f8f9fa' }" style="margin-top: 20px;">
        <el-table-column prop="exam_name" label="考级名称" width="150" />
        <el-table-column prop="instrument" label="乐器" width="80" />
        <el-table-column prop="level" label="考级级别" width="100" />
        <el-table-column prop="exam_date" label="考试日期" width="120" />
        <el-table-column prop="result" label="考试结果" width="100">
          <template #default="{ row }">
            <el-tag :type="getResultType(row.result)">{{ getResultText(row.result) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="成绩" width="80" />
        <el-table-column prop="certificate_no" label="证书编号" width="150" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { getExams, getChildren } from '../api/parent.js'

const exams = ref([])
const children = ref([])
const filterChild = ref(null)

function getResultType(result) {
  const map = { passed: 'success', failed: 'danger' }
  return map[result] || 'info'
}

function getResultText(result) {
  const map = { passed: '通过', failed: '未通过' }
  return map[result] || (result || '待考')
}

function getProgressWidth(result) {
  if (result === 'passed') return '100%'
  if (result === 'failed') return '50%'
  return '30%'
}

function getProgressText(result) {
  if (result === 'passed') return '已完成'
  if (result === 'failed') return '需重考'
  return '备考中'
}

async function loadData() {
  try {
    exams.value = await getExams(filterChild.value)
  } catch (e) {
    console.error('加载考级记录失败', e)
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

watch(filterChild, () => {
  loadData()
})
</script>

<style scoped>
.exams-page { padding: 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-right { display: flex; align-items: center; gap: 12px; }
.progress-section { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.progress-card { background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.exam-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.exam-name { font-size: 16px; font-weight: 600; margin: 0; color: #333; }
.exam-meta { display: flex; gap: 12px; margin-top: 4px; }
.exam-instrument, .exam-level { font-size: 13px; color: #999; }
.exam-detail { display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 16px; }
.detail-item { min-width: 45%; }
.detail-label { font-size: 12px; color: #999; display: block; margin-bottom: 2px; }
.detail-value { font-size: 14px; color: #333; }
.progress-bar { margin-top: 12px; }
.progress-track { height: 8px; background: #f0f0f0; border-radius: 4px; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 4px; transition: width 0.3s; }
.progress-fill.success { background: linear-gradient(90deg, #2ecc71, #27ae60); }
.progress-fill.danger { background: linear-gradient(90deg, #e74c3c, #c0392b); }
.progress-fill.info { background: linear-gradient(90deg, #3498db, #2980b9); }
.progress-text { font-size: 12px; color: #999; margin-top: 8px; text-align: right; }
.empty-hint { grid-column: 1 / -1; text-align: center; padding: 40px; }
</style>