<template>
  <div class="history-page">
    <div class="page-header">
      <h1>历史记录</h1>
      <p>查看您的SQL分析和优化历史</p>
    </div>

    <div class="main-content">
      <div class="card filter-card">
        <div class="card-body">
          <div class="filter-row">
            <input v-model="searchKeyword" placeholder="搜索SQL内容..." class="filter-input" />
            <select v-model="filterType" class="filter-select">
              <option value="all">全部</option>
              <option value="optimize">SQL优化</option>
              <option value="natural">自然语言转SQL</option>
            </select>
            <button class="btn btn-primary" @click="loadHistory">搜索</button>
            <button class="btn btn-outline" @click="clearFilters">清除筛选</button>
          </div>
        </div>
      </div>

      <div class="history-list" v-if="historyList.length > 0">
        <div class="timeline">
          <div v-for="(item, index) in historyList" :key="index" class="timeline-item">
            <div class="timeline-dot" :class="item.type"></div>
            <div class="card history-card">
              <div class="card-body">
                <div class="history-header">
                  <span class="history-type" :class="item.type">{{ item.type === 'user' ? '用户查询' : 'AI回复' }}</span>
                  <span class="history-time">{{ formatTime(item.createdAt) }}</span>
                </div>
                <div class="history-content">
                  <pre class="code-block">{{ truncateContent(item.content) }}</pre>
                </div>
                <div class="history-actions">
                  <button class="btn btn-sm btn-outline" @click="viewDetail(item)">查看详情</button>
                  <button class="btn btn-sm btn-outline" @click="copyContent(item.content)">复制</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="empty-state" v-else>
        <p>暂无历史记录</p>
        <p class="empty-hint">开始使用SQL优化或自然语言转SQL功能，记录将保存在这里</p>
      </div>

      <div class="pagination-section" v-if="total > pageSize">
        <div class="pagination">
          <button class="btn btn-sm btn-outline" :disabled="currentPage <= 1" @click="currentPage > 1 && handlePageChange(currentPage - 1)">上一页</button>
          <span class="page-info">{{ currentPage }} / {{ Math.ceil(total / pageSize) }}</span>
          <button class="btn btn-sm btn-outline" :disabled="currentPage >= Math.ceil(total / pageSize)" @click="currentPage < Math.ceil(total / pageSize) && handlePageChange(currentPage + 1)">下一页</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { memoryApi } from '../api'

const historyList = ref([])
const searchKeyword = ref('')
const filterType = ref('all')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

onMounted(() => {
  loadHistory()
})

const loadHistory = async () => {
  try {
    const response = await memoryApi.getConversation('user_1')
    if (response.data.success) {
      historyList.value = response.data.data || []
      total.value = historyList.value.length
    }
  } catch (error) {
    console.error('Failed to load history:', error)
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return '未知时间'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

const truncateContent = (content) => {
  if (content.length <= 200) return content
  return content.substring(0, 200) + '...'
}

const viewDetail = (item) => {
  alert('内容详情:\n\n' + item.content)
}

const copyContent = async (content) => {
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

const handlePageChange = (page) => {
  currentPage.value = page
}
</script>

<style scoped>
.history-page {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 1.5rem;
}

.page-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.page-header p {
  color: #64748b;
  font-size: 0.9rem;
}

.filter-card {
  margin-bottom: 1.5rem;
}

.filter-row {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.filter-input {
  flex: 1;
  max-width: 300px;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #1e293b;
}

.filter-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
}

.filter-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #1e293b;
  background: white;
}

.btn {
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.15s ease;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8rem;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-outline {
  background: white;
  color: #475569;
  border: 1px solid #d1d5db;
}

.btn-outline:hover:not(:disabled) {
  border-color: #94a3b8;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
}

.card-body {
  padding: 1.25rem;
}

.history-list {
  margin-bottom: 2rem;
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
  background: #e2e8f0;
}

.timeline-item {
  position: relative;
  margin-bottom: 1.5rem;
}

.timeline-dot {
  position: absolute;
  left: -1.625rem;
  top: 1.25rem;
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
  border: 2px solid #e2e8f0;
  background: white;
}

.timeline-dot.user {
  border-color: #2563eb;
  background: #dbeafe;
}

.timeline-dot.assistant {
  border-color: #16a34a;
  background: #dcfce7;
}

.history-card {
  margin-bottom: 0;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.history-type {
  padding: 0.2rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.history-type.user {
  background: #dbeafe;
  color: #2563eb;
}

.history-type.assistant {
  background: #dcfce7;
  color: #16a34a;
}

.history-time {
  font-size: 0.8rem;
  color: #94a3b8;
}

.history-content {
  margin-bottom: 0.75rem;
}

.code-block {
  background: #0f172a;
  color: #e2e8f0;
  padding: 0.875rem;
  border-radius: 6px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  overflow-x: auto;
  max-height: 150px;
  overflow-y: auto;
  line-height: 1.5;
}

.history-actions {
  display: flex;
  gap: 0.5rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.empty-state p {
  color: #64748b;
  margin-bottom: 0.5rem;
}

.empty-hint {
  font-size: 0.9rem;
  color: #94a3b8;
}

.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: 1.5rem;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.page-info {
  font-size: 0.85rem;
  color: #64748b;
}

@media (max-width: 600px) {
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-input {
    max-width: 100%;
  }
}
</style>
