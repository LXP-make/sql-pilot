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
                style="font-family:var(--font-sans);"
              ></textarea>
            </div>
            <div class="form-group">
              <label>联系方式（可选）</label>
              <input v-model="contact" placeholder="邮箱或手机号" class="form-input" />
            </div>
            <div class="form-actions">
              <button class="btn btn-primary" :disabled="submitting" @click="submitFeedback">
                <span v-if="submitting" class="spinner"></span>
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
                <span class="review-type-tag">{{ getTypeLabel(review.type) }}</span>
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
  const labels = { suggestion: '功能建议', bug: 'Bug报告', experience: '使用体验', other: '其他' }
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
}

.stat-item {
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

.reviews-list {
  max-height: 400px;
  overflow-y: auto;
}

.review-item {
  padding: var(--space-4);
  border-bottom: 1px solid var(--gray-200);
}
.review-item:last-child {
  border-bottom: none;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}

.review-stars {
  display: flex;
  gap: 0.125rem;
}

.star-mini {
  font-size: 1rem;
  color: var(--gray-300);
}
.star-mini.filled {
  color: var(--color-warning);
}

.review-time {
  font-size: var(--text-xs);
  color: var(--gray-400);
}

.review-content {
  color: var(--gray-600);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  margin-bottom: var(--space-2);
}

.review-type-tag {
  font-size: var(--text-xs);
  color: var(--color-primary);
  background: var(--color-primary-light);
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-sm);
  display: inline-block;
}

.empty-reviews {
  text-align: center;
  color: var(--gray-400);
  font-size: var(--text-sm);
  padding: var(--space-8) 0;
}
</style>
