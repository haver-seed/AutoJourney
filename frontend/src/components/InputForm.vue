<template>
  <el-card class="input-form">
    <el-form :model="form" label-width="100px" @submit.prevent="handleSubmit">
      <el-form-item label="出发城市">
        <el-input v-model="form.departure" placeholder="如：北京" clearable />
        <div class="hot-tags">
          <el-tag
            v-for="city in hotCities"
            :key="city"
            size="small"
            class="hot-tag"
            @click="form.departure = city"
          >
            {{ city }}
          </el-tag>
        </div>
      </el-form-item>

      <el-form-item label="行程天数">
        <el-slider
          v-model="dayRange"
          range
          :min="3"
          :max="14"
          :marks="dayMarks"
          show-stops
        />
        <span class="day-label">{{ dayRange[0] }} - {{ dayRange[1] }} 天</span>
      </el-form-item>

      <el-form-item label="目的地">
        <div class="dest-input">
          <el-input
            v-model="newDest"
            placeholder="输入城市名，回车添加"
            @keyup.enter="addDestination"
            clearable
          >
            <template #append>
              <el-button @click="addDestination">添加</el-button>
            </template>
          </el-input>
        </div>
        <div class="hot-tags">
          <el-tag
            v-for="city in hotCities"
            :key="city"
            size="small"
            class="hot-tag"
            @click="addDestDirectly(city)"
          >
            {{ city }}
          </el-tag>
        </div>
        <div class="dest-tags" v-if="form.destinations.length">
          <el-tag
            v-for="(dest, idx) in form.destinations"
            :key="idx"
            closable
            @close="removeDestination(idx)"
          >
            {{ dest }}
          </el-tag>
        </div>
      </el-form-item>

      <el-form-item label="旅行模式">
        <el-radio-group v-model="form.mode">
          <el-radio value="multi-city">多城市串联游</el-radio>
          <el-radio value="single-city">单城市深度游</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="个人偏好">
        <el-input
          v-model="form.preferences"
          type="textarea"
          :rows="2"
          placeholder="可选，如：喜欢历史古迹、预算紧张、不吃辣"
        />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" size="large" :loading="loading" @click="handleSubmit">
          生成行程
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, reactive } from 'vue'

const emit = defineEmits(['submit'])
defineProps({ loading: Boolean })

const hotCities = ['北京', '上海', '西安', '成都', '杭州', '南京', '重庆', '广州', '武汉', '长沙']

const dayMarks = { 3: '3天', 5: '5天', 7: '7天', 10: '10天', 14: '14天' }

const dayRange = ref([5, 7])
const newDest = ref('')

const form = reactive({
  departure: '',
  destinations: [],
  mode: 'multi-city',
  preferences: '',
})

function addDestination() {
  const dest = newDest.value.trim()
  if (dest && !form.destinations.includes(dest)) {
    form.destinations.push(dest)
    newDest.value = ''
  }
}

function addDestDirectly(city) {
  if (!form.destinations.includes(city)) {
    form.destinations.push(city)
  }
}

function removeDestination(idx) {
  form.destinations.splice(idx, 1)
}

function handleSubmit() {
  if (!form.departure) return
  if (!form.destinations.length) return
  emit('submit', {
    departure: form.departure,
    minDays: dayRange.value[0],
    maxDays: dayRange.value[1],
    destinations: [...form.destinations],
    mode: form.mode,
    preferences: form.preferences,
  })
}
</script>

<style scoped>
.input-form {
  max-width: 800px;
  margin: 0 auto;
}
.hot-tags {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.hot-tag {
  cursor: pointer;
}
.hot-tag:hover {
  opacity: 0.8;
}
.dest-tags {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.day-label {
  margin-left: 16px;
  color: #409eff;
  font-weight: bold;
}
</style>
