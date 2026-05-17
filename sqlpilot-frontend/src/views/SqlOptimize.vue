<template>
  <div class="sql-optimize-page">
    <div class="page-header">
      <h1>SQL优化</h1>
      <p>输入您的SQL查询，AI将为您提供优化建议</p>
    </div>

    <div class="main-content">
      <div class="input-section">
        <el-card title="输入SQL">
          <div class="form-group">
            <label>数据库类型</label>
            <el-select v-model="dbType" placeholder="选择数据库类型">
              <el-option label="MySQL" value="MYSQL"></el-option>
              <el-option label="PostgreSQL" value="POSTGRESQL"></el-option>
              <el-option label="SQL Server" value="SQLSERVER"></el-option>
            </el-select>
          </div>
          <div class="form-group">
            <label>SQL查询</label>
            <el-textarea
              v-model="inputSql"
              :rows="8"
              placeholder="请输入需要优化的SQL查询..."
              class="sql-textarea"
            ></el-textarea>
          </div>
          <div class="form-actions">
            <el-button type="primary" :loading="loading" @click="optimizeSql">
              <span v-if="!loading">🚀 开始优化</span>
              <span v-else>优化中...</span>
            </el-button>
            <el-button @click="clearInput">清空</el-button>
          </div>
        </el-card>
      </div>

      <div class="output-section">
        <el-card title="优化结果" v-if="result">
          <div v-if="result.originalSql" class="result-block">
            <h4>原始SQL</h4>
            <pre class="code-block">{{ result.originalSql }}</pre>
          </div>
          <div v-if="result.optimizedSql" class="result-block">
            <h4>优化后SQL</h4>
            <pre class="code-block optimized">{{ result.optimizedSql }}</pre>
          </div>
          <div v-if="result.analysisResult" class="result-block">
            <h4>分析结果</h4>
            <div class="analysis-content">{{ formatAnalysis(result.analysisResult) }}</div>
          </div>
          <div v-if="result.performanceScore !== undefined" class="result-block">
            <h4>性能评分</h4>
            <el-rate :value="Math.round(result.performanceScore / 20)" disabled show-score text-color="#ff9900"></el-rate>
            <span class="score-text">{{ result.performanceScore }}/100</span>
          </div>
          <div v-if="result.riskLevel" class="result-block">
            <h4>风险等级</h4>
            <el-tag :type="getRiskTagType(result.riskLevel)">{{ result.riskLevel }}</el-tag>
          </div>
          <div class="feedback-section" v-if="result">
            <h4>反馈评价</h4>
            <div class="feedback-stars">
              <el-rate v-model="rating" max="5" show-text text-color="#ff9900"></el-rate>
            </div>
            <el-input v-model="comment" placeholder="请输入您的评价..."></el-input>
            <el-button type="success" @click="submitFeedback">提交反馈</el-button>
          </div>
        </el-card>

        <el-card title="优化建议" v-if="suggestions.length > 0">
          <el-timeline>
            <el-timeline-item v-for="(suggestion, index) in suggestions" :key="index">
              <template #dot>
                <span class="suggestion-icon">{{ suggestion.icon }}</span>
              </template>
              <h4>{{ suggestion.title }}</h4>
              <p>{{ suggestion.description }}</p>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { sqlApi, aiSqlApi, memoryApi } from '../api'

const dbType = ref('MYSQL')
const inputSql = ref('')
const loading = ref(false)
const result = ref(null)
const suggestions = ref([])
const rating = ref(3)
const comment = ref('')

const optimizeSql = async () => {
  if (!inputSql.value.trim()) {
    alert('请输入SQL查询')
    return
  }

  loading.value = true
  result.value = null
  suggestions.value = []

  try {
    const response = await aiSqlApi.optimize(inputSql.value)
    result.value = response.data

    await memoryApi.addConversation('user_' + Date.now(), inputSql.value, 'user')
    await memoryApi.addConversation('user_' + Date.now(), JSON.stringify(result.value), 'assistant')

    generateSuggestions()
  } catch (error) {
    console.error('Optimization failed:', error)
    alert('优化失败，请检查后端服务是否正常运行')
  } finally {
    loading.value = false
  }
}

const generateSuggestions = () => {
  suggestions.value = [
    { icon: '📊', title: '执行计划分析', description: '建议使用EXPLAIN分析查询执行计划，了解查询的执行路径和潜在瓶颈。' },
    { icon: '🏷️', title: '索引优化', description: '检查WHERE子句和JOIN条件中的列是否有合适的索引，考虑添加复合索引。' },
    { icon: '📝', title: '避免SELECT *', description: '只选择需要的列，减少数据传输量和内存占用。' },
    { icon: '🔗', title: 'JOIN优化', description: '确保JOIN条件使用等值连接，避免笛卡尔积。' }
  ]
}

const formatAnalysis = (analysis) => {
  if (typeof analysis === 'string') {
    try {
      const obj = JSON.parse(analysis)
      return JSON.stringify(obj, null, 2)
    } catch {
      return analysis
    }
  }
  return JSON.stringify(analysis, null, 2)
}

const getRiskTagType = (level) => {
  const types = {
    'LOW': 'success',
    'MEDIUM': 'warning',
    'HIGH': 'danger',
    'CRITICAL': 'danger'
  }
  return types[level] || 'info'
}

const submitFeedback = async () => {
  if (!result.value) return

  try {
    await memoryApi.submitFeedback(
      'conv_' + Date.now(),
      'user_' + Date.now(),
      rating.value,
      comment.value
    )
    alert('感谢您的反馈！')
    rating.value = 3
    comment.value = ''
  } catch (error) {
    console.error('Feedback failed:', error)
    alert('提交反馈失败')
  }
}

const clearInput = () => {
  inputSql.value = ''
  result.value = null
  suggestions.value = []
}
</script>

<style scoped>
.sql-optimize-page {
  max-width: 1200px;
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

.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.input-section {
  grid-column: 1;
}

.output-section {
  grid-column: 2;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #475569;
}

.sql-textarea {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
}

.form-actions {
  display: flex;
  gap: 1rem;
}

.result-block {
  margin-bottom: 1.5rem;
}

.result-block h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 0.75rem;
}

.code-block {
  background: #1e293b;
  color: #e2e8f0;
  padding: 1rem;
  border-radius: 8px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  overflow-x: auto;
  max-height: 200px;
  overflow-y: auto;
}

.code-block.optimized {
  background: linear-gradient(135deg, #1e3a2f 0%, #1e3a5f 100%);
  border-left: 4px solid #10b981;
}

.analysis-content {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 8px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  color: #475569;
  max-height: 200px;
  overflow-y: auto;
}

.score-text {
  margin-left: 1rem;
  color: #667eea;
  font-weight: 600;
}

.feedback-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.feedback-section h4 {
  margin-bottom: 1rem;
}

.feedback-stars {
  margin-bottom: 1rem;
}

.suggestion-icon {
  font-size: 1.25rem;
}

@media (max-width: 900px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  .input-section, .output-section {
    grid-column: 1;
  }
}
</style>
