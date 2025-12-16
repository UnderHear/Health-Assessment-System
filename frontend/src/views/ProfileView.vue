<template>
  <div class="page-container">
    <NavBar />
    <el-main>
      <div class="content-container">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="box-card">
            <template #header>
              <div class="card-header">
                <span>基本信息</span>
              </div>
            </template>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="用户名">{{ userInfo?.username }}</el-descriptions-item>
              <el-descriptions-item label="姓名">{{ userInfo?.realName }}</el-descriptions-item>
              <el-descriptions-item label="邮箱">{{ userInfo?.email || '未设置' }}</el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
        
        <el-col :span="16">
          <el-card class="box-card">
            <template #header>
              <div class="card-header">
                <span>身体档案</span>
                <el-button type="primary" size="small" @click="saveProfile" :loading="saving">保存修改</el-button>
              </div>
            </template>
            
            <el-form :model="form" label-width="160px" size="default" v-loading="loading">
              <el-divider content-position="left">基本指标</el-divider>
              <el-row>
                <el-col :span="12">
                  <el-form-item label="年龄 (20-79岁)" required>
                    <el-input-number v-model="form.age" :min="20" :max="79" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="性别" required>
                    <el-radio-group v-model="form.gender">
                      <el-radio label="男">男</el-radio>
                      <el-radio label="女">女</el-radio>
                    </el-radio-group>
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-row>
                <el-col :span="12">
                  <el-form-item label="身高 (cm)">
                    <el-input-number v-model="form.height" :min="50" :max="250" :precision="1" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="体重 (kg)">
                    <el-input-number v-model="form.weight" :min="10" :max="250" :precision="1" />
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-row>
                <el-col :span="12">
                  <el-form-item label="BMI (kg/m²)">
                    <el-input-number v-model="calculatedBMI" :min="10" :max="50" :precision="1" disabled />
                    <span class="unit-text">自动计算</span>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="体脂率 (%)">
                    <el-input-number v-model="form.bodyFatRate" :min="0" :max="60" :precision="1" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-divider content-position="left">体能指标</el-divider>
              
              <el-row>
                <el-col :span="12">
                  <el-form-item label="肺活量 (ml)">
                    <el-input-number v-model="form.vitalCapacity" :min="0" :step="100" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="坐位体前屈 (cm)">
                    <el-input-number v-model="form.sitAndReach" :min="-30" :max="60" :precision="1" />
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-row>
                <el-col :span="12">
                  <el-form-item label="闭眼单脚站立 (s)">
                    <el-input-number v-model="form.singleLegStand" :min="0" :max="300" :precision="1" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="选择反应时间 (s)">
                    <el-input-number v-model="form.reactionTime" :min="0" :max="5" :precision="2" :step="0.01" />
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-row>
                <el-col :span="12">
                  <el-form-item label="握力 (kg)">
                    <el-input-number v-model="form.gripStrength" :min="0" :max="150" :precision="1" />
                  </el-form-item>
                </el-col>
              </el-row>

              <!-- 成年人特有指标 (20-59岁) -->
              <div v-if="form.age >= 20 && form.age <= 59">
                <el-divider content-position="left">成年人专项指标 (20-59岁)</el-divider>
                
                <el-form-item label="最大摄氧量相对值">
                  <el-input-number v-model="form.maxOxygenUptake" :min="0" :max="100" :precision="1" />
                  <span class="unit-text">ml/kg/min</span>
                </el-form-item>
                
                <el-form-item label="一分钟仰卧起坐 (次)">
                  <el-input-number v-model="form.sitUpsPerMinute" :min="0" :max="150" />
                </el-form-item>
                
                <el-form-item :label="form.gender === '男' ? '俯卧撑 (次)' : '跪卧撑 (次)'">
                  <el-input-number v-model="form.pushUps" :min="0" :max="150" />
                </el-form-item>
                
                <!-- 20-49岁特有指标 -->
                <el-form-item v-if="form.age <= 49" label="纵跳 (cm)">
                  <el-input-number v-model="form.verticalJump" :min="0" :max="200" :precision="1" />
                </el-form-item>
              </div>

              <!-- 老年人特有指标 (60-79岁) -->
              <div v-if="form.age >= 60 && form.age <= 79">
                <el-divider content-position="left">老年人专项指标 (60-79岁)</el-divider>
                
                <el-form-item label="2分钟原地高抬腿 (次)">
                  <el-input-number v-model="form.highKnees2min" :min="0" :max="500" />
                </el-form-item>
                
                <el-form-item label="30秒坐站 (次)">
                  <el-input-number v-model="form.sitToStand30s" :min="0" :max="100" />
                </el-form-item>
              </div>

              <el-divider content-position="left">其他信息</el-divider>
              
              <el-form-item label="运动偏好">
                <el-checkbox-group
                  v-model="exercisePreferencesSelected"
                  :max="2"
                  @change="handleExercisePreferencesChange"
                >
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
                  v-if="exercisePreferencesSelected.includes('其他')"
                  v-model="otherExercisePreference"
                  placeholder="请输入其他运动偏好"
                  class="other-input"
                />
              </el-form-item>
              
              <el-form-item label="是否使用器械">
                <el-radio-group v-model="form.usesEquipment">
                  <el-radio :label="true">是</el-radio>
                  <el-radio :label="false">否</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="运动风险等级">
                <el-select v-model="form.exerciseRiskLevel" placeholder="请选择">
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
            </el-form>
          </el-card>
        </el-col>
      </el-row>
      </div>
    </el-main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import NavBar from '../components/NavBar.vue'
import { API_ENDPOINTS, buildUrl } from '../api/config'

const router = useRouter()
const userInfo = ref(null)
const loading = ref(false)
const saving = ref(false)
const otherExercisePreference = ref('')
const exercisePreferencesSelected = ref([])

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

