<template>
  <div class="input-form">
    <el-form :model="form" label-width="90px" @submit.prevent="handleSubmit">
      <el-form-item label="出发站点">
        <el-autocomplete
          v-model="form.departure"
          :fetch-suggestions="searchStation"
          placeholder="输入城市或站点名，如：茌平、北京南"
          clearable
          style="width: 100%"
        />
        <div class="hot-tags">
          <el-tag
            v-for="s in hotStations"
            :key="s"
            size="small"
            class="hot-tag"
            effect="plain"
            @click="form.departure = s"
          >
            {{ s }}
          </el-tag>
        </div>
      </el-form-item>

      <el-form-item label="出发日期">
        <el-date-picker
          v-model="form.departureDate"
          type="date"
          placeholder="选择出发日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          :disabled-date="disablePastDates"
          style="width: 100%"
        />
      </el-form-item>

      <!-- 目的地 -->
      <el-form-item label="目的地">
        <div class="dest-input-row">
          <el-autocomplete
            v-model="newDest"
            :fetch-suggestions="searchCity"
            placeholder="搜索城市，回车或点击添加"
            clearable
            @keyup.enter="addDestination"
            @select="handleCitySelect"
            class="dest-input"
          />
          <el-button type="primary" @click="addDestination" class="dest-add-btn">添加</el-button>
        </div>
        <div class="hot-tags">
          <el-tag
            v-for="city in hotCities"
            :key="city"
            size="small"
            class="hot-tag"
            effect="plain"
            @click="addDestDirectly(city)"
          >
            + {{ city }}
          </el-tag>
        </div>

        <!-- 已选目的地 -->
        <div class="dest-list" v-if="form.destinations.length">
          <div class="dest-item" v-for="(dest, idx) in form.destinations" :key="idx">
            <div class="dest-index">{{ idx + 1 }}</div>
            <div class="dest-name">{{ dest }}</div>
            <div class="dest-stay">
              <span class="stay-label">停留</span>
              <el-input-number
                v-model="form.stayDays[idx]"
                :min="1"
                :max="30"
                size="small"
                controls-position="right"
              />
              <span class="stay-label">天</span>
            </div>
            <div class="dest-actions">
              <el-button v-if="idx > 0" :icon="Top" size="small" circle @click="moveUp(idx)" />
              <el-button v-if="idx < form.destinations.length - 1" :icon="Bottom" size="small" circle @click="moveDown(idx)" />
              <el-button :icon="Delete" size="small" type="danger" circle @click="removeDestination(idx)" />
            </div>
          </div>
        </div>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" size="large" :loading="loading" @click="handleSubmit" class="submit-btn">
          查询车票
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Top, Bottom, Delete } from '@element-plus/icons-vue'
import { searchStations } from '../api/index.js'

const emit = defineEmits(['submit'])
defineProps({ loading: Boolean })

const hotStations = ['北京南', '上海虹桥', '西安北', '成都东', '杭州东', '南京南', '重庆北', '广州南', '武汉', '长沙南']

const hotCities = ['北京', '上海', '西安', '成都', '杭州', '南京', '重庆', '广州', '武汉', '长沙', '昆明', '大理', '桂林', '洛阳', '苏州', '青岛', '厦门', '哈尔滨', '拉萨', '乌鲁木齐']

const newDest = ref('')

const today = new Date()
const defaultDate = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000)
  .toISOString().split('T')[0]

const form = reactive({
  departure: '',
  departureDate: defaultDate,
  destinations: [],
  stayDays: [],
})

function disablePastDates(date) {
  return date < new Date(new Date().toDateString())
}

// --- 站点搜索 ---

let searchTimer = null

function isStation(entry) {
  if (hotStations.includes(entry.name)) return true
  if (entry.name === entry.city) return false
  return true
}

function searchStation(queryString, cb) {
  if (!queryString || !queryString.trim()) {
    cb(hotStations.map(s => ({ value: s })))
    return
  }
  const q = queryString.trim()
  clearTimeout(searchTimer)
  searchTimer = setTimeout(async () => {
    try {
      const results = await searchStations(q, 20)
      const stations = results.filter(isStation)
      cb(stations.map(s => ({ value: s.name })))
    } catch {
      cb([])
    }
  }, 200)
}

