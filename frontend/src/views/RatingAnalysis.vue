<template>
  <div>
    <div class="chart-row">
      <ChartCard title="评分分布" :option="distOption" />
      <ChartCard title="各维度平均评分" :option="dimOption" />
    </div>

    <div class="chart-row">
      <ChartCard title="品牌平均评分 TOP 15" :option="brandOption" :height="500" />
      <ChartCard title="车型综合评分 TOP 20" :option="modelOption" :height="500" />
    </div>

    <div class="chart-card">
      <h3>品牌雷达图对比</h3>
      <div style="margin-bottom: 16px">
        <el-select v-model="selectedBrands" multiple placeholder="选择品牌（最多5个）" style="width: 400px" :max="5">
          <el-option v-for="b in brandList" :key="b" :label="b" :value="b" />
        </el-select>
        <el-button @change="fetchRadar" style="margin-left: 8px">更新</el-button>
      </div>
      <div ref="radarRef" style="height: 500px"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getRatingDistribution, getBrandRatingRanking, getModelRatingRanking, getBrandRadarData } from '../api'
import ChartCard from '../components/ChartCard.vue'

const distOption = ref({})
const dimOption = ref({})
const brandOption = ref({})
const modelOption = ref({})
const selectedBrands = ref(['比亚迪', '大众', '丰田'])
const brandList = ref([])
const radarRef = ref(null)

async function fetchData() {
  const [dist, brands, models] = await Promise.all([
    getRatingDistribution(),
    getBrandRatingRanking(),
    getModelRatingRanking(20),
  ])

  distOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: dist.data.map(d => d.rating_range) },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: dist.data.map(d => d.model_count), itemStyle: { color: '#1890ff' } }],
  }

  const dims = ['外观', '内饰', '动力', '空间', '油耗', '操控', '舒适性', '性价比']
  const dimScores = [
    brands.data.reduce((s, b) => s + b.appearance_score, 0) / brands.data.length,
    brands.data.reduce((s, b) => s + b.interior_score, 0) / brands.data.length,
    brands.data.reduce((s, b) => s + b.power_score, 0) / brands.data.length,
    brands.data.reduce((s, b) => s + b.space_score, 0) / brands.data.length,
    brands.data.reduce((s, b) => s + b.fuel_score, 0) / brands.data.length,
    brands.data.reduce((s, b) => s + b.handling_score, 0) / brands.data.length,
    brands.data.reduce((s, b) => s + b.comfort_score, 0) / brands.data.length,
    brands.data.reduce((s, b) => s + b.value_score, 0) / brands.data.length,
  ]
  dimOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: dims },
    yAxis: { type: 'value', min: 3.5, max: 5 },
    series: [{ type: 'bar', data: dimScores.map(s => s.toFixed(2)), itemStyle: { color: '#faad14' } }],
  }

  const top15 = brands.data.slice(0, 15)
  brandOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value', min: 3.5, max: 5 },
    yAxis: { type: 'category', data: top15.map(b => b.brand_name).reverse() },
    series: [{ type: 'bar', data: top15.map(b => b.overall_score).reverse(), itemStyle: { color: '#52c41a' } }],
  }

  brandList.value = brands.data.map(b => b.brand_name)

  const top20 = models.data.slice(0, 20)
  modelOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value', min: 3.5, max: 5 },
    yAxis: { type: 'category', data: top20.map(m => m.model_name).reverse() },
    series: [{ type: 'bar', data: top20.map(m => m.overall_score).reverse(), itemStyle: { color: '#eb2f96' } }],
  }
}

async function fetchRadar() {
  if (!radarRef.value || selectedBrands.value.length === 0) return
  const chart = echarts.init(radarRef.value)
  const colors = ['#1890ff', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
  const dims = ['外观', '内饰', '动力', '空间', '油耗', '操控', '舒适性', '性价比']

  const series = []
  for (let i = 0; i < selectedBrands.value.length; i++) {
    const res = await getBrandRadarData(selectedBrands.value[i])
    const d = res.data[0]
    series.push({
      name: selectedBrands.value[i],
      type: 'radar',
      data: [{
        value: [d.appearance, d.interior, d.power, d.space, d.fuel, d.handling, d.comfort, d.value],
        areaStyle: { opacity: 0.2 },
      }],
      lineStyle: { color: colors[i] },
      itemStyle: { color: colors[i] },
    })
  }

  chart.setOption({
    tooltip: {},
    legend: { data: selectedBrands.value },
    radar: { indicator: dims.map(d => ({ name: d, max: 5, min: 3 })) },
    series,
  })
}

onMounted(() => {
  fetchData().then(fetchRadar)
})
</script>
