<template>
  <el-card class="budget-card">
    <template #header>
      <div class="budget-header">
        <span>预算总览</span>
        <span class="total">¥{{ budget.total }}</span>
      </div>
    </template>
    <div class="chart-container">
      <v-chart :option="chartOption" autoresize />
    </div>
    <el-descriptions :column="2" border size="small">
      <el-descriptions-item label="交通费用">¥{{ budget.transport }}</el-descriptions-item>
      <el-descriptions-item label="住宿费用">¥{{ budget.accommodation }}</el-descriptions-item>
      <el-descriptions-item label="门票费用">¥{{ budget.tickets }}</el-descriptions-item>
      <el-descriptions-item label="餐饮费用">¥{{ budget.meals }}</el-descriptions-item>
    </el-descriptions>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([PieChart, TitleComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const props = defineProps({
  budget: {
    type: Object,
    default: () => ({ transport: 0, accommodation: 0, tickets: 0, meals: 0, total: 0 }),
  },
})

const chartOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
  legend: { bottom: 0 },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    label: { formatter: '{b}\n¥{c}' },
    data: [
      { value: props.budget.transport, name: '交通', itemStyle: { color: '#409eff' } },
      { value: props.budget.accommodation, name: '住宿', itemStyle: { color: '#67c23a' } },
      { value: props.budget.tickets, name: '门票', itemStyle: { color: '#e6a23c' } },
      { value: props.budget.meals, name: '餐饮', itemStyle: { color: '#f56c6c' } },
    ],
  }],
}))
</script>

<style scoped>
.budget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.total {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}
.chart-container {
  height: 300px;
}
</style>
