<template>
  <div>
    <div class="filter-bar">
      <span>年份：</span>
      <el-select v-model="year" @change="fetchData" style="width: 120px">
        <el-option v-for="y in years" :key="y" :label="y + '年'" :value="y" />
      </el-select>
    </div>

    <div class="chart-row">
      <ChartCard title="车型销量排名 TOP 20" :option="modelRankingOption" :height="500" />
      <ChartCard title="各能源类型平均价格" :option="energyPriceOption" />
    </div>

    <div class="chart-row">
      <ChartCard title="品牌类别平均价格" :option="categoryPriceOption" />
      <ChartCard title="各车身类型平均价格" :option="bodyPriceOption" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getModelRanking } from '../api'
import ChartCard from '../components/ChartCard.vue'

const year = ref(2024)
const years = [2024, 2025, 2026]
const modelRankingOption = ref({})
const energyPriceOption = ref({})
const categoryPriceOption = ref({})
const bodyPriceOption = ref({})

async function fetchData() {
  const models = await getModelRanking(year.value, 50)
  const data = models.data

  const top20 = data.slice(0, 20)
  modelRankingOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: top20.map(m => m.model_name).reverse() },
    series: [{
      type: 'bar',
      data: top20.map(m => m.total_sales).reverse(),
      itemStyle: { color: '#eb2f96' },
    }],
  }

  // 按能源类型分组
  const energyGroups = {}
  data.forEach(m => {
    if (!energyGroups[m.energy_type]) energyGroups[m.energy_type] = []
    energyGroups[m.energy_type].push((m.guide_price_min + m.guide_price_max) / 2)
  })
  energyPriceOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: Object.keys(energyGroups) },
    yAxis: { type: 'value', name: '均价(万元)' },
    series: [{
      type: 'bar',
      data: Object.entries(energyGroups).map(([k, v]) => (v.reduce((a, b) => a + b, 0) / v.length).toFixed(1)),
      itemStyle: { color: '#1890ff' },
    }],
  }

  // 按品牌类别分组
  const catGroups = {}
  data.forEach(m => {
    const cat = m.brand_category || '未知'
    if (!catGroups[cat]) catGroups[cat] = []
    catGroups[cat].push((m.guide_price_min + m.guide_price_max) / 2)
  })
  categoryPriceOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: Object.keys(catGroups) },
    yAxis: { type: 'value', name: '均价(万元)' },
    series: [{
      type: 'bar',
      data: Object.entries(catGroups).map(([k, v]) => (v.reduce((a, b) => a + b, 0) / v.length).toFixed(1)),
      itemStyle: { color: '#52c41a' },
    }],
  }

  // 按车身类型分组
  const bodyGroups = {}
  data.forEach(m => {
    if (!bodyGroups[m.body_type]) bodyGroups[m.body_type] = []
    bodyGroups[m.body_type].push((m.guide_price_min + m.guide_price_max) / 2)
  })
  bodyPriceOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: Object.keys(bodyGroups) },
    yAxis: { type: 'value', name: '均价(万元)' },
    series: [{
      type: 'bar',
      data: Object.entries(bodyGroups).map(([k, v]) => (v.reduce((a, b) => a + b, 0) / v.length).toFixed(1)),
      itemStyle: { color: '#722ed1' },
    }],
  }
}

onMounted(fetchData)
</script>
