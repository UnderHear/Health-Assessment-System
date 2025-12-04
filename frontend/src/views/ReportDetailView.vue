<template>
  <div class="report-container">
    <NavBar />
    
    <el-main>
      <el-page-header @back="goBack" content="测试报告详情" class="page-header" />
      
      <div v-loading="loading" class="content-wrapper">
        <el-card class="box-card result-card" v-if="result">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <span class="title">分析报告</span>
                <span class="date">{{ formatDate(profileData.createTime) }}</span>
              </div>
              <el-tag :type="getRatingType(result.overall_rating)" effect="dark" size="large">
                {{ result.overall_rating }} ({{ result.overall_score }}分)
              </el-tag>
            </div>
          </template>
          
          <div class="report-content">
            <!-- 1. 综合概览 -->
            <div class="overview-section">
              <el-row :gutter="20" align="middle">
                <el-col :span="10">
                  <div ref="radarChartRef" class="radar-chart"></div>
                </el-col>
                <el-col :span="14">
                  <div class="score-summary">
                    <h3 class="section-title">体质测试总评</h3>
                    <div class="score-circle">
                      <el-progress 
                        type="dashboard" 
                        :percentage="result.overall_score" 
                        :color="getScoreColor"
                        :width="180"
                        :stroke-width="15"
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
            </div>

            <el-divider><span class="divider-title">各项指标详细评分</span></el-divider>

            <!-- 2. 指标详情表格 -->
            <el-table :data="metricsTableData" style="width: 100%" stripe border size="default" class="metrics-table">
              <el-table-column prop="name" label="指标" width="160">
                <template #default="scope">
                  <span class="metric-name">{{ scope.row.name }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="value" label="测试值" width="120" align="center">
                <template #default="scope">
                  {{ scope.row.value }}
                </template>
              </el-table-column>
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

            <el-divider><span class="divider-title">运动处方建议</span></el-divider>

            <!-- 3. 报告文本内容 -->
            <div class="markdown-content">
              <!-- Intro -->
              <div v-if="parsedReport.intro" class="md-body intro-text" v-html="renderMarkdown(parsedReport.intro)"></div>

              <!-- 摘要 -->
              <div class="section-block" v-if="parsedReport.summary">
                <h3 class="section-title">一、体质分析总结</h3>
                <div class="md-body" v-html="renderMarkdown(parsedReport.summary)"></div>
              </div>

              <!-- Evaluation -->
              <div class="section-block" v-if="parsedReport.evaluation">
                <h3 class="section-title">二、各项指标评价</h3>
                <div class="md-body" v-html="renderMarkdown(parsedReport.evaluation)"></div>
              </div>

              <!-- 目标 -->
              <div class="section-block" v-if="parsedReport.goals">
                <h3 class="section-title">三、运动处方目标</h3>
                <div class="md-body" v-html="renderMarkdown(parsedReport.goals)"></div>
              </div>

              <!-- 训练计划 -->
              <div class="section-block" v-if="parsedReport.plan">
                <h3 class="section-title">四、分阶段训练计划</h3>
                
                <!-- Display Intro Text if exists -->
                <div v-if="parsedReport.planIntro" class="md-body" v-html="renderMarkdown(parsedReport.planIntro)"></div>

                <!-- 阶段展示 -->
                <div v-if="parsedReport.phases.length > 0" class="phases-container">
                  <div v-for="(phase, index) in parsedReport.phases" :key="index" class="phase-item">
                    <h4 class="phase-title">{{ phase.title }}</h4>
                    <div class="md-body" v-html="renderMarkdown(phase.content)"></div>
                  </div>
                </div>
                <div v-else-if="!parsedReport.planIntro" class="md-body" v-html="renderMarkdown(parsedReport.plan)"></div>
              </div>

              <!-- 运动禁忌 -->
              <div class="section-block warning-section" v-if="parsedReport.contraindications">
                <h3 class="section-title">五、运动禁忌</h3>
                <div class="md-body" v-html="renderMarkdown(parsedReport.contraindications)"></div>
              </div>

              <!-- 进度监测和营养建议 -->
              <div class="section-row">
                <div class="section-block half-width" v-if="parsedReport.monitoring">
                  <h3 class="section-title">六、进度监测</h3>
                  <div class="md-body" v-html="renderMarkdown(parsedReport.monitoring)"></div>
                </div>
                
                <div class="section-block half-width" v-if="parsedReport.nutrition">
                  <h3 class="section-title">七、营养建议</h3>
                  <div class="md-body" v-html="renderMarkdown(parsedReport.nutrition)"></div>
                </div>
              </div>
              
              <div class="disclaimer">
                <p>本运动推荐仅供参考，请您务必在专业人士指导下进行运动。</p>
              </div>
            </div>
          </div>
        </el-card>
        
        <el-empty v-else-if="!loading" description="未找到报告数据" />
      </div>
    </el-main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { InfoFilled, Flag, Calendar, Warning, TrendCharts, Apple, DataAnalysis } from '@element-plus/icons-vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { marked } from 'marked'
import NavBar from '../components/NavBar.vue'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const profileData = ref(null)
const result = ref(null)
const activeNames = ref(['1', '2', '3'])
const radarChartRef = ref(null)
let radarChart = null

const metricNameMap = {
  "bmi": "BMI",
  "body_fat_rate": "体脂率",
  "vital_capacity": "肺活量",
  "max_oxygen_uptake": "最大摄氧量",
  "sit_and_reach": "坐位体前屈",
  "single_leg_stand": "闭眼单脚站立",
  "reaction_time": "选择反应时间",
  "grip_strength": "握力",
  "sit_ups_per_minute": "仰卧起坐",
  "push_ups": "俯卧撑",
  "vertical_jump": "纵跳",
  "high_knees_2min": "2分钟高抬腿",
  "sit_to_stand_30s": "30秒坐站"
}

// Map backend field names to metric keys
const fieldToMetricMap = {
  "bmi": "bmi",
  "bodyFatRate": "body_fat_rate",
  "vitalCapacity": "vital_capacity",
  "maxOxygenUptake": "max_oxygen_uptake",
  "sitAndReach": "sit_and_reach",
  "singleLegStand": "single_leg_stand",
  "reactionTime": "reaction_time",
  "gripStrength": "grip_strength",
  "sitUpsPerMinute": "sit_ups_per_minute",
  "pushUps": "push_ups",
  "verticalJump": "vertical_jump",
  "highKnees2min": "high_knees_2min",
  "sitToStand30s": "sit_to_stand_30s"
}

const goBack = () => {
  router.back()
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

const fetchReport = async () => {
  const id = route.params.id
  if (!id) return
  
  const token = localStorage.getItem('token')
  if (!token) {
    router.push('/login')
    return
  }
  
  loading.value = true
  try {
    const response = await axios.get(`http://localhost:8080/api/profile/${id}`, {
      headers: { 'Authorization': token }
    })
    
    if (response.data.code === 200) {
      profileData.value = response.data.data
      
      if (profileData.value.analysisResult) {
        try {
          const analysisData = JSON.parse(profileData.value.analysisResult)
          result.value = {
            ...analysisData,
            report: profileData.value.report
          }
          
          nextTick(() => {
            initRadarChart()
          })
        } catch (e) {
          console.error("Failed to parse analysis result JSON", e)
          ElMessage.error("报告数据解析失败")
        }
      } else {
        ElMessage.warning("该记录没有分析结果")
      }
    } else {
      ElMessage.error(response.data.message || '获取报告失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取报告失败')
  } finally {
    loading.value = false
  }
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
  if (!result.value || !result.value.individual_scores || !profileData.value) return []
  
  const scores = result.value.individual_scores
  const ratings = result.value.individual_ratings || {}
  
  return Object.keys(scores).map(key => {
    // Find the original value from profileData
    let originalValue = '-'
    // Try to find the matching field in profileData
    // We need a reverse mapping or just check known fields
    // The keys in scores are snake_case (e.g. body_fat_rate)
    // The keys in profileData are camelCase (e.g. bodyFatRate)
    
    // Simple conversion strategy: snake_case to camelCase
    const camelKey = key.replace(/_([a-z])/g, (g) => g[1].toUpperCase())
    if (profileData.value[camelKey] !== undefined && profileData.value[camelKey] !== null) {
      originalValue = profileData.value[camelKey]
    }
    
    return {
      key,
      name: metricNameMap[key] || key,
      score: scores[key],
      rating: ratings[key] || '-',
      value: originalValue
    }
  })
})

const initRadarChart = () => {
  if (!radarChartRef.value || !result.value) return
  
  if (radarChart) {
    radarChart.dispose()
  }
  
  radarChart = echarts.init(radarChartRef.value)
  
  const indicators = metricsTableData.value.map(item => ({
    name: item.name,
    max: 100
  }))
  
  const dataValues = metricsTableData.value.map(item => item.score)
  
  const option = {
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
        color: '#666'
      },
      splitArea: {
        areaStyle: {
          color: ['#f5f7fa', '#f5f7fa', '#f5f7fa', '#f5f7fa'],
          shadowColor: 'rgba(0, 0, 0, 0.1)',
          shadowBlur: 10
        }
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
            color: 'rgba(64, 158, 255, 0.2)'
          },
          lineStyle: {
            color: '#409EFF'
          },
          itemStyle: {
            color: '#409EFF'
          }
        }
      ]
    }]
  }
  
  radarChart.setOption(option)
}

