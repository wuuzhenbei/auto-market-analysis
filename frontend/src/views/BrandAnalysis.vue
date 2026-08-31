<template>
  <div>
    <div class="filter-bar">
      <span>年份：</span>
      <el-select v-model="year" @change="fetchData" style="width: 120px">
        <el-option v-for="y in years" :key="y" :label="y + '年'" :value="y" />
      </el-select>
    </div>

    <div class="chart-row">
      <ChartCard title="品牌销量排名 TOP 20" :option="rankingOption" :height="500" />
      <ChartCard title="品牌类别销量占比" :option="categoryPieOption" />
    </div>

    <div class="chart-row">
      <ChartCard title="品牌国别分布" :option="countryOption" />
      <ChartCard title="品牌平均评分 TOP 15" :option="ratingOption" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getBrandRanking, getBrandCategories, getBrandCountries, getBrandRatingRanking } from '../api'
import ChartCard from '../components/ChartCard.vue'

const year = ref(2024)
const years = [2024, 2025, 2026]
const rankingOption = ref({})
const categoryPieOption = ref({})
const countryOption = ref({})
const ratingOption = ref({})

async function fetchData() {
  const [ranking, cats, countries, ratings] = await Promise.all([
    getBrandRanking(year.value),
    getBrandCategories(year.value),
    getBrandCountries(year.value),
    getBrandRatingRanking(),
  ])

  const top20 = ranking.data.slice(0, 20)
  rankingOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: top20.map(b => b.brand_name).reverse() },
    series: [{
      type: 'bar',
      data: top20.map(b => b.total_sales).reverse(),
      itemStyle: { color: '#1890ff' },
    }],
  }

  categoryPieOption.value = {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie', radius: ['40%', '70%'],
      data: cats.data.map(c => ({ name: c.brand_category, value: c.total_sales })),
    }],
  }

  countryOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: countries.data.map(c => c.brand_country) },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: countries.data.map(c => c.total_sales), itemStyle: { color: '#52c41a' } }],
  }

  const top15 = ratings.data.slice(0, 15)
  ratingOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value', min: 3.5, max: 5 },
    yAxis: { type: 'category', data: top15.map(b => b.brand_name).reverse() },
    series: [{ type: 'bar', data: top15.map(b => b.overall_score).reverse(), itemStyle: { color: '#faad14' } }],
  }
}

onMounted(fetchData)
</script>
