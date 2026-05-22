<template>
  <div class="home-page">
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">SQL Pilot</h1>
        <p class="hero-subtitle">SQL性能优化助手</p>
        <p class="hero-desc">基于RAG技术和大厂SQL规范知识库，智能分析和优化您的SQL查询</p>
        <div class="hero-buttons">
          <router-link to="/optimize" class="btn btn-primary">开始优化</router-link>
          <router-link to="/natural-to-sql" class="btn btn-outline">自然语言转SQL</router-link>
        </div>
      </div>
      <div class="hero-illustration">
        <div class="sql-visual">
          <div class="sql-card static">SELECT * FROM users</div>
          <div class="arrow">&rarr;</div>
          <div class="sql-card optimized">SELECT id, name FROM users WHERE status = 1</div>
        </div>
      </div>
    </div>

    <div class="features-section">
      <h2 class="section-title">核心功能</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">&#128269;</div>
          <h3>SQL分析</h3>
          <p>识别查询中的性能瓶颈，检测SELECT *、索引失效等常见问题</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">&#9889;</div>
          <h3>AI优化</h3>
          <p>基于大厂SQL规范知识库，提供精准的优化建议</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">&#128172;</div>
          <h3>自然语言转SQL</h3>
          <p>用自然语言描述查询需求，自动生成对应的SQL语句</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">&#9881;</div>
          <h3>规则引擎</h3>
          <p>内置阿里巴巴、腾讯等大厂SQL规范规则，自动检测不良写法</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">&#128203;</div>
          <h3>记忆系统</h3>
          <p>记录对话历史，提供上下文感知的优化建议</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">&#128218;</div>
          <h3>知识库</h3>
          <p>集成大厂SQL规范，持续更新知识库内容</p>
        </div>
      </div>
    </div>

    <div class="card" v-if="stats">
      <div class="card-header">系统概览</div>
      <div class="card-body">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">{{ stats.sql_analysis_history || 0 }}</div>
            <div class="stat-label">分析记录</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.optimization_suggestion || 0 }}</div>
            <div class="stat-label">优化建议</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.index_suggestion || 0 }}</div>
            <div class="stat-label">索引建议</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const stats = ref(null)

onMounted(async () => {
  try {
    const response = await axios.get('/api/memory/table-stats')
    if (response.data.success) {
      stats.value = response.data.data
    }
  } catch (e) {
    console.error('Failed to load stats:', e)
  }
})
</script>

<style scoped>
.home-page {
  padding: var(--space-4) 0;
}

.hero-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4rem;
  padding: var(--space-12) var(--space-8);
  margin-bottom: var(--space-8);
  background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-xl);
  position: relative;
  overflow: hidden;
}
.hero-section::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(37, 99, 235, 0.03) 0%, transparent 70%);
  border-radius: 50%;
}

.hero-content {
  flex: 1;
  position: relative;
  z-index: 1;
}

.hero-title {
  font-size: var(--text-4xl);
  font-weight: 800;
  color: var(--gray-800);
  margin-bottom: var(--space-2);
}

.hero-subtitle {
  font-size: var(--text-xl);
  color: var(--color-primary);
  font-weight: 600;
  margin-bottom: var(--space-3);
}

.hero-desc {
  font-size: var(--text-base);
  color: var(--gray-500);
  margin-bottom: var(--space-8);
  max-width: 480px;
  line-height: var(--leading-relaxed);
}

.hero-buttons {
  display: flex;
  gap: var(--space-3);
}

.hero-illustration {
  flex: 1;
  display: flex;
  justify-content: center;
  position: relative;
  z-index: 1;
}

.sql-visual {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.sql-card {
  background: white;
  padding: var(--space-4) var(--space-6);
  border-radius: var(--radius-lg);
  border: 1px solid var(--gray-200);
  box-shadow: var(--shadow-md);
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--gray-500);
  transition: all var(--transition-base);
}
.sql-card.static {
  background: var(--gray-50);
}
.sql-card.optimized {
  background: var(--color-success-light);
  border-color: var(--color-success);
  color: var(--color-success);
  font-weight: 600;
  box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.1);
}

.arrow {
  font-size: var(--text-2xl);
  color: var(--gray-400);
}

.features-section {
  margin-bottom: var(--space-6);
}

.section-title {
  font-size: var(--text-2xl);
  font-weight: 700;
  text-align: center;
  margin-bottom: var(--space-6);
  color: var(--gray-800);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-4);
}

.feature-card {
  background: white;
  padding: var(--space-6);
  border-radius: var(--radius-lg);
  border: 1px solid var(--gray-200);
  transition: all var(--transition-base);
}
.feature-card:hover {
  border-color: var(--color-primary-lighter);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 1.5rem;
  margin-bottom: var(--space-3);
}

.feature-card h3 {
  font-size: var(--text-lg);
  font-weight: 600;
  margin-bottom: var(--space-2);
  color: var(--gray-800);
}

.feature-card p {
  color: var(--gray-500);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
}

.stat-card {
  text-align: center;
  padding: var(--space-5);
  background: var(--gray-50);
  border-radius: var(--radius-lg);
  border: 1px solid var(--gray-200);
}

.stat-value {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: var(--space-1);
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--gray-500);
}

@media (max-width: 900px) {
  .hero-section {
    flex-direction: column;
    gap: var(--space-8);
    padding: var(--space-8) var(--space-6);
  }
  .hero-title {
    font-size: var(--text-3xl);
  }
  .sql-visual {
    flex-direction: column;
  }
  .arrow {
    transform: rotate(90deg);
  }
}
</style>
