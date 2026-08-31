<template>
  <div class="kpi-card">
    <div class="value">{{ formattedValue }}</div>
    <div class="label">{{ label }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: { type: [Number, String], default: 0 },
  label: { type: String, default: '' },
  suffix: { type: String, default: '' },
  decimal: { type: Number, default: 0 },
})

const formattedValue = computed(() => {
  if (typeof props.value === 'string') return props.value
  const v = Number(props.value)
  if (v >= 10000) {
    return (v / 10000).toFixed(1) + '万' + props.suffix
  }
  return props.decimal > 0 ? v.toFixed(props.decimal) + props.suffix : v.toLocaleString() + props.suffix
})
</script>
