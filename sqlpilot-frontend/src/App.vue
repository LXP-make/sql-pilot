<template>
  <div class="app-container">
    <header class="app-header">
      <div class="header-content">
        <div class="logo">
          <span class="logo-icon">⚡</span>
          <span class="logo-text">SQL Pilot</span>
        </div>
        <nav class="nav-menu">
          <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">首页</router-link>
          <router-link to="/optimize" class="nav-item" :class="{ active: $route.path === '/optimize' }">SQL优化</router-link>
          <router-link to="/natural-to-sql" class="nav-item" :class="{ active: $route.path === '/natural-to-sql' }">自然语言转SQL</router-link>
          <router-link to="/history" class="nav-item" :class="{ active: $route.path === '/history' }">历史记录</router-link>
          <router-link to="/feedback" class="nav-item" :class="{ active: $route.path === '/feedback' }">用户反馈</router-link>
        </nav>
      </div>
    </header>
    <main class="app-main">
      <router-view />
    </main>
    <footer class="app-footer">
      <p>SQL Pilot - AI驱动的SQL性能优化助手</p>
    </footer>
  </div>
</template>

<script setup>
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  font-size: 1.75rem;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 700;
}

.nav-menu {
  display: flex;
  gap: 2rem;
}

.nav-item {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.app-main {
  flex: 1;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  padding: 2rem;
}

.app-footer {
  text-align: center;
  padding: 1.5rem;
  background: #f5f5f5;
  color: #666;
  font-size: 0.9rem;
}
</style>
