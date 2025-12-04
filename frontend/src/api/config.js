// API 基础配置
export const API_BASE_URL = 'http://localhost:8080/api'

// API 端点配置
export const API_ENDPOINTS = {
  // 认证相关
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register'
  },
  
  // 用户档案相关
  PROFILE: {
    GET: '/profile',
    UPDATE: '/profile',
    ANALYZE: '/profile/analyze',
    HISTORY: '/profile/history',
    GET_BY_ID: (id) => `/profile/${id}`
  },
  
  // 训练计划相关
  TRAINING: {
    GET_PLANS: '/training/plans',
    GET_ACTIVE: '/training/active-plan',
    CREATE: '/training/create',
    CHECK_IN: '/training/check-in',
    GET_CHECK_INS: (planId) => `/training/check-ins/${planId}`,
    GET_WEEK_CHECK_INS: (planId, weekNumber) => `/training/check-ins/${planId}/week/${weekNumber}`,
    PAUSE: (planId) => `/training/pause/${planId}`,
    RESUME: (planId) => `/training/resume/${planId}`,
    COMPLETE: (planId) => `/training/complete/${planId}`,
    DELETE: (planId) => `/training/${planId}`
  }
}

// 构建完整URL的辅助函数
export const buildUrl = (endpoint) => {
  return `${API_BASE_URL}${endpoint}`
}
