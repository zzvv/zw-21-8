<template>
  <div class="schedule-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>课程表</span>
          <div class="header-right">
            <el-select v-model="filterChild" placeholder="选择孩子" @change="loadData">
              <el-option :label="c.name" :value="c.id" v-for="c in children" :key="c.id" />
              <el-option label="全部" :value="null" />
            </el-select>
          </div>
        </div>
      </template>

      <div class="week-view">
        <div class="week-header">
          <div class="day-cell" v-for="(day, idx) in weekDays" :key="idx">
            <div class="day-name">{{ day.name }}</div>
            <div class="day-date">{{ day.date }}</div>
          </div>
        </div>
        <div class="week-body">
          <div class="time-column">
            <div class="time-slot" v-for="t in timeSlots" :key="t">{{ t }}</div>
          </div>
          <div class="days-container">
            <div class="day-column" v-for="(day, idx) in weekDays" :key="idx">
              <div class="time-slot" v-for="t in timeSlots" :key="t">
                <div class="slot-content">
                  <div v-for="course in getCoursesForDay(day.weekday, t)" :key="course.id" class="course-card">
                    <div class="course-title">{{ course.course_name }}</div>
                    <div class="course-teacher">{{ course.teacher_name }}</div>
                    <div class="course-classroom">{{ course.classroom_name }}</div>
                    <div class="course-student">{{ course.student_name }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <el-table :data="schedules" border :header-cell-style="{ background: '#f8f9fa' }" style="margin-top: 20px;">
        <el-table-column prop="student_name" label="孩子" width="80" />
        <el-table-column prop="course_name" label="课程名称" width="150" />
        <el-table-column prop="instrument" label="乐器" width="80" />
        <el-table-column prop="teacher_name" label="授课老师" width="100" />
        <el-table-column prop="classroom_name" label="教室" width="100" />
        <el-table-column prop="weekday" label="星期" width="60">
          <template #default="{ row }">{{ formatWeekday(row.weekday) }}</template>
        </el-table-column>
        <el-table-column prop="start_time" label="上课时间" width="120">
          <template #default="{ row }">{{ row.start_time }} - {{ row.end_time }}</template>
        </el-table-column>
        <el-table-column prop="start_date" label="开始日期" width="100" />
        <el-table-column prop="end_date" label="结束日期" width="100">
          <template #default="{ row }">{{ row.end_date || '长期' }}</template>
        </el-table-column>
      </el-table>

      <div v-if="schedules.length === 0" class="empty-hint">暂无排课信息</div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { getSchedules, getChildren } from '../api/parent.js'

const schedules = ref([])
const children = ref([])
const filterChild = ref(null)

const timeSlots = ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00']

const weekDays = computed(() => {
  const days = []
  const today = new Date()
  const dayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  for (let i = 0; i < 7; i++) {
    const d = new Date(today)
    d.setDate(today.getDate() + i)
    days.push({
      name: dayNames[d.getDay()],
      date: `${d.getMonth() + 1}/${d.getDate()}`,
      weekday: d.getDay()
    })
  }
  return days
})

function formatWeekday(d) {
  const map = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return map[d] || d
}

function getCoursesForDay(weekday, time) {
  return schedules.value.filter(s => s.weekday === weekday && s.start_time.startsWith(time.substring(0, 2)))
}

async function loadData() {
  try {
    schedules.value = await getSchedules(filterChild.value)
  } catch (e) {
    console.error('加载课表失败', e)
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
.schedule-page { padding: 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-right { display: flex; align-items: center; gap: 12px; }
.week-view { margin-bottom: 20px; }
.week-header { display: flex; border-bottom: 2px solid #e4e7ed; }
.day-cell { flex: 1; padding: 12px; text-align: center; border-right: 1px solid #e4e7ed; }
.day-cell:last-child { border-right: none; }
.day-name { font-weight: 600; color: #333; }
.day-date { font-size: 12px; color: #999; }
.week-body { display: flex; }
.time-column { width: 60px; border-right: 2px solid #e4e7ed; }
.time-slot { height: 60px; padding: 4px; font-size: 12px; color: #999; }
.days-container { flex: 1; display: flex; }
.day-column { flex: 1; border-right: 1px solid #e4e7ed; }
.day-column:last-child { border-right: none; }
.slot-content { height: 60px; padding: 4px; }
.course-card { background: #e8f4fd; border-radius: 4px; padding: 4px; font-size: 11px; border: 1px solid #b3d9f5; }
.course-title { font-weight: 600; color: #3498db; margin-bottom: 2px; }
.course-teacher, .course-classroom, .course-student { color: #666; }
.empty-hint { text-align: center; padding: 40px; color: #999; }
</style>