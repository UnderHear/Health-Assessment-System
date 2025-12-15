<template>
  <div class="home-container">
    <NavBar />
    
    <el-main>
      <el-row justify="center">
        <el-col :span="14">
          <el-card class="box-card">
            <template #header>
              <div class="card-header">
                <span>体质测试数据录入</span>
                <el-button size="small" @click="applyProfileTemplate">使用个人信息模板</el-button>
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

              <el-form-item label="姓名" required>
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
                <el-input-number v-model="calculatedBMI" :min="10" :max="50" :precision="1" disabled />
                <span class="unit-text">自动计算</span>
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
                <el-checkbox-group v-model="form.exercise_preferences" :max="2">
                  <el-checkbox label="健步">健步</el-checkbox>
                  <el-checkbox label="跑步">跑步</el-checkbox>
                  <el-checkbox label="骑车">骑车</el-checkbox>
                  <el-checkbox label="力量练习">力量练习</el-checkbox>
                  <el-checkbox label="乒羽网柔">乒羽网柔</el-checkbox>
                  <el-checkbox label="足篮排">足篮排</el-checkbox>
                  <el-checkbox label="健身路径">健身路径</el-checkbox>
                  <el-checkbox label="游泳">游泳</el-checkbox>
                  <el-checkbox label="舞蹈">舞蹈</el-checkbox>
                  <el-checkbox label="踢跳">踢跳</el-checkbox>
                  <el-checkbox label="体操">体操</el-checkbox>
                  <el-checkbox label="气功">气功</el-checkbox>
                  <el-checkbox label="武术">武术</el-checkbox>
                  <el-checkbox label="保龄地掷门球">保龄地掷门球</el-checkbox>
                  <el-checkbox label="格斗">格斗</el-checkbox>
                  <el-checkbox label="登山">登山</el-checkbox>
                  <el-checkbox label="冰雪运动">冰雪运动</el-checkbox>
                  <el-checkbox label="其他">其他</el-checkbox>
                </el-checkbox-group>
                <el-input
                  v-if="form.exercise_preferences.includes('其他')"
                  v-model="otherExercisePreference"
                  placeholder="请输入其他运动偏好"
                  class="other-input"
                />
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
              
              <el-form-item label="疾病相关">
                <el-checkbox-group v-model="form.diseases">
                  <el-checkbox label="高血压">高血压</el-checkbox>
                  <el-checkbox label="血脂异常">血脂异常</el-checkbox>
                  <el-checkbox label="糖尿病">糖尿病</el-checkbox>
                  <el-checkbox label="心脏病">心脏病</el-checkbox>
                  <el-checkbox label="消化系统疾病">消化系统疾病</el-checkbox>
                  <el-checkbox label="关节疾病">关节疾病</el-checkbox>
                  <el-checkbox label="呼吸系统疾病">呼吸系统疾病</el-checkbox>
                  <el-checkbox label="职业病">职业病</el-checkbox>
                  <el-checkbox label="骨质疏松">骨质疏松</el-checkbox>
                  <el-checkbox label="不知道/无">不知道/无</el-checkbox>
                </el-checkbox-group>
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="submitForm" :loading="loading">生成运动处方</el-button>
                <el-button @click="resetForm">重置</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
      </el-row>
    </el-main>
  </div>
</template>

