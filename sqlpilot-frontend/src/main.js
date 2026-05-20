const { createApp, ref, onMounted } = Vue
const { createRouter, createWebHistory } = VueRouter

const StarRating = {
  props: ['modelValue'],
  emits: ['update:modelValue'],
  template: `
    <div class="rating-stars">
      <span v-for="i in 5" :key="i"
            class="star"
            :class="{ active: i <= modelValue }"
            @click="$emit('update:modelValue', i)">&#9733;</span>
    </div>
  `
}

const Home = {
  template: `
    <div>
      <div class="hero-section">
        <div class="hero-content">
          <h1 class="hero-title">SQL Pilot</h1>
          <p class="hero-subtitle">SQL性能优化助手</p>
          <p class="hero-desc">基于RAG技术和大厂SQL规范知识库，智能分析和优化您的SQL查询</p>
          <div class="hero-buttons">
            <router-link to="/optimize"><button class="btn btn-primary">开始优化</button></router-link>
            <router-link to="/natural-to-sql"><button class="btn btn-secondary">自然语言转SQL</button></router-link>
          </div>
        </div>
      </div>
      <div class="features-grid">
        <div class="feature-card"><h3>SQL分析</h3><p>识别查询中的性能瓶颈，检测SELECT *、索引失效等常见问题</p></div>
        <div class="feature-card"><h3>AI优化</h3><p>基于大厂SQL规范知识库，提供精准的优化建议</p></div>
        <div class="feature-card"><h3>自然语言转SQL</h3><p>用自然语言描述查询需求，自动生成对应的SQL语句</p></div>
        <div class="feature-card"><h3>规则引擎</h3><p>内置阿里巴巴、腾讯等大厂SQL规范规则，自动检测不良写法</p></div>
        <div class="feature-card"><h3>记忆系统</h3><p>记录对话历史，提供上下文感知的优化建议</p></div>
        <div class="feature-card"><h3>知识库</h3><p>集成大厂SQL规范，持续更新知识库内容</p></div>
      </div>
      <div class="card" v-if="stats">
        <h2 class="card-title">系统概览</h2>
        <div class="stats-grid">
          <div class="stat-card"><div class="stat-value">{{ stats.sql_analysis_history }}</div><div class="stat-label">分析记录</div></div>
          <div class="stat-card"><div class="stat-value">{{ stats.optimization_suggestion }}</div><div class="stat-label">优化建议</div></div>
          <div class="stat-card"><div class="stat-value">{{ stats.index_suggestion }}</div><div class="stat-label">索引建议</div></div>
        </div>
      </div>
    </div>
  `,
  setup() {
    const stats = ref(null)
    onMounted(async () => {
      try {
        const response = await axios.get('/api/memory/table-stats')
        if (response.data.success) stats.value = response.data.data
      } catch (e) { console.error(e) }
    })
    return { stats }
  }
}

