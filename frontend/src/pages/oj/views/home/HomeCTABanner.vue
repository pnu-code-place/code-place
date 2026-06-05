<template>
  <div class="cta-padding">
    <div class="cta-banner">
      <div class="cta-left">
        <div class="cta-icon">
          <svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="13" cy="13" r="11.5" stroke="#7F77DD" stroke-width="1.5"/>
            <circle cx="13" cy="13" r="7.5" stroke="#7F77DD" stroke-width="1.5"/>
            <circle cx="13" cy="13" r="3.5" fill="#7F77DD"/>
          </svg>
        </div>
        <div class="cta-text">
          <p class="cta-title">오늘의 목표를 달성해보세요!</p>
          <p class="cta-desc">매일 꾸준한 학습이 실력을 만듭니다.</p>
        </div>
      </div>
      <button class="cta-btn" @click="goProblemList">
        문제 풀러 가기 &nbsp;→
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "HomeCTABanner",
  methods: {
    goProblemList() {
      this.$router.push({ name: "problem-list" })
    },
  },
}
</script>

<style scoped lang="less">
.cta-padding {
  width: 100%;
  padding: 40px 0 36px;
}

.cta-banner {
  background-color: #efeeff;
  border-radius: 20px;
  height: 88px;
  display: flex;
  align-items: center;
  padding: 0 40px;
}

.cta-left {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
}

.cta-icon {
  width: 52px;
  height: 52px;
  background-color: #ffffff;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow:
    0 0 0 1px rgba(0, 0, 0, 0.06),
    0 2px 6px rgba(0, 0, 0, 0.06);
}

.cta-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cta-title {
  font-size: 16px;
  font-weight: 700;
  color: #3a3870;
  margin: 0;
  white-space: nowrap;
}

.cta-desc {
  font-size: 13px;
  color: #7e7db0;
  margin: 0;
  white-space: nowrap;
}

.cta-btn {
  background-color: #8b85d4;
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  padding: 14px 28px;
  border-radius: 14px;
  border: none;
  cursor: pointer;
  white-space: nowrap;
  transition: background-color 0.2s;

  &:hover {
    background-color: #7a74c4;
  }
}
</style>
