<template>
  <div class="page-container">
    <NavBar />

    <el-main>
      <div class="content-container">
        <div class="header-section">
          <div class="header-left">
            <h2 class="page-title">健康管理</h2>
            <div v-if="activeRecord" class="page-subtitle">
              最新体测：{{ formatDateTime(activeRecord.createTime) }}
            </div>
          </div>

          <div class="header-right">
            <el-select
              v-model="selectedRecordId"
              filterable
              placeholder="选择体测报告"
              class="record-select"
              :loading="historyLoading"
            >
              <el-option
                v-for="record in historyList"
                :key="record.id"
                :label="recordOptionLabel(record)"
                :value="record.id"
                :disabled="record.status !== 'COMPLETED'"
              />
            </el-select>

            <el-button type="primary" :disabled="!activeRecord" @click="goReportDetail">
              查看报告详情
            </el-button>
          </div>
        </div>

        <div v-loading="loading" class="content-wrapper">
          <el-empty v-if="!loading && completedCount === 0" description="暂无已完成的测试报告" />

          <template v-else-if="activeRecord">
            <el-card class="overview-card">
              <template #header>
                <div class="card-header">
                  <div class="card-title">综合评分</div>
                  <el-tag
                    v-if="result"
                    :type="getRatingType(result.overall_rating)"
                    effect="dark"
                    size="large"
                  >
                    {{ result.overall_rating }} ({{ result.overall_score }}分)
                  </el-tag>
                  <el-tag v-else type="info" effect="plain">无分析结果</el-tag>
                </div>
              </template>

              <el-row v-if="result" :gutter="20" align="middle">
                <el-col :span="10">
                  <div ref="radarChartRef" class="radar-chart"></div>
                </el-col>
                <el-col :span="14">
                  <div class="score-summary">
                    <div class="score-title">体质测试总评</div>
                    <div class="score-circle">
                      <el-progress
                        type="dashboard"
                        :percentage="result.overall_score"
                        :color="getScoreColor"
                        :width="176"
                        :stroke-width="14"
                      >
                        <template #default="{ percentage }">
                          <span class="percentage-value">{{ percentage }}</span>
                          <span class="percentage-label">分</span>
                        </template>
                      </el-progress>
                    </div>
                    <div class="rating-badge">
                      <el-tag :type="getRatingType(result.overall_rating)" effect="dark" size="large" class="rating-tag">
                        {{ result.overall_rating }}
                      </el-tag>
                    </div>
                  </div>
                </el-col>
              </el-row>

              <el-alert
                v-else
                title="该记录暂无分析结果，请在“开始测试”中重新生成报告"
                type="warning"
                show-icon
                :closable="false"
              />
            </el-card>

            <el-card v-if="result" class="metrics-card">
              <template #header>
                <div class="card-header">
                  <div class="card-title">各项指标</div>
                </div>
              </template>

              <el-table :data="metricsTableData" stripe border size="default" class="metrics-table">
                <el-table-column prop="name" label="指标" width="160">
                  <template #default="scope">
                    <span class="metric-name">{{ scope.row.name }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="value" label="测试值" width="120" align="center" />
                <el-table-column prop="score" label="得分" width="100" align="center">
                  <template #default="scope">
                    <span class="metric-score" :style="{ color: getScoreColor(scope.row.score) }">{{ scope.row.score }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="评分进度" min-width="200">
                  <template #default="scope">
                    <el-progress
                      :percentage="scope.row.score"
                      :color="getScoreColor(scope.row.score)"
                      :format="() => ''"
                      :stroke-width="12"
                    />
                  </template>
                </el-table-column>
                <el-table-column prop="rating" label="等级" width="120" align="center">
                  <template #default="scope">
                    <el-tag :type="getRatingType(scope.row.rating)" effect="plain">{{ scope.row.rating }}</el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </template>
        </div>
      </div>
    </el-main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import * as echarts from 'echarts'
import NavBar from '../components/NavBar.vue'
import { API_ENDPOINTS, buildUrl } from '../api/config'

const router = useRouter()

const loading = ref(false)
const historyLoading = ref(false)
const historyList = ref([])
const selectedRecordId = ref(null)

const radarChartRef = ref(null)
let radarChart = null

const metricNameMap = {
  bmi: 'BMI',
  body_fat_rate: '体脂率',
  vital_capacity: '肺活量',
  max_oxygen_uptake: '最大摄氧量',
  sit_and_reach: '坐位体前屈',
  single_leg_stand: '闭眼单脚站立',
  reaction_time: '选择反应时间',
  grip_strength: '握力',
  sit_ups_per_minute: '一分钟仰卧起坐',
  push_ups: '俯卧撑/跪卧撑',
  vertical_jump: '纵跳',
  high_knees_2min: '2分钟原地高抬腿',
  sit_to_stand_30s: '30秒坐站'
}

const completedCount = computed(() => historyList.value.filter(r => r.status === 'COMPLETED').length)
const activeRecord = computed(() => historyList.value.find(r => r.id === selectedRecordId.value) || null)

const result = ref(null)

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getStatusText = (status) => {
  if (status === 'COMPLETED') return '已完成'
  if (status === 'GENERATING') return '生成中'
  if (status === 'FAILED') return '失败'
  return status || '未知'
}

const recordOptionLabel = (record) => {
  const time = formatDateTime(record.createTime)
  if (record.status !== 'COMPLETED') return `${time} · ${getStatusText(record.status)}`

  try {
    const analysis = record.analysisResult ? JSON.parse(record.analysisResult) : null
    if (analysis?.overall_score != null && analysis?.overall_rating) {
      return `${time} · ${analysis.overall_score}分 ${analysis.overall_rating}`
    }
  } catch {
    // ignore
  }

  return `${time} · 已完成`
}

const getRatingType = (rating) => {
  if (rating === '优秀') return 'success'
  if (rating === '良好') return 'primary'
  if (rating === '合格') return 'warning'
  return 'danger'
}

const getScoreColor = (score) => {
  if (score >= 85) return '#67C23A'
  if (score >= 75) return '#409EFF'
  if (score >= 60) return '#E6A23C'
  return '#F56C6C'
}

const metricsTableData = computed(() => {
  if (!result.value?.individual_scores || !activeRecord.value) return []

  const scores = result.value.individual_scores || {}
  const ratings = result.value.individual_ratings || {}

  return Object.keys(scores).map((key) => {
    const camelKey = key.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
    let originalValue = activeRecord.value?.[camelKey]
    if (originalValue === undefined || originalValue === null || originalValue === '') {
      originalValue = '-'
    }

    return {
      key,
      name: metricNameMap[key] || key,
      value: originalValue,
      score: scores[key],
      rating: ratings[key] || '-'
    }
  })
})

const disposeRadar = () => {
  if (radarChart) {
    radarChart.dispose()
    radarChart = null
  }
}

const initRadarChart = async () => {
  if (!radarChartRef.value || !result.value) return
  if (metricsTableData.value.length === 0) return

  disposeRadar()

  radarChart = echarts.init(radarChartRef.value)

  const indicators = metricsTableData.value.map(item => ({
    name: item.name,
    max: 100
  }))
  const dataValues = metricsTableData.value.map(item => item.score)

  radarChart.setOption({
    tooltip: {
      appendToBody: true,
      confine: false,
      extraCssText: 'z-index: 9999;'
    },
    radar: {
      indicator: indicators,
      radius: '65%',
      splitNumber: 4,
      axisName: {
        color: '#606266'
      },
      splitLine: {
        lineStyle: { color: '#e4e7ed' }
      },
      splitArea: {
        areaStyle: { color: ['#fafcff', '#ffffff', '#fafcff', '#ffffff'] }
      }
    },
    series: [
      {
        name: '体质评分',
        type: 'radar',
        data: [
          {
            value: dataValues,
            name: '各项指标得分',
            areaStyle: { color: 'rgba(64, 158, 255, 0.18)' },
            lineStyle: { color: '#409EFF', width: 2 },
            itemStyle: { color: '#409EFF' }
          }
        ]
      }
    ]
  })
}

const applyActiveRecord = async () => {
  disposeRadar()
  const record = activeRecord.value
  if (!record) {
    result.value = null
    return
  }

  if (!record.analysisResult) {
    result.value = null
    return
  }

  try {
    result.value = JSON.parse(record.analysisResult)
  } catch (e) {
    console.error('Failed to parse analysisResult JSON', e)
    result.value = null
    ElMessage.error('分析结果解析失败')
    return
  }

  await nextTick()
  await initRadarChart()
}

const goReportDetail = () => {
  if (!activeRecord.value) return
  router.push(`/report/${activeRecord.value.id}`)
}

const fetchHistory = async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    router.push('/login')
    return
  }

  historyLoading.value = true
  loading.value = true
  try {
    const response = await axios.get(buildUrl(API_ENDPOINTS.PROFILE.HISTORY), {
      headers: { Authorization: token }
    })

    if (response.data.code === 200) {
      historyList.value = response.data.data || []
      const firstCompleted = historyList.value.find(r => r.status === 'COMPLETED')
      selectedRecordId.value = firstCompleted ? firstCompleted.id : null
    } else {
      ElMessage.error(response.data.message || '获取测试记录失败')
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('获取测试记录失败')
  } finally {
    historyLoading.value = false
    loading.value = false
  }
}

const handleResize = () => {
  if (radarChart) radarChart.resize()
}

watch(selectedRecordId, async () => {
  await applyActiveRecord()
})

onMounted(async () => {
  await fetchHistory()
  await applyActiveRecord()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  disposeRadar()
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
  align-items: flex-end;
  gap: 16px;
  margin-bottom: 16px;
}

.page-title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: #303133;
}

.page-subtitle {
  margin-top: 6px;
  font-size: 13px;
  color: #909399;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.record-select {
  width: 280px;
}

.content-wrapper {
  min-height: 240px;
}

.overview-card {
  margin-bottom: 18px;
  border: 1px solid #e4e7ed;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  color: #303133;
}

.radar-chart {
  width: 100%;
  height: 300px;
}

.score-summary {
  text-align: center;
  padding-top: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.score-title {
  font-size: 16px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 10px;
}

.score-circle {
  margin-bottom: 14px;
}

.percentage-value {
  display: block;
  margin-top: 8px;
  font-size: 40px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.percentage-label {
  display: block;
  font-size: 13px;
  color: #909399;
}

.rating-tag {
  font-size: 16px;
  padding: 6px 16px;
  height: auto;
}

.metrics-card {
  border: 1px solid #e4e7ed;
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.03);
}

.metrics-table {
  margin-bottom: 0;
}

.metric-name {
  font-weight: 600;
  font-size: 14px;
}

.metric-score {
  font-weight: 700;
  font-size: 15px;
}
</style>