const SqlOptimize = {
  components: { StarRating },
  template: `
    <div>
      <div class="page-header"><h1>SQL优化</h1><p>输入SQL查询，获取基于大厂规范的优化建议</p></div>
      <div class="main-content">
        <div>
          <div class="card">
            <h2 class="card-title">输入SQL</h2>
            <div class="form-group">
              <label>数据库类型</label>
              <select v-model="dbType">
                <option value="MYSQL">MySQL</option>
                <option value="POSTGRESQL">PostgreSQL</option>
                <option value="SQLSERVER">SQL Server</option>
              </select>
            </div>
            <div class="form-group">
              <label>SQL查询</label>
              <textarea v-model="inputSql" rows="8" placeholder="请输入需要优化的SQL查询..."></textarea>
            </div>
            <div class="form-actions">
              <button class="btn btn-primary" :class="{ loading: loading }" :disabled="loading" @click="optimizeSql">{{ loading ? '优化中...' : '开始优化' }}</button>
              <button class="btn btn-secondary" @click="clearForm">清空</button>
            </div>
          </div>
        </div>
        <div>
          <div class="card" v-if="result">
            <h2 class="card-title">优化结果</h2>
            <div v-if="result.original_sql" style="margin-bottom: 1rem;">
              <h4 style="font-size:0.85rem; font-weight:600; color:#475569; margin-bottom:0.5rem;">原始SQL</h4>
              <pre class="code-block">{{ result.original_sql }}</pre>
            </div>
            <div v-if="result.optimized_sql" style="margin-bottom: 1rem;">
              <h4 style="font-size:0.85rem; font-weight:600; color:#475569; margin-bottom:0.5rem;">优化后SQL</h4>
              <pre class="code-block" style="border-left: 3px solid #22c55e;">{{ result.optimized_sql }}</pre>
            </div>
            <div v-if="result.problems && result.problems.length > 0" style="margin-bottom: 1rem;">
              <h4 style="font-size:0.85rem; font-weight:600; color:#475569; margin-bottom:0.5rem;">发现的问题</h4>
              <div v-for="(p, i) in result.problems" :key="i" style="background:#fef2f2; color:#dc2626; padding:0.5rem 0.75rem; border-radius:6px; margin-bottom:0.25rem; font-size:0.85rem;">{{ p }}</div>
            </div>
            <div v-if="result.suggestions && result.suggestions.length > 0" style="margin-bottom: 1rem;">
              <h4 style="font-size:0.85rem; font-weight:600; color:#475569; margin-bottom:0.5rem;">优化建议</h4>
              <div v-for="(s, i) in result.suggestions" :key="i" style="background:#eff6ff; color:#1d4ed8; padding:0.5rem 0.75rem; border-radius:6px; margin-bottom:0.25rem; font-size:0.85rem;">{{ s.description || s }}</div>
            </div>
            <div v-if="result.rag_info && result.rag_info.length > 0" style="margin-bottom: 1rem;">
              <h4 style="font-size:0.85rem; font-weight:600; color:#475569; margin-bottom:0.5rem;">知识来源</h4>
              <div style="display:flex; flex-wrap:wrap; gap:0.375rem;">
                <span v-for="(doc, i) in result.rag_info" :key="i" style="background:#f1f5f9; color:#475569; padding:0.25rem 0.5rem; border-radius:4px; font-size:0.75rem; font-family:Consolas,monospace;">{{ doc.filename }}</span>
              </div>
            </div>
            <div style="margin-bottom: 1rem; padding-top: 1rem; border-top: 1px solid #e2e8f0;">
              <h4 style="font-size:0.85rem; font-weight:600; color:#475569; margin-bottom:0.75rem;">性能对比</h4>
              <div style="display:flex; gap:0.5rem; margin-bottom:0.75rem;">
                <button class="btn btn-sm btn-primary" :disabled="execLoading" @click="executeSql(result.original_sql, 'original')">{{ execLoading && executingTarget === 'original' ? '执行中...' : '执行原始SQL' }}</button>
                <button class="btn btn-sm btn-success" :disabled="execLoading" @click="executeSql(result.optimized_sql, 'optimized')">{{ execLoading && executingTarget === 'optimized' ? '执行中...' : '执行优化后SQL' }}</button>
              </div>
              <div v-if="originalExecResult || optimizedExecResult" style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem;">
                <div v-if="originalExecResult" style="border:1px solid #e2e8f0; border-radius:6px; padding:0.75rem;">
                  <div style="font-size:0.75rem; font-weight:600; color:#64748b; margin-bottom:0.5rem;">原始SQL</div>
                  <div v-if="originalExecResult.success" style="font-size:0.85rem;">
                    <span style="color:#16a34a; font-weight:600;">成功</span>
                    <div style="margin-top:0.375rem; color:#475569;">耗时: <strong>{{ originalExecResult.executionTimeMs }}</strong> ms</div>
                    <div style="color:#475569;">行数: <strong>{{ originalExecResult.rowCount }}</strong></div>
                  </div>
                  <div v-else style="font-size:0.8rem; color:#dc2626;">{{ originalExecResult.error }}</div>
                </div>
                <div v-if="optimizedExecResult" style="border:1px solid #e2e8f0; border-radius:6px; padding:0.75rem;">
                  <div style="font-size:0.75rem; font-weight:600; color:#64748b; margin-bottom:0.5rem;">优化后SQL</div>
                  <div v-if="optimizedExecResult.success" style="font-size:0.85rem;">
                    <span style="color:#16a34a; font-weight:600;">成功</span>
                    <div style="margin-top:0.375rem; color:#475569;">耗时: <strong>{{ optimizedExecResult.executionTimeMs }}</strong> ms</div>
                    <div style="color:#475569;">行数: <strong>{{ optimizedExecResult.rowCount }}</strong></div>
                  </div>
                  <div v-else style="font-size:0.8rem; color:#dc2626;">{{ optimizedExecResult.error }}</div>
                </div>
              </div>
              <div v-if="originalExecResult && originalExecResult.success && optimizedExecResult && optimizedExecResult.success && optimizedExecResult.executionTimeMs > 0" style="margin-top:0.5rem; padding:0.5rem; background:#f0fdf4; border-radius:6px; font-size:0.85rem;">
                性能提升: <strong style="color:#16a34a;">{{ Math.round((1 - optimizedExecResult.executionTimeMs / originalExecResult.executionTimeMs) * 100) }}%</strong>
                <span style="color:#64748b;">({{ originalExecResult.executionTimeMs }}ms → {{ optimizedExecResult.executionTimeMs }}ms)</span>
              </div>
            </div>
            <div class="feedback-section">
              <h4>反馈评价</h4>
              <star-rating v-model="rating"></star-rating>
              <div class="form-group">
                <input type="text" v-model="comment" placeholder="输入评价...">
              </div>
              <button class="btn btn-success" @click="submitFeedback">提交</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  setup() {
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
          axios.post('/api/memory/conversation', null, { params: { userId: 'user_1', content: inputSql.value, role: 'user' } })
          axios.post('/api/memory/conversation', null, { params: { userId: 'user_1', content: data.data.optimized_sql, role: 'assistant' } })
        } else {
          throw new Error(data.message || '优化失败')
        }
      } catch (e) {
        console.error(e)
        alert('优化失败，请检查后端服务是否正常运行')
      }
      loading.value = false
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
      } catch (e) {
        const errResult = { success: false, error: e.message || '执行失败', executionTimeMs: 0, rowCount: 0 }
        if (target === 'original') originalExecResult.value = errResult
        else optimizedExecResult.value = errResult
      }
      execLoading.value = false
    }

    const submitFeedback = async () => {
      if (!result.value) return
      alert('感谢您的反馈！')
      rating.value = 3
      comment.value = ''
    }

    const clearForm = () => { inputSql.value = ''; result.value = null; originalExecResult.value = null; optimizedExecResult.value = null }

    return { dbType, inputSql, loading, result, rating, comment, originalExecResult, optimizedExecResult, execLoading, executingTarget, optimizeSql, executeSql, submitFeedback, clearForm }
  }
}

const NaturalToSql = {
  template: `
    <div>
      <div class="page-header"><h1>自然语言转SQL</h1><p>用自然语言描述您的查询需求，AI将自动生成SQL语句</p></div>
      <div class="main-content">
        <div>
          <div class="card">
            <h2 class="card-title">输入描述</h2>
            <div class="form-group">
              <label>自然语言描述</label>
              <textarea v-model="inputText" rows="6" placeholder="例如：查询2024年1月的订单总金额，按客户分组..."></textarea>
            </div>
            <div class="form-group">
              <label>目标表（可选）</label>
              <input type="text" v-model="tableName" placeholder="例如：orders, customers">
            </div>
            <div class="form-actions">
              <button class="btn btn-primary" :class="{ loading: loading }" :disabled="loading" @click="convertToSql">{{ loading ? '生成中...' : '生成SQL' }}</button>
              <button class="btn btn-secondary" @click="clearForm">清空</button>
            </div>
            <div class="examples">
              <div class="example-item" @click="inputText = '查询所有状态为活跃的用户'">查询所有状态为活跃的用户</div>
              <div class="example-item" @click="inputText = '计算每个部门的员工数量'">计算每个部门的员工数量</div>
              <div class="example-item" @click="inputText = '查询订单金额大于1000的订单详情'">查询订单金额大于1000的订单详情</div>
              <div class="example-item" @click="inputText = '找出最近一周注册的用户'">找出最近一周注册的用户</div>
            </div>
          </div>
        </div>
        <div>
          <div class="card" v-if="result">
            <h2 class="card-title">生成的SQL</h2>
            <pre class="code-block" style="border-left: 3px solid #22c55e;">{{ result }}</pre>
            <div class="form-actions">
              <button class="btn btn-success" @click="copySql">复制SQL</button>
            </div>
          </div>
          <div class="card" v-if="executionResult">
            <h2 class="card-title">执行结果</h2>
            <div class="execution-status" :class="executionResult.success ? 'success' : 'error'">
              <span>{{ executionResult.success ? '执行成功' : '执行失败' }}</span>
            </div>
            <div v-if="executionResult.message" style="background:#f8fafc; padding:1rem; border-radius:6px; font-family:Consolas,monospace; font-size:13px; color:#475569;">{{ executionResult.message }}</div>
          </div>
        </div>
      </div>
    </div>
  `,
  setup() {
    const inputText = ref('')
    const tableName = ref('')
    const loading = ref(false)
    const result = ref(null)
    const executionResult = ref(null)

    const convertToSql = async () => {
      if (!inputText.value.trim()) return alert('请输入查询描述')
      loading.value = true
      result.value = null
      executionResult.value = null
      try {
        const body = { natural_query: inputText.value }
        if (tableName.value) body.table_schema = { table: tableName.value }
        const response = await axios.post('/ai/natural-to-sql', body)
        const data = response.data
        if (data.success && data.data) {
          result.value = data.data.generated_sql
          axios.post('/api/memory/conversation', null, { params: { userId: 'user_1', content: inputText.value, role: 'user' } })
          if (data.data.generated_sql) {
            axios.post('/api/memory/conversation', null, { params: { userId: 'user_1', content: data.data.generated_sql, role: 'assistant' } })
          }
        } else {
          throw new Error(data.message || '转换失败')
        }
      } catch (e) {
        console.error(e)
        alert('转换失败，请检查后端服务是否正常运行')
      }
      loading.value = false
    }

    const copySql = async () => {
      try { await navigator.clipboard.writeText(result.value); alert('SQL已复制到剪贴板') }
      catch (e) { alert('复制失败') }
    }

    const clearForm = () => { inputText.value = ''; tableName.value = ''; result.value = null; executionResult.value = null }

    return { inputText, tableName, loading, result, executionResult, convertToSql, copySql, clearForm }
  }
}

const History = {
  template: `
    <div>
      <div class="page-header"><h1>历史记录</h1><p>查看您的SQL分析和优化历史</p></div>
      <div class="card" style="margin-bottom:1.5rem;">
        <div class="filter-row">
          <input type="text" v-model="searchKeyword" placeholder="搜索SQL内容...">
          <select v-model="filterType">
            <option value="all">全部</option>
            <option value="optimize">SQL优化</option>
            <option value="natural">自然语言转SQL</option>
          </select>
          <button class="btn btn-primary" @click="loadHistory">搜索</button>
          <button class="btn btn-secondary" @click="clearFilters">清除筛选</button>
        </div>
      </div>
      <div v-if="hasData">
        <div class="timeline">
          <div v-for="(item, i) in historyList" :key="i" class="timeline-item">
            <div class="timeline-dot" :class="item.optimizedSql === 'user' ? 'user' : 'assistant'"></div>
            <div class="card" style="margin-bottom:0;">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                <span class="history-type" :class="item.optimizedSql === 'user' ? 'user' : 'assistant'">{{ item.optimizedSql === 'user' ? '用户查询' : 'AI回复' }}</span>
                <span style="font-size:0.8rem; color:#94a3b8;">{{ formatTime(item.createdAt) }}</span>
              </div>
              <pre class="code-block" style="max-height:150px; margin-bottom:0.75rem;">{{ truncateContent(item.originalSql) }}</pre>
              <div class="form-actions">
                <button class="btn btn-sm btn-secondary" @click="viewDetail(item)">查看详情</button>
                <button class="btn btn-sm btn-secondary" @click="copyContent(item.originalSql)">复制</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <p>暂无历史记录</p>
        <p class="empty-hint">开始使用SQL优化或自然语言转SQL功能，记录将保存在这里</p>
      </div>
      <div class="pagination" v-if="total > pageSize">
        <button class="btn btn-sm btn-secondary" :disabled="currentPage <= 1" @click="currentPage > 1 && handlePageChange(currentPage - 1)">上一页</button>
        <span class="page-info">{{ currentPage }} / {{ Math.ceil(total / pageSize) }}</span>
        <button class="btn btn-sm btn-secondary" :disabled="currentPage >= Math.ceil(total / pageSize)" @click="currentPage < Math.ceil(total / pageSize) && handlePageChange(currentPage + 1)">下一页</button>
      </div>
    </div>
  `,
  setup() {
    const historyList = ref([])
    const hasData = ref(false)
    const searchKeyword = ref('')
    const filterType = ref('all')
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = ref(0)

    onMounted(() => { loadHistory() })

    const loadHistory = async () => {
      try {
        const response = await axios.get('/api/memory/conversation/user_1')
        if (response.data.success) {
          historyList.value = response.data.data || []
          hasData.value = historyList.value.length > 0
          total.value = historyList.value.length
        }
      } catch (e) { console.error(e) }
    }

    const formatTime = (ts) => {
      if (!ts) return '未知时间'
      return new Date(ts).toLocaleString('zh-CN')
    }

    const truncateContent = (content) => {
      if (!content || content.length <= 200) return content || ''
      return content.substring(0, 200) + '...'
    }

    const viewDetail = (item) => { alert('内容详情:\n\n' + (item.originalSql || item.optimizedSql)) }

    const copyContent = async (content) => {
      try { await navigator.clipboard.writeText(content); alert('已复制到剪贴板') }
      catch (e) { alert('复制失败') }
    }

    const clearFilters = () => { searchKeyword.value = ''; filterType.value = 'all'; loadHistory() }

    const handlePageChange = (page) => { currentPage.value = page }

    return { historyList, hasData, searchKeyword, filterType, currentPage, pageSize, total, loadHistory, formatTime, truncateContent, viewDetail, copyContent, clearFilters, handlePageChange }
  }
}

const Feedback = {
  components: { StarRating },
  template: `
    <div>
      <div class="page-header"><h1>用户反馈</h1><p>帮助我们改进服务质量</p></div>
      <div class="main-content">
        <div>
          <div class="card">
            <h2 class="card-title">提交反馈</h2>
            <div class="form-group">
              <label>您的评分</label>
              <star-rating v-model="rating"></star-rating>
            </div>
            <div class="form-group">
              <label>反馈类型</label>
              <select v-model="feedbackType">
                <option value="suggestion">功能建议</option>
                <option value="bug">Bug报告</option>
                <option value="experience">使用体验</option>
                <option value="other">其他</option>
              </select>
            </div>
            <div class="form-group">
              <label>详细描述</label>
              <textarea v-model="feedbackContent" rows="6" placeholder="请详细描述您的反馈内容..."></textarea>
            </div>
            <div class="form-group">
              <label>联系方式（可选）</label>
              <input type="text" v-model="contact" placeholder="邮箱或手机号">
            </div>
            <div class="form-actions">
              <button class="btn btn-primary" :class="{ loading: submitting }" :disabled="submitting" @click="submitFeedback">{{ submitting ? '提交中...' : '提交反馈' }}</button>
              <button class="btn btn-secondary" @click="resetForm">重置</button>
            </div>
          </div>
        </div>
        <div>
          <div class="card">
            <h2 class="card-title">反馈统计</h2>
            <div class="stats-grid">
              <div class="stat-card"><div class="stat-value">4.8</div><div class="stat-label">平均评分</div></div>
              <div class="stat-card"><div class="stat-value">{{ feedbackCount }}</div><div class="stat-label">总反馈数</div></div>
              <div class="stat-card"><div class="stat-value">85%</div><div class="stat-label">好评率</div></div>
            </div>
          </div>
          <div class="card">
            <h2 class="card-title">用户评价</h2>
            <div v-if="reviews.length > 0">
              <div v-for="(review, i) in reviews" :key="i" style="padding:1rem 0; border-bottom:1px solid #e2e8f0;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                  <div class="rating-stars" style="font-size:1rem;">
                    <span v-for="n in 5" :key="n" class="star" :class="{ active: n <= review.rating }" style="font-size:1rem;">&#9733;</span>
                  </div>
                  <span style="font-size:0.8rem; color:#94a3b8;">{{ review.time }}</span>
                </div>
                <p style="color:#475569; font-size:0.85rem; line-height:1.5; margin-bottom:0.5rem;">{{ review.content }}</p>
                <span style="font-size:0.75rem; color:#2563eb; background:#eff6ff; padding:0.2rem 0.5rem; border-radius:4px; display:inline-block;">{{ getTypeLabel(review.type) }}</span>
              </div>
            </div>
            <div v-else style="text-align:center; color:#94a3b8; padding:2rem 0;">暂无评价</div>
          </div>
        </div>
      </div>
    </div>
  `,
  setup() {
    const rating = ref(5)
    const feedbackType = ref('suggestion')
    const feedbackContent = ref('')
    const contact = ref('')
    const submitting = ref(false)
    const feedbackCount = ref(0)

    const reviews = ref([
      { rating: 5, content: 'AI优化功能非常好用，帮我发现了很多SQL性能问题！', type: 'experience', time: '2024-01-15' },
      { rating: 5, content: '自然语言转SQL功能很强大，节省了很多写SQL的时间。', type: 'experience', time: '2024-01-14' },
      { rating: 4, content: '希望能支持更多数据库类型，比如Oracle。', type: 'suggestion', time: '2024-01-13' },
      { rating: 5, content: '界面简洁美观，使用体验很好！', type: 'experience', time: '2024-01-12' },
      { rating: 4, content: '建议增加批量优化功能，可以一次优化多个SQL。', type: 'suggestion', time: '2024-01-11' }
    ])

    const getTypeLabel = (type) => {
      const labels = { suggestion: '功能建议', bug: 'Bug报告', experience: '使用体验', other: '其他' }
      return labels[type] || '其他'
    }

    const submitFeedback = async () => {
      if (!feedbackContent.value.trim()) return alert('请填写反馈内容')
      submitting.value = true
      try {
        await axios.post('/api/memory/feedback', {
          conversationId: 'feedback_' + Date.now(),
          userId: 'user_' + Date.now(),
          rating: rating.value,
          comment: feedbackContent.value
        })
        reviews.value.unshift({ rating: rating.value, content: feedbackContent.value, type: feedbackType.value, time: new Date().toLocaleDateString('zh-CN') })
        feedbackCount.value++
        alert('感谢您的反馈！我们会认真对待每一条建议。')
        resetForm()
      } catch (e) { alert('提交失败，请稍后重试') }
      submitting.value = false
    }

    const resetForm = () => { rating.value = 5; feedbackType.value = 'suggestion'; feedbackContent.value = ''; contact.value = '' }

    return { rating, feedbackType, feedbackContent, contact, submitting, feedbackCount, reviews, getTypeLabel, submitFeedback, resetForm }
  }
}

const routes = [
  { path: '/', component: Home },
  { path: '/optimize', component: SqlOptimize },
  { path: '/natural-to-sql', component: NaturalToSql },
  { path: '/history', component: History },
  { path: '/feedback', component: Feedback }
]

const router = createRouter({ history: createWebHistory(), routes })

const App = {
  template: `
    <div class="app-container">
      <header class="app-header">
        <div class="header-content">
          <div class="logo"><span class="logo-text">SQL Pilot</span></div>
          <nav class="nav-menu">
            <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">首页</router-link>
            <router-link to="/optimize" class="nav-item" :class="{ active: $route.path === '/optimize' }">SQL优化</router-link>
            <router-link to="/natural-to-sql" class="nav-item" :class="{ active: $route.path === '/natural-to-sql' }">自然语言转SQL</router-link>
            <router-link to="/history" class="nav-item" :class="{ active: $route.path === '/history' }">历史记录</router-link>
            <router-link to="/feedback" class="nav-item" :class="{ active: $route.path === '/feedback' }">反馈</router-link>
          </nav>
        </div>
      </header>
      <main class="app-main"><router-view /></main>
      <footer class="app-footer"><p>SQL Pilot &mdash; SQL性能优化助手</p></footer>
    </div>
  `
}

const app = createApp(App)
app.use(router)
app.component('star-rating', StarRating)
app.mount('#app')
