<template>
  <div class="page-container">
    <NavBar />
    <el-main>
      <div class="content-container">
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
                  <el-button type="primary" size="large" @click="openCheckInDialog()" class="check-in-btn">
                    立即打卡
                  </el-button>
                </div>
              </div>
              <div v-if="todayPlan" class="today-plan-hint">
                <div class="hint-title">今日计划</div>
                <div class="hint-text">{{ todayPlan.summary || '按计划训练' }}</div>
              </div>
            </el-card>
          </el-col>
          </el-row>

          <!-- 日历视图 -->
          <el-card class="calendar-card">
            <div class="calendar-header">
              <h4 class="card-title">训练日历</h4>
            </div>

            <el-tabs v-model="calendarView" type="card" class="calendar-tabs">
              <el-tab-pane label="周视图" name="week">
                <div class="calendar-subtitle">本周训练 (第{{ planData.currentWeek }}周)</div>
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
                    <div v-if="getDayPlan(day.date)?.summary" class="day-info recommended-info">
                      <el-popover v-if="getDayPlan(day.date)?.detail" placement="top" trigger="hover" width="360">
                        <template #reference>
                          <div class="day-plan-summary">任务：{{ getDayPlan(day.date).summary }}</div>
                        </template>
                        <div class="md-body md-compact" v-html="renderMarkdown(getDayPlan(day.date).detail || getDayPlan(day.date).summary)"></div>
                      </el-popover>
                      <div v-else class="day-plan-summary">任务：{{ getDayPlan(day.date).summary }}</div>
                    </div>
                    <div v-if="getDayCheckIn(day.date)" class="day-info checked-info">
                      已打卡：{{ getDayCheckIn(day.date).exerciseType }} · {{ getDayCheckIn(day.date).duration }}分钟
                    </div>
                    <div v-if="getDayCheckIn(day.date)" class="day-info checked-metrics">
                      <span v-if="getDayCheckIn(day.date).avgHeartRate">心率 {{ getDayCheckIn(day.date).avgHeartRate }} bpm</span>
                      <span v-if="getDayCheckIn(day.date).rpe"> · RPE {{ getDayCheckIn(day.date).rpe }} ({{ rpeLabel(getDayCheckIn(day.date).rpe) }})</span>
                      <span v-if="getDayCheckIn(day.date).fatigueLevel"> · 疲劳 {{ getDayCheckIn(day.date).fatigueLevel }}</span>
                    </div>
                  </div>
                </div>
              </el-tab-pane>

              <el-tab-pane label="月视图" name="month">
                <el-calendar v-model="monthCursor" class="month-calendar">
                  <template #date-cell="{ data }">
                    <div
                      class="month-cell"
                      :class="{
                        'month-cell--other': data.type !== 'current',
                        'month-cell--today': isToday(data.date),
                        'month-cell--future': isFuture(data.date),
                        'month-cell--checked': isDayChecked(data.date)
                      }"
                      @click="handleMonthDayClick(data)"
                    >
                      <div class="month-cell__head">
                        <span class="month-cell__day">{{ Number(String(data.day).slice(8)) }}</span>
                        <el-tag v-if="isDayChecked(data.date)" size="small" type="success" effect="plain">已打卡</el-tag>
                      </div>
                      <div v-if="getDayPlan(data.date)?.summary" class="month-cell__task">
                        {{ getDayPlan(data.date).summary }}
                      </div>
                      <div v-else class="month-cell__task month-cell__task--empty">—</div>
                    </div>
                  </template>
                </el-calendar>
              </el-tab-pane>
            </el-tabs>
          </el-card>

          <el-card class="plan-structured-card" v-if="planReportMd">
            <div class="plan-card-header">
              <h4 class="card-title">分阶段训练计划</h4>
              <div class="plan-card-tags">
                <el-tag v-if="activePlan?.testRecordId" type="info" effect="plain">报告 #{{ activePlan.testRecordId }}</el-tag>
                <el-tag v-if="currentWeekPhase?.tabLabel" type="success" effect="plain">当前阶段：{{ currentWeekPhase.tabLabel }}</el-tag>
              </div>
            </div>

            <div v-if="reportPlan.planIntro" class="md-body plan-intro" v-html="renderMarkdown(reportPlan.planIntro)"></div>

            <div v-if="structuredPhases.length > 0" class="plan-tabs">
              <el-tabs v-model="activePhaseKey" type="card" class="plan-tabs-inner">
                <el-tab-pane v-for="phase in structuredPhases" :key="phase.key" :label="phase.tabLabel" :name="phase.key">
                  <el-row :gutter="16" class="plan-summary-row">
                    <el-col :span="12">
                      <el-card shadow="never" class="plan-info-card">
                        <div class="plan-info-title">
                          <el-icon><InfoFilled /></el-icon>
                          训练特点
                        </div>
                        <div class="md-body" v-html="renderMarkdown(phase.features || phase.goal || '')"></div>
                      </el-card>
                    </el-col>
                    <el-col :span="12">
                      <el-card shadow="never" class="plan-info-card goal-card">
                        <div class="plan-info-title">
                          <el-icon><Flag /></el-icon>
                          阶段目标
                        </div>
                        <div class="md-body" v-html="renderMarkdown(phase.goal || '')"></div>
                      </el-card>
                    </el-col>
                  </el-row>

                  <div class="weekly-title">
                    <el-icon><Calendar /></el-icon>
                    每周安排
                  </div>

                  <div class="week-grid">
                    <el-card
                      v-for="day in phase.week"
                      :key="day.dayKey"
                      shadow="never"
                      class="day-card"
                      :class="{ 'day-card--empty': !day.summary }"
                    >
                      <div class="plan-day-name">{{ day.dayName }}</div>
                      <el-popover v-if="day.detail" placement="top" trigger="hover" width="360">
                        <template #reference>
                          <div class="plan-day-content">
                            <div class="plan-day-summary">{{ day.summary }}</div>
                            <div v-if="day.subSummary" class="plan-day-sub">{{ day.subSummary }}</div>
                          </div>
                        </template>
                        <div class="md-body" v-html="renderMarkdown(day.detail)"></div>
                      </el-popover>
                      <div v-else class="plan-day-content">
                        <div class="plan-day-summary">{{ day.summary || '—' }}</div>
                        <div v-if="day.subSummary" class="plan-day-sub">{{ day.subSummary }}</div>
                      </div>
                    </el-card>
                  </div>

                  <div v-if="phase.notes" class="phase-notes">
                    <el-alert title="注意事项" type="warning" show-icon :closable="false">
                      <div class="md-body" v-html="renderMarkdown(phase.notes)"></div>
                    </el-alert>
                  </div>
                </el-tab-pane>
              </el-tabs>
            </div>

            <div v-else class="md-body" v-html="renderMarkdown(planReportMd)"></div>
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
                    <div v-if="checkIn.avgHeartRate || checkIn.rpe || checkIn.fatigueLevel" class="check-in-metrics">
                      <span v-if="checkIn.avgHeartRate">平均心率 {{ checkIn.avgHeartRate }} bpm</span>
                      <span v-if="checkIn.rpe"> · RPE {{ checkIn.rpe }} ({{ rpeLabel(checkIn.rpe) }})</span>
                      <span v-if="checkIn.fatigueLevel"> · 疲劳 {{ checkIn.fatigueLevel }}</span>
                    </div>
                    <div v-if="checkIn.notes" class="check-in-notes">{{ checkIn.notes }}</div>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </div>
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
          <el-form-item label="打卡日期">
            <el-tag type="info" effect="plain">{{ selectedCheckInDateStr }}</el-tag>
            <span v-if="getDayPlan(selectedCheckInDate)?.summary" class="plan-task-inline">
              任务：{{ getDayPlan(selectedCheckInDate).summary }}
            </span>
          </el-form-item>
          <el-form-item label="运动类型">
            <el-select v-model="checkInForm.exerciseType" placeholder="选择运动类型" style="width: 100%">
              <el-option label="有氧运动" value="有氧运动" />
              <el-option label="力量训练" value="力量训练" />
              <el-option label="柔韧训练" value="柔韧训练" />
              <el-option label="综合训练" value="综合训练" />
              <el-option label="休息" value="休息" />
            </el-select>
          </el-form-item>
          <el-form-item label="运动有效时间">
            <el-input-number v-model="checkInForm.duration" :min="5" :max="180" />
            <span style="margin-left: 10px; color: #909399;">分钟</span>
          </el-form-item>
          <el-form-item label="运动平均心率">
            <el-input-number v-model="checkInForm.avgHeartRate" :min="40" :max="220" />
            <span style="margin-left: 10px; color: #909399;">bpm</span>
          </el-form-item>
          <el-form-item label="主观用力等级">
            <el-select v-model="checkInForm.rpe" placeholder="选择 PRE/RPE 等级(6-20)" style="width: 100%">
              <el-option
                v-for="v in 15"
                :key="v + 5"
                :label="`${v + 5} - ${rpeLabel(v + 5)}`"
                :value="v + 5"
              />
            </el-select>
            <div v-if="checkInForm.rpe" class="form-hint">当前：{{ checkInForm.rpe }} - {{ rpeLabel(checkInForm.rpe) }}</div>
          </el-form-item>
          <el-form-item label="运动后疲劳">
            <el-select v-model="checkInForm.fatigueLevel" placeholder="选择运动后疲劳程度" style="width: 100%">
              <el-option v-for="opt in fatigueOptions" :key="opt" :label="opt" :value="opt" />
            </el-select>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, MoreFilled, VideoPause, VideoPlay, CircleCheck, Delete,
  SuccessFilled, CircleClose, InfoFilled, Flag, Calendar
} from '@element-plus/icons-vue'
import axios from 'axios'
import { marked } from 'marked'
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
const allCheckIns = ref([])
const showCreateDialog = ref(false)
const showCheckInDialog = ref(false)
const planReportMd = ref('')
const activePhaseKey = ref('')
const calendarView = ref('week')
const monthCursor = ref(new Date())

