<template>
  <div class="home-container">
    <el-header>
      <h1>体质测试健康分析系统</h1>
    </el-header>
    
    <el-main>
      <el-row :gutter="20">
        <el-col :span="10">
          <el-card class="box-card">
            <template #header>
              <div class="card-header">
                <span>体质测试数据录入</span>
              </div>
            </template>
            
            <el-form :model="form" label-width="160px" ref="formRef" size="default">
              
              <el-divider content-position="left">基本信息</el-divider>
              
              <el-form-item label="年龄 (20-79岁)" required>
                <el-input-number v-model="form.age" :min="20" :max="79" @change="handleAgeChange" />
              </el-form-item>
              
              <el-form-item label="性别" required>
                <el-radio-group v-model="form.gender">
                  <el-radio label="男">男</el-radio>
                  <el-radio label="女">女</el-radio>
                </el-radio-group>
              </el-form-item>

              <el-form-item label="姓名">
                <el-input v-model="form.name" placeholder="请输入姓名" />
              </el-form-item>

              <el-divider content-position="left">身体形态</el-divider>
              
              <el-form-item label="身高 (cm)">
                <el-input-number v-model="form.height" :min="50" :max="250" :precision="1" />
              </el-form-item>
              
              <el-form-item label="体重 (kg)">
                <el-input-number v-model="form.weight" :min="10" :max="250" :precision="1" />
              </el-form-item>
              
              <el-form-item label="BMI (kg/m²)">
                <el-input-number v-model="form.bmi" :min="10" :max="50" :precision="1" />
              </el-form-item>
              
              <el-form-item label="体脂率 (%)">
                <el-input-number v-model="form.body_fat_rate" :min="0" :max="60" :precision="1" />
              </el-form-item>

              <el-divider content-position="left">身体机能与素质</el-divider>
              
              <el-form-item label="肺活量 (ml)">
                <el-input-number v-model="form.vital_capacity" :min="0" :step="100" />
              </el-form-item>
              
              <el-form-item label="坐位体前屈 (cm)">
                <el-input-number v-model="form.sit_and_reach" :min="-30" :max="60" :precision="1" />
              </el-form-item>
              
              <el-form-item label="闭眼单脚站立 (s)">
                <el-input-number v-model="form.single_leg_stand" :min="0" :max="300" :precision="1" />
              </el-form-item>
              
              <el-form-item label="选择反应时间 (s)">
                <el-input-number v-model="form.reaction_time" :min="0" :max="5" :precision="2" :step="0.01" />
              </el-form-item>
              
              <el-form-item label="握力 (kg)">
                <el-input-number v-model="form.grip_strength" :min="0" :max="150" :precision="1" />
              </el-form-item>

              <!-- 成年人特有指标 (20-59岁) -->
              <div v-if="form.age >= 20 && form.age <= 59">
                <el-divider content-position="left">成年人专项指标 (20-59岁)</el-divider>
                
                <el-form-item label="最大摄氧量相对值">
                  <el-input-number v-model="form.max_oxygen_uptake" :min="0" :max="100" :precision="1" />
                  <span class="unit-text">ml/kg/min</span>
                </el-form-item>
                
                <el-form-item label="一分钟仰卧起坐 (次)">
                  <el-input-number v-model="form.sit_ups_per_minute" :min="0" :max="150" />
                </el-form-item>
                
                <el-form-item :label="form.gender === '男' ? '俯卧撑 (次)' : '跪卧撑 (次)'">
                  <el-input-number v-model="form.push_ups" :min="0" :max="150" />
                </el-form-item>
                
                <!-- 20-49岁特有指标 -->
                <el-form-item v-if="form.age <= 49" label="纵跳 (cm)">
                  <el-input-number v-model="form.vertical_jump" :min="0" :max="200" :precision="1" />
                </el-form-item>
              </div>

              <!-- 老年人特有指标 (60-79岁) -->
              <div v-if="form.age >= 60 && form.age <= 79">
                <el-divider content-position="left">老年人专项指标 (60-79岁)</el-divider>
                
                <el-form-item label="2分钟原地高抬腿 (次)">
                  <el-input-number v-model="form.high_knees_2min" :min="0" :max="500" />
                </el-form-item>
                
                <el-form-item label="30秒坐站 (次)">
                  <el-input-number v-model="form.sit_to_stand_30s" :min="0" :max="100" />
                </el-form-item>
              </div>

              <el-divider content-position="left">其他信息</el-divider>
              
              <el-form-item label="运动偏好">
                <el-checkbox-group v-model="form.exercise_preferences">
                  <el-checkbox label="健步走">健步走</el-checkbox>
                  <el-checkbox label="慢跑">慢跑</el-checkbox>
                  <el-checkbox label="游泳">游泳</el-checkbox>
                  <el-checkbox label="骑行">骑行</el-checkbox>
                  <el-checkbox label="太极拳">太极拳</el-checkbox>
                  <el-checkbox label="广场舞">广场舞</el-checkbox>
                  <el-checkbox label="力量训练">力量训练</el-checkbox>
                  <el-checkbox label="瑜伽">瑜伽</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              
              <el-form-item label="是否使用器械">
                <el-radio-group v-model="form.uses_equipment">
                  <el-radio :label="true">是</el-radio>
                  <el-radio :label="false">否</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="运动风险等级">
                <el-select v-model="form.exercise_risk_level" placeholder="请选择">
                  <el-option label="低" value="低" />
                  <el-option label="中" value="中" />
                  <el-option label="高" value="高" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="疾病史">
                <el-input v-model="diseasesInput" placeholder="多个疾病用逗号分隔" />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="submitForm" :loading="loading">生成运动处方</el-button>
                <el-button @click="resetForm">重置</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
        
        <el-col :span="14">
          <el-card class="box-card result-card" v-loading="loading">
            <template #header>
              <div class="card-header">
                <span>分析报告</span>
                <el-tag v-if="result" :type="getRatingType(result.overall_rating)" effect="dark">
                  {{ result.overall_rating }} ({{ result.overall_score }}分)
                </el-tag>
              </div>
            </template>
            
            <div v-if="result" class="report-content">
              <!-- 1. 综合概览 -->
              <div class="overview-section">
                <el-row :gutter="20">
                  <el-col :span="10">
                    <div ref="radarChartRef" class="radar-chart"></div>
                  </el-col>
                  <el-col :span="14">
                    <div class="score-summary">
                      <h3>体质测试总评</h3>
                      <el-progress 
                        type="dashboard" 
                        :percentage="result.overall_score" 
                        :color="getScoreColor"
                      >
                        <template #default="{ percentage }">
                          <span class="percentage-value">{{ percentage }}</span>
                          <span class="percentage-label">分</span>
                        </template>
                      </el-progress>
                      <div class="rating-text">{{ result.overall_rating }}</div>
                    </div>
                  </el-col>
                </el-row>
              </div>

              <el-divider>各项指标详细评分</el-divider>

              <!-- 2. 指标详情表格 -->
              <el-table :data="metricsTableData" style="width: 100%" stripe border size="small">
                <el-table-column prop="name" label="指标" width="140" />
                <el-table-column prop="score" label="得分" width="100">
                  <template #default="scope">
                    <span :style="{ color: getScoreColor(scope.row.score) }">{{ scope.row.score }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="评分" width="180">
                  <template #default="scope">
                    <el-progress 
                      :percentage="scope.row.score" 
                      :color="getScoreColor(scope.row.score)" 
                      :format="() => ''"
                    />
                  </template>
                </el-table-column>
                <el-table-column prop="rating" label="等级">
                  <template #default="scope">
                    <el-tag :type="getRatingType(scope.row.rating)" size="small">{{ scope.row.rating }}</el-tag>
                  </template>
                </el-table-column>
              </el-table>

              <el-divider>运动处方建议</el-divider>

              <!-- 3. 报告文本内容 -->
              <div class="markdown-content">
                <!-- 摘要 -->
                <el-card shadow="hover" class="text-card" v-if="parsedReport.summary">
                  <template #header>
                    <div class="card-header-small">
                      <el-icon><InfoFilled /></el-icon> <span>体质分析总结</span>
                    </div>
                  </template>
                  <div class="md-body" v-html="renderMarkdown(parsedReport.summary)"></div>
                </el-card>

                <!-- 目标 -->
                <el-card shadow="hover" class="text-card" v-if="parsedReport.goals">
                  <template #header>
                    <div class="card-header-small">
                      <el-icon><Flag /></el-icon> <span>运动处方目标</span>
                    </div>
                  </template>
                  <div class="md-body" v-html="renderMarkdown(parsedReport.goals)"></div>
                </el-card>

                <!-- 训练计划 (时间轴) -->
                <el-card shadow="hover" class="text-card" v-if="parsedReport.plan">
                  <template #header>
                    <div class="card-header-small">
                      <el-icon><Calendar /></el-icon> <span>分阶段训练计划</span>
                    </div>
                  </template>
                  
                  <!-- 尝试解析阶段 -->
                  <div v-if="parsedReport.phases.length > 0">
                    <el-timeline>
                      <el-timeline-item
                        v-for="(phase, index) in parsedReport.phases"
                        :key="index"
                        :type="index === 0 ? 'primary' : 'success'"
                        :hollow="index === 0"
                        :timestamp="phase.title"
                        placement="top"
                      >
                        <el-card class="phase-card">
                          <div class="md-body" v-html="renderMarkdown(phase.content)"></div>
                        </el-card>
                      </el-timeline-item>
                    </el-timeline>
                  </div>
                  <div v-else class="md-body" v-html="renderMarkdown(parsedReport.plan)"></div>
                </el-card>

                <!-- 其他建议 -->
                <el-collapse v-model="activeNames">
                  <el-collapse-item title="运动禁忌" name="1" v-if="parsedReport.contraindications">
                    <div class="md-body" v-html="renderMarkdown(parsedReport.contraindications)"></div>
                  </el-collapse-item>
                  <el-collapse-item title="进度监测" name="2" v-if="parsedReport.monitoring">
                    <div class="md-body" v-html="renderMarkdown(parsedReport.monitoring)"></div>
                  </el-collapse-item>
                  <el-collapse-item title="营养建议" name="3" v-if="parsedReport.nutrition">
                    <div class="md-body" v-html="renderMarkdown(parsedReport.nutrition)"></div>
                  </el-collapse-item>
                </el-collapse>
                
                <div class="disclaimer">
                  <p>本运动推荐仅供参考，请您务必在专业人士指导下进行运动。</p>
                </div>
              </div>
            </div>
            
            <div v-else class="empty-state">
              <el-empty description="暂无分析结果，请在左侧填写数据并提交" />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-main>
  </div>
</template>

<script setup>
import { reactive, ref, computed, nextTick, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled, Flag, Calendar } from '@element-plus/icons-vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { marked } from 'marked'

const loading = ref(false)
const result = ref(null)
const diseasesInput = ref('')
const activeNames = ref(['1', '2', '3'])
const radarChartRef = ref(null)
let radarChart = null

const form = reactive({
  age: 30,
  gender: '男',
  name: '',
  height: 170,
  weight: 65,
  bmi: 22.5,
  body_fat_rate: 18,
  vital_capacity: 3500,
  sit_and_reach: 10,
  single_leg_stand: 30,
  reaction_time: 0.4,
  grip_strength: 40,
  max_oxygen_uptake: 35,
  sit_ups_per_minute: 30,
  push_ups: 20,
  vertical_jump: 40,
  high_knees_2min: null,
  sit_to_stand_30s: null,
  exercise_preferences: [],
  uses_equipment: false,
  exercise_risk_level: '低',
  diseases: []
})

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

const handleAgeChange = (val) => {
  // Reset age-specific fields if needed
}

const submitForm = async () => {
  loading.value = true
  try {
    form.diseases = diseasesInput.value ? diseasesInput.value.split(/[,，]/).map(s => s.trim()).filter(s => s) : []
    
    const response = await axios.post('http://localhost:8000/analyze', form)
    
    result.value = response.data
    ElMessage.success('分析完成')
    
    nextTick(() => {
      initRadarChart()
    })
  } catch (error) {
    console.error(error)
    ElMessage.error('分析失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  result.value = null
  if (radarChart) {
    radarChart.dispose()
    radarChart = null
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
  if (!result.value || !result.value.individual_scores) return []
  
  const scores = result.value.individual_scores
  const ratings = result.value.individual_ratings || {}
  
  return Object.keys(scores).map(key => ({
    key,
    name: metricNameMap[key] || key,
    score: scores[key],
    rating: ratings[key] || '-'
  }))
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
    tooltip: {},
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

// Report Parsing Logic
const parsedReport = computed(() => {
  if (!result.value || !result.value.report) return {}
  
  const report = result.value.report
  const sections = {
    summary: '',
    goals: '',
    plan: '',
    phases: [],
    contraindications: '',
    monitoring: '',
    nutrition: ''
  }
  
  // Split by headers (###)
  const parts = report.split(/###\s+/g)
  
  parts.forEach(part => {
    if (part.includes('体质分析总结')) {
      sections.summary = part.replace(/\*\*一、\s*体质分析总结\*\*/, '').trim()
    } else if (part.includes('运动处方目标')) {
      sections.goals = part.replace(/\*\*三、\s*运动处方目标\*\*/, '').trim()
    } else if (part.includes('分阶段训练计划')) {
      const content = part.replace(/\*\*四、\s*分阶段训练计划\*\*/, '').trim()
      sections.plan = content
      
      // Try to extract phases
      const phaseRegex = /\*\*阶段(\d+)：(.*?)\*\*/g
      let match
      let lastIndex = 0
      const phases = []
      
      // Find all phase headers
      const matches = [...content.matchAll(phaseRegex)]
      
      for (let i = 0; i < matches.length; i++) {
        const currentMatch = matches[i]
        const nextMatch = matches[i + 1]
        
        const title = `阶段${currentMatch[1]}：${currentMatch[2]}`
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
      }
      
    } else if (part.includes('运动禁忌')) {
      sections.contraindications = part.replace(/\*\*五、\s*运动禁忌\*\*/, '').trim()
    } else if (part.includes('进度监测')) {
      sections.monitoring = part.replace(/\*\*六、\s*进度监测\*\*/, '').trim()
    } else if (part.includes('营养建议')) {
      sections.nutrition = part.replace(/\*\*七、\s*营养建议\*\*/, '').trim()
    }
  })
  
  return sections
})

const renderMarkdown = (text) => {
  if (!text) return ''
  return marked(text)
}

// Resize chart on window resize
window.addEventListener('resize', () => {
  if (radarChart) {
    radarChart.resize()
  }
})
</script>

<style scoped>
.home-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.box-card {
  margin-bottom: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-header-small {
  display: flex;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}
.card-header-small .el-icon {
  margin-right: 8px;
}
.unit-text {
  margin-left: 10px;
  color: #909399;
}
.overview-section {
  margin-bottom: 20px;
}
.radar-chart {
  width: 100%;
  height: 250px;
}
.score-summary {
  text-align: center;
  padding-top: 20px;
}
.percentage-value {
  display: block;
  margin-top: 10px;
  font-size: 28px;
}
.percentage-label {
  display: block;
  margin-top: 10px;
  font-size: 12px;
}
.rating-text {
  margin-top: 10px;
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
}
.text-card {
  margin-bottom: 15px;
}
.phase-card {
  margin-bottom: 10px;
}
.md-body {
  line-height: 1.6;
  font-size: 14px;
  color: #303133;
}
.md-body :deep(h1), .md-body :deep(h2), .md-body :deep(h3) {
  margin-top: 10px;
  margin-bottom: 10px;
}
.md-body :deep(ul), .md-body :deep(ol) {
  padding-left: 20px;
}
.md-body :deep(li) {
  margin-bottom: 5px;
}
.disclaimer {
  margin-top: 20px;
  text-align: center;
  color: #909399;
  font-size: 12px;
}
.empty-state {
  padding: 40px 0;
}
</style>
