<template>
  <div>
    <div class="filter-bar">
      <span>年份：</span>
      <el-select v-model="year" @change="fetchData" style="width: 120px">
        <el-option v-for="y in years" :key="y" :label="y + '年'" :value="y" />
      </el-select>
    </div>

    <div class="chart-row">
      <ChartCard title="城市销量 TOP 20" :option="cityOption" :height="500" />
      <ChartCard title="区域销量分布" :option="regionPieOption" />
    </div>

    <div class="chart-row">
      <ChartCard title="区域销量对比" :option="regionBarOption" />
      <ChartCard title="省份销量 TOP 20" :option="provinceOption" :height="500" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getCitySales, getRegionSales } from '../api'
import ChartCard from '../components/ChartCard.vue'

const year = ref(2024)
const years = [2024, 2025, 2026]
const cityOption = ref({})
const regionPieOption = ref({})
const regionBarOption = ref({})
const provinceOption = ref({})

async function fetchData() {
  const [cities, regions] = await Promise.all([
    getCitySales(year.value, 30),
    getRegionSales(year.value),
  ])

  const top20 = cities.data.slice(0, 20)
  cityOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: top20.map(c => c.city).reverse() },
    series: [{
      type: 'bar',
      data: top20.map(c => c.sales_volume).reverse(),
      itemStyle: { color: '#1890ff' },
    }],
  }

  regionPieOption.value = {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie', radius: ['40%', '70%'],
      data: regions.data.map(r => ({ name: r.region, value: r.sales_volume })),
    }],
  }

  regionBarOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: regions.data.map(r => r.region) },
    yAxis: { type: 'value' },
    series: [{
      type: 'bar',
      data: regions.data.map(r => r.sales_volume),
      itemStyle: { color: '#52c41a' },
    }],
  }

  // 省份聚合
  const provinceMap = {}
  cities.data.forEach(c => {
    if (!provinceMap[c.province]) provinceMap[c.province] = 0
    provinceMap[c.province] += c.sales_volume
  })
  const provinces = Object.entries(provinceMap).sort((a, b) => b[1] - a[1]).slice(0, 20)

  provinceOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: provinces.map(p => p[0]).reverse() },
    series: [{
      type: 'bar',
      data: provinces.map(p => p[1]).reverse(),
      itemStyle: { color: '#722ed1' },
    }],
  }
}

onMounted(fetchData)
</script>
