<template>
  <div class="history-page">
    <div class="page-header">
      <h1>历史记录</h1>
      <p>查看您的SQL分析和优化历史</p>
    </div>

    <div class="main-content">
      <div class="filter-section">
        <el-card>
          <div class="filter-row">
            <el-input v-model="searchKeyword" placeholder="搜索SQL内容..." class="search-input"></el-input>
            <el-select v-model="filterType" placeholder="筛选类型">
              <el-option label="全部" value="all"></el-option>
              <el-option label="SQL优化" value="optimize"></el-option>
              <el-option label="自然语言转SQL" value="natural"></el-option>
            </el-select>
            <el-button type="primary" @click="loadHistory">🔍 搜索</el-button>
            <el-button @click="clearFilters">清除筛选</el-button>
          </div>
        </el-card>
      </div>

      <div class="history-list" v-if="historyList.length > 0">
        <el-timeline>
          <el-timeline-item v-for="(item, index) in historyList" :key="index">
            <template #dot>
              <span class="history-icon">{{ item.type === 'user' ? '👤' : '🤖' }}</span>
            </template>
            <el-card class="history-card">
              <div class="history-header">
                <span class="history-type" :class="item.type">{{ item.type === 'user' ? '用户查询' : 'AI回复' }}</span>
                <span class="history-time">{{ formatTime(item.createdAt) }}</span>
              </div>
              <div class="history-content">
                <pre class="code-block">{{ truncateContent(item.content) }}</pre>
              </div>
              <div class="history-actions">
                <el-button size="small" @click="viewDetail(item)">查看详情</el-button>
                <el-button size="small" @click="copyContent(item.content)">复制</el-button>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>

      <div class="empty-state" v-else>
        <div class="empty-icon">📋</div>
        <p>暂无历史记录</p>
        <p class="empty-hint">开始使用SQL优化或自然语言转SQL功能，记录将保存在这里</p>
      </div>

      <div class="pagination-section" v-if="total > pageSize">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          @current-change="handlePageChange"
          layout="prev, pager, next"
        ></el-pagination>
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
  text-align: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.page-header p {
  color: #64748b;
}

.filter-section {
  margin-bottom: 2rem;
}

.filter-row {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-input {
  flex: 1;
  max-width: 300px;
}

.history-list {
  margin-bottom: 2rem;
}

.history-icon {
  font-size: 1.25rem;
}

.history-card {
  margin-bottom: 1rem;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.history-type {
  padding: 0.25rem 0.75rem;
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
  margin-bottom: 1rem;
}

.code-block {
  background: #1e293b;
  color: #e2e8f0;
  padding: 1rem;
  border-radius: 8px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  overflow-x: auto;
  max-height: 150px;
  overflow-y: auto;
}

.history-actions {
  display: flex;
  gap: 0.5rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state p {
  color: #64748b;
  margin-bottom: 0.5rem;
}

.empty-hint {
  font-size: 0.9rem !important;
  color: #94a3b8 !important;
}

.pagination-section {
  display: flex;
  justify-content: center;
}

@media (max-width: 600px) {
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }
  .search-input {
    max-width: 100%;
  }
}
</style>