const createForm = ref({
  planName: '',
  testRecordId: null,
  startDate: new Date(),
  totalWeeks: 10
})

const checkInForm = ref({
  exerciseType: '',
  duration: 30,
  avgHeartRate: null,
  rpe: null,
  fatigueLevel: '',
  notes: ''
})

const selectedCheckInDate = ref(new Date())
const toDateKey = (date) => {
  const d = date instanceof Date ? date : new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}
const selectedCheckInDateStr = computed(() => {
  try {
    return toDateKey(selectedCheckInDate.value)
  } catch {
    return ''
  }
})

const rpeLabel = (v) => {
  const n = Number(v)
  if (!Number.isFinite(n)) return ''
  if (n === 6) return '无任何用力感'
  if (n >= 7 && n <= 8) return '极轻微用力'
  if (n >= 9 && n <= 10) return '轻微用力'
  if (n >= 11 && n <= 12) return '中等用力'
  if (n >= 13 && n <= 14) return '较用力'
  if (n >= 15 && n <= 16) return '用力'
  if (n >= 17 && n <= 18) return '非常用力'
  if (n === 19) return '极度用力'
  if (n === 20) return '极限用力'
  return ''
}

const fatigueOptions = ['无疲劳', '轻微疲劳', '中度疲劳', '重度疲劳', '极度疲劳']

