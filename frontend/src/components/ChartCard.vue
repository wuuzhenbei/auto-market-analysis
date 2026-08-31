<template>
  <div class="chart-card">
    <h3>{{ title }}</h3>
    <div ref="chartRef" :style="{ height: height + 'px' }"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  title: { type: String, default: '' },
  option: { type: Object, required: true },
  height: { type: Number, default: 400 },
})

const chartRef = ref(null)
let chart = null

onMounted(() => {
  chart = echarts.init(chartRef.value)
  chart.setOption(props.option)
  window.addEventListener('resize', () => chart?.resize())
})

watch(() => props.option, (newOption) => {
  if (chart) {
    chart.setOption(newOption, true)
  }
}, { deep: true })
</script>
