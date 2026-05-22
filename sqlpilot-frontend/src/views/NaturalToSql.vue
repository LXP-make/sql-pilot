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
                style="font-family:var(--font-sans);"
              ></textarea>
            </div>
            <div class="form-group">
              <label>目标表（可选）</label>
              <input v-model="tableName" placeholder="例如：orders, customers" class="form-input" />
            </div>
            <div class="form-actions">
              <button class="btn btn-primary" :disabled="loading" @click="convertToSql">
                <span v-if="loading" class="spinner"></span>
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
              <button class="example-chip" @click="useExample('查询所有状态为活跃的用户')">
                查询所有状态为活跃的用户
              </button>
              <button class="example-chip" @click="useExample('计算每个部门的员工数量')">
                计算每个部门的员工数量
              </button>
              <button class="example-chip" @click="useExample('查询订单金额大于1000的订单详情')">
                查询订单金额大于1000的订单详情
              </button>
              <button class="example-chip" @click="useExample('找出最近一周注册的用户')">
                找出最近一周注册的用户
              </button>
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
              <button class="btn btn-primary" :disabled="loading" @click="optimizeGeneratedSql">
                <span v-if="loading" class="spinner"></span>
                {{ loading ? '优化中...' : '优化SQL' }}
              </button>
            </div>
          </div>
        </div>

        <div class="card" v-if="executionResult">
          <div class="card-header">执行结果</div>
          <div class="card-body">
            <div class="execution-status" :class="executionResult.success ? 'success' : 'error'">
              {{ executionResult.success ? '执行成功' : '执行失败' }}
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
            <input v-model="comment" placeholder="请输入您的评价..." class="form-input" style="margin-bottom:0.75rem;" />
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
    const tableSchema = tableName.value ? { table: tableName.value } : null
    const response = await aiSqlApi.naturalToSql(inputText.value, tableSchema)
    result.value = response.data?.data?.generated_sql || response.data?.data?.sql || response.data

    await memoryApi.addConversation('user_1', inputText.value, 'user')
    if (result.value) {
      await memoryApi.addConversation('user_1', result.value, 'assistant')
    }
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
    alert('复制失败，请手动复制')
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
      'user_1',
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

.examples {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.example-chip {
  background: var(--gray-50);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  color: var(--gray-500);
  cursor: pointer;
  border: 1px solid var(--gray-200);
  transition: all var(--transition-fast);
  font-family: inherit;
}
.example-chip:hover {
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.sql-result {
  border-left: 3px solid var(--color-success);
}

.copy-section {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-4);
}

.execution-message {
  background: var(--gray-100);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--gray-600);
}
</style>