<script setup>
import { reactive, ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import NavBar from '../components/NavBar.vue'
import { API_ENDPOINTS, buildUrl } from '../api/config'

const router = useRouter()
const loading = ref(false)
const otherExercisePreference = ref('')

const form = reactive({
  age: null,
  gender: '',
  name: '',
  height: null,
  weight: null,
  bmi: null,
  body_fat_rate: null,
  vital_capacity: null,
  sit_and_reach: null,
  single_leg_stand: null,
  reaction_time: null,
  grip_strength: null,
  max_oxygen_uptake: null,
  sit_ups_per_minute: null,
  push_ups: null,
  vertical_jump: null,
  high_knees_2min: null,
  sit_to_stand_30s: null,
  exercise_preferences: [],
  uses_equipment: null,
  exercise_risk_level: '',
  diseases: []
})

const EXERCISE_PREFERENCE_OPTIONS = [
  '健步',
  '跑步',
  '骑车',
  '力量练习',
  '乒羽网柔',
  '足篮排',
  '健身路径',
  '游泳',
  '舞蹈',
  '踢跳',
  '体操',
  '气功',
  '武术',
  '保龄地掷门球',
  '格斗',
  '登山',
  '冰雪运动',
  '其他'
]
const EXERCISE_PREFERENCE_SET = new Set(EXERCISE_PREFERENCE_OPTIONS)
const LEGACY_EXERCISE_PREFERENCE_MAP = {
  健步走: '健步',
  慢跑: '跑步',
  骑行: '骑车',
  力量训练: '力量练习',
  广场舞: '舞蹈',
  太极拳: '武术',
  瑜伽: '乒羽网柔'
}

const DISEASE_OPTIONS = [
  '高血压',
  '血脂异常',
  '糖尿病',
  '心脏病',
  '消化系统疾病',
  '关节疾病',
  '呼吸系统疾病',
  '职业病',
  '骨质疏松',
  '不知道/无'
]
const DISEASE_SET = new Set(DISEASE_OPTIONS)

function parseExercisePreferences(value) {
  if (!value) {
    otherExercisePreference.value = ''
    return []
  }
  const listSource = Array.isArray(value) ? value : String(value).split(/[,，]/)
  const list = listSource.map((item) => String(item).trim()).filter((item) => item)
  const result = []
  otherExercisePreference.value = ''

  list.forEach((raw) => {
    const match = raw.match(/^其他\((.*)\)$/)
    if (match) {
      if (!result.includes('其他')) result.push('其他')
      otherExercisePreference.value = match[1]
      return
    }

    const mapped = LEGACY_EXERCISE_PREFERENCE_MAP[raw] || raw
    if (EXERCISE_PREFERENCE_SET.has(mapped)) {
      if (!result.includes(mapped)) result.push(mapped)
      return
    }

    if (!result.includes('其他')) result.push('其他')
    if (!otherExercisePreference.value) {
      otherExercisePreference.value = raw
    } else if (!otherExercisePreference.value.includes(raw)) {
      otherExercisePreference.value = `${otherExercisePreference.value}、${raw}`
    }
  })

  return result.slice(0, 2)
}

function sanitizeDiseases(value) {
  if (!value) return []
  const listSource = Array.isArray(value) ? value : String(value).split(/[,，]/)
  const list = listSource.map((item) => String(item).trim()).filter((item) => item)
  const filtered = list.filter((item) => DISEASE_SET.has(item))
  return Array.from(new Set(filtered))
}

const calculatedBMI = computed(() => {
  if (form.height && form.weight) {
    const heightInMeters = form.height / 100
    return Number((form.weight / (heightInMeters * heightInMeters)).toFixed(1))
  }
  return null
})

// Watch for BMI changes to update form.bmi
watch(calculatedBMI, (newVal) => {
  form.bmi = newVal
})

const handleAgeChange = (val) => {
  // Reset age-specific fields if needed
}

const applyProfileTemplate = async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    const storedUserInfo = localStorage.getItem('userInfo')
    if (storedUserInfo && !form.name) {
      const parsedUserInfo = JSON.parse(storedUserInfo)
      if (parsedUserInfo?.realName) {
        form.name = parsedUserInfo.realName
      }
    }

    const response = await axios.get(buildUrl(API_ENDPOINTS.PROFILE.GET), {
      headers: { Authorization: token }
    })

    if (response.data.code !== 200) {
      throw new Error(response.data.message || '获取身体档案失败')
    }

    const data = response.data.data
    if (!data) {
      ElMessage.warning('未填写身体档案，请前往个人信息页面填写')
      router.push('/profile')
      return
    }

    form.age = data.age ?? null
    form.gender = data.gender ?? ''
    form.height = data.height ?? null
    form.weight = data.weight ?? null
    form.bmi = data.bmi ?? null
    form.body_fat_rate = data.bodyFatRate ?? null
    form.vital_capacity = data.vitalCapacity ?? null
    form.sit_and_reach = data.sitAndReach ?? null
    form.single_leg_stand = data.singleLegStand ?? null
    form.reaction_time = data.reactionTime ?? null
    form.grip_strength = data.gripStrength ?? null
    form.max_oxygen_uptake = data.maxOxygenUptake ?? null
    form.sit_ups_per_minute = data.sitUpsPerMinute ?? null
    form.push_ups = data.pushUps ?? null
    form.vertical_jump = data.verticalJump ?? null
    form.high_knees_2min = data.highKnees2min ?? null
    form.sit_to_stand_30s = data.sitToStand30s ?? null
    form.exercise_preferences = parseExercisePreferences(data.exercisePreferences)
    form.uses_equipment = data.usesEquipment === null || data.usesEquipment === undefined ? null : Boolean(data.usesEquipment)
    form.exercise_risk_level = data.exerciseRiskLevel ?? ''
    form.diseases = sanitizeDiseases(data.diseases)

    ElMessage.success('已填入身体档案数据')
  } catch (error) {
    console.error(error)
    ElMessage.error('获取身体档案失败: ' + (error.response?.data?.message || error.message))
  }
}

