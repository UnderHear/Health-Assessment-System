<template>
  <div class="page-container">
    <NavBar />
    <el-main>
      <div class="header-section">
        <h2 class="page-title">我的训练计划</h2>
        <el-button v-if="!activePlan" type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon> 创建新计划
        </el-button>
      </div>

      <div v-loading="loading">
        <!-- 无计划状态 -->
        <div v-if="!activePlan && !loading" class="empty-state">
          <el-empty description="暂无活跃计划">
            <el-button type="primary" @click="showCreateDialog = true">创建我的第一个计划</el-button>
          </el-empty>
        </div>

        <!-- 活跃计划 -->
        <div v-else-if="activePlan" class="plan-content">
          <!-- 计划概览卡片 -->
          <el-row :gutter="20">
            <el-col :span="16">
              <el-card class="overview-card">
                <div class="plan-header">
                  <div class="plan-info">
                    <h3 class="plan-name">{{ activePlan.planName }}</h3>
                    <div class="plan-meta">
                      <span>{{ formatDate(activePlan.startDate) }} - {{ formatDate(activePlan.endDate) }}</span>
                      <el-divider direction="vertical" />
                      <span>第 {{ planData.currentWeek }} / {{ activePlan.totalWeeks }} 周</span>
                    </div>
                  </div>
                  <el-dropdown @command="handlePlanAction">
                    <el-button type="info" text>
                      <el-icon><MoreFilled /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="pause" v-if="activePlan.status === 'ACTIVE'">
                          <el-icon><VideoPause /></el-icon> 暂停计划
                        </el-dropdown-item>
                        <el-dropdown-item command="resume" v-if="activePlan.status === 'PAUSED'">
                          <el-icon><VideoPlay /></el-icon> 恢复计划
                        </el-dropdown-item>
                        <el-dropdown-item command="complete">
                          <el-icon><CircleCheck /></el-icon> 完成计划
                        </el-dropdown-item>
                        <el-dropdown-item command="delete" divided>
                          <el-icon><Delete /></el-icon> 删除计划
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>

                <div class="progress-section">
                  <div class="progress-header">
                    <span class="progress-label">整体进度</span>
                    <span class="progress-value">{{ Math.round(planData.progress) }}%</span>
                  </div>
                  <el-progress :percentage="Math.round(planData.progress)" :stroke-width="12" />
                  
                  <div class="stats-row">
                    <div class="stat-item">
                      <div class="stat-value">{{ planData.totalCompleted }}</div>
                      <div class="stat-label">已完成</div>
                    </div>
                    <div class="stat-item">
                      <div class="stat-value">{{ planData.remainingDays }}</div>
                      <div class="stat-label">剩余天数</div>
                    </div>
                    <div class="stat-item">
                      <div class="stat-value">{{ activePlan.totalWeeks }}</div>
                      <div class="stat-label">总周数</div>
                    </div>
                  </div>
                </div>
              </el-card>
            </el-col>

            <el-col :span="8">
              <el-card class="quick-action-card">
                <h4 class="card-title">今日打卡</h4>
                <div class="today-check">
                  <div v-if="todayCheckIn" class="checked-status">
                    <el-icon :size="50" color="#67C23A"><SuccessFilled /></el-icon>
                    <div class="checked-text">今日已打卡</div>
                    <div class="checked-detail">{{ todayCheckIn.exerciseType }} · {{ todayCheckIn.duration }}分钟</div>
                  </div>
                  <div v-else class="not-checked">
                    <el-button type="primary" size="large" @click="showCheckInDialog = true" class="check-in-btn">
                      立即打卡
                    </el-button>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 本周训练日历 -->
          <el-card class="calendar-card">
            <div class="calendar-header">
              <h4 class="card-title">本周训练 (第{{ planData.currentWeek }}周)</h4>
            </div>
            <div class="week-calendar">
              <div 
                v-for="day in weekDays" 
                :key="day.date"
                class="day-item"
                :class="{ 
                  'is-today': isToday(day.date),
                  'is-checked': isDayChecked(day.date),
                  'is-future': isFuture(day.date)
                }"
                @click="handleDayClick(day)"
              >
                <div class="day-header">
                  <span class="day-name">{{ day.name }}</span>
                  <span class="day-date">{{ day.dateStr }}</span>
                </div>
                <div class="day-content">
                  <div v-if="isDayChecked(day.date)" class="checked-mark">
                    <el-icon :size="24"><CircleCheck /></el-icon>
                  </div>
                  <div v-else-if="!isFuture(day.date)" class="unchecked-mark">
                    <el-icon :size="24"><CircleClose /></el-icon>
                  </div>
                  <div v-else class="future-mark">-</div>
                </div>
                <div v-if="getDayCheckIn(day.date)" class="day-info">
                  {{ getDayCheckIn(day.date).exerciseType }}
                </div>
              </div>
            </div>
          </el-card>

          <!-- 打卡历史 -->
          <el-card class="history-card">
            <h4 class="card-title">打卡历史</h4>
            <el-timeline>
              <el-timeline-item
                v-for="checkIn in recentCheckIns"
                :key="checkIn.id"
                :timestamp="formatDateTime(checkIn.createTime)"
                placement="top"
              >
                <el-card class="check-in-item">
                  <div class="check-in-content">
                    <div class="check-in-main">
                      <span class="exercise-type">{{ checkIn.exerciseType }}</span>
                      <span class="duration">{{ checkIn.duration }}分钟</span>
                    </div>
                    <div v-if="checkIn.notes" class="check-in-notes">{{ checkIn.notes }}</div>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </div>
      </div>

      <!-- 创建计划对话框 -->
      <el-dialog v-model="showCreateDialog" title="创建训练计划" width="500px">
        <el-form :model="createForm" label-width="100px">
          <el-form-item label="计划名称">
            <el-input v-model="createForm.planName" placeholder="例如：10周健身计划" />
          </el-form-item>
          <el-form-item label="关联报告">
            <el-select v-model="createForm.testRecordId" placeholder="选择测试报告" style="width: 100%">
              <el-option
                v-for="record in completedRecords"
                :key="record.id"
                :label="formatDateTimeSeconds(record.createTime)"
                :value="record.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="开始日期">
            <el-date-picker
              v-model="createForm.startDate"
              type="date"
              placeholder="选择开始日期"
              style="width: 100%"
              :disabledDate="disabledDate"
            />
          </el-form-item>
          <el-form-item label="训练周数">
            <el-input-number v-model="createForm.totalWeeks" :min="4" :max="20" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="createPlan" :loading="creating">创建</el-button>
        </template>
      </el-dialog>

      <!-- 打卡对话框 -->
      <el-dialog v-model="showCheckInDialog" title="训练打卡" width="450px">
        <el-form :model="checkInForm" label-width="100px">
          <el-form-item label="运动类型">
            <el-select v-model="checkInForm.exerciseType" placeholder="选择运动类型" style="width: 100%">
              <el-option label="有氧运动" value="有氧运动" />
              <el-option label="力量训练" value="力量训练" />
              <el-option label="柔韧训练" value="柔韧训练" />
              <el-option label="综合训练" value="综合训练" />
            </el-select>
          </el-form-item>
          <el-form-item label="运动时长">
            <el-input-number v-model="checkInForm.duration" :min="5" :max="180" />
            <span style="margin-left: 10px; color: #909399;">分钟</span>
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="checkInForm.notes" type="textarea" :rows="3" placeholder="记录今天的感受..." />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showCheckInDialog = false">取消</el-button>
          <el-button type="primary" @click="submitCheckIn" :loading="checkingIn">提交</el-button>
        </template>
      </el-dialog>
    </el-main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, MoreFilled, VideoPause, VideoPlay, CircleCheck, Delete,
  SuccessFilled, CircleClose
} from '@element-plus/icons-vue'
import axios from 'axios'
import NavBar from '../components/NavBar.vue'
import { API_BASE_URL, API_ENDPOINTS, buildUrl } from '../api/config'

