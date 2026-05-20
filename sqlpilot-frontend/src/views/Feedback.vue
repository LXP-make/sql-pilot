<template>
  <div class="feedback-page">
    <div class="page-header">
      <h1>用户反馈</h1>
      <p>帮助我们改进服务质量</p>
    </div>

    <div class="main-content">
      <div class="feedback-form-section">
        <div class="card">
          <div class="card-header">提交反馈</div>
          <div class="card-body">
            <div class="form-group">
              <label>您的评分</label>
              <div class="stars">
                <span v-for="n in 5" :key="n" class="star" :class="{ filled: n <= rating }" @click="rating = n">&#9733;</span>
              </div>
            </div>
            <div class="form-group">
              <label>反馈类型</label>
              <select v-model="feedbackType" class="form-select">
                <option value="suggestion">功能建议</option>
                <option value="bug">Bug报告</option>
                <option value="experience">使用体验</option>
                <option value="other">其他</option>
              </select>
            </div>
            <div class="form-group">
              <label>详细描述</label>
              <textarea
                v-model="feedbackContent"
                :rows="6"
                placeholder="请详细描述您的反馈内容..."
                class="form-textarea"
              ></textarea>
            </div>
            <div class="form-group">
              <label>联系方式（可选）</label>
              <input v-model="contact" placeholder="邮箱或手机号" class="form-input" />
            </div>
            <div class="form-actions">
              <button class="btn btn-primary" :disabled="submitting" @click="submitFeedback">
                {{ submitting ? '提交中...' : '提交反馈' }}
              </button>
              <button class="btn btn-outline" @click="resetForm">重置</button>
            </div>
          </div>
        </div>
      </div>

      <div class="stats-section">
        <div class="card">
          <div class="card-header">反馈统计</div>
          <div class="card-body">
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-value">4.8</div>
                <div class="stat-label">平均评分</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ feedbackCount }}</div>
                <div class="stat-label">总反馈数</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">85%</div>
                <div class="stat-label">好评率</div>
              </div>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">用户评价</div>
          <div class="card-body">
            <div class="reviews-list" v-if="reviews.length > 0">
              <div class="review-item" v-for="(review, index) in reviews" :key="index">
                <div class="review-header">
                  <div class="review-stars">
                    <span v-for="n in 5" :key="n" class="star-mini" :class="{ filled: n <= review.rating }">&#9733;</span>
                  </div>
                  <span class="review-time">{{ review.time }}</span>
                </div>
                <p class="review-content">{{ review.content }}</p>
                <span class="review-type">{{ getTypeLabel(review.type) }}</span>
              </div>
            </div>
            <div v-else class="empty-reviews">暂无评价</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { memoryApi } from '../api'

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
  const labels = {
    suggestion: '功能建议',
    bug: 'Bug报告',
    experience: '使用体验',
    other: '其他'
  }
  return labels[type] || '其他'
}

const submitFeedback = async () => {
  if (!feedbackContent.value.trim()) {
    alert('请填写反馈内容')
    return
  }

  submitting.value = true

  try {
    await memoryApi.submitFeedback(
      'feedback_' + Date.now(),
      'user_' + Date.now(),
      rating.value,
      feedbackContent.value
    )

    reviews.value.unshift({
      rating: rating.value,
      content: feedbackContent.value,
      type: feedbackType.value,
      time: new Date().toLocaleDateString('zh-CN')
    })

    feedbackCount.value++

    alert('感谢您的反馈！我们会认真对待每一条建议。')
    resetForm()
  } catch (error) {
    console.error('Feedback submission failed:', error)
    alert('提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  rating.value = 5
  feedbackType.value = 'suggestion'
  feedbackContent.value = ''
  contact.value = ''
}
</script>

<style scoped>
.feedback-page {
  max-width: 1000px;
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

.form-select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #1e293b;
  background: white;
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2563eb;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.8rem;
  color: #64748b;
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

.reviews-list {
  max-height: 400px;
  overflow-y: auto;
}

.review-item {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.review-item:last-child {
  border-bottom: none;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.review-stars {
  display: flex;
  gap: 0.125rem;
}

.star-mini {
  font-size: 1rem;
  color: #d1d5db;
}

.star-mini.filled {
  color: #f59e0b;
}

.review-time {
  font-size: 0.8rem;
  color: #94a3b8;
}

.review-content {
  color: #475569;
  font-size: 0.85rem;
  line-height: 1.5;
  margin-bottom: 0.5rem;
}

.review-type {
  font-size: 0.75rem;
  color: #2563eb;
  background: #eff6ff;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
}

.empty-reviews {
  text-align: center;
  color: #94a3b8;
  font-size: 0.9rem;
  padding: 2rem 0;
}

@media (max-width: 900px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}
</style>