const submitForm = async () => {
  if (!form.name || !String(form.name).trim()) {
    ElMessage.warning('请填写姓名')
    return
  }

  if (form.exercise_preferences.length === 0) {
    ElMessage.warning('请选择1-2项运动偏好')
    return
  }

  if (form.exercise_preferences.includes('其他') && !otherExercisePreference.value.trim()) {
    ElMessage.warning('请填写其他运动偏好内容')
    return
  }
  
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  loading.value = true
  try {
    
    // 构建符合 Java 后端 UserProfile 实体的驼峰格式数据
    const profileData = {
      name: form.name,
      age: form.age,
      gender: form.gender,
      height: form.height,
      weight: form.weight,
      bmi: form.bmi,
      bodyFatRate: form.body_fat_rate,
      vitalCapacity: form.vital_capacity,
      sitAndReach: form.sit_and_reach,
      singleLegStand: form.single_leg_stand,
      reactionTime: form.reaction_time,
      gripStrength: form.grip_strength,
      maxOxygenUptake: form.max_oxygen_uptake,
      sitUpsPerMinute: form.sit_ups_per_minute,
      pushUps: form.push_ups,
      verticalJump: form.vertical_jump,
      highKnees2min: form.high_knees_2min,
      sitToStand30s: form.sit_to_stand_30s,
      exercisePreferences: form.exercise_preferences.map(pref => {
        if (pref === '其他') {
          return otherExercisePreference.value ? `其他(${otherExercisePreference.value.trim()})` : '其他'
        }
        return pref
      }).join(','),
      usesEquipment: form.uses_equipment,
      exerciseRiskLevel: form.exercise_risk_level,
      diseases: form.diseases.join(',')
    }
    
    // 请求 Java 后端进行分析（Java 后端会保存数据并调用 Python 后端）
    const response = await axios.post(buildUrl(API_ENDPOINTS.PROFILE.ANALYZE), profileData, {
      headers: { 'Authorization': token }
    })
    
    if (response.data.code === 200) {
      ElMessage.success('分析完成')
      
      const responseData = response.data.data
      if (responseData && responseData.id) {
        router.push(`/report/${responseData.id}`)
      }
    } else {
      throw new Error(response.data.message || '分析失败')
    }

  } catch (error) {
    console.error(error)
    ElMessage.error('分析失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  // Reset form to empty values
  form.age = null
  form.gender = ''
  form.name = ''
  form.height = null
  form.weight = null
  form.bmi = null
  form.body_fat_rate = null
  form.vital_capacity = null
  form.sit_and_reach = null
  form.single_leg_stand = null
  form.reaction_time = null
  form.grip_strength = null
  form.max_oxygen_uptake = null
  form.sit_ups_per_minute = null
  form.push_ups = null
  form.vertical_jump = null
  form.high_knees_2min = null
  form.sit_to_stand_30s = null
  form.exercise_preferences = []
  form.uses_equipment = null
  form.exercise_risk_level = ''
  form.diseases = []
  otherExercisePreference.value = ''
}
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
  font-size: 18px; /* Increased font size */
  color: #303133;
}
.header-icon {
  margin-right: 10px;
  font-size: 20px;
  color: #409EFF;
}
.warning-header .header-icon {
  color: #E6A23C;
}
.unit-text {
  margin-left: 10px;
  color: #909399;
}
.overview-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
}
.radar-chart {
  width: 100%;
  height: 300px; /* Increased height */
}
.score-summary {
  text-align: center;
  padding-top: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.section-title {
  font-size: 20px;
  margin-bottom: 20px;
  color: #303133;
}
.score-circle {
  margin-bottom: 15px;
}
.percentage-value {
  display: block;
  margin-top: 10px;
  font-size: 42px; /* Much larger font */
  font-weight: bold;
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
  font-size: 18px;
  padding: 8px 20px;
  height: auto;
}
.divider-title {
  font-size: 18px;
  font-weight: bold;
  color: #606266;
}
.metrics-table {
  margin-bottom: 30px;
}
.metric-name {
  font-weight: bold;
  font-size: 15px;
}
.metric-score {
  font-weight: bold;
  font-size: 16px;
}
.text-card {
  margin-bottom: 20px;
  border-radius: 8px;
  transition: all 0.3s;
}
.text-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.summary-card {
  border-left: 5px solid #409EFF;
}
.goals-card {
  border-left: 5px solid #67C23A;
}
.plan-card {
  border-left: 5px solid #E6A23C;
}
.warning-card {
  border-left: 5px solid #F56C6C;
}
.info-card {
  border-left: 5px solid #909399;
}
.success-card {
  border-left: 5px solid #67C23A;
}
.phase-card {
  margin-bottom: 10px;
  background-color: #fdfdfd;
}
.timeline-container {
  padding: 10px 0;
}
.md-body {
  line-height: 1.8;
  font-size: 15px;
  color: #303133;
}
.large-text {
  font-size: 16px; /* Larger body text */
}
.md-body :deep(h1), .md-body :deep(h2), .md-body :deep(h3) {
  margin-top: 15px;
  margin-bottom: 15px;
  font-weight: 600;
}
.md-body :deep(strong) {
  color: #303133;
  font-weight: 700;
}
.md-body :deep(ul), .md-body :deep(ol) {
  padding-left: 25px;
  margin-bottom: 15px;
}
.md-body :deep(li) {
  margin-bottom: 8px;
}
.disclaimer {
  margin-top: 30px;
  text-align: center;
  color: #909399;
  font-size: 14px;
  padding: 15px;
  background: #f4f4f5;
  border-radius: 4px;
}
.empty-state {
  padding: 60px 0;
}
.other-input {
  margin-top: 10px;
  max-width: 240px;
}
</style>
