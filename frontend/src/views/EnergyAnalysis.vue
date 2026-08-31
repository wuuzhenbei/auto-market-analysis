<template>
  <div>
    <div class="filter-bar">
      <span>年份：</span>
      <el-select v-model="year" @change="fetchData" style="width: 120px">
        <el-option v-for="y in years" :key="y" :label="y + '年'" :value="y" />
      </el-select>
    </div>

    <div class="kpi-cards">
      <KPICard :value="neData.total" label="新能源总销量" />
      <KPICard :value="neData.penetration" label="渗透率" suffix="%" :decimal="1" />
    </div>

    <div class="chart-row">
      <ChartCard title="新能源类型销量" :option="typePieOption" />
      <ChartCard title="新能源品牌排名 TOP 15" :option="brandOption" :height="500" />
    </div>

    <div class="chart-row">
      <ChartCard title="渗透率趋势" :option="penetrationOption" />
      <ChartCard title="续航分布" :option="rangeOption" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getEnergyTypes, getNEBrands, getPenetration, getRangeAnalysis } from '../api'
import ChartCard from '../components/ChartCard.vue'
import KPICard from '../components/KPICard.vue'

const year = ref(2024)
const years = [2024, 2025, 2026]
const neData = ref({ total: 0, penetration: 0 })
const typePieOption = ref({})
const brandOption = ref({})
const penetrationOption = ref({})
const rangeOption = ref({})

async function fetchData() {
  const [types, brands, pen, range] = await Promise.all([
    getEnergyTypes(year.value),
    getNEBrands(year.value),
    getPenetration(2024, 2026),
    getRangeAnalysis(),
  ])

  const neTotal = types.data.filter(t => ['纯电动', '插电混动', '增程式'].includes(t.energy_type)).reduce((s, t) => s + t.total_sales, 0)
  const allTotal = types.data.reduce((s, t) => s + t.total_sales, 0)
  neData.value = { total: neTotal, penetration: allTotal > 0 ? (neTotal / allTotal * 100).toFixed(1) : 0 }

  typePieOption.value = {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie', radius: ['40%', '70%'],
      data: types.data.map(t => ({ name: t.energy_type, value: t.total_sales })),
    }],
  }

  const top15 = brands.data.slice(0, 15)
  brandOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: top15.map(b => b.brand_name).reverse() },
    series: [{ type: 'bar', data: top15.map(b => b.total_sales).reverse(), itemStyle: { color: '#13c2c2' } }],
  }

  penetrationOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: pen.data.map(p => p.year_month) },
    yAxis: { type: 'value', name: '渗透率(%)', max: 100 },
    series: [{
      type: 'line', data: pen.data.map(p => p.penetration_rate),
      smooth: true, itemStyle: { color: '#00d4aa' },
      areaStyle: { color: 'rgba(0, 212, 170, 0.2)' },
    }],
  }

  rangeOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: range.data.map(r => r.range_group) },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: range.data.map(r => r.model_count), itemStyle: { color: '#faad14' } }],
  }
}

onMounted(fetchData)
</script>