const router = useRouter()
const loading = ref(false)
const creating = ref(false)
const checkingIn = ref(false)
const activePlan = ref(null)
const planData = ref({})
const completedRecords = ref([])
const recentCheckIns = ref([])
const showCreateDialog = ref(false)
const showCheckInDialog = ref(false)

const createForm = ref({
  planName: '',
  testRecordId: null,
  startDate: new Date(),
  totalWeeks: 10
})

const checkInForm = ref({
  exerciseType: '',
  duration: 30,
  notes: ''
})

const weekDays = computed(() => {
  if (!activePlan.value) return []
  
  const today = new Date()
  const currentDay = today.getDay() || 7 // 1-7, 周一到周日
  const monday = new Date(today)
  monday.setDate(today.getDate() - currentDay + 1)
  
  const days = []
  const dayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  
  for (let i = 0; i < 7; i++) {
    const date = new Date(monday)
    date.setDate(monday.getDate() + i)
    days.push({
      name: dayNames[i],
      date: date,
      dateStr: `${date.getMonth() + 1}/${date.getDate()}`
    })
  }
  
  return days
})

const todayCheckIn = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return planData.value.weekCheckIns?.find(c => c.checkInDate === today)
})

const fetchActivePlan = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(buildUrl(API_ENDPOINTS.TRAINING.GET_ACTIVE), {
      headers: { Authorization: token }
    })
    
    if (response.data.code === 200 && response.data.data) {
      activePlan.value = response.data.data.plan
      planData.value = response.data.data
      await fetchRecentCheckIns()
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取计划失败')
  } finally {
    loading.value = false
  }
}

