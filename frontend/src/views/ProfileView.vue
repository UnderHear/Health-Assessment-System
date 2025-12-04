<template>
  <div class="page-container">
    <NavBar />
    <el-main>
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
                    <el-input-number v-model="form.weight" :min="20" :max="200" :precision="1" />
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-row>
                <el-col :span="12">
                  <el-form-item label="BMI (kg/m²)">
                    <el-input-number v-model="calculatedBMI" :min="10" :max="50" :precision="1" disabled />
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
                    <el-input-number v-model="form.sitAndReach" :min="-30" :max="50" :precision="1" />
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-row>
                <el-col :span="12">
                  <el-form-item label="闭眼单脚站立 (s)">
                    <el-input-number v-model="form.singleLegStand" :min="0" :max="300" />
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
                    <el-input-number v-model="form.gripStrength" :min="0" :max="100" :precision="1" />
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
                <el-checkbox-group v-model="exercisePreferencesList" :max="2">
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
              
              <el-form-item label="疾病史">
                <el-input v-model="form.diseases" type="textarea" rows="2" placeholder="如有疾病史请填写，多个疾病用逗号分隔" />
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
      </el-row>
    </el-main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import NavBar from '../components/NavBar.vue'

const userInfo = ref(null)
const loading = ref(false)
const saving = ref(false)
const API_BASE = 'http://localhost:8080/api'

const form = reactive({
  age: 30,
  gender: '男',
  height: 170,
  weight: 65,
  bmi: 22.5,
  bodyFatRate: 18,
  vitalCapacity: 3500,
  sitAndReach: 10,
  singleLegStand: 30,
  reactionTime: 0.4,
  gripStrength: 40,
  maxOxygenUptake: null,
  sitUpsPerMinute: null,
  pushUps: null,
  verticalJump: null,
  highKnees2min: null,
  sitToStand30s: null,
  exercisePreferences: '',
  usesEquipment: false,
  exerciseRiskLevel: '低',
  diseases: ''
})

const calculatedBMI = computed(() => {
  if (form.height && form.weight) {
    const heightInMeters = form.height / 100
    return Number((form.weight / (heightInMeters * heightInMeters)).toFixed(1))
  }
  return 0
})

// Watch for BMI changes to update form.bmi
watch(calculatedBMI, (newVal) => {
  form.bmi = newVal
})

const exercisePreferencesList = computed({
  get: () => form.exercisePreferences ? form.exercisePreferences.split(',') : [],
  set: (val) => {
    form.exercisePreferences = val.join(',')
  }
})

onMounted(async () => {
  const storedUserInfo = localStorage.getItem('userInfo')
  if (storedUserInfo) {
    userInfo.value = JSON.parse(storedUserInfo)
    await fetchProfile()
  }
})

const fetchProfile = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`${API_BASE}/profile`, {
      headers: { Authorization: token }
    })
    
    if (response.data.code === 200 && response.data.data) {
      Object.assign(form, response.data.data)
    }
  } catch (error) {
    console.error('Failed to fetch profile', error)
  } finally {
    loading.value = false
  }
}

const saveProfile = async () => {
  saving.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.post(`${API_BASE}/profile`, form, {
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
</script>

<style scoped>
.page-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
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
</style>
