import request from './request.js'

export function getDashboard() {
  return request.get('/parent/dashboard')
}

export function getChildren() {
  return request.get('/parent/children')
}

export function bindChild(studentId) {
  return request.post('/parent/children', { student_id: studentId })
}

export function unbindChild(studentId) {
  return request.delete(`/parent/children/${studentId}`)
}

export function getSchedules(studentId) {
  const params = studentId ? { student_id: studentId } : {}
  return request.get('/parent/schedules', { params })
}

export function getLessonRecords(studentId, start, end) {
  const params = {}
  if (studentId) params.student_id = studentId
  if (start) params.start = start
  if (end) params.end = end
  return request.get('/parent/lesson-records', { params })
}

export function getExams(studentId) {
  const params = studentId ? { student_id: studentId } : {}
  return request.get('/parent/exams', { params })
}