<template>
  <div>
    <div class="filter-bar">
      <span>年份：</span>
      <el-select v-model="year" @change="fetchData" style="width: 120px">
        <el-option v-for="y in years" :key="y" :label="y + '年'" :value="y" />
      </el-select>
    </div>

    <div class="kpi-cards">
      <KPICard :value="overview.total_sales" label="总销量(辆)" />
      <KPICard :value="overview.brand_count" label="品牌数量" />
      <KPICard :value="overview.model_count" label="车型数量" />
      <KPICard :value="overview.new_energy_penetration" label="新能源渗透率" suffix="%" :decimal="1" />
      <KPICard :value="overview.avg_price" label="平均售价(万)" suffix="" :decimal="1" />
      <KPICard :value="overview.avg_rating" label="平均评分" suffix="" :decimal="1" />
    </div>

    <div class="chart-row">
      <ChartCard title="品牌销量 TOP 10" :option="brandChartOption" />
      <ChartCard title="新能源 vs 传统燃油" :option="energyPieOption" />
    </div>

    <div class="chart-row">
      <ChartCard title="价格区间销量分布" :option="priceChartOption" />
      <ChartCard title="品牌类别销量对比" :option="categoryChartOption" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getOverview, getBrandRanking, getEnergyTypes, getBrandCategories } from '../api'
import { getMonthlySales } from '../api'
import ChartCard from '../components/ChartCard.vue'
import KPICard from '../components/KPICard.vue'

const year = ref(2024)
const years = [2024, 2025, 2026]
const overview = ref({ total_sales: 0, brand_count: 0, model_count: 0, new_energy_penetration: 0, avg_price: 0, avg_rating: 0 })

const brandChartOption = ref({})
const energyPieOption = ref({})
const priceChartOption = ref({})
const categoryChartOption = ref({})

async function fetchData() {
  const [ov, brands, energy, cats] = await Promise.all([
    getOverview(year.value),
    getBrandRanking(year.value),
    getEnergyTypes(year.value),
    getBrandCategories(year.value),
  ])
  overview.value = ov.data

  const top10 = brands.data.slice(0, 10)
  brandChartOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: top10.map(b => b.brand_name).reverse() },
    series: [{ type: 'bar', data: top10.map(b => b.total_sales).reverse(), itemStyle: { color: '#1890ff' } }],
  }

  energyPieOption.value = {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie', radius: ['40%', '70%'],
      data: energy.data.map(e => ({ name: e.energy_type, value: e.total_sales })),
      label: { formatter: '{b}: {d}%' },
    }],
  }

  priceChartOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['5万以下', '5-10万', '10-15万', '15-20万', '20-30万', '30-50万', '50-100万', '100万以上'] },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: [0, 0, 0, 0, 0, 0, 0, 0], itemStyle: { color: '#722ed1' } }],
  }

  categoryChartOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: cats.data.map(c => c.brand_category) },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: cats.data.map(c => c.total_sales), itemStyle: { color: '#13c2c2' } }],
  }
}

onMounted(fetchData)
</script>
