<template>
  <div class="map-container">
    <div ref="mapRef" class="map" />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader'

const props = defineProps({
  transport: { type: Array, default: () => [] },
  dailyPlans: { type: Array, default: () => [] },
  activeDay: { type: Number, default: 0 },
})

const mapRef = ref(null)
let map = null
let markers = []
let polylines = []

onMounted(async () => {
  try {
    const AMap = await AMapLoader.load({
      key: 'YOUR_AMAP_KEY',
      version: '2.0',
      plugins: ['AMap.Scale', 'AMap.ToolBar'],
    })
    map = new AMap.Map(mapRef.value, {
      zoom: 6,
      center: [110, 35],
    })
    map.addControl(new AMap.Scale())
    map.addControl(new AMap.ToolBar())
    updateMap()
  } catch (e) {
    console.error('高德地图加载失败:', e)
  }
})

onUnmounted(() => {
  if (map) {
    map.destroy()
    map = null
  }
})

watch(() => [props.transport, props.dailyPlans, props.activeDay], updateMap, { deep: true })

function clearOverlays() {
  markers.forEach(m => map.remove(m))
  polylines.forEach(p => map.remove(p))
  markers = []
  polylines = []
}

function updateMap() {
  if (!map || !props.dailyPlans.length) return
  clearOverlays()

  const allPoints = []

  props.dailyPlans.forEach((day, idx) => {
    day.schedule.forEach(item => {
      if (item.activity) {
        const marker = new AMap.Marker({
          position: getApproxPosition(day.city, item.activity),
          title: item.activity,
          label: {
            content: item.activity,
            direction: 'top',
          },
        })
        marker.on('click', () => {
          const info = new AMap.InfoWindow({
            content: `<div style="padding:8px">
              <b>${item.activity}</b><br/>
              ${item.time} | ${item.duration}<br/>
              费用：¥${item.cost}
            </div>`,
            offset: new AMap.Pixel(0, -30),
          })
          info.open(map, marker.getPosition())
        })
        map.add(marker)
        markers.push(marker)
        allPoints.push(marker.getPosition())
      }
    })
  })

  props.transport.forEach(t => {
    const fromPos = getCityCenter(t.fr)
    const toPos = getCityCenter(t.to)
    if (fromPos && toPos) {
      const line = new AMap.Polyline({
        path: [fromPos, toPos],
        strokeColor: '#409eff',
        strokeWeight: 3,
        strokeStyle: 'dashed',
      })
      map.add(line)
      polylines.push(line)
    }
  })

  if (allPoints.length) {
    map.setFitView(markers)
  }
}

function getCityCenter(city) {
  const cityCoords = {
    '北京': [116.40, 39.90], '上海': [121.47, 31.23], '西安': [108.94, 34.26],
    '成都': [104.07, 30.57], '杭州': [120.15, 30.28], '南京': [118.78, 32.06],
    '重庆': [106.55, 29.56], '广州': [113.26, 23.13], '武汉': [114.30, 30.59],
    '长沙': [112.97, 28.23], '昆明': [102.83, 25.02], '大理': [100.23, 25.59],
    '丽江': [100.23, 26.87], '桂林': [110.29, 25.27], '洛阳': [112.45, 34.62],
    '开封': [114.35, 34.79], '苏州': [120.62, 31.30], '无锡': [120.31, 31.57],
    '青岛': [120.38, 36.07], '大连': [121.61, 38.91], '厦门': [118.09, 24.48],
    '深圳': [114.07, 22.55], '天津': [117.20, 39.08], '石家庄': [114.51, 38.04],
    '郑州': [113.65, 34.76], '合肥': [117.28, 31.82], '福州': [119.30, 26.08],
    '贵阳': [106.71, 26.57], '哈尔滨': [126.63, 45.75], '长春': [125.32, 43.88],
    '沈阳': [123.43, 41.80], '济南': [117.00, 36.67], '太原': [112.55, 37.87],
    '南昌': [115.89, 28.68], '兰州': [103.83, 36.06], '西宁': [101.74, 36.62],
    '银川': [106.23, 38.49], '乌鲁木齐': [87.62, 43.83], '拉萨': [91.11, 29.65],
    '呼和浩特': [111.75, 40.84], '南宁': [108.32, 22.82],
  }
  return cityCoords[city] ? new AMap.LngLat(...cityCoords[city]) : null
}

function getApproxPosition(city, activity) {
  const center = getCityCenter(city)
  if (!center) return new AMap.LngLat(110, 35)
  const offset = (Math.random() - 0.5) * 0.05
  return new AMap.LngLat(center.getLng() + offset, center.getLat() + offset)
}
</script>

<style scoped>
.map-container {
  height: 100%;
  min-height: 500px;
}
.map {
  width: 100%;
  height: 100%;
}
</style>
