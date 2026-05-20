<template>
  <div class="natural-to-sql-page">
    <div class="page-header">
      <h1>自然语言转SQL</h1>
      <p>用自然语言描述您的查询需求，AI将自动生成SQL语句</p>
    </div>

    <div class="main-content">
      <div class="input-section">
        <div class="card">
          <div class="card-header">输入描述</div>
          <div class="card-body">
            <div class="form-group">
              <label>自然语言描述</label>
              <textarea
                v-model="inputText"
                :rows="6"
                placeholder="例如：查询2024年1月的订单总金额，按客户分组..."
                class="form-textarea"
              ></textarea>
            </div>
            <div class="form-group">
              <label>目标表（可选）</label>
              <input v-model="tableName" placeholder="例如：orders, customers" class="form-input" />
            </div>
            <div class="form-actions">
              <button class="btn btn-primary" :disabled="loading" @click="convertToSql">
                {{ loading ? '生成中...' : '生成SQL' }}
              </button>
              <button class="btn btn-outline" @click="clearInput">清空</button>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">示例</div>
          <div class="card-body">
            <div class="examples">
              <div class="example-item" @click="useExample('查询所有状态为活跃的用户')">
                查询所有状态为活跃的用户
              </div>
              <div class="example-item" @click="useExample('计算每个部门的员工数量')">
                计算每个部门的员工数量
              </div>
              <div class="example-item" @click="useExample('查询订单金额大于1000的订单详情')">
                查询订单金额大于1000的订单详情
              </div>
              <div class="example-item" @click="useExample('找出最近一周注册的用户')">
                找出最近一周注册的用户
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="output-section">
        <div class="card" v-if="result">
          <div class="card-header">生成的SQL</div>
          <div class="card-body">
            <pre class="code-block sql-result">{{ result }}</pre>
            <div class="copy-section">
              <button class="btn btn-success" @click="copySql">复制SQL</button>
              <button class="btn btn-primary" @click="optimizeGeneratedSql">优化SQL</button>
            </div>
          </div>
        </div>

        <div class="card" v-if="executionResult">
          <div class="card-header">执行结果</div>
          <div class="card-body">
            <div class="execution-status" :class="executionResult.success ? 'success' : 'error'">
              <span>{{ executionResult.success ? '执行成功' : '执行失败' }}</span>
            </div>
            <div v-if="executionResult.message" class="execution-message">
              {{ executionResult.message }}
            </div>
          </div>
        </div>

        <div class="card feedback-section" v-if="result">
          <div class="card-header">反馈评价</div>
          <div class="card-body">
            <div class="stars">
              <span v-for="n in 5" :key="n" class="star" :class="{ filled: n <= rating }" @click="rating = n">&#9733;</span>
            </div>
            <input v-model="comment" placeholder="请输入您的评价..." class="form-input" />
            <button class="btn btn-success" @click="submitFeedback">提交</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { aiSqlApi, memoryApi } from '../api'

const inputText = ref('')
const tableName = ref('')
const loading = ref(false)
const result = ref(null)
const executionResult = ref(null)
const rating = ref(3)
const comment = ref('')

const convertToSql = async () => {
  if (!inputText.value.trim()) {
    alert('请输入查询描述')
    return
  }

  loading.value = true
  result.value = null
  executionResult.value = null

  try {
    const response = await aiSqlApi.naturalToSql(inputText.value)
    result.value = response.data.sql || response.data

    await memoryApi.addConversation('user_' + Date.now(), inputText.value, 'user')
    await memoryApi.addConversation('user_' + Date.now(), result.value, 'assistant')
  } catch (error) {
    console.error('Conversion failed:', error)
    alert('转换失败，请检查后端服务是否正常运行')
  } finally {
    loading.value = false
  }
}

const optimizeGeneratedSql = async () => {
  if (!result.value) return

  loading.value = true

  try {
    const response = await aiSqlApi.optimize(result.value)
    result.value = response.data.optimizedSql || response.data
  } catch (error) {
    console.error('Optimization failed:', error)
    alert('优化失败')
  } finally {
    loading.value = false
  }
}

const copySql = async () => {
  if (!result.value) return

  try {
    await navigator.clipboard.writeText(result.value)
    alert('SQL已复制到剪贴板')
  } catch (error) {
    console.error('Copy failed:', error)
    alert('复制失败')
  }
}

const useExample = (example) => {
  inputText.value = example
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
  inputText.value = ''
  tableName.value = ''
  result.value = null
  executionResult.value = null
}
</script>

<style scoped>
.natural-to-sql-page {
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
  margin-bottom: 1.5rem;
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

.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-family: inherit;
  font-size: 0.875rem;
  line-height: 1.5;
  resize: vertical;
  color: #1e293b;
}

.form-textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
}

.form-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #1e293b;
}

.form-input:focus {
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

.examples {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.example-item {
  background: #f8fafc;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s ease;
  border: 1px solid #e2e8f0;
}

.example-item:hover {
  background: #eff6ff;
  color: #2563eb;
  border-color: #2563eb;
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

.sql-result {
  border-left: 3px solid #22c55e;
}

.copy-section {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.execution-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.execution-status.success {
  background: #dcfce7;
  color: #16a34a;
}

.execution-status.error {
  background: #fee2e2;
  color: #dc2626;
}

.execution-message {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 6px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  color: #475569;
}

.feedback-section {
  margin-top: 0;
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

@media (max-width: 900px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}
</style>
