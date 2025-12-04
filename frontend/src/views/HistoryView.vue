<template>
  <div class="page-container">
    <NavBar />
    <el-main>
      <div class="header-section">
        <h2 class="page-title">测试记录</h2>
      </div>

      <div v-loading="loading" class="records-container">
        <div v-if="historyList.length === 0 && !loading" class="empty-state">
          <el-empty description="暂无测试记录" />
        </div>

        <div class="records-grid">
          <el-card 
            v-for="record in historyList" 
            :key="record.id"
            class="record-card" 
            :class="{ 'disabled-card': record.status !== 'COMPLETED' }" 
            @click="handleCardClick(record)"
          >
            <div class="card-header-section">
              <div class="time-status">
                <div class="test-time">{{ formatDate(record.createTime) }}</div>
                <el-tag :type="getStatusType(record.status)" size="small">
                  {{ getStatusText(record.status) }}
                </el-tag>
              </div>
            </div>

            <div v-if="record.status === 'COMPLETED'" class="card-content">
              <div :ref="el => setChartRef(el, record.id)" class="mini-radar-chart"></div>
              
              <div class="score-info">
                <div class="overall-score">
                  <span class="score-value">{{ getOverallScore(record) }}</span>
                  <span class="score-label">分</span>
                </div>
                <div class="rating-text">{{ getOverallRating(record) }}</div>
              </div>

              <el-button type="primary" size="small" class="view-btn" @click.stop="viewDetail(record.id)">
                查看详情
              </el-button>
            </div>

            <div v-else class="card-content-placeholder">
              <div class="status-icon">
                <el-icon v-if="record.status === 'GENERATING'" :size="40" class="loading-icon">
                  <Loading />
                </el-icon>
                <el-icon v-else-if="record.status === 'FAILED'" :size="40" class="error-icon">
                  <CircleClose />
                </el-icon>
              </div>
              <div class="status-text">
                {{ record.status === 'GENERATING' ? '报告生成中...' : '生成失败' }}
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </el-main>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Loading, CircleClose } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import NavBar from '../components/NavBar.vue'
import { API_BASE_URL, API_ENDPOINTS, buildUrl } from '../api/config'

const router = useRouter()
const loading = ref(false)
const historyList = ref([])
const chartRefs = ref({})
const charts = {}

const metricNameMap = {
  "bmi": "BMI",
  "body_fat_rate": "体脂率",
  "vital_capacity": "肺活量",
  "max_oxygen_uptake": "最大摄氧量",
  "sit_and_reach": "坐位体前屈",
  "single_leg_stand": "单脚站立",
  "reaction_time": "反应时间",
  "grip_strength": "握力",
  "sit_ups_per_minute": "仰卧起坐",
  "push_ups": "俯卧撑",
  "vertical_jump": "纵跳",
  "high_knees_2min": "高抬腿",
  "sit_to_stand_30s": "坐站"
}

const setChartRef = (el, id) => {
  if (el) {
    chartRefs.value[id] = el
  }
}

const fetchHistory = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
      return
    }
    
    const response = await axios.get(buildUrl(API_ENDPOINTS.PROFILE.HISTORY), {
      headers: { 'Authorization': token }
    })
    
    if (response.data.code === 200) {
      historyList.value = response.data.data
      await nextTick()
      initCharts()
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取记录失败')
  } finally {
    loading.value = false
  }
}

const initCharts = () => {
  historyList.value.forEach(record => {
    if (record.status === 'COMPLETED' && chartRefs.value[record.id]) {
      initRadarChart(record.id, record)
    }
  })
}

