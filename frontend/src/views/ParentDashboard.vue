<template>
  <div class="dashboard">
    <el-card v-if="!loaded" class="loading-card">
      <el-empty description="加载中..." />
    </el-card>

    <template v-else-if="children.length === 0">
      <el-card class="empty-card">
        <el-empty description="您还未绑定任何学员，请先绑定孩子">
          <template #image>
            <el-icon :size="48" color="#909399"><UserFilled /></el-icon>
          </template>
          <el-button type="primary" @click="showBindDialog = true">绑定学员</el-button>
        </el-empty>
      </el-card>
    </template>

    <template v-else>
      <div class="stats-row">
        <el-card class="stat-card">
          <div class="stat-icon blue"><el-icon><UserFilled /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ children.length }}</div>
            <div class="stat-label">绑定的孩子</div>
          </div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-icon green"><el-icon><Calendar /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ upcomingLessons.length }}</div>
            <div class="stat-label">近期课程</div>
          </div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-icon orange"><el-icon><Document /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ recentRecords.length }}</div>
            <div class="stat-label">最近记录</div>
          </div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-icon purple"><el-icon><Medal /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ examProgress.length }}</div>
            <div class="stat-label">考级记录</div>
          </div>
        </el-card>
      </div>

      <div class="children-section">
        <el-card header="我的孩子" class="section-card">
          <el-row :gutter="16">
            <el-col :span="6" v-for="child in children" :key="child.id">
              <div class="child-card" :class="{ active: parentStore.selectedChildId === child.id }" @click="selectChild(child.id)">
                <div class="child-avatar">
                  <el-icon :size="32" color="#3498db"><UserFilled /></el-icon>
                </div>
                <div class="child-name">{{ child.name }}</div>
                <div class="child-level">级别: {{ child.level }}</div>
                <div class="child-phone">{{ child.phone }}</div>
              </div>
            </el-col>
          </el-row>
          <div style="margin-top: 12px; text-align: right;">
            <el-button size="small" @click="showBindDialog = true">绑定更多</el-button>
          </div>
        </el-card>
      </div>

      <div class="content-row">
        <el-card header="近期课表" class="section-card">
          <el-table :data="upcomingLessons" border :header-cell-style="{ background: '#f8f9fa' }">
            <el-table-column prop="student_name" label="孩子" width="80" />
            <el-table-column prop="course_name" label="课程" width="140" />
            <el-table-column prop="teacher_name" label="老师" width="80" />
            <el-table-column prop="weekday" label="周几" width="60">
              <template #default="{ row }">{{ formatWeekday(row.weekday) }}</template>
            </el-table-column>
            <el-table-column prop="start_time" label="时间" width="120">
              <template #default="{ row }">{{ row.start_time }} - {{ row.end_time }}</template>
            </el-table-column>
            <el-table-column prop="classroom_name" label="教室" width="100" />
          </el-table>
          <div v-if="upcomingLessons.length === 0" class="empty-hint">暂无近期课程</div>
        </el-card>

        <el-card header="最近上课记录" class="section-card">
          <el-table :data="recentRecords" border :header-cell-style="{ background: '#f8f9fa' }">
            <el-table-column prop="lesson_date" label="日期" width="100" />
            <el-table-column prop="course_name" label="课程" width="120" />
            <el-table-column prop="teacher_name" label="老师" width="80" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="content" label="上课内容" min-width="150" />
          </el-table>
          <div v-if="recentRecords.length === 0" class="empty-hint">暂无上课记录</div>
        </el-card>
      </div>

      <div class="content-row">
        <el-card header="作业与留言" class="section-card">
          <div v-if="homeworkList.length === 0" class="empty-hint">暂无作业</div>
          <div v-else>
            <el-timeline>
              <el-timeline-item v-for="item in homeworkList" :key="item.id" :timestamp="item.lesson_date" placement="top">
                <el-card shadow="hover">
                  <div class="homework-header">
                    <span class="homework-course">{{ item.course_name }}</span>
                    <span class="homework-teacher">{{ item.teacher_name }}</span>
                  </div>
                  <div class="homework-content">
                    <p><strong>上课内容:</strong> {{ item.content || '无' }}</p>
                    <p><strong>作业:</strong> {{ item.homework || '无' }}</p>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-card>

        <el-card header="考级进度" class="section-card">
          <el-table :data="examProgress" border :header-cell-style="{ background: '#f8f9fa' }">
            <el-table-column prop="exam_name" label="考级名称" width="150" />
            <el-table-column prop="instrument" label="乐器" width="80" />
            <el-table-column prop="level" label="级别" width="80" />
            <el-table-column prop="exam_date" label="考试日期" width="100" />
            <el-table-column prop="result" label="结果" width="80">
              <template #default="{ row }">
                <el-tag :type="getResultType(row.result)">{{ row.result || '待定' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="score" label="成绩" width="80" />
          </el-table>
          <div v-if="examProgress.length === 0" class="empty-hint">暂无考级记录</div>
        </el-card>
      </div>
    </template>

    <el-dialog title="绑定学员" v-model="showBindDialog" width="420px">
      <el-form :model="bindForm" :rules="bindRules" ref="bindFormRef">
        <el-form-item prop="studentId">
          <el-input v-model="bindForm.studentId" placeholder="请输入学员ID" />
        </el-form-item>
        <el-form-item prop="studentName">
          <el-input v-model="bindForm.studentName" placeholder="请输入学员姓名" />
        </el-form-item>
        <el-form-item>
          <el-alert title="绑定说明" type="info" :closable="false" show-icon>
            <p>绑定需验证您的手机号与学员登记的家长手机号一致</p>
            <p>如无法绑定，请联系教务确认：</p>
            <ul>
              <li>学员是否已登记家长手机号</li>
              <li>您的账号是否已登记手机号</li>
              <li>登记的手机号是否一致</li>
            </ul>
          </el-alert>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBindDialog = false">取消</el-button>
        <el-button type="primary" @click="doBind">确认绑定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useParentStore } from '../stores/parent.js'
import { getDashboard, bindChild } from '../api/parent.js'

const parentStore = useParentStore()
const loaded = ref(false)
const upcomingLessons = ref([])
const recentRecords = ref([])
const examProgress = ref([])
const showBindDialog = ref(false)
const bindFormRef = ref()
const bindForm = ref({ studentId: '', studentName: '' })

const children = computed(() => parentStore.children)

const bindRules = {
  studentId: [{ required: true, message: '请输入学员ID', trigger: 'blur' }],
  studentName: [{ required: true, message: '请输入学员姓名', trigger: 'blur' }],
}

const homeworkList = computed(() => {
  return recentRecords.value.filter(r => r.homework || r.content)
})

function formatWeekday(d) {
  const map = ['日', '一', '二', '三', '四', '五', '六']
  return map[d] || d
}

function getStatusType(status) {
  const map = { attended: 'success', absent: 'danger', pending: 'warning' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { attended: '已上课', absent: '缺席', pending: '待上课' }
  return map[status] || status
}

function getResultType(result) {
  const map = { passed: 'success', failed: 'danger' }
  return map[result] || 'info'
}

function selectChild(id) {
  parentStore.selectChild(id)
}

async function loadData() {
  try {
    const data = await getDashboard()
    upcomingLessons.value = data.upcoming_lessons || []
    recentRecords.value = data.recent_lesson_records || []
    examProgress.value = data.exam_progress || []
    if (data.children && data.children.length > 0) {
      parentStore.children = data.children
    }
  } catch (e) {
    ElMessage.error('加载数据失败')
    console.error(e)
  } finally {
    loaded.value = true
  }
}

async function doBind() {
  await bindFormRef.value.validate()
  try {
    await bindChild(parseInt(bindForm.value.studentId))
    ElMessage.success('绑定成功')
    showBindDialog.value = false
    bindForm.value = { studentId: '', studentName: '' }
    await parentStore.loadChildren()
    loadData()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '绑定失败')
  }
}

onMounted(() => {
  parentStore.loadChildren().then(() => {
    loadData()
  })
})

watch(() => parentStore.selectedChildId, () => {
  loadData()
})
</script>

<style scoped>
.dashboard { padding: 0; }
.loading-card, .empty-card { margin-bottom: 20px; }
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
.stat-card { display: flex; align-items: center; gap: 16px; }
.stat-icon { width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.stat-icon.blue { background: #e8f4fd; color: #3498db; }
.stat-icon.green { background: #e8f8f0; color: #2ecc71; }
.stat-icon.orange { background: #fff7e8; color: #f39c12; }
.stat-icon.purple { background: #f5e8f8; color: #9b59b6; }
.stat-value { font-size: 24px; font-weight: bold; color: #333; }
.stat-label { font-size: 13px; color: #999; }
.children-section { margin-bottom: 20px; }
.child-card { text-align: center; padding: 16px; border-radius: 8px; cursor: pointer; transition: all 0.3s; border: 2px solid transparent; }
.child-card:hover { background: #f8f9fa; }
.child-card.active { border-color: #3498db; background: #e8f4fd; }
.child-avatar { margin-bottom: 8px; }
.child-name { font-weight: 600; margin-bottom: 4px; }
.child-level, .child-phone { font-size: 12px; color: #999; }
.content-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
.section-card { min-height: 300px; }
.empty-hint { text-align: center; padding: 40px; color: #999; }
.homework-header { display: flex; justify-content: space-between; margin-bottom: 8px; }
.homework-course { font-weight: 600; color: #333; }
.homework-teacher { font-size: 12px; color: #999; }
.homework-content { font-size: 13px; line-height: 1.6; color: #666; }
</style>