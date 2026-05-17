const { createApp, ref, onMounted } = Vue
const { createRouter, createWebHistory } = VueRouter

const API_BASE = 'http://localhost:8081'
const AI_API_BASE = 'http://localhost:8080'

const StarRating = {
  props: ['modelValue'],
  emits: ['update:modelValue'],
  template: `
    <div class="rating-stars">
      <span v-for="i in 5" :key="i" 
            class="star" 
            :class="{ active: i <= modelValue }"
            @click="$emit('update:modelValue', i)">★</span>
    </div>
  `
}

const Home = {
  components: { StarRating },
  template: `
    <div>
      <div class="hero-section">
        <h1 class="hero-title">⚡ SQL Pilot</h1>
        <p class="hero-subtitle">AI驱动的SQL性能优化助手</p>
        <p class="hero-desc">基于RAG技术，智能分析和优化您的SQL查询，提升数据库性能</p>
        <div class="hero-buttons">
          <router-link to="/optimize"><button class="btn-primary">开始优化</button></router-link>
          <router-link to="/natural-to-sql"><button class="btn-secondary">自然语言转SQL</button></router-link>
        </div>
      </div>
      <div class="features-grid">
        <div class="feature-card"><div class="feature-icon">🔍</div><h3>SQL分析</h3><p>智能分析SQL查询的性能问题</p></div>
        <div class="feature-card"><div class="feature-icon">⚡</div><h3>AI优化</h3><p>基于RAG技术提供精准优化建议</p></div>
        <div class="feature-card"><div class="feature-icon">💬</div><h3>自然语言转SQL</h3><p>输入自然语言描述自动生成SQL</p></div>
        <div class="feature-card"><div class="feature-icon">🧠</div><h3>记忆系统</h3><p>智能记忆对话历史</p></div>
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
        const response = await axios.get(API_BASE + '/api/memory/table-stats')
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
      <div class="page-header"><h1>SQL优化</h1><p>输入您的SQL查询，AI将为您提供优化建议</p></div>
      <div class="main-content">
        <div>
          <div class="card">
            <h3 class="card-title">输入SQL</h3>
            <div class="form-group">
              <label>SQL查询</label>
              <textarea v-model="inputSql" rows="8" placeholder="请输入需要优化的SQL查询..."></textarea>
            </div>
            <div class="form-actions">
              <button class="btn-primary" :class="{ loading: loading }" @click="optimizeSql">{{ loading ? '优化中...' : '🚀 开始优化' }}</button>
              <button class="btn-secondary" @click="clearForm">清空</button>
            </div>
          </div>
        </div>
        <div>
          <div class="card" v-if="result">
            <h3 class="card-title">优化结果</h3>
            <div v-if="result.originalSql"><h4>原始SQL</h4><pre class="code-block">{{ result.originalSql }}</pre></div>
            <div v-if="result.optimizedSql"><h4>优化后SQL</h4><pre class="code-block" style="border-left: 4px solid #10b981;">{{ result.optimizedSql }}</pre></div>
            <div class="feedback-section">
              <h4>反馈评价</h4>
              <star-rating v-model="rating"></star-rating>
              <div class="form-group">
                <input type="text" v-model="comment" placeholder="请输入您的评价...">
              </div>
              <button class="btn-primary" @click="submitFeedback">提交反馈</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  setup() {
    const inputSql = ref('')
    const loading = ref(false)
    const result = ref(null)
    const rating = ref(3)
    const comment = ref('')
    
    const optimizeSql = async () => {
      if (!inputSql.value.trim()) return alert('请输入SQL查询')
      loading.value = true
      try {
        const response = await axios.post(AI_API_BASE + '/ai/optimize', { sql: inputSql.value })
        const data = response.data
        if (data.success && data.data) {
          result.value = {
            originalSql: data.data.original_sql,
            optimizedSql: data.data.optimized_sql
          }
        }
      } catch (e) { alert('优化失败，请检查后端服务') }
      loading.value = false
    }
    
    const submitFeedback = async () => {
      try {
        await axios.post(API_BASE + '/api/memory/feedback', { conversationId: 'conv_' + Date.now(), userId: 'user_' + Date.now(), rating: rating.value, comment: comment.value })
        alert('感谢反馈！'); rating.value = 3; comment.value = ''
      } catch (e) { alert('提交失败') }
    }
    
    const clearForm = () => { inputSql.value = ''; result.value = null }
    
    return { inputSql, loading, result, rating, comment, optimizeSql, submitFeedback, clearForm }
  }
}

const NaturalToSql = {
  template: `
    <div>
      <div class="page-header"><h1>自然语言转SQL</h1><p>用自然语言描述您的查询需求</p></div>
      <div class="main-content">
        <div>
          <div class="card">
            <h3 class="card-title">输入描述</h3>
            <div class="form-group">
              <label>自然语言描述</label>
              <textarea v-model="inputText" rows="6" placeholder="例如：查询所有状态为活跃的用户"></textarea>
            </div>
            <div class="form-actions">
              <button class="btn-primary" :class="{ loading: loading }" @click="convertToSql">{{ loading ? '生成中...' : '✨ 生成SQL' }}</button>
            </div>
            <div class="examples">
              <div class="example-item" @click="inputText = '查询所有状态为活跃的用户'">查询所有状态为活跃的用户</div>
              <div class="example-item" @click="inputText = '计算每个部门的员工数量'">计算每个部门的员工数量</div>
              <div class="example-item" @click="inputText = '查询订单金额大于1000的订单详情'">查询订单金额大于1000的订单详情</div>
            </div>
          </div>
        </div>
        <div>
          <div class="card" v-if="result">
            <h3 class="card-title">生成的SQL</h3>
            <pre class="code-block" style="border-left: 4px solid #10b981;">{{ result }}</pre>
            <div class="form-actions">
              <button class="btn-secondary" @click="copySql">📋 复制SQL</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  setup() {
    const inputText = ref('')
    const loading = ref(false)
    const result = ref(null)
    
    const convertToSql = async () => {
      if (!inputText.value.trim()) return alert('请输入查询描述')
      loading.value = true
      try {
        const response = await axios.post(AI_API_BASE + '/ai/natural-to-sql', { natural_query: inputText.value })
        const data = response.data
        if (data.success && data.data) {
          result.value = data.data.generated_sql
        }
      } catch (e) { alert('转换失败，请检查后端服务') }
      loading.value = false
    }
    
    const copySql = async () => {
      try { await navigator.clipboard.writeText(result.value); alert('已复制到剪贴板') }
      catch (e) { alert('复制失败') }
    }
    
    return { inputText, loading, result, convertToSql, copySql }
  }
}

