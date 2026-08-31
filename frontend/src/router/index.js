import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('../views/Dashboard.vue') },
  { path: '/brands', component: () => import('../views/BrandAnalysis.vue') },
  { path: '/price', component: () => import('../views/PriceAnalysis.vue') },
  { path: '/energy', component: () => import('../views/EnergyAnalysis.vue') },
  { path: '/ratings', component: () => import('../views/RatingAnalysis.vue') },
  { path: '/trends', component: () => import('../views/TrendAnalysis.vue') },
  { path: '/cities', component: () => import('../views/CityAnalysis.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
