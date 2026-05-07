<template>
  <div class="home">
    <div class="header">
      <h1>AutoJourney</h1>
      <p>输入你的旅行信息，AI 为你规划完美行程</p>
    </div>

    <InputForm :loading="loading" @submit="handleGenerate" />

    <div v-if="result" class="result-section">
      <el-alert :title="result.overview" type="success" show-icon :closable="false" />

      <el-row :gutter="20" class="content-row">
        <el-col :span="12">
          <div class="cards-area">
            <DailyCard
              v-for="plan in result.daily_plans"
              :key="plan.day"
              :plan="plan"
              :is-active="activeDay === plan.day"
              @click="activeDay = plan.day"
            />
          </div>
        </el-col>
        <el-col :span="12">
          <RouteMap
            :transport="result.transport"
            :daily-plans="result.daily_plans"
            :active-day="activeDay"
          />
        </el-col>
      </el-row>

      <BudgetChart :budget="result.budget_breakdown" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import InputForm from '../components/InputForm.vue'
import DailyCard from '../components/DailyCard.vue'
import RouteMap from '../components/RouteMap.vue'
import BudgetChart from '../components/BudgetChart.vue'
import { generatePlan } from '../api/index.js'

const loading = ref(false)
const result = ref(null)
const activeDay = ref(1)

async function handleGenerate(formData) {
  loading.value = true
  result.value = null
  try {
    result.value = await generatePlan(formData)
    activeDay.value = 1
  } catch (err) {
    const msg = err.response?.data?.detail || '生成失败，请稍后重试'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}
.header {
  text-align: center;
  margin-bottom: 32px;
}
.header h1 {
  font-size: 36px;
  color: #303133;
  margin-bottom: 8px;
}
.header p {
  color: #909399;
  font-size: 16px;
}
.result-section {
  margin-top: 32px;
}
.content-row {
  margin-top: 20px;
}
.cards-area {
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 8px;
}
</style>
