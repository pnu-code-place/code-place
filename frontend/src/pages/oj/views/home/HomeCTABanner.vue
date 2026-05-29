<template>
  <div class="cta-padding">
    <div class="cta-banner">
      <div class="cta-left">
        <div class="cta-icon">🎯</div>
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
  padding: 24px 0 36px;
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
  width: 48px;
  height: 48px;
  background-color: #ccc7ff;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.cta-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cta-title {
  font-size: 16px;
  font-weight: 700;
  color: #14141f;
  margin: 0;
  white-space: nowrap;
}

.cta-desc {
  font-size: 13px;
  color: #73738c;
  margin: 0;
  white-space: nowrap;
}

.cta-btn {
  background-color: #5b64ed;
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
    background-color: #4a53d4;
  }
}
</style>
