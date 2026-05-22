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
              <select v-model="dbType" class="form-select">
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
                class="form-textarea"
              ></textarea>
            </div>
            <div class="form-actions">
              <button class="btn btn-primary" :disabled="loading" @click="optimizeSql">
                <span v-if="loading" class="spinner"></span>
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
            <div v-if="result.problems?.length" class="result-block">
              <h4>发现的问题</h4>
              <ul class="result-list problem-list">
                <li v-for="(p, i) in result.problems" :key="i">{{ p }}</li>
              </ul>
            </div>
            <div v-if="result.suggestions?.length" class="result-block">
              <h4>优化建议</h4>
              <ul class="result-list suggestion-list">
                <li v-for="(s, i) in result.suggestions" :key="i">{{ s.description || s }}</li>
              </ul>
            </div>
            <div v-if="result.rag_info?.length" class="result-block">
              <h4>知识来源</h4>
              <div class="rag-sources">
                <span v-for="(doc, i) in result.rag_info" :key="i" class="tag">{{ doc.filename }}</span>
              </div>
            </div>

            <!-- Performance Comparison -->
            <div class="result-block perf-section">
              <h4>性能对比</h4>
              <div class="perf-actions">
                <button
                  class="btn btn-sm btn-outline"
                  :disabled="execLoading"
                  @click="executeSql(result.original_sql, 'original')"
                >
                  <span v-if="execLoading && executingTarget === 'original'" class="spinner"></span>
                  {{ execLoading && executingTarget === 'original' ? '执行中...' : '执行原始SQL' }}
                </button>
                <button
                  class="btn btn-sm btn-success"
                  :disabled="execLoading"
                  @click="executeSql(result.optimized_sql, 'optimized')"
                >
                  <span v-if="execLoading && executingTarget === 'optimized'" class="spinner"></span>
                  {{ execLoading && executingTarget === 'optimized' ? '执行中...' : '执行优化后SQL' }}
                </button>
              </div>
              <div v-if="originalExecResult || optimizedExecResult" class="perf-results">
                <div v-if="originalExecResult" class="perf-card">
                  <div class="perf-label">原始SQL</div>
                  <div v-if="originalExecResult.success">
                    <span class="perf-badge success">成功</span>
                    <div class="perf-metric">耗时: <strong>{{ originalExecResult.executionTimeMs }}</strong> ms</div>
                    <div class="perf-metric">行数: <strong>{{ originalExecResult.rowCount }}</strong></div>
                  </div>
                  <div v-else class="perf-error">{{ originalExecResult.error }}</div>
                </div>
                <div v-if="optimizedExecResult" class="perf-card">
                  <div class="perf-label">优化后SQL</div>
                  <div v-if="optimizedExecResult.success">
                    <span class="perf-badge success">成功</span>
                    <div class="perf-metric">耗时: <strong>{{ optimizedExecResult.executionTimeMs }}</strong> ms</div>
                    <div class="perf-metric">行数: <strong>{{ optimizedExecResult.rowCount }}</strong></div>
                  </div>
                  <div v-else class="perf-error">{{ optimizedExecResult.error }}</div>
                </div>
              </div>
              <div
                v-if="originalExecResult?.success && optimizedExecResult?.success && optimizedExecResult.executionTimeMs > 0"
                class="perf-improvement"
              >
                性能提升: <strong class="improvement-value">{{ improvementPercent }}%</strong>
                <span class="improvement-detail">({{ originalExecResult.executionTimeMs }}ms &rarr; {{ optimizedExecResult.executionTimeMs }}ms)</span>
              </div>
            </div>

            <div class="feedback-section">
              <h4>反馈评价</h4>
              <div class="stars">
                <span v-for="n in 5" :key="n" class="star" :class="{ filled: n <= rating }" @click="rating = n">&#9733;</span>
              </div>
              <input v-model="comment" placeholder="输入评价..." class="form-input" style="margin-bottom:0.75rem;" />
              <button class="btn btn-success" @click="submitFeedback">提交</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'

const dbType = ref('MYSQL')
const inputSql = ref('')
const loading = ref(false)
const result = ref(null)
const rating = ref(3)
const comment = ref('')
const originalExecResult = ref(null)
const optimizedExecResult = ref(null)
const execLoading = ref(false)
const executingTarget = ref('')

