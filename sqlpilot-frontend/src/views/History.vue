<template>
  <div class="history-page">
    <div class="page-header">
      <h1>历史记录</h1>
      <p>查看您的SQL分析和优化历史</p>
    </div>

    <div class="main-content" style="max-width:1000px;margin:0 auto;">
      <div class="card filter-card">
        <div class="card-body">
          <div class="filter-row">
            <input v-model="searchKeyword" placeholder="搜索SQL内容..." class="form-input" style="flex:1;max-width:300px;" />
            <select v-model="filterType" class="form-select" style="width:auto;min-width:140px;">
              <option value="all">全部</option>
              <option value="user">用户查询</option>
              <option value="assistant">AI回复</option>
            </select>
            <button class="btn btn-primary" @click="loadHistory">搜索</button>
            <button class="btn btn-outline" @click="clearFilters">清除筛选</button>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="card" style="text-align:center;padding:var(--space-12);color:var(--gray-400);">
        <div style="font-size:2rem;margin-bottom:var(--space-4);">&#8987;</div>
        <p>加载中...</p>
      </div>

      <!-- Timeline -->
      <div v-else-if="paginatedList.length > 0" class="history-list">
        <div class="timeline">
          <div v-for="(item, index) in paginatedList" :key="index" class="timeline-item slide-up" :style="{ animationDelay: index * 0.03 + 's' }">
            <div class="timeline-dot" :class="item.role || item.type"></div>
            <div class="card history-card">
              <div class="card-body">
                <div class="history-header">
                  <span class="history-badge" :class="item.role || item.type">
                    {{ (item.role || item.type) === 'user' ? '用户查询' : 'AI回复' }}
                  </span>
                  <span class="history-time">{{ formatTime(item.createdAt) }}</span>
                </div>
                <div class="history-content">
                  <pre class="code-block">{{ truncateContent(item.content || item.originalSql || '') }}</pre>
                </div>
                <div class="history-actions">
                  <button class="btn btn-sm btn-outline" @click="viewDetail(item)">查看详情</button>
                  <button class="btn btn-sm btn-outline" @click="copyContent(item.content || item.originalSql || '')">复制</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="pagination" v-if="totalPages > 1">
          <button class="btn btn-sm btn-outline" :disabled="currentPage <= 1" @click="goPage(currentPage - 1)">上一页</button>
          <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
          <button class="btn btn-sm btn-outline" :disabled="currentPage >= totalPages" @click="goPage(currentPage + 1)">下一页</button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div style="font-size:3rem;margin-bottom:var(--space-4);">&#128203;</div>
        <p>暂无历史记录</p>
        <p class="empty-hint">开始使用SQL优化或自然语言转SQL功能，记录将保存在这里</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { memoryApi } from '../api'

const historyList = ref([])
const searchKeyword = ref('')
const filterType = ref('all')
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)

const filteredList = computed(() => {
  let items = historyList.value
  if (filterType.value !== 'all') {
    items = items.filter(item => (item.role || item.type) === filterType.value)
  }
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.trim().toLowerCase()
    items = items.filter(item => {
      const content = (item.content || item.originalSql || '').toLowerCase()
      return content.includes(keyword)
    })
  }
  return items
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredList.value.length / pageSize.value)))

const paginatedList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredList.value.slice(start, start + pageSize.value)
})

onMounted(() => {
  loadHistory()
})

const loadHistory = async () => {
  loading.value = true
  currentPage.value = 1
  try {
    const response = await memoryApi.getConversation('user_1')
    if (response.data.success) {
      const raw = response.data.data || []
      historyList.value = raw.map(item => ({
        ...item,
        role: item.optimizedSql || (item.role || item.type),
        content: item.originalSql || item.content
      }))
    }
  } catch (error) {
    console.error('Failed to load history:', error)
  } finally {
    loading.value = false
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return '未知时间'
  return new Date(timestamp).toLocaleString('zh-CN')
}

const truncateContent = (content) => {
  if (!content) return ''
  return content.length <= 200 ? content : content.substring(0, 200) + '...'
}

const viewDetail = (item) => {
  alert('内容详情:\n\n' + (item.content || item.originalSql || ''))
}

const copyContent = async (content) => {
  if (!content) return
  try {
    await navigator.clipboard.writeText(content)
    alert('内容已复制到剪贴板')
  } catch (error) {
    console.error('Copy failed:', error)
    alert('复制失败')
  }
}

const clearFilters = () => {
  searchKeyword.value = ''
  filterType.value = 'all'
  loadHistory()
}

const goPage = (page) => {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<style scoped>
.history-page {
  max-width: 1000px;
  margin: 0 auto;
}

.filter-row {
  display: flex;
  gap: var(--space-3);
  align-items: center;
  flex-wrap: wrap;
}

.filter-card {
  margin-bottom: var(--space-6);
}

.history-list {
  margin-bottom: var(--space-6);
}

.timeline {
  position: relative;
  padding-left: 2rem;
}
.timeline::before {
  content: '';
  position: absolute;
  left: 0.5rem;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--gray-200);
}

.timeline-item {
  position: relative;
  margin-bottom: var(--space-6);
  opacity: 0;
  animation: slideUp 0.3s ease forwards;
}

.timeline-dot {
  position: absolute;
  left: -1.625rem;
  top: 1.25rem;
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
  border: 2px solid var(--gray-200);
  background: white;
}
.timeline-dot.user {
  border-color: var(--color-primary);
  background: var(--color-primary-lighter);
}
.timeline-dot.assistant {
  border-color: var(--color-success);
  background: var(--color-success-light);
}

.history-card {
  margin-bottom: 0;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.history-badge {
  padding: 0.2rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
}
.history-badge.user {
  background: var(--color-primary-lighter);
  color: var(--color-primary);
}
.history-badge.assistant {
  background: var(--color-success-light);
  color: var(--color-success);
}

.history-time {
  font-size: var(--text-xs);
  color: var(--gray-400);
}

.history-content {
  margin-bottom: var(--space-3);
}

.history-actions {
  display: flex;
  gap: var(--space-2);
}

@media (max-width: 640px) {
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-row .form-input {
    max-width: 100% !important;
  }
  .filter-row .form-select {
    width: 100% !important;
  }
}
</style>
