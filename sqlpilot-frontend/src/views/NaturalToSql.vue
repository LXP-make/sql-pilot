<template>
  <div class="natural-to-sql-page">
    <div class="page-header">
      <h1>自然语言转SQL</h1>
      <p>用自然语言描述您的查询需求，AI将自动生成SQL语句</p>
    </div>

    <div class="main-content">
      <div class="input-section">
        <el-card title="输入描述">
          <div class="form-group">
            <label>自然语言描述</label>
            <el-textarea
              v-model="inputText"
              :rows="6"
              placeholder="例如：查询2024年1月的订单总金额，按客户分组..."
              class="text-textarea"
            ></el-textarea>
          </div>
          <div class="form-group">
            <label>目标表（可选）</label>
            <el-input v-model="tableName" placeholder="例如：orders, customers"></el-input>
          </div>
          <div class="form-actions">
            <el-button type="primary" :loading="loading" @click="convertToSql">
              <span v-if="!loading">✨ 生成SQL</span>
              <span v-else>生成中...</span>
            </el-button>
            <el-button @click="clearInput">清空</el-button>
          </div>
        </el-card>

        <el-card title="示例">
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
        </el-card>
      </div>

      <div class="output-section">
        <el-card title="生成的SQL" v-if="result">
          <pre class="code-block sql-result">{{ result }}</pre>
          <div class="copy-section">
            <el-button type="success" @click="copySql">📋 复制SQL</el-button>
            <el-button type="primary" @click="optimizeGeneratedSql">⚡ 优化SQL</el-button>
          </div>
        </el-card>

        <el-card title="执行结果" v-if="executionResult">
          <div class="execution-status" :class="executionResult.success ? 'success' : 'error'">
            <span class="status-icon">{{ executionResult.success ? '✅' : '❌' }}</span>
            <span>{{ executionResult.success ? '执行成功' : '执行失败' }}</span>
          </div>
          <div v-if="executionResult.message" class="execution-message">
            {{ executionResult.message }}
          </div>
        </el-card>

        <div class="feedback-section" v-if="result">
          <h4>反馈评价</h4>
          <div class="feedback-stars">
            <el-rate v-model="rating" max="5" show-text text-color="#ff9900"></el-rate>
          </div>
          <el-input v-model="comment" placeholder="请输入您的评价..."></el-input>
          <el-button type="success" @click="submitFeedback">提交反馈</el-button>
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

.text-textarea {
  font-size: 14px;
}

.form-actions {
  display: flex;
  gap: 1rem;
}

.examples {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.example-item {
  background: #f8fafc;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e2e8f0;
}

.example-item:hover {
  background: #e0e7ff;
  color: #667eea;
  border-color: #667eea;
}

.code-block {
  background: #1e293b;
  color: #e2e8f0;
  padding: 1rem;
  border-radius: 8px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  overflow-x: auto;
  max-height: 250px;
  overflow-y: auto;
}

.sql-result {
  border-left: 4px solid #10b981;
}

.copy-section {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.execution-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.execution-status.success {
  background: #dcfce7;
  color: #16a34a;
}

.execution-status.error {
  background: #fee2e2;
  color: #dc2626;
}

.status-icon {
  font-size: 1.25rem;
}

.execution-message {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 8px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  color: #475569;
}

.feedback-section {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.feedback-section h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 1rem;
}

.feedback-stars {
  margin-bottom: 1rem;
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