const History = {
  template: `
    <div>
      <div class="page-header"><h1>历史记录</h1><p>查看您的SQL分析和优化历史</p></div>
      <div v-if="!hasData" class="card" style="text-align: center; padding: 4rem;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">📋</div>
        <p>暂无历史记录</p>
        <p style="color: #94a3b8; font-size: 0.9rem;">开始使用SQL优化或自然语言转SQL功能</p>
      </div>
      <div v-else>
        <div class="card" v-for="(item, i) in historyList" :key="i">
          <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
            <span>{{ item.type === 'user' ? '👤 用户查询' : '🤖 AI回复' }}</span>
          </div>
          <pre class="code-block">{{ item.content }}</pre>
        </div>
      </div>
    </div>
  `,
  setup() {
    const historyList = ref([])
    const hasData = ref(false)
    onMounted(async () => {
      try {
        const response = await axios.get(API_BASE + '/api/memory/conversation/user_1')
        if (response.data.success) { historyList.value = response.data.data; hasData.value = historyList.value.length > 0 }
      } catch (e) { console.error(e) }
    })
    return { historyList, hasData }
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
            <h3 class="card-title">提交反馈</h3>
            <div class="form-group">
              <label>您的评分</label>
              <star-rating v-model="rating"></star-rating>
            </div>
            <div class="form-group">
              <label>详细描述</label>
              <textarea v-model="feedbackContent" rows="6" placeholder="请详细描述您的反馈内容..."></textarea>
            </div>
            <div class="form-actions">
              <button class="btn-primary" :class="{ loading: submitting }" @click="submitFeedback">{{ submitting ? '提交中...' : '📤 提交反馈' }}</button>
              <button class="btn-secondary" @click="resetForm">重置</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  setup() {
    const rating = ref(5)
    const feedbackContent = ref('')
    const submitting = ref(false)
    
    const submitFeedback = async () => {
      if (!feedbackContent.value.trim()) return alert('请填写反馈内容')
      submitting.value = true
      try {
        await axios.post(API_BASE + '/api/memory/feedback', { conversationId: 'feedback_' + Date.now(), userId: 'user_' + Date.now(), rating: rating.value, comment: feedbackContent.value })
        alert('感谢您的反馈！'); resetForm()
      } catch (e) { alert('提交失败') }
      submitting.value = false
    }
    
    const resetForm = () => { rating.value = 5; feedbackContent.value = '' }
    return { rating, feedbackContent, submitting, submitFeedback, resetForm }
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
          <div class="logo"><span class="logo-icon">⚡</span><span class="logo-text">SQL Pilot</span></div>
          <nav class="nav-menu">
            <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">首页</router-link>
            <router-link to="/optimize" class="nav-item" :class="{ active: $route.path === '/optimize' }">SQL优化</router-link>
            <router-link to="/natural-to-sql" class="nav-item" :class="{ active: $route.path === '/natural-to-sql' }">自然语言转SQL</router-link>
            <router-link to="/history" class="nav-item" :class="{ active: $route.path === '/history' }">历史记录</router-link>
            <router-link to="/feedback" class="nav-item" :class="{ active: $route.path === '/feedback' }">用户反馈</router-link>
          </nav>
        </div>
      </header>
      <main class="app-main"><router-view /></main>
      <footer class="app-footer"><p>SQL Pilot - AI驱动的SQL性能优化助手</p></footer>
    </div>
  `
}

const app = createApp(App)
app.use(router)
app.component('star-rating', StarRating)
app.mount('#app')
