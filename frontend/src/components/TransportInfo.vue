<template>
  <div class="transport-section" v-if="segments && segments.length">
    <h2 class="section-title">车票方案</h2>
    <div class="transport-list">
      <div v-for="(seg, idx) in segments" :key="idx" class="transport-item">
        <!-- 路线 -->
        <div class="route-col">
          <div class="station">{{ seg.from }}</div>
          <div class="arrow-icon">→</div>
          <div class="station">{{ seg.to }}</div>
        </div>

        <!-- 车次详情 -->
        <div class="detail-col">
          <template v-if="seg.train_info && seg.train_info.train_no">
            <div class="train-header">
              <span class="train-no">{{ seg.train_info.train_no }}</span>
              <span v-if="seg.travel_date" class="train-date">{{ seg.travel_date }}</span>
            </div>
            <div class="time-row" v-if="seg.train_info.start_time">
              <span class="time-depart">{{ seg.train_info.start_time }} 发车</span>
              <span class="time-arrow">→</span>
              <span v-if="seg.train_info.arrive_time" class="time-arrive">{{ seg.train_info.arrive_time }} 到达</span>
              <span v-if="seg.train_info.duration" class="time-dur">历时 {{ seg.train_info.duration }}</span>
            </div>
            <div class="seat-row" v-if="seg.train_info.seat_types">
              {{ seg.train_info.seat_types }}
            </div>
            <div class="reason-row" v-if="seg.train_info.reason">
              <span class="reason-icon">💡</span> {{ seg.train_info.reason }}
            </div>
          </template>
          <template v-else>
            <span class="no-result">未查到车次信息</span>
          </template>
        </div>

        <!-- 停留 + 票价 -->
        <div class="price-col">
          <span v-if="seg.stay_days > 0 && idx < segments.length - 1" class="stay-info">停留 {{ seg.stay_days }} 天</span>
          <span class="price-label">票价</span>
          <span v-if="seg.cost > 0" class="price-value">¥{{ seg.cost }}</span>
          <span v-else class="price-na">未查到</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  segments: { type: Array, default: () => [] },
})
</script>

<style scoped>
.transport-section {
  margin-top: 32px;
}
.section-title {
  font-size: 34px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 24px;
  letter-spacing: -0.374px;
  line-height: 1.1;
}
.transport-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.transport-item {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 18px 22px;
  background: #f5f5f7;
  border-radius: 14px;
}
.route-col {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 180px;
  flex-shrink: 0;
}
.station {
  font-weight: 600;
  font-size: 17px;
  color: #1d1d1f;
  letter-spacing: -0.374px;
}
.arrow-icon {
  color: #86868b;
  font-size: 16px;
}
.detail-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.train-header {
  display: flex;
  align-items: baseline;
  gap: 10px;
}
.train-no {
  font-size: 18px;
  font-weight: 700;
  color: #1d1d1f;
  letter-spacing: -0.374px;
  font-variant-numeric: tabular-nums;
}
.train-date {
  font-size: 13px;
  color: #86868b;
  margin-left: auto;
}
.time-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #1d1d1f;
  margin-top: 4px;
}
.time-depart {
  font-weight: 600;
}
.time-arrow {
  color: #86868b;
  font-size: 12px;
}
.time-arrive {
  font-weight: 500;
}
.time-dur {
  color: #86868b;
  font-size: 13px;
}
.seat-row {
  font-size: 13px;
  color: #7a7a7a;
  margin-top: 2px;
}
.reason-row {
  font-size: 12px;
  color: #86868b;
  margin-top: 4px;
  line-height: 1.4;
}
.reason-icon {
  font-size: 12px;
}
.no-result {
  font-size: 14px;
  color: #86868b;
}
.price-col {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: 90px;
  flex-shrink: 0;
  gap: 4px;
}
.stay-info {
  font-size: 12px;
  color: #1d1d1f;
  background: rgba(29, 29, 31, 0.06);
  padding: 2px 8px;
  border-radius: 9999px;
}
.price-label {
  font-size: 12px;
  color: #86868b;
}
.price-value {
  font-size: 24px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.28px;
  font-variant-numeric: tabular-nums;
}
.price-na {
  font-size: 14px;
  color: #86868b;
  font-weight: 400;
}
</style>