const improvementPercent = computed(() => {
  if (!originalExecResult.value?.success || !optimizedExecResult.value?.success) return 0
  if (!optimizedExecResult.value.executionTimeMs) return 0
  return Math.round((1 - optimizedExecResult.value.executionTimeMs / originalExecResult.value.executionTimeMs) * 100)
})

const optimizeSql = async () => {
  if (!inputSql.value.trim()) return
  loading.value = true
  result.value = null
  originalExecResult.value = null
  optimizedExecResult.value = null

  try {
    const response = await axios.post('/ai/optimize', {
      sql: inputSql.value,
      db_type: dbType.value
    })
    const data = response.data
    if (data.success && data.data) {
      result.value = {
        original_sql: data.data.original_sql,
        optimized_sql: data.data.optimized_sql,
        problems: data.data.problems,
        suggestions: data.data.optimization_suggestions || [],
        rag_info: data.data.rag_info || []
      }
      // Save to memory in background
      axios.post('/api/memory/conversation', null, {
        params: { userId: 'user_1', content: inputSql.value, role: 'user' }
      })
      if (data.data.optimized_sql) {
        axios.post('/api/memory/conversation', null, {
          params: { userId: 'user_1', content: data.data.optimized_sql, role: 'assistant' }
        })
      }
    } else {
      throw new Error(data.message || '优化失败')
    }
  } catch (error) {
    console.error('Optimization failed:', error)
    alert('优化失败，请检查后端服务是否正常运行')
  } finally {
    loading.value = false
  }
}

const executeSql = async (sql, target) => {
  if (!sql) return
  execLoading.value = true
  executingTarget.value = target

  try {
    const response = await axios.post('/api/sql/execute', { sql, maxRows: 10 })
    const data = response.data
    if (data.success && data.data) {
      if (target === 'original') originalExecResult.value = data.data
      else optimizedExecResult.value = data.data
    } else {
      throw new Error(data.message || '执行失败')
    }
  } catch (error) {
    const errResult = { success: false, error: error.message || '执行失败', executionTimeMs: 0, rowCount: 0 }
    if (target === 'original') originalExecResult.value = errResult
    else optimizedExecResult.value = errResult
  } finally {
    execLoading.value = false
  }
}

const submitFeedback = () => {
  if (!result.value) return
  alert('感谢您的反馈！')
  rating.value = 3
  comment.value = ''
}

const clearInput = () => {
  inputSql.value = ''
  result.value = null
  originalExecResult.value = null
  optimizedExecResult.value = null
}
</script>

<style scoped>
.sql-optimize-page {
  max-width: 1200px;
  margin: 0 auto;
}

.result-block {
  margin-bottom: var(--space-5);
}
.result-block h4 {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--gray-600);
  margin-bottom: var(--space-2);
}

.result-list {
  list-style: none;
  padding: 0;
}
.result-list li {
  padding: var(--space-2) var(--space-3);
  margin-bottom: var(--space-1);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  line-height: 1.5;
}

.problem-list li {
  background: var(--color-danger-light);
  color: var(--color-danger);
}

.suggestion-list li {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.rag-sources {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
}

/* Performance */
.perf-section {
  padding-top: var(--space-4);
  border-top: 1px solid var(--gray-200);
}

.perf-actions {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.perf-results {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.perf-card {
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  background: var(--gray-50);
}

.perf-label {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--gray-500);
  margin-bottom: var(--space-2);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.perf-badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: 600;
  margin-bottom: var(--space-2);
}
.perf-badge.success {
  background: var(--color-success-light);
  color: var(--color-success);
}

.perf-metric {
  font-size: var(--text-sm);
  color: var(--gray-600);
  margin-top: var(--space-1);
}

.perf-error {
  font-size: var(--text-xs);
  color: var(--color-danger);
}

.perf-improvement {
  margin-top: var(--space-2);
  padding: var(--space-3);
  background: var(--color-success-light);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
}

.improvement-value {
  color: var(--color-success);
  font-size: var(--text-lg);
}

.improvement-detail {
  color: var(--gray-500);
  font-size: var(--text-xs);
  margin-left: var(--space-2);
}

@media (max-width: 640px) {
  .perf-results {
    grid-template-columns: 1fr;
  }
  .perf-actions {
    flex-direction: column;
  }
}
</style>
