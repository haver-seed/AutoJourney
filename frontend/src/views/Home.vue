<template>
  <div class="home">
    <!-- Hero -->
    <header class="hero">
      <h1 class="hero-title">AutoJourney</h1>
      <p class="hero-sub">多城市火车票智能规划。输入出发地与目的地，一键查询最优车票方案。</p>
    </header>

    <InputForm :loading="loading" @submit="handleQuery" />

    <!-- 进度条 -->
    <transition name="fade-up">
      <div v-if="loading" class="progress-section">
        <div class="progress-bar-track">
          <div class="progress-bar-fill" :style="{ width: progress.percent + '%' }" />
        </div>
        <div class="progress-info">
          <span class="progress-message">{{ progress.message }}</span>
          <span class="progress-percent">{{ progress.percent }}%</span>
        </div>
      </div>
    </transition>

    <!-- 结果区域 -->
    <transition name="fade-up">
      <div v-if="result" class="result-section">
        <!-- 汇总 -->
        <div class="summary-bar">
          <div class="summary-item">
            <span class="summary-label">总行程</span>
            <span class="summary-value">{{ result.total_days }} 天</span>
          </div>
          <div class="summary-divider" />
          <div class="summary-item">
            <span class="summary-label">总票价</span>
            <span class="summary-value">¥{{ result.total_cost.toFixed(0) }}</span>
          </div>
          <div class="summary-divider" />
          <div class="summary-item">
            <span class="summary-label">共 {{ result.segments.length }} 段</span>
          </div>
        </div>

        <TransportInfo :segments="result.segments" />
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import InputForm from '../components/InputForm.vue'
import TransportInfo from '../components/TransportInfo.vue'
import { queryTickets } from '../api/index.js'

const loading = ref(false)
const result = ref(null)
const progress = reactive({ percent: 0, message: '', stage: '' })

async function handleQuery(formData) {
  loading.value = true
  result.value = null
  progress.percent = 0
  progress.message = '准备中...'
  progress.stage = ''

  try {
    result.value = await queryTickets(formData, (p) => {
      progress.percent = p.percent
      progress.message = p.message
      progress.stage = p.stage
    })
  } catch (err) {
    ElMessage.error(err.message || '查询失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px 80px;
}

/* ---- Hero ---- */
.hero {
  text-align: center;
  padding: 72px 20px 56px;
}
.hero-title {
  font-size: 56px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 12px;
  letter-spacing: -0.28px;
  line-height: 1.07;
}
.hero-sub {
  color: #7a7a7a;
  font-size: 21px;
  font-weight: 400;
  margin: 0;
  letter-spacing: 0.231px;
  line-height: 1.19;
}

/* ---- Progress ---- */
.progress-section {
  max-width: 640px;
  margin: 32px auto 0;
}
.progress-bar-track {
  height: 4px;
  background: #e8e8ed;
  border-radius: 2px;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  background: #1d1d1f;
  border-radius: 2px;
  transition: width 0.4s ease;
}
.progress-info {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 14px;
  color: #7a7a7a;
}
.progress-percent {
  font-weight: 600;
  color: #1d1d1f;
}

/* ---- Summary ---- */
.summary-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 32px;
  background: #f5f5f7;
  border-radius: 14px;
  padding: 20px 28px;
  margin-top: 32px;
}
.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.summary-label {
  font-size: 13px;
  color: #86868b;
}
.summary-value {
  font-size: 28px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.28px;
  font-variant-numeric: tabular-nums;
}
.summary-divider {
  width: 1px;
  height: 40px;
  background: #d2d2d7;
}

/* ---- Fade-up ---- */
.fade-up-enter-active {
  transition: all 0.4s ease;
}
.fade-up-enter-from {
  opacity: 0;
  transform: translateY(16px);
}
</style>
