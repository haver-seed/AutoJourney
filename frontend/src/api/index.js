import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 35000,
})

export async function generatePlan(formData) {
  const payload = {
    departure: formData.departure,
    min_days: formData.minDays,
    max_days: formData.maxDays,
    destinations: formData.destinations,
    mode: formData.mode,
    preferences: formData.preferences || null,
  }
  const { data } = await api.post('/plan', payload)
  return data
}

export async function healthCheck() {
  const { data } = await api.get('/health')
  return data
}