// Report Parsing Logic with Improved Section Extraction
const parsedReport = computed(() => {
  if (!result.value || !result.value.report) return {}
  
  const report = result.value.report
  const sections = {
    intro: '',
    summary: '',
    evaluation: '',
    goals: '',
    plan: '',
    phases: [],
    planIntro: '',
    contraindications: '',
    monitoring: '',
    nutrition: ''
  }
  
  // Extract intro (before the first ### header)
  const firstHeaderMatch = report.match(/###\s+/)
  if (firstHeaderMatch) {
    sections.intro = report.substring(0, firstHeaderMatch.index).trim()
  }
  
  // Extract each section by matching between ### headers
  // 一、体质分析总结
  const summaryMatch = report.match(/###\s+\*\*?一、\s*体质分析总结\*\*?/i)
  if (summaryMatch) {
    const startIdx = summaryMatch.index + summaryMatch[0].length
    const nextHeaderMatch = report.substring(startIdx).match(/###\s+\*\*?[二三四五六七]/i)
    const endIdx = nextHeaderMatch ? startIdx + nextHeaderMatch.index : report.length
    sections.summary = report.substring(startIdx, endIdx).trim()
  }
  
  // 二、各项指标评价
  const evaluationMatch = report.match(/###\s+\*\*?二、\s*各项指标评价\*\*?/i)
  if (evaluationMatch) {
    const startIdx = evaluationMatch.index + evaluationMatch[0].length
    const nextHeaderMatch = report.substring(startIdx).match(/###\s+\*\*?[三四五六七]/i)
    const endIdx = nextHeaderMatch ? startIdx + nextHeaderMatch.index : report.length
    sections.evaluation = report.substring(startIdx, endIdx).trim()
  }
  
  // 三、运动处方目标
  const goalsMatch = report.match(/###\s+\*\*?三、\s*运动处方目标\*\*?/i)
  if (goalsMatch) {
    const startIdx = goalsMatch.index + goalsMatch[0].length
    const nextHeaderMatch = report.substring(startIdx).match(/###\s+\*\*?[四五六七]/i)
    const endIdx = nextHeaderMatch ? startIdx + nextHeaderMatch.index : report.length
    sections.goals = report.substring(startIdx, endIdx).trim()
  }
  
  // 四、分阶段训练计划
  const planMatch = report.match(/###\s+\*\*?四、\s*分阶段训练计划\*\*?/i)
  if (planMatch) {
    const startIdx = planMatch.index + planMatch[0].length
    const nextHeaderMatch = report.substring(startIdx).match(/###\s+\*\*?[五六七]/i)
    const endIdx = nextHeaderMatch ? startIdx + nextHeaderMatch.index : report.length
    const content = report.substring(startIdx, endIdx).trim()
    sections.plan = content
    
    // Try to extract phases using #### headers
    const phaseRegex = /####\s+(?:\*\*)?阶段([一二三四五六七八九十\d]+)\s*[:：]\s*(.*?)(?:\*\*)?(?:\n|$)/gi
    const phases = []
    
    // Find all phase headers
    const matches = [...content.matchAll(phaseRegex)]
    
    for (let i = 0; i < matches.length; i++) {
      const currentMatch = matches[i]
      const nextMatch = matches[i + 1]
      
      const title = `阶段${currentMatch[1]}：${currentMatch[2].replace(/\*\*/g, '').trim()}`
      const startIndex = currentMatch.index + currentMatch[0].length
      const endIndex = nextMatch ? nextMatch.index : content.length
      
      const phaseContent = content.substring(startIndex, endIndex).trim()
      phases.push({
        title,
        content: phaseContent
      })
    }
    
    if (phases.length > 0) {
      sections.phases = phases
      // Extract intro text (before the first phase)
      if (matches.length > 0) {
        sections.planIntro = content.substring(0, matches[0].index).trim()
      }
    }
  }
  
  // 五、运动禁忌
  const contraindicationsMatch = report.match(/###\s+\*\*?五、\s*运动禁忌\*\*?/i)
  if (contraindicationsMatch) {
    const startIdx = contraindicationsMatch.index + contraindicationsMatch[0].length
    const nextHeaderMatch = report.substring(startIdx).match(/###\s+\*\*?[六七]/i)
    const endIdx = nextHeaderMatch ? startIdx + nextHeaderMatch.index : report.length
    sections.contraindications = report.substring(startIdx, endIdx).trim()
  }
  
  // 六、进度监测
  const monitoringMatch = report.match(/###\s+\*\*?六、\s*进度监测\*\*?/i)
  if (monitoringMatch) {
    const startIdx = monitoringMatch.index + monitoringMatch[0].length
    const nextHeaderMatch = report.substring(startIdx).match(/###\s+\*\*?七/i)
    const endIdx = nextHeaderMatch ? startIdx + nextHeaderMatch.index : report.length
    sections.monitoring = report.substring(startIdx, endIdx).trim()
  }
  
  // 七、营养建议
  const nutritionMatch = report.match(/###\s+\*\*?七、\s*营养建议\*\*?/i)
  if (nutritionMatch) {
    const startIdx = nutritionMatch.index + nutritionMatch[0].length
    // This is likely the last section, so take everything after it
    // But exclude any disclaimer text at the very end
    const disclaimerMatch = report.substring(startIdx).match(/\*\*本运动推荐仅供参考/i)
    const endIdx = disclaimerMatch ? startIdx + disclaimerMatch.index : report.length
    sections.nutrition = report.substring(startIdx, endIdx).trim()
  }
  
  return sections
})

const renderMarkdown = (text) => {
  if (!text) return ''
  return marked(text)
}

onMounted(() => {
  fetchReport()
})

// Resize chart on window resize
window.addEventListener('resize', () => {
  if (radarChart) {
    radarChart.resize()
  }
})
</script>

<style scoped>
.report-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.page-header {
  margin-bottom: 20px;
}
.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
}
.box-card {
  margin-bottom: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-left {
  display: flex;
  flex-direction: column;
}
.title {
  font-size: 18px;
  font-weight: 600;
}
.date {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}
.overview-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #fff;
  border-radius: 4px;
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
.score-circle {
  margin-bottom: 15px;
}
.percentage-value {
  display: block;
  margin-top: 10px;
  font-size: 40px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}
.percentage-label {
  display: block;
  font-size: 14px;
  color: #909399;
}
.rating-badge {
  margin-top: 10px;
}
.rating-tag {
  font-size: 16px;
  padding: 6px 16px;
  height: auto;
}
.divider-title {
  font-size: 16px;
  font-weight: 600;
  color: #606266;
}
.metrics-table {
  margin-bottom: 30px;
}
.metric-name {
  font-weight: 500;
  font-size: 14px;
}
.metric-score {
  font-weight: 600;
  font-size: 15px;
}

/* 简化的报告内容样式 */
.markdown-content {
  background: #fff;
  padding: 30px;
  border-radius: 4px;
}
.intro-text {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}
.section-block {
  margin-bottom: 35px;
}
.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e4e7ed;
}
.warning-section .section-title {
  color: #E6A23C;
  border-bottom-color: #E6A23C;
}

/* 阶段展示 */
.phases-container {
  margin-top: 20px;
}
.phase-item {
  margin-bottom: 25px;
  padding: 20px;
  background: #fafafa;
  border-radius: 4px;
  border-left: 3px solid #409EFF;
}
.phase-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

/* 并排布局 */
.section-row {
  display: flex;
  gap: 20px;
  margin-bottom: 35px;
}
.half-width {
  flex: 1;
}

/* Markdown 内容样式 */
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
.disclaimer {
  margin-top: 30px;
  text-align: center;
  color: #909399;
  font-size: 13px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}
</style>
