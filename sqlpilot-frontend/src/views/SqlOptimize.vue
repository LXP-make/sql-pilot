<template>
  <div class="sql-optimize-page">
    <div class="page-header">
      <h1>SQL优化</h1>
      <p>输入SQL查询，获取基于大厂规范的优化建议</p>
    </div>

    <div class="main-content">
      <div class="input-section">
        <div class="card">
          <div class="card-header">输入SQL</div>
          <div class="card-body">
            <div class="form-group">
              <label>数据库类型</label>
              <select v-model="dbType" class="select-input">
                <option value="MYSQL">MySQL</option>
                <option value="POSTGRESQL">PostgreSQL</option>
                <option value="SQLSERVER">SQL Server</option>
              </select>
            </div>
            <div class="form-group">
              <label>SQL查询</label>
              <textarea
                v-model="inputSql"
                :rows="8"
                placeholder="请输入需要优化的SQL查询..."
                class="sql-textarea"
              ></textarea>
            </div>
            <div class="form-actions">
              <button class="btn btn-primary" :disabled="loading" @click="optimizeSql">
                {{ loading ? '优化中...' : '开始优化' }}
              </button>
              <button class="btn btn-outline" @click="clearInput">清空</button>
            </div>
          </div>
        </div>
      </div>

      <div class="output-section">
        <div class="card" v-if="result">
          <div class="card-header">优化结果</div>
          <div class="card-body">
            <div v-if="result.original_sql" class="result-block">
              <h4>原始SQL</h4>
              <pre class="code-block">{{ result.original_sql }}</pre>
            </div>
            <div v-if="result.optimized_sql" class="result-block">
              <h4>优化后SQL</h4>
              <pre class="code-block optimized">{{ result.optimized_sql }}</pre>
            </div>
            <div v-if="result.problems && result.problems.length > 0" class="result-block">
              <h4>发现的问题</h4>
              <ul class="problem-list">
                <li v-for="(p, i) in result.problems" :key="i">{{ p }}</li>
              </ul>
            </div>
            <div v-if="result.suggestions && result.suggestions.length > 0" class="result-block">
              <h4>优化建议</h4>
              <ul class="suggestion-list">
                <li v-for="(s, i) in result.suggestions" :key="i">{{ s.description || s }}</li>
              </ul>
            </div>
            <div v-if="result.rag_info && result.rag_info.length > 0" class="result-block">
              <h4>知识来源</h4>
              <div class="rag-sources">
                <span v-for="(doc, i) in result.rag_info" :key="i" class="rag-tag">{{ doc.filename }}</span>
              </div>
            </div>

            <div class="feedback-section">
              <h4>反馈评价</h4>
              <div class="stars">
                <span v-for="n in 5" :key="n" class="star" :class="{ filled: n <= rating }" @click="rating = n">&#9733;</span>
              </div>
              <input v-model="comment" placeholder="输入评价..." class="input" />
              <button class="btn btn-success" @click="submitFeedback">提交</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { aiSqlApi } from '../api'

const dbType = ref('MYSQL')
const inputSql = ref('')
const loading = ref(false)
const result = ref(null)
const rating = ref(3)
const comment = ref('')

const optimizeSql = async () => {
  if (!inputSql.value.trim()) return
  loading.value = true
  result.value = null

  try {
    const response = await aiSqlApi.optimize(inputSql.value)
    result.value = response.data
  } catch (error) {
    console.error('Optimization failed:', error)
    alert('优化失败，请检查后端服务是否正常运行')
  } finally {
    loading.value = false
  }
}

const submitFeedback = async () => {
  if (!result.value) return
  alert('感谢您的反馈！')
  rating.value = 3
  comment.value = ''
}

const clearInput = () => {
  inputSql.value = ''
  result.value = null
}
</script>

<style scoped>
.sql-optimize-page {
  max-width: 1200px;
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

.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
}

.card-header {
  padding: 0.875rem 1.25rem;
  font-weight: 600;
  font-size: 0.9rem;
  color: #1e293b;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.card-body {
  padding: 1.25rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.375rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #475569;
}

.select-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #1e293b;
  background: white;
}

.sql-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.5;
  resize: vertical;
  color: #1e293b;
}

.sql-textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
}

.form-actions {
  display: flex;
  gap: 0.5rem;
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

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-outline {
  background: white;
  color: #475569;
  border: 1px solid #d1d5db;
}

.btn-outline:hover {
  border-color: #94a3b8;
}

.btn-success {
  background: #16a34a;
  color: white;
}

.btn-success:hover {
  background: #15803d;
}

.result-block {
  margin-bottom: 1.25rem;
}

.result-block h4 {
  font-size: 0.85rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 0.5rem;
}

.code-block {
  background: #0f172a;
  color: #e2e8f0;
  padding: 0.875rem;
  border-radius: 6px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  overflow-x: auto;
  max-height: 200px;
  overflow-y: auto;
  line-height: 1.5;
}

.code-block.optimized {
  border-left: 3px solid #22c55e;
}

.problem-list, .suggestion-list {
  list-style: none;
  padding: 0;
}

.problem-list li, .suggestion-list li {
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.375rem;
  border-radius: 6px;
  font-size: 0.85rem;
  line-height: 1.5;
}

.problem-list li {
  background: #fef2f2;
  color: #dc2626;
}

.suggestion-list li {
  background: #eff6ff;
  color: #1d4ed8;
}

.rag-sources {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.rag-tag {
  background: #f1f5f9;
  color: #475569;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-family: 'Consolas', monospace;
}

.feedback-section {
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.feedback-section h4 {
  margin-bottom: 0.5rem;
}

.stars {
  display: flex;
  gap: 0.25rem;
  margin-bottom: 0.75rem;
}

.star {
  font-size: 1.5rem;
  color: #d1d5db;
  cursor: pointer;
  transition: color 0.15s;
}

.star.filled {
  color: #f59e0b;
}

.input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.85rem;
  margin-bottom: 0.75rem;
}

.input:focus {
  outline: none;
  border-color: #2563eb;
}

@media (max-width: 900px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}
</style>