const weeklySchedule = computed(() => planData.value.weeklySchedule || [])
const dayKeyMap = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
const resolveDate = (value) => {
  if (value instanceof Date) return value
  if (value && value.date instanceof Date) return value.date
  if (typeof value === 'string' || typeof value === 'number') {
    const d = new Date(value)
    if (!Number.isNaN(d.getTime())) return d
  }
  return new Date()
}
const getDayKey = (value) => dayKeyMap[resolveDate(value).getDay()]
const getDayPlan = (date) => {
  const key = getDayKey(date)
  const fromPlan = weeklySchedule.value.find((d) => d.dayKey === key)
  if (fromPlan && (fromPlan.summary || fromPlan.detail)) return fromPlan
  const parsed = getPlanTaskFromReport(date)
  if (parsed) {
    return {
      dayKey: key,
      dayName: parsed.dayName,
      summary: parsed.summary,
      detail: parsed.detail || parsed.summary
    }
  }
  return null
}
const todayPlan = computed(() => getDayPlan(new Date()))

const extractPlanMarkdown = (report) => {
  if (!report) return ''

  // 优先按标准报告结构截取：### 四、分阶段训练计划 ... 到下一个 ### 五/六/七 之前
  const planMatch = report.match(/#{3,4}\\s+(?:\\*\\*)?四、\\s*分阶段训练计划(?:\\s*（[^）]+）)?(?:\\*\\*)?/i)
  if (planMatch) {
    const startIdx = planMatch.index + planMatch[0].length
    const nextHeaderMatch = report.substring(startIdx).match(/#{3,4}\\s+(?:\\*\\*)?[五六七]/i)
    const endIdx = nextHeaderMatch ? startIdx + nextHeaderMatch.index : report.length
    return report.substring(startIdx, endIdx).trim()
  }

  // 兜底：从“分阶段训练计划”开始截取（去掉所在标题行）
  const startIdx = report.indexOf('分阶段训练计划')
  if (startIdx === -1) return ''
  const after = report.substring(startIdx)
  const firstNl = after.indexOf('\n')
  const content = firstNl !== -1 ? after.substring(firstNl + 1) : after

  const endMarkers = ['五、', '5、', '运动禁忌', '### **五', '### 五']
  let endIdx = content.length
  for (const mk of endMarkers) {
    const idx = content.indexOf(mk)
    if (idx !== -1 && idx < endIdx) {
      endIdx = idx
    }
  }
  return content.substring(0, endIdx).trim()
}

const fetchPlanReport = async (testRecordId) => {
  if (!testRecordId) return
  try {
    const token = localStorage.getItem('token')
    const resp = await axios.get(buildUrl(API_ENDPOINTS.PROFILE.GET_BY_ID(testRecordId)), {
      headers: { Authorization: token }
    })
    if (resp.data.code === 200 && resp.data.data) {
      const report = resp.data.data.report
      const planMd = extractPlanMarkdown(report)
      planReportMd.value = planMd || ''
    }
  } catch (e) {
    console.error(e)
  }
}

// 复刻报告详情页的 Markdown 兼容处理
const normalizeMarkdown = (text) => {
  if (!text) return ''
  const escapeSingleTildes = (input) => {
    let out = ''
    for (let i = 0; i < input.length; i++) {
      const ch = input[i]
      if (ch === '~') {
        const prev = i > 0 ? input[i - 1] : ''
        const next = i + 1 < input.length ? input[i + 1] : ''
        if (prev !== '\\' && prev !== '~' && next !== '~') {
          out += '\\~'
          continue
        }
      }
      out += ch
    }
    return out
  }
  const normalized = escapeSingleTildes(String(text).replace(/\r\n/g, '\n'))
  const withKeyValueBold = normalized.replace(
    /^\s*\*\*([^*\n]+?[：:])\*\*\s*([^\n]+)\s*$/gm,
    '**$1$2**'
  )
  const withListSpacing = withKeyValueBold.replace(
    /([^\n])\n(\s*(?:[*+-]|\d+\.)\s+)/g,
    '$1\n\n$2'
  )
  const withBoldSpacing = withListSpacing.replace(
    /^(\s*\*\*[^*\n]+?\*\*.*)\n(\s*\*\*[^*\n]+?\*\*.*)$/gm,
    '$1\n\n$2'
  )
  return withBoldSpacing
}

const renderMarkdown = (text) => {
  if (!text) return ''
  return marked.parse(normalizeMarkdown(text))
}

// 从报告 Markdown 中解析阶段与每日安排（简化版）
const chineseToInt = (txt) => {
  if (!txt) return null
  const map = { '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9 }
  if (/^\d+$/.test(txt)) return parseInt(txt, 10)
  let total = 0
  if (txt === '十') return 10
  if (txt.startsWith('十')) {
    total += 10
    const tail = map[txt[1]]
    if (tail) total += tail
    return total
  }
  const tenIdx = txt.indexOf('十')
  if (tenIdx > 0) {
    const tens = map[txt[tenIdx - 1]] || 0
    total += tens * 10
    const tail = map[txt[tenIdx + 1]]
    if (tail) total += tail
    return total
  }
  return map[txt] ?? null
}

const reportPlan = computed(() => {
  const content = planReportMd.value || ''
  const section = { planIntro: '', phases: [], raw: content }
  if (!content) return section

  // report:  #### **阶段一：...**
  // report2: **阶段1：...**
  const phaseRegex = /^(?:####\s+)?(?:\*\*)?阶段([一二三四五六七八九十0-9]+)\s*[：:]\s*(.*?)(?:\*\*)?\s*$/gmi
  const matches = [...content.matchAll(phaseRegex)]
  if (matches.length === 0) return section

  section.planIntro = content.substring(0, matches[0].index).trim()

  const phases = []
  for (let i = 0; i < matches.length; i++) {
    const currentMatch = matches[i]
    const nextMatch = matches[i + 1]

    const title = `阶段${currentMatch[1]}：${String(currentMatch[2] || '').replace(/\*\*/g, '').trim()}`
    const startIndex = currentMatch.index + currentMatch[0].length
    const endIndex = nextMatch ? nextMatch.index : content.length

    const phaseContent = content.substring(startIndex, endIndex).trim()
    phases.push({ title, content: phaseContent })
  }

  section.phases = phases
  return section
})

const structuredPhases = computed(() => {
  const phases = reportPlan.value?.phases || []
  if (!Array.isArray(phases) || phases.length === 0) return []

  const dayKeyMap = {
    周一: 'mon',
    周二: 'tue',
    周三: 'wed',
    周四: 'thu',
    周五: 'fri',
    周六: 'sat',
    周日: 'sun',
    周天: 'sun'
  }

  const weekOrder = [
    { dayName: '周一', dayKey: 'mon' },
    { dayName: '周二', dayKey: 'tue' },
    { dayName: '周三', dayKey: 'wed' },
    { dayName: '周四', dayKey: 'thu' },
    { dayName: '周五', dayKey: 'fri' },
    { dayName: '周六', dayKey: 'sat' },
    { dayName: '周日', dayKey: 'sun' }
  ]

  const stripMarkdown = (text) => String(text || '').replace(/\*\*/g, '').replace(/`/g, '').trim()

  const extractGoal = (plain) => {
    const match = plain.match(/阶段目标\s*[：:]\s*([^\n]+)/)
    return match ? match[1].trim() : ''
  }

  const extractNotes = (plain) => {
    const match = plain.match(/注意事项\s*[：:]\s*([\s\S]*)/)
    return match ? match[1].trim() : ''
  }

  const extractFeatures = (goal) => {
    const text = (goal || '').trim()
    if (!text) return ''
    const parts = text.split(/[。；]/).map((s) => s.trim()).filter(Boolean)
    if (parts.length > 0) return parts[0]
    const commaParts = text.split('，').map((s) => s.trim()).filter(Boolean)
    return commaParts[0] || text
  }

  const parseWeek = (plain) => {
    const weeklyStart = plain.indexOf('每周训练安排')
    if (weeklyStart === -1) {
      return weekOrder.map((d) => ({ ...d, summary: '', subSummary: '', detail: '' }))
    }

    const afterStart = plain.slice(weeklyStart)
    const endByNotes = afterStart.indexOf('注意事项')
    const weeklyText = (endByNotes === -1 ? afterStart : afterStart.slice(0, endByNotes))
      .replace(/^.*每周训练安排[：:]*\s*/m, '')
      .trim()

    const dayRegex = /^\s*[*+-]\s*(周[一二三四五六日天])\s*[：:]\s*([\s\S]*?)(?=^\s*[*+-]\s*周[一二三四五六日天]\s*[：:]|\s*$)/gmi
    const weekMap = {}
    let match

    while ((match = dayRegex.exec(weeklyText)) !== null) {
      const dayName = match[1].replace('周天', '周日')
      const key = dayKeyMap[dayName]
      const detail = String(match[2] || '').trim()

      const oneLine = detail.replace(/\s+/g, ' ').trim()
      const firstSentence = oneLine.split('。')[0].trim()
      const summary = firstSentence || oneLine
      const remaining = oneLine.slice(summary.length).replace(/^。/, '').trim()
      const subSummary = remaining ? remaining.split('。')[0].trim() : ''

      weekMap[key] = {
        dayName,
        dayKey: key,
        summary,
        subSummary,
        detail
      }
    }

    return weekOrder.map((d) => weekMap[d.dayKey] || { ...d, summary: '', subSummary: '', detail: '' })
  }

  const extractWeekRange = (title) => {
    const rangeMatch = String(title || '').match(/[（(]([^）)]+)[）)]/)
    const range = rangeMatch ? rangeMatch[1].trim() : ''
    const weekMatch = range.match(/第?\s*([一二三四五六七八九十0-9]+)\s*(?:[-~—–－至到]\s*([一二三四五六七八九十0-9]+))?\s*周/)
    if (!weekMatch) return { startWeek: null, endWeek: null }
    const startWeek = chineseToInt(weekMatch[1])
    const endWeek = weekMatch[2] ? (chineseToInt(weekMatch[2]) || startWeek) : startWeek
    return { startWeek, endWeek }
  }

  return phases.map((phase, idx) => {
    const key = `phase-${idx}`
    const title = stripMarkdown(phase.title || '')
    const plain = stripMarkdown(phase.content || '')

    const goal = extractGoal(plain)
    const features = extractFeatures(goal)
    const notes = extractNotes(plain)
    const week = parseWeek(plain)

    const rangeMatch = title.match(/（([^）]+)）/)
    const range = rangeMatch ? rangeMatch[1].trim() : ''
    const nameOnly = title
      .replace(/^阶段[一二三四五六七八九十0-9]+[：:]\s*/, '')
      .replace(/（[^）]+）/, '')
      .trim()

    const isPhaseRange = (text) => {
      const t = String(text || '').replace(/\s+/g, '')
      if (!t || !t.includes('周')) return false
      if (/[\\-~—–]/.test(t)) return true
      return /第?\d+周/.test(t)
    }

    const rangeLabel = isPhaseRange(range) ? range.replace(/\s+/g, '') : ''
    const rawTabLabel = rangeLabel ? `${rangeLabel}：${nameOnly}` : (nameOnly || title || `阶段${idx + 1}`)
    const tabLabel = rawTabLabel.replace(/\*/g, '').trim()

    const { startWeek, endWeek } = extractWeekRange(title)

    return { key, tabLabel, title, features, goal, week, notes, startWeek, endWeek }
  })
})

const currentWeekPhase = computed(() => {
  const phases = structuredPhases.value
  if (!Array.isArray(phases) || phases.length === 0) return null
  const weekNum = planData.value?.currentWeek || 1
  return (
    phases.find((p) => p.startWeek && p.endWeek && weekNum >= p.startWeek && weekNum <= p.endWeek) ||
    phases[0]
  )
})

const activePhase = computed(() => {
  const phases = structuredPhases.value
  if (!Array.isArray(phases) || phases.length === 0) return null
  return phases.find((p) => p.key === activePhaseKey.value) || phases[0]
})

watch([structuredPhases, () => planData.value?.currentWeek], () => {
  const phases = structuredPhases.value
  if (!Array.isArray(phases) || phases.length === 0) return
  if (!activePhaseKey.value || !phases.some((p) => p.key === activePhaseKey.value)) {
    activePhaseKey.value = currentWeekPhase.value?.key || phases[0].key
  }
})

const parseYmdDate = (value) => {
  const s = String(value || '')
  const m = s.match(/^(\d{4})-(\d{2})-(\d{2})/)
  if (m) return new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]))
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? null : d
}

const getWeekNumberForDate = (date) => {
  if (!activePlan.value?.startDate) return null
  const start = parseYmdDate(activePlan.value.startDate)
  if (!start) return null
  const d = resolveDate(date)
  const startMid = new Date(start.getFullYear(), start.getMonth(), start.getDate())
  const dateMid = new Date(d.getFullYear(), d.getMonth(), d.getDate())
  const diffDays = Math.floor((dateMid - startMid) / (24 * 60 * 60 * 1000))
  if (diffDays < 0) return null
  return Math.floor(diffDays / 7) + 1
}

const isInPlanRange = (date) => {
  const start = activePlan.value?.startDate ? parseYmdDate(activePlan.value.startDate) : null
  const end = activePlan.value?.endDate ? parseYmdDate(activePlan.value.endDate) : null
  if (!start || !end) return true
  const d = resolveDate(date)
  const sMid = new Date(start.getFullYear(), start.getMonth(), start.getDate())
  const eMid = new Date(end.getFullYear(), end.getMonth(), end.getDate())
  const dMid = new Date(d.getFullYear(), d.getMonth(), d.getDate())
  return dMid >= sMid && dMid <= eMid
}

const getPlanTaskFromReport = (date) => {
  if (!isInPlanRange(date)) return null
  const phases = structuredPhases.value
  if (!Array.isArray(phases) || phases.length === 0) return null
  const weekNum = getWeekNumberForDate(date) ?? (planData.value?.currentWeek || 1)
  const phase =
    phases.find((p) => p.startWeek && p.endWeek && weekNum >= p.startWeek && weekNum <= p.endWeek) ||
    phases[0]
  if (!phase || !Array.isArray(phase.week)) return null
  const dayKey = getDayKey(date)
  return phase.week.find((d) => d.dayKey === dayKey) || null
}

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
  const today = toDateKey(new Date())
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
      const testRecordId = activePlan.value?.testRecordId ?? activePlan.value?.test_record_id
      if (testRecordId) fetchPlanReport(testRecordId)
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
      allCheckIns.value = response.data.data || []
      recentCheckIns.value = allCheckIns.value.slice(0, 10)
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

const resetCheckInForm = () => {
  checkInForm.value = {
    exerciseType: '',
    duration: 30,
    avgHeartRate: null,
    rpe: null,
    fatigueLevel: '',
    notes: ''
  }
}

const prefillCheckInWithPlan = (date) => {
  const plan = getDayPlan(date || new Date())

  const pickExerciseType = (text) => {
    const t = String(text || '')
    if (t.includes('休息')) return '休息'
    if (t.includes('有氧')) return '有氧运动'
    if (t.includes('抗阻') || t.includes('力量') || t.includes('深蹲') || t.includes('俯卧撑') || t.includes('卧推')) return '力量训练'
    if (t.includes('拉伸') || t.includes('柔韧') || t.includes('瑜伽') || t.includes('平衡')) return '柔韧训练'
    return '综合训练'
  }

  const pickDuration = (text) => {
    const m = String(text || '').match(/(\\d+)\\s*分钟/)
    return m ? parseInt(m[1], 10) : null
  }

  if (plan?.summary) {
    checkInForm.value.notes = checkInForm.value.notes || `按计划：${plan.summary}`
  }
  if (!checkInForm.value.exerciseType && plan?.summary) {
    const type = pickExerciseType(plan.summary)
    if (type) checkInForm.value.exerciseType = type
  }
  if ((checkInForm.value.duration === 30 || !checkInForm.value.duration) && plan?.summary) {
    const mins = pickDuration(plan.summary)
    if (mins) checkInForm.value.duration = mins
  }
}

const openCheckInDialog = (date = new Date()) => {
  const resolved = resolveDate(date)
  selectedCheckInDate.value = resolved

  const existing = getDayCheckIn(resolved)
  if (existing) {
    checkInForm.value = {
      exerciseType: existing.exerciseType || '',
      duration: existing.duration ?? 30,
      avgHeartRate: existing.avgHeartRate ?? null,
      rpe: existing.rpe ?? null,
      fatigueLevel: existing.fatigueLevel || '',
      notes: existing.notes || ''
    }
  } else {
    resetCheckInForm()
    prefillCheckInWithPlan(resolved)
  }

  showCheckInDialog.value = true
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
      checkInDate: selectedCheckInDateStr.value,
      ...checkInForm.value,
      completed: true
    }, {
      headers: { Authorization: token }
    })
    
    if (response.data.code === 200) {
      ElMessage.success('打卡成功！')
      showCheckInDialog.value = false
      resetCheckInForm()
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
  openCheckInDialog(day.date)
}

const handleMonthDayClick = (data) => {
  const date = resolveDate(data?.date)
  if (isFuture(date)) return
  openCheckInDialog(date)
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
  return !!getDayCheckIn(date)?.completed
}

const getDayCheckIn = (date) => {
  const dateStr = toDateKey(date)
  const getCheckInDateKey = (raw) => {
    if (!raw) return ''
    if (typeof raw === 'string') {
      const m = raw.match(/^\d{4}-\d{2}-\d{2}/)
      if (m) return m[0]
    }
    return toDateKey(raw)
  }
  return allCheckIns.value?.find(c => getCheckInDateKey(c.checkInDate) === dateStr) || null
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
.content-container {
  max-width: 1200px;
  margin: 0 auto;
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
.plan-content {}
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
.today-plan-hint {
  margin-top: 12px;
  padding: 10px 12px;
  background: #f0f9ff;
  border: 1px dashed #b3d8ff;
  border-radius: 6px;
}
.hint-title {
  font-size: 13px;
  font-weight: 600;
  color: #409EFF;
  margin-bottom: 6px;
}
.hint-text {
  font-size: 14px;
  color: #303133;
  line-height: 1.5;
}
.calendar-card {
  margin-bottom: 20px;
}
.calendar-header {
  margin-bottom: 16px;
}
.calendar-tabs {
  margin-top: 8px;
}
.calendar-subtitle {
  font-size: 14px;
  color: #606266;
  margin-bottom: 12px;
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
  text-align: left;
}
.recommended-info {
  color: #1677ff;
}
.checked-info {
  color: #67C23A;
}
.checked-metrics {
  color: #909399;
}
.plan-task-inline {
  margin-left: 10px;
  font-size: 12px;
  color: #606266;
  line-height: 1.4;
}
.form-hint {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}
.day-plan-summary {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
}
.md-compact {
  font-size: 14px;
}

/* 月视图 */
.month-calendar :deep(.el-calendar__body) {
  padding: 0;
}
.month-calendar :deep(.el-calendar-day) {
  padding: 0;
}
.month-cell {
  height: 100%;
  min-height: 78px;
  padding: 0 8px 0 8px;
  border-radius: 8px;
  transition: all 0.15s ease;
  cursor: pointer;
}
.month-cell:hover {
  border-color: #b9d3ff;
  background: #eef5ff;
}
.month-cell--other {
  opacity: 0.45;
}
.month-cell--future {
  cursor: not-allowed;
  opacity: 0.55;
}
.month-cell--today {
  border-color: #409EFF;
  background: #ecf5ff;
}
.month-cell--checked {
  border-color: #67C23A;
  background: #f0f9ff;
}
.month-cell__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  margin-bottom: 6px;
}
.month-cell__day {
  font-weight: 700;
  color: #303133;
}
.month-cell__task {
  font-size: 12px;
  line-height: 1.35;
  color: #606266;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.month-cell__task--empty {
  color: #c0c4cc;
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
.check-in-metrics {
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
  margin-bottom: 6px;
}
.check-in-notes {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}
.plan-structured-card {
  margin-bottom: 20px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  border: 1px solid #e4e7ed;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.04);
}

.plan-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}
.plan-card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
}
.plan-intro {
  margin-bottom: 14px;
}

/* Markdown 内容样式（复刻报告详情页） */
.md-body {
  line-height: 1.8;
  font-size: 15px;
  color: #606266;
}
.md-body :deep(h1), .md-body :deep(h2), .md-body :deep(h3), .md-body :deep(h4) {
  margin-top: 12px;
  margin-bottom: 12px;
  font-weight: 600;
  color: #303133;
}
.md-body :deep(p) {
  margin-bottom: 12px;
}
.md-body :deep(strong) {
  font-weight: 600;
  color: #303133;
}
.md-body :deep(ul), .md-body :deep(ol) {
  padding-left: 24px;
  margin-bottom: 12px;
}
.md-body :deep(li) {
  margin-bottom: 6px;
}
.md-body :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 15px 0;
}
.md-body :deep(th), .md-body :deep(td) {
  border: 1px solid #dcdfe6;
  padding: 8px 12px;
  text-align: left;
}
.md-body :deep(th) {
  background: #f5f7fa;
  font-weight: 600;
}

/* 分阶段训练计划（复刻报告详情页卡片样式） */
.plan-tabs {
  margin-top: 16px;
}
.plan-tabs-inner :deep(.el-tabs__header) {
  margin: 0 0 16px 0;
}
.plan-tabs-inner :deep(.el-tabs__item) {
  font-size: 14px;
  font-weight: 600;
}
.plan-tabs-inner :deep(.el-tabs__item.is-active) {
  color: #1677ff;
}
.plan-tabs-inner :deep(.el-tabs__nav-wrap::after) {
  background-color: transparent;
}
.plan-summary-row {
  margin-bottom: 14px;
}
.plan-info-card {
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
}
.goal-card {
  border-left: 3px solid #1677ff;
}
.plan-info-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 16px;
  color: #303133;
  margin-bottom: 10px;
}
.plan-info-title :deep(.el-icon) {
  color: #1677ff;
}
.weekly-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 16px;
  color: #303133;
  margin: 12px 0 10px 0;
}
.weekly-title :deep(.el-icon) {
  color: #1677ff;
}
.week-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
}
.day-card {
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  background: #fff;
  transition: box-shadow 0.15s ease, transform 0.15s ease, border-color 0.15s ease;
}
.day-card:hover {
  border-color: #b9d3ff;
  box-shadow: 0 8px 18px rgba(22, 119, 255, 0.12);
  transform: translateY(-1px);
}
.day-card--empty {
  opacity: 0.6;
}
.plan-day-name {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(22, 119, 255, 0.08);
  color: #1677ff;
  font-weight: 700;
  font-size: 14px;
  margin-bottom: 10px;
}
.plan-day-content {
  cursor: default;
}
.plan-day-summary {
  font-size: 14px;
  color: #303133;
  line-height: 1.5;
}
.plan-day-sub {
  margin-top: 6px;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}
.phase-notes {
  margin-top: 14px;
}

@media (max-width: 1200px) {
  .week-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
@media (max-width: 900px) {
  .week-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
