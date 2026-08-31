import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// 市场总览
export const getOverview = (year) => api.get('/overview', { params: { year } })
export const getInsights = () => api.get('/overview/insights')

// 品牌分析
export const getBrandRanking = (year) => api.get('/brands/ranking', { params: { year } })
export const getBrandCategories = (year) => api.get('/brands/categories', { params: { year } })
export const getBrandCountries = (year) => api.get('/brands/countries', { params: { year } })
export const getBrandModels = (name, year, top_n) => api.get(`/brands/${name}/models`, { params: { year, top_n } })
export const getBrandRatings = (name) => api.get(`/brands/${name}/ratings`)

// 车型分析
export const getModelRanking = (year, top_n) => api.get('/models/ranking', { params: { year, top_n } })
export const getModelDetail = (name) => api.get(`/models/detail/${name}`)
export const searchModels = (q) => api.get('/models/search', { params: { q } })

// 销量分析
export const getMonthlySales = (start, end) => api.get('/sales/monthly', { params: { start_year: start, end_year: end } })
export const getMonthlyByEnergy = (start, end) => api.get('/sales/monthly/by-energy', { params: { start_year: start, end_year: end } })
export const getYoYGrowth = (year) => api.get('/sales/yoy', { params: { year } })
export const getCitySales = (year, top_n) => api.get('/sales/cities', { params: { year, top_n } })
export const getRegionSales = (year) => api.get('/sales/regions', { params: { year } })
export const getBrandMonthly = (name, start, end) => api.get(`/sales/brand-monthly/${name}`, { params: { start_year: start, end_year: end } })

// 新能源分析
export const getEnergyTypes = (year) => api.get('/energy/types', { params: { year } })
export const getPenetration = (start, end) => api.get('/energy/penetration', { params: { start_year: start, end_year: end } })
export const getNEBrands = (year) => api.get('/energy/brands', { params: { year } })
export const getNEModels = (year, top_n) => api.get('/energy/models', { params: { year, top_n } })
export const getRangeAnalysis = () => api.get('/energy/range')
export const getEvVsPhev = (year) => api.get('/energy/ev-vs-phev', { params: { year } })

// 口碑分析
export const getRatingDistribution = () => api.get('/ratings/distribution')
export const getBrandRatingRanking = () => api.get('/ratings/brands')
export const getModelRatingRanking = (top_n) => api.get('/ratings/models', { params: { top_n } })
export const getBrandRadarData = (name) => api.get(`/ratings/radar/${name}`)
export const getDimensionAnalysis = () => api.get('/ratings/dimension-analysis')

// 数据导入
export const startDongchediImport = () => api.post('/import/dongchedi')
export const getImportStatus = (taskId) => api.get(`/import/status/${taskId}`)

export default api