const initRadarChart = (id, record) => {
  const chartEl = chartRefs.value[id]
  if (!chartEl) return

  if (charts[id]) {
    charts[id].dispose()
  }

  try {
    const analysisData = JSON.parse(record.analysisResult)
    const scores = analysisData.individual_scores || {}
    
    const indicators = Object.keys(scores).map(key => ({
      name: metricNameMap[key] || key,
      max: 100
    }))
    
    const dataValues = Object.values(scores)
    
    const chart = echarts.init(chartEl)
    
    const option = {
      tooltip: {
        appendToBody: true,
        confine: false,
        extraCssText: 'z-index: 9999;'
      },
      radar: {
        indicator: indicators,
        radius: '60%',
        splitNumber: 4,
        axisName: {
          color: '#666',
          fontSize: 10
        },
        splitLine: {
          lineStyle: {
            color: '#e4e7ed'
          }
        },
        splitArea: {
          show: false
        }
      },
      series: [{
        name: '体质评分',
        type: 'radar',
        data: [
          {
            value: dataValues,
            name: '各项指标得分',
            areaStyle: {
              color: 'rgba(64, 158, 255, 0.15)'
            },
            lineStyle: {
              color: '#409EFF',
              width: 2
            },
            itemStyle: {
              color: '#409EFF'
            }
          }
        ]
      }]
    }
    
    chart.setOption(option)
    charts[id] = chart
  } catch (e) {
    console.error('Failed to init chart for record', id, e)
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusType = (status) => {
  if (status === 'COMPLETED') return 'success'
  if (status === 'GENERATING') return 'warning'
  if (status === 'FAILED') return 'danger'
  return 'info'
}

const getStatusText = (status) => {
  if (status === 'COMPLETED') return '已完成'
  if (status === 'GENERATING') return '生成中'
  if (status === 'FAILED') return '生成失败'
  return '未知'
}

const getOverallScore = (row) => {
  if (row.analysisResult) {
    try {
      const data = JSON.parse(row.analysisResult)
      return data.overall_score || '-'
    } catch (e) {
      return '-'
    }
  }
  return '-'
}

const getOverallRating = (row) => {
  if (row.analysisResult) {
    try {
      const data = JSON.parse(row.analysisResult)
      return data.overall_rating || '-'
    } catch (e) {
      return '-'
    }
  }
  return '-'
}

const handleCardClick = (record) => {
  if (record.status === 'COMPLETED') {
    viewDetail(record.id)
  }
}

const viewDetail = (id) => {
  router.push(`/report/${id}`)
}

onMounted(() => {
  fetchHistory()
})

// Resize charts on window resize
window.addEventListener('resize', () => {
  Object.values(charts).forEach(chart => {
    if (chart) {
      chart.resize()
    }
  })
})
</script>

<style scoped>
.page-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.header-section {
  margin-bottom: 24px;
}
.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}
.records-container {
  min-height: 400px;
}
.records-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}
.record-card {
  cursor: pointer;
  transition: all 0.3s;
  height: 100%;
}
.record-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}
.disabled-card {
  cursor: not-allowed;
  opacity: 0.8;
}
.disabled-card:hover {
  transform: none;
  box-shadow: none;
}
.card-header-section {
  margin-bottom: 16px;
}
.time-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.test-time {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}
.card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.mini-radar-chart {
  width: 100%;
  height: 200px;
  margin-bottom: 16px;
}
.score-info {
  text-align: center;
  margin-bottom: 16px;
}
.overall-score {
  margin-bottom: 8px;
}
.score-value {
  font-size: 36px;
  font-weight: 600;
  color: #303133;
}
.score-label {
  font-size: 16px;
  color: #909399;
  margin-left: 4px;
}
.rating-text {
  font-size: 18px;
  font-weight: 500;
  color: #409EFF;
}
.view-btn {
  width: 100%;
}
.card-content-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  padding: 20px;
}
.status-icon {
  margin-bottom: 16px;
}
.loading-icon {
  color: #E6A23C;
  animation: rotate 1.5s linear infinite;
}
.error-icon {
  color: #F56C6C;
}
.status-text {
  font-size: 14px;
  color: #909399;
}
@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
@media (max-width: 768px) {
  .page-container {
    padding: 12px;
  }
  .page-title {
    font-size: 20px;
  }
  .mini-radar-chart {
    height: 180px;
  }
}
</style>
