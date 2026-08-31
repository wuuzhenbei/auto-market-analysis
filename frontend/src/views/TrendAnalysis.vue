<template>
  <div>
    <div class="filter-bar">
      <span>起始年份：</span>
      <el-select v-model="startYear" @change="fetchData" style="width: 120px">
        <el-option v-for="y in years" :key="y" :label="y + '年'" :value="y" />
      </el-select>
      <span>结束年份：</span>
      <el-select v-model="endYear" @change="fetchData" style="width: 120px">
        <el-option v-for="y in years" :key="y" :label="y + '年'" :value="y" />
      </el-select>
    </div>

    <ChartCard title="月度销量趋势" :option="monthlyOption" />

    <div class="chart-row">
      <ChartCard title="按能源类型月度趋势" :option="energyMonthlyOption" />
      <ChartCard title="新能源渗透率趋势" :option="penetrationOption" />
    </div>

    <ChartCard title="同比增长分析" :option="yoyOption" :height="500" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMonthlySales, getMonthlyByEnergy, getPenetration, getYoYGrowth } from '../api'
import ChartCard from '../components/ChartCard.vue'

const startYear = ref(2024)
const endYear = ref(2026)
const years = [2024, 2025, 2026]
const monthlyOption = ref({})
const energyMonthlyOption = ref({})
const penetrationOption = ref({})
const yoyOption = ref({})

async function fetchData() {
  const [monthly, energy, pen, yoy] = await Promise.all([
    getMonthlySales(startYear.value, endYear.value),
    getMonthlyByEnergy(startYear.value, endYear.value),
    getPenetration(startYear.value, endYear.value),
    getYoYGrowth(endYear.value),
  ])

  monthlyOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: monthly.data.map(m => m.year_month), axisLabel: { rotate: 45 } },
    yAxis: { type: 'value' },
    series: [{
      type: 'line', data: monthly.data.map(m => m.total_sales),
      smooth: true, itemStyle: { color: '#1890ff' },
      areaStyle: { color: 'rgba(24, 144, 255, 0.2)' },
    }],
  }

  // 按能源类型分组
  const energyTypes = [...new Set(energy.data.map(e => e.energy_type))]
  const months = [...new Set(energy.data.map(e => e.year_month))]
  const colors = { '纯电动': '#00d4aa', '插电混动': '#ffd93d', '增程式': '#6c5ce7', '燃油': '#ff6b6b', '油电混动': '#a8e6cf' }

  energyMonthlyOption.value = {
    tooltip: { trigger: 'axis' },
    legend: { data: energyTypes },
    xAxis: { type: 'category', data: months, axisLabel: { rotate: 45 } },
    yAxis: { type: 'value' },
    series: energyTypes.map(et => ({
      name: et, type: 'line', smooth: true,
      data: months.map(m => {
        const item = energy.data.find(e => e.year_month === m && e.energy_type === et)
        return item ? item.total_sales : 0
      }),
      itemStyle: { color: colors[et] || '#999' },
    })),
  }

  penetrationOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: pen.data.map(p => p.year_month), axisLabel: { rotate: 45 } },
    yAxis: { type: 'value', name: '渗透率(%)', max: 100 },
    series: [{
      type: 'line', data: pen.data.map(p => p.penetration_rate),
      smooth: true, itemStyle: { color: '#00d4aa' },
      areaStyle: { color: 'rgba(0, 212, 170, 0.2)' },
    }],
  }

  const top20 = yoy.data.slice(0, 20)
  yoyOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value', name: '同比增长(%)' },
    yAxis: { type: 'category', data: top20.map(b => b.brand_name).reverse() },
    series: [{
      type: 'bar',
      data: top20.map(b => b.yoy_growth).reverse(),
      itemStyle: {
        color: (params) => params.value >= 0 ? '#52c41a' : '#ff4d4f',
      },
    }],
  }
}

onMounted(fetchData)
</script>
