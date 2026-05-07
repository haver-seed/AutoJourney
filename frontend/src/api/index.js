import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 180000,
})

/**
 * Query tickets via SSE streaming.
 * @param {Object} formData
 * @param {Function} onProgress - callback({ stage, percent, message })
 * @returns {Promise<Object>} final ticket response
 */
export function queryTickets(formData, onProgress) {
  const payload = {
    departure: formData.departure,
    departure_date: formData.departureDate,
    destinations: formData.destinations,
    stay_days: formData.stayDays,
  }

  return new Promise((resolve, reject) => {
    fetch('/api/tickets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then(response => {
      if (!response.ok) {
        reject(new Error(`HTTP ${response.status}`))
        return
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      function read() {
        reader.read().then(({ done, value }) => {
          if (done) {
            reject(new Error('连接已关闭，未收到结果'))
            return
          }

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          let currentEvent = ''
          for (const line of lines) {
            if (line.startsWith('event: ')) {
              currentEvent = line.slice(7).trim()
            } else if (line.startsWith('data: ')) {
              const jsonStr = line.slice(6)
              try {
                const data = JSON.parse(jsonStr)
                if (currentEvent === 'progress' && onProgress) {
                  onProgress(data)
                } else if (currentEvent === 'result') {
                  resolve(data)
                  return
                } else if (currentEvent === 'error') {
                  reject(new Error(data.message || '查询失败'))
                  return
                }
              } catch (e) {
                // skip non-JSON lines
              }
            }
          }
          read()
        }).catch(reject)
      }
      read()
    }).catch(reject)
  })
}

export async function healthCheck() {
  const { data } = await api.get('/health')
  return data
}

export async function searchStations(query, limit = 15) {
  if (!query || !query.trim()) return []
  const { data } = await api.get('/stations', { params: { q: query.trim(), limit } })
  return data
}