const fetchCompletedRecords = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(buildUrl(API_ENDPOINTS.PROFILE.HISTORY), {
      headers: { Authorization: token }
    })
    
    if (response.data.code === 200) {
      completedRecords.value = response.data.data.filter(r => r.status === 'COMPLETED')
    }
  } catch (error) {
    console.error(error)
  }
}

const fetchRecentCheckIns = async () => {
  if (!activePlan.value) return
  
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(buildUrl(API_ENDPOINTS.TRAINING.GET_CHECK_INS(activePlan.value.id)), {
      headers: { Authorization: token }
    })
    
    if (response.data.code === 200) {
      recentCheckIns.value = response.data.data.slice(0, 10)
    }
  } catch (error) {
    console.error(error)
  }
}

const createPlan = async () => {
  if (!createForm.value.planName) {
    ElMessage.warning('请输入计划名称')
    return
  }
  if (!createForm.value.testRecordId) {
    ElMessage.warning('请选择关联报告')
    return
  }
  
  creating.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.post(buildUrl(API_ENDPOINTS.TRAINING.CREATE), {
      ...createForm.value,
      startDate: createForm.value.startDate.toISOString().split('T')[0]
    }, {
      headers: { Authorization: token }
    })
    
    if (response.data.code === 200) {
      ElMessage.success('计划创建成功')
      showCreateDialog.value = false
      await fetchActivePlan()
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

const submitCheckIn = async () => {
  if (!checkInForm.value.exerciseType) {
    ElMessage.warning('请选择运动类型')
    return
  }
  
  checkingIn.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.post(buildUrl(API_ENDPOINTS.TRAINING.CHECK_IN), {
      planId: activePlan.value.id,
      checkInDate: new Date().toISOString().split('T')[0],
      ...checkInForm.value,
      completed: true
    }, {
      headers: { Authorization: token }
    })
    
    if (response.data.code === 200) {
      ElMessage.success('打卡成功！')
      showCheckInDialog.value = false
      checkInForm.value = { exerciseType: '', duration: 30, notes: '' }
      await fetchActivePlan()
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('打卡失败')
  } finally {
    checkingIn.value = false
  }
}

const handlePlanAction = async (command) => {
  const token = localStorage.getItem('token')
  
  try {
    if (command === 'delete') {
      await ElMessageBox.confirm('确定要删除这个计划吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      await axios.delete(buildUrl(API_ENDPOINTS.TRAINING.DELETE(activePlan.value.id)), {
        headers: { Authorization: token }
      })
      ElMessage.success('计划已删除')
      activePlan.value = null
    } else if (command === 'complete') {
      await ElMessageBox.confirm('确定要标记计划为已完成吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'success'
      })
      await axios.put(buildUrl(API_ENDPOINTS.TRAINING.COMPLETE(activePlan.value.id)), {}, {
        headers: { Authorization: token }
      })
      ElMessage.success('恭喜完成计划！')
      activePlan.value = null
    } else if (command === 'pause') {
      await axios.put(buildUrl(API_ENDPOINTS.TRAINING.PAUSE(activePlan.value.id)), {}, {
        headers: { Authorization: token }
      })
      ElMessage.success('计划已暂停')
      await fetchActivePlan()
    } else if (command === 'resume') {
      await axios.put(buildUrl(API_ENDPOINTS.TRAINING.RESUME(activePlan.value.id)), {}, {
        headers: { Authorization: token }
      })
      ElMessage.success('计划已恢复')
      await fetchActivePlan()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
      ElMessage.error('操作失败')
    }
  }
}

