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
          <div class="sql-card">SELECT * FROM users</div>
          <div class="arrow">&rarr;</div>
          <div class="sql-card optimized">SELECT id, name FROM users WHERE status = 1</div>
        </div>
      </div>
    </div>

    <div class="features-section">
      <h2 class="section-title">核心功能</h2>
      <div class="features-grid">
        <div class="feature-card">
          <h3>SQL分析</h3>
          <p>识别查询中的性能瓶颈，检测SELECT *、索引失效等常见问题</p>
        </div>
        <div class="feature-card">
          <h3>AI优化</h3>
          <p>基于大厂SQL规范知识库，提供精准的优化建议</p>
        </div>
        <div class="feature-card">
          <h3>自然语言转SQL</h3>
          <p>用自然语言描述查询需求，自动生成对应的SQL语句</p>
        </div>
        <div class="feature-card">
          <h3>规则引擎</h3>
          <p>内置阿里巴巴、腾讯等大厂SQL规范规则，自动检测不良写法</p>
        </div>
        <div class="feature-card">
          <h3>记忆系统</h3>
          <p>记录对话历史，提供上下文感知的优化建议</p>
        </div>
        <div class="feature-card">
          <h3>知识库</h3>
          <p>集成大厂SQL规范，持续更新知识库内容</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.home-page {
  padding: 1rem 0;
}

.hero-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4rem;
  padding: 3rem 2rem;
  margin-bottom: 3rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
}

.hero-content {
  flex: 1;
}

.hero-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: #2563eb;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.hero-desc {
  font-size: 1rem;
  color: #64748b;
  margin-bottom: 2rem;
  max-width: 480px;
  line-height: 1.6;
}

.hero-buttons {
  display: flex;
  gap: 0.75rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.15s ease;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-outline {
  background: white;
  color: #475569;
  border: 1px solid #d1d5db;
}

.btn-outline:hover {
  border-color: #2563eb;
  color: #2563eb;
}

.hero-illustration {
  flex: 1;
  display: flex;
  justify-content: center;
}

.sql-visual {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.sql-card {
  background: #f8fafc;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  color: #64748b;
}

.sql-card.optimized {
  background: #f0fdf4;
  border-color: #86efac;
  color: #166534;
  font-weight: 600;
}

.arrow {
  font-size: 1.5rem;
  color: #94a3b8;
}

.features-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 1.5rem;
  color: #1e293b;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.feature-card {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  transition: all 0.15s ease;
}

.feature-card:hover {
  border-color: #93c5fd;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.feature-card h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #1e293b;
}

.feature-card p {
  color: #64748b;
  font-size: 0.9rem;
  line-height: 1.5;
}
</style>
