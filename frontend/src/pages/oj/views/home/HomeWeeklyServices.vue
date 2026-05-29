<template>
  <div class="weekly-padding">
    <p class="section-title">이주의 서비스</p>
    <div class="services-row">
      <div class="service-card ai-review" @click="goAIReview">
        <div class="service-text">
          <p class="service-name" style="color: #3840bf">AI 코드 리뷰</p>
          <p class="service-desc" style="color: #5961b8">
            AI가 여러분의 코드를 분석하고<br />개선점을 제안드려요.
          </p>
          <span class="service-link" style="color: #3840bf">사용해보기 →</span>
        </div>
        <div class="service-icon" style="background-color: #c7c7ff">
          🤖
        </div>
      </div>

      <div class="service-card roadmap" @click="goRoadmap">
        <div class="service-text">
          <p class="service-name" style="color: #1a8059">학습 로드맵</p>
          <p class="service-desc" style="color: #268c66">
            단계별 학습 로드맵으로<br />꾸준히 실력을 높여보세요.
          </p>
          <span class="service-link" style="color: #1a8059">확인하기 →</span>
        </div>
        <div class="service-icon" style="background-color: #b8edd1">
          🗺️
        </div>
      </div>

      <div class="service-card recommend" @click="goRecommend">
        <div class="service-text">
          <p class="service-name" style="color: #99610d">맞춤 문제 추천</p>
          <p class="service-desc" style="color: #a66b14">
            여러분의 실력에 맞는 문제를<br />추천해드려요.
          </p>
          <span class="service-link" style="color: #99610d">추천받기 →</span>
        </div>
        <div class="service-icon" style="background-color: #ffe0a6">
          🎯
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "HomeWeeklyServices",
  methods: {
    goAIReview() {
      this.$router.push({ name: "problem-list" })
    },
    goRoadmap() {
      this.$router.push({ name: "problem-list" })
    },
    goRecommend() {
      this.$router.push({ name: "problem-list" })
    },
  },
}
</script>

<style scoped lang="less">
.weekly-padding {
  width: 100%;
  padding: 24px 0 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #14141f;
  margin: 0;
}

.services-row {
  display: flex;
  gap: 20px;
}

.service-card {
  flex: 1;
  height: 160px;
  border-radius: 20px;
  padding: 24px 24px 24px 28px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  }

  &.ai-review {
    background-color: #ecebff;
  }

  &.roadmap {
    background-color: #e5f9f2;
  }

  &.recommend {
    background-color: #fff9e5;
  }
}

.service-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow: hidden;
}

.service-name {
  font-size: 15px;
  font-weight: 700;
  margin: 0;
  white-space: nowrap;
}

.service-desc {
  font-size: 12px;
  margin: 0;
  line-height: 1.6;
}

.service-link {
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.service-icon {
  flex-shrink: 0;
  width: 64px;
  height: 64px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin-left: auto;
}
</style>