function searchCity(queryString, cb) {
  if (!queryString || !queryString.trim()) {
    cb(hotCities.map(c => ({ value: c })))
    return
  }
  clearTimeout(searchTimer)
  searchTimer = setTimeout(async () => {
    try {
      const results = await searchStations(queryString.trim(), 15)
      const seen = new Set()
      const cities = []
      for (const s of results) {
        const city = s.city || s.name
        if (!seen.has(city)) {
          seen.add(city)
          cities.push({ value: city })
        }
      }
      cb(cities.length ? cities : hotCities.filter(c => c.includes(queryString)).map(c => ({ value: c })))
    } catch {
      cb(hotCities.filter(c => c.includes(queryString)).map(c => ({ value: c })))
    }
  }, 200)
}

function handleCitySelect(item) {
  addDestDirectly(item.value)
  newDest.value = ''
}

// --- 目的地操作 ---

function addDestination() {
  const dest = newDest.value.trim()
  if (dest && !form.destinations.includes(dest)) {
    form.destinations.push(dest)
    form.stayDays.push(2)
    newDest.value = ''
  }
}

function addDestDirectly(city) {
  if (!form.destinations.includes(city)) {
    form.destinations.push(city)
    form.stayDays.push(2)
  }
}

function removeDestination(idx) {
  form.destinations.splice(idx, 1)
  form.stayDays.splice(idx, 1)
}

function moveUp(idx) {
  const arr = form.destinations
  ;[arr[idx - 1], arr[idx]] = [arr[idx], arr[idx - 1]]
  const days = form.stayDays
  ;[days[idx - 1], days[idx]] = [days[idx], days[idx - 1]]
}

function moveDown(idx) {
  const arr = form.destinations
  ;[arr[idx], arr[idx + 1]] = [arr[idx + 1], arr[idx]]
  const days = form.stayDays
  ;[days[idx], days[idx + 1]] = [days[idx + 1], days[idx]]
}

// --- 提交 ---

function handleSubmit() {
  if (!form.departure) {
    ElMessage.warning('请填写出发站点')
    return
  }
  if (!form.departureDate) {
    ElMessage.warning('请选择出发日期')
    return
  }
  if (!form.destinations.length) {
    ElMessage.warning('请添加目的地城市')
    return
  }
  emit('submit', {
    departure: form.departure,
    departureDate: form.departureDate,
    destinations: [...form.destinations],
    stayDays: [...form.stayDays],
  })
}
</script>

<style scoped>
.input-form {
  max-width: 820px;
  margin: 0 auto;
  background: #f5f5f7;
  border-radius: 18px;
  padding: 36px 40px 28px;
}
.input-form :deep(.el-form-item__label) {
  font-weight: 600;
  color: #1d1d1f;
  font-size: 14px;
  letter-spacing: -0.224px;
}
.input-form :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #d2d2d7 !important;
}
.input-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #86868b !important;
}
.input-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(29, 29, 31, 0.1) !important;
}
.hot-tags {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.hot-tag {
  cursor: pointer;
  border-radius: 9999px;
  transition: all 0.15s;
  color: #1d1d1f;
  border-color: #d2d2d7;
  background: #fff;
}
.hot-tag:hover {
  background: #1d1d1f;
  color: #fff;
  border-color: #1d1d1f;
}
.dest-input-row {
  display: flex;
  gap: 8px;
  width: 100%;
}
.dest-input {
  flex: 1;
  min-width: 0;
}
.dest-add-btn {
  flex-shrink: 0;
}
.dest-list {
  margin-top: 12px;
  width: 100%;
  background: #fff;
  border-radius: 11px;
  overflow: hidden;
}
.dest-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  gap: 12px;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.15s;
}
.dest-item:last-child {
  border-bottom: none;
}
.dest-item:hover {
  background: #fafafa;
}
.dest-index {
  width: 24px;
  height: 24px;
  background: #1d1d1f;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}
.dest-name {
  min-width: 80px;
  font-size: 15px;
  font-weight: 400;
  color: #1d1d1f;
}
.dest-stay {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
}
.stay-label {
  font-size: 13px;
  color: #86868b;
}
.dest-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}
.submit-btn {
  padding: 14px 40px !important;
  font-size: 17px !important;
  letter-spacing: -0.374px;
}
</style>
