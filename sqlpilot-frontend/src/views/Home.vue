<template>
  <div class="home-page">
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          <span class="title-icon">⚡</span>
          SQL Pilot
        </h1>
        <p class="hero-subtitle">AI驱动的SQL性能优化助手</p>
        <p class="hero-desc">基于RAG技术，智能分析和优化您的SQL查询，提升数据库性能</p>
        <div class="hero-buttons">
          <router-link to="/optimize" class="btn-primary">开始优化</router-link>
          <router-link to="/natural-to-sql" class="btn-secondary">自然语言转SQL</router-link>
        </div>
      </div>
      <div class="hero-illustration">
        <div class="sql-visual">
          <div class="sql-card">SELECT * FROM users</div>
          <div class="arrow">→</div>
          <div class="sql-card optimized">SELECT id, name FROM users WHERE status = 1</div>
        </div>
      </div>
    </div>

    <div class="features-section">
      <h2 class="section-title">核心功能</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">🔍</div>
          <h3>SQL分析</h3>
          <p>智能分析SQL查询的性能问题，识别潜在的性能瓶颈</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">⚡</div>
          <h3>AI优化</h3>
          <p>基于RAG技术提供精准的SQL优化建议，提升查询效率</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">💬</div>
          <h3>自然语言转SQL</h3>
          <p>输入自然语言描述，自动生成对应的SQL查询语句</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📜</div>
          <h3>规则引擎</h3>
          <p>内置SQL规则检测，自动识别SELECT *等不良写法</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🧠</div>
          <h3>记忆系统</h3>
          <p>智能记忆对话历史，提供个性化服务体验</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">⭐</div>
          <h3>奖惩机制</h3>
          <p>用户反馈驱动持续学习，不断优化服务质量</p>
        </div>
      </div>
    </div>

    <div class="stats-section" v-if="stats">
      <h2 class="section-title">系统概览</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ stats.sql_analysis_history }}</div>
          <div class="stat-label">分析记录</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.optimization_suggestion }}</div>
          <div class="stat-label">优化建议</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.index_suggestion }}</div>
          <div class="stat-label">索引建议</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { memoryApi } from '../api'

const stats = ref(null)

onMounted(() => {
  loadStats()
})

const loadStats = async () => {
  try {
    const response = await memoryApi.getTableStats()
    if (response.data.success) {
      stats.value = response.data.data
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}
</script>

<style scoped>
.home-page {
  padding: 2rem 0;
}

.hero-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4rem;
  padding: 4rem 0;
  background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%);
  border-radius: 20px;
  padding: 3rem 2rem;
  margin-bottom: 3rem;
}

.hero-content {
  flex: 1;
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.title-icon {
  font-size: 3.5rem;
}

.hero-subtitle {
  font-size: 1.5rem;
  color: #667eea;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.hero-desc {
  font-size: 1.1rem;
  color: #64748b;
  margin-bottom: 2rem;
  max-width: 500px;
}

.hero-buttons {
  display: flex;
  gap: 1rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.875rem 2rem;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.btn-secondary {
  background: white;
  color: #667eea;
  padding: 0.875rem 2rem;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  border: 2px solid #e2e8f0;
}

.btn-secondary:hover {
  border-color: #667eea;
  background: #f8fafc;
}

.hero-illustration {
  flex: 1;
  display: flex;
  justify-content: center;
}

.sql-visual {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.sql-card {
  background: white;
  padding: 1.5rem 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  font-family: 'Consolas', monospace;
  font-size: 14px;
  color: #64748b;
}

.sql-card.optimized {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
  color: #1e293b;
  font-weight: 600;
}

.arrow {
  font-size: 2rem;
  color: #667eea;
}

.features-section {
  margin-bottom: 3rem;
}

.section-title {
  font-size: 1.75rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 2rem;
  color: #1e293b;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  text-align: center;
  transition: all 0.3s ease;
  border: 1px solid #e2e8f0;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: #1e293b;
}

.feature-card p {
  color: #64748b;
  line-height: 1.6;
}

.stats-section {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
}

.stat-card {
  text-align: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 800;
  color: #667eea;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: #64748b;
  font-size: 0.9rem;
}
</style>
