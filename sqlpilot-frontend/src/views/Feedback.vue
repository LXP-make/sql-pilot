<template>
  <div class="feedback-page">
    <div class="page-header">
      <h1>用户反馈</h1>
      <p>帮助我们改进服务质量</p>
    </div>

    <div class="main-content">
      <div class="feedback-form-section">
        <el-card title="提交反馈">
          <div class="form-group">
            <label>您的评分</label>
            <div class="rating-section">
              <el-rate v-model="rating" max="5" show-text text-color="#ff9900" size="large"></el-rate>
            </div>
          </div>
          <div class="form-group">
            <label>反馈类型</label>
            <el-select v-model="feedbackType" placeholder="请选择反馈类型">
              <el-option label="功能建议" value="suggestion"></el-option>
              <el-option label="Bug报告" value="bug"></el-option>
              <el-option label="使用体验" value="experience"></el-option>
              <el-option label="其他" value="other"></el-option>
            </el-select>
          </div>
          <div class="form-group">
            <label>详细描述</label>
            <el-textarea
              v-model="feedbackContent"
              :rows="6"
              placeholder="请详细描述您的反馈内容..."
            ></el-textarea>
          </div>
          <div class="form-group">
            <label>联系方式（可选）</label>
            <el-input v-model="contact" placeholder="邮箱或手机号"></el-input>
          </div>
          <div class="form-actions">
            <el-button type="primary" :loading="submitting" @click="submitFeedback">
              <span v-if="!submitting">📤 提交反馈</span>
              <span v-else>提交中...</span>
            </el-button>
            <el-button @click="resetForm">重置</el-button>
          </div>
        </el-card>
      </div>

      <div class="stats-section">
        <el-card title="反馈统计">
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-icon">⭐</div>
              <div class="stat-value">4.8</div>
              <div class="stat-label">平均评分</div>
            </div>
            <div class="stat-item">
              <div class="stat-icon">📝</div>
              <div class="stat-value">{{ feedbackCount }}</div>
              <div class="stat-label">总反馈数</div>
            </div>
            <div class="stat-item">
              <div class="stat-icon">✅</div>
              <div class="stat-value">85%</div>
              <div class="stat-label">好评率</div>
            </div>
          </div>
        </el-card>

        <el-card title="用户评价">
          <div class="reviews-list">
            <div class="review-item" v-for="(review, index) in reviews" :key="index">
              <div class="review-header">
                <el-rate :value="review.rating" disabled show-score text-color="#ff9900" size="small"></el-rate>
                <span class="review-time">{{ review.time }}</span>
              </div>
              <p class="review-content">{{ review.content }}</p>
              <div class="review-type">{{ getTypeLabel(review.type) }}</div>
            </div>
          </div>
        </el-card>
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

.feedback-form-section {
  grid-column: 1;
}

.stats-section {
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

.rating-section {
  padding: 1rem 0;
}

.form-actions {
  display: flex;
  gap: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
}

.stat-icon {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.8rem;
  color: #64748b;
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

.review-time {
  font-size: 0.8rem;
  color: #94a3b8;
}

.review-content {
  color: #475569;
  line-height: 1.5;
  margin-bottom: 0.5rem;
}

.review-type {
  font-size: 0.75rem;
  color: #667eea;
  background: #e0e7ff;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
}

@media (max-width: 900px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  .feedback-form-section, .stats-section {
    grid-column: 1;
  }
}
</style>
