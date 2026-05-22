import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000
})

const aiApi = axios.create({
  baseURL: '/ai',
  timeout: 60000
})

export const sqlApi = {
  analyze: (sql, dbType = 'MYSQL') => api.post('/sql/analyze', { sql, databaseType: dbType }),
  optimize: (sql, dbType = 'MYSQL') => api.post('/sql/optimize', { sql, databaseType: dbType }),
  naturalToSql: (query) => api.post('/sql/natural-to-sql', { query })
}

export const aiSqlApi = {
  optimize: (sql) => aiApi.post('/optimize', { sql }),
  naturalToSql: (query, tableSchema) => aiApi.post('/natural-to-sql', {
    natural_query: query,
    table_schema: tableSchema || null
  })
}

export const memoryApi = {
  addConversation: (userId, content, role) => api.post('/memory/conversation', { userId, content, role }),
  getConversation: (userId) => api.get(`/memory/conversation/${userId}`),
  getContext: (userId) => api.get(`/memory/context/${userId}`),
  updatePreference: (userId, key, value) => api.post('/memory/preference', { userId, key, value }),
  submitFeedback: (conversationId, userId, rating, comment) => api.post('/memory/feedback', { conversationId, userId, rating, comment }),
  getProfile: (userId) => api.get(`/memory/profile/${userId}`),
  getSummary: (userId) => api.get(`/memory/summary/${userId}`),
  getTableStats: () => api.get('/memory/table-stats')
}

export default { sqlApi, aiSqlApi, memoryApi }