const form = reactive({
  age: null,
  gender: '',
  height: null,
  weight: null,
  bmi: null,
  bodyFatRate: null,
  vitalCapacity: null,
  sitAndReach: null,
  singleLegStand: null,
  reactionTime: null,
  gripStrength: null,
  maxOxygenUptake: null,
  sitUpsPerMinute: null,
  pushUps: null,
  verticalJump: null,
  highKnees2min: null,
  sitToStand30s: null,
  usesEquipment: null,
  exerciseRiskLevel: '',
  diseases: []
})

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

onMounted(async () => {
  const storedUserInfo = localStorage.getItem('userInfo')
  if (storedUserInfo) {
    userInfo.value = JSON.parse(storedUserInfo)
    await fetchProfile()
  }
})

const saveProfile = async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  if (exercisePreferencesSelected.value.length === 0) {
    ElMessage.warning('请选择1-2项运动偏好')
    return
  }

  if (exercisePreferencesSelected.value.includes('其他') && !otherExercisePreference.value.trim()) {
    ElMessage.warning('请填写其他运动偏好内容')
    return
  }

  saving.value = true
  try {
    const payload = buildPayload()
    const response = await axios.post(buildUrl(API_ENDPOINTS.PROFILE.UPDATE), payload, {
      headers: { Authorization: token }
    })
    
    if (response.data.code === 200) {
      ElMessage.success('保存成功')
    } else {
      ElMessage.error(response.data.message || '保存失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

function parseExercisePreferences(value) {
  if (!value) {
    otherExercisePreference.value = ''
    return []
  }
  const listSource = Array.isArray(value) ? value : value.split(/[,，]/)
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

function parseDiseases(value) {
  if (!value) return []
  const listSource = Array.isArray(value) ? value : value.split(/[,，]/)
  return listSource.map((item) => String(item).trim()).filter((item) => item)
}

function sanitizeExercisePreferences(value) {
  const list = Array.isArray(value) ? value : []
  const filtered = list
    .map((item) => String(item).trim())
    .filter((item) => item && EXERCISE_PREFERENCE_SET.has(item))
  return Array.from(new Set(filtered)).slice(0, 2)
}

function handleExercisePreferencesChange(val) {
  const sanitized = sanitizeExercisePreferences(val)
  if (Array.isArray(val) && val.length > 2) {
    ElMessage.warning('最多选择2项运动偏好')
  }
  exercisePreferencesSelected.value = sanitized
}

function populateForm(data) {
  form.age = data.age ?? null
  form.gender = data.gender ?? ''
  form.height = data.height ?? null
  form.weight = data.weight ?? null
  form.bmi = data.bmi ?? null
  form.bodyFatRate = data.bodyFatRate ?? null
  form.vitalCapacity = data.vitalCapacity ?? null
  form.sitAndReach = data.sitAndReach ?? null
  form.singleLegStand = data.singleLegStand ?? null
  form.reactionTime = data.reactionTime ?? null
  form.gripStrength = data.gripStrength ?? null
  form.maxOxygenUptake = data.maxOxygenUptake ?? null
  form.sitUpsPerMinute = data.sitUpsPerMinute ?? null
  form.pushUps = data.pushUps ?? null
  form.verticalJump = data.verticalJump ?? null
  form.highKnees2min = data.highKnees2min ?? null
  form.sitToStand30s = data.sitToStand30s ?? null
  exercisePreferencesSelected.value = sanitizeExercisePreferences(parseExercisePreferences(data.exercisePreferences))
  form.usesEquipment = data.usesEquipment === null || data.usesEquipment === undefined ? null : Boolean(data.usesEquipment)
  form.exerciseRiskLevel = data.exerciseRiskLevel ?? ''
  form.diseases = parseDiseases(data.diseases)
}

function buildPayload() {
  const selected = Array.isArray(exercisePreferencesSelected.value) ? exercisePreferencesSelected.value : []
  const exercisePreferences = selected.map((pref) => {
    if (pref === '其他') {
      return otherExercisePreference.value ? `其他(${otherExercisePreference.value.trim()})` : '其他'
    }
    return pref
  }).join(',')

  return {
    age: form.age,
    gender: form.gender,
    height: form.height,
    weight: form.weight,
    bmi: form.bmi,
    bodyFatRate: form.bodyFatRate,
    vitalCapacity: form.vitalCapacity,
    sitAndReach: form.sitAndReach,
    singleLegStand: form.singleLegStand,
    reactionTime: form.reactionTime,
    gripStrength: form.gripStrength,
    maxOxygenUptake: form.maxOxygenUptake,
    sitUpsPerMinute: form.sitUpsPerMinute,
    pushUps: form.pushUps,
    verticalJump: form.verticalJump,
    highKnees2min: form.highKnees2min,
    sitToStand30s: form.sitToStand30s,
    exercisePreferences,
    usesEquipment: form.usesEquipment,
    exerciseRiskLevel: form.exerciseRiskLevel,
    diseases: form.diseases.join(',')
  }
}

const fetchProfile = async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    router.push('/login')
    return
  }

  loading.value = true
  try {
    const response = await axios.get(buildUrl(API_ENDPOINTS.PROFILE.GET), {
      headers: { Authorization: token }
    })
    
    if (response.data.code === 200 && response.data.data) {
      populateForm(response.data.data)
    }
  } catch (error) {
    console.error('Failed to fetch profile', error)
    if (error.response && error.response.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      router.push('/login')
    }
  } finally {
    loading.value = false
  }
}
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
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.box-card {
  margin-bottom: 20px;
}
.unit-text {
  margin-left: 10px;
    color: #909399;
}
.other-input {
  margin-top: 10px;
  max-width: 240px;
}
</style>
