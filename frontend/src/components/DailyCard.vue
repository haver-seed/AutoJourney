<template>
  <el-card class="daily-card" :class="{ active: isActive }" @click="$emit('click')">
    <template #header>
      <div class="card-header">
        <span class="day-badge">Day {{ plan.day }}</span>
        <span class="city">{{ plan.city }}</span>
        <el-tag size="small" type="info">{{ plan.theme }}</el-tag>
      </div>
    </template>

    <div class="timeline">
      <div v-for="item in plan.schedule" :key="item.time" class="timeline-item">
        <div class="time">{{ item.time }}</div>
        <div class="dot" />
        <div class="content">
          <div class="activity">{{ item.activity }}</div>
          <div class="meta">
            <span>{{ item.duration }}</span>
            <span v-if="item.cost > 0" class="cost">¥{{ item.cost }}</span>
            <span v-else class="cost free">免费</span>
          </div>
        </div>
      </div>
    </div>

    <el-divider />
    <div class="summary">
      <span>住宿：{{ plan.accommodation.name }} ¥{{ plan.accommodation.cost }}</span>
      <span>餐饮：¥{{ plan.meals_cost }}</span>
      <span class="day-total">当日合计：¥{{ plan.day_total }}</span>
    </div>
  </el-card>
</template>

<script setup>
defineProps({
  plan: { type: Object, required: true },
  isActive: { type: Boolean, default: false },
})
defineEmits(['click'])
</script>

<style scoped>
.daily-card {
  cursor: pointer;
  transition: box-shadow 0.2s;
  margin-bottom: 16px;
}
.daily-card:hover,
.daily-card.active {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}
.day-badge {
  background: #409eff;
  color: white;
  padding: 2px 10px;
  border-radius: 12px;
  font-weight: bold;
  font-size: 14px;
}
.city {
  font-weight: bold;
  font-size: 16px;
}
.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}
.time {
  min-width: 50px;
  color: #909399;
  font-size: 13px;
}
.dot {
  width: 8px;
  height: 8px;
  background: #409eff;
  border-radius: 50%;
  margin-top: 6px;
  flex-shrink: 0;
}
.activity {
  font-weight: 500;
}
.meta {
  font-size: 13px;
  color: #909399;
  margin-top: 2px;
  display: flex;
  gap: 12px;
}
.cost {
  color: #e6a23c;
}
.cost.free {
  color: #67c23a;
}
.summary {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #606266;
  flex-wrap: wrap;
}
.day-total {
  color: #409eff;
  font-weight: bold;
}
</style>