const handleDayClick = (day) => {
  if (isFuture(day.date)) return
  if (isToday(day.date) && !todayCheckIn.value) {
    showCheckInDialog.value = true
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

const formatDateTimeSeconds = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ` +
    `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`
}

const isToday = (date) => {
  const today = new Date()
  return date.toDateString() === today.toDateString()
}

const isFuture = (date) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return date > today
}

const isDayChecked = (date) => {
  const dateStr = date.toISOString().split('T')[0]
  return planData.value.weekCheckIns?.some(c => c.checkInDate === dateStr && c.completed)
}

const getDayCheckIn = (date) => {
  const dateStr = date.toISOString().split('T')[0]
  return planData.value.weekCheckIns?.find(c => c.checkInDate === dateStr)
}

const disabledDate = (date) => {
  return date < new Date(new Date().setHours(0, 0, 0, 0))
}

onMounted(async () => {
  await fetchActivePlan()
  await fetchCompletedRecords()
})
</script>

<style scoped>
.page-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}
.plan-content {
  max-width: 1200px;
  margin: 0 auto;
}
.overview-card {
  margin-bottom: 20px;
}
.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}
.plan-name {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}
.plan-meta {
  font-size: 14px;
  color: #909399;
}
.progress-section {
  margin-top: 16px;
}
.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}
.progress-label {
  font-size: 14px;
  color: #606266;
}
.progress-value {
  font-size: 18px;
  font-weight: 600;
  color: #409EFF;
}
.stats-row {
  display: flex;
  justify-content: space-around;
  margin-top: 24px;
}
.stat-item {
  text-align: center;
}
.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}
.stat-label {
  font-size: 13px;
  color: #909399;
}
.quick-action-card {
  margin-bottom: 20px;
  height: calc(100% - 20px);
}
.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
}
.today-check {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 150px;
}
.checked-status {
  text-align: center;
}
.checked-text {
  font-size: 16px;
  font-weight: 500;
  color: #67C23A;
  margin: 12px 0 8px;
}
.checked-detail {
  font-size: 14px;
  color: #909399;
}
.check-in-btn {
  width: 100%;
  height: 50px;
  font-size: 16px;
}
.calendar-card {
  margin-bottom: 20px;
}
.calendar-header {
  margin-bottom: 16px;
}
.week-calendar {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 12px;
}
.day-item {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}
.day-item:hover:not(.is-future) {
  background: #e4e7ed;
  transform: translateY(-2px);
}
.day-item.is-today {
  background: #ecf5ff;
  border: 2px solid #409EFF;
}
.day-item.is-checked {
  background: #f0f9ff;
  border: 2px solid #67C23A;
}
.day-item.is-future {
  opacity: 0.5;
  cursor: not-allowed;
}
.day-header {
  display: flex;
  flex-direction: column;
  margin-bottom: 8px;
}
.day-name {
  font-size: 13px;
  color: #606266;
  margin-bottom: 4px;
}
.day-date {
  font-size: 12px;
  color: #909399;
}
.day-content {
  margin: 12px 0;
}
.checked-mark {
  color: #67C23A;
}
.unchecked-mark {
  color: #F56C6C;
}
.future-mark {
  color: #dcdfe6;
  font-size: 20px;
}
.day-info {
  font-size: 12px;
  color: #606266;
  margin-top: 8px;
}
.history-card {
  margin-bottom: 20px;
}
.check-in-item {
  background: #fafafa;
}
.check-in-content {
  padding: 8px;
}
.check-in-main {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}
.exercise-type {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}
.duration {
  font-size: 14px;
  color: #409EFF;
}
.check-in-notes {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}
</style>
