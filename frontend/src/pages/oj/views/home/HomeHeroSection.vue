<template>
  <div class="hero-padding">
    <div class="hero-section">
      <div class="hero-left">
        <span class="hero-eyebrow">
          <template v-if="isAuthenticated"
            >안녕하세요, {{ user.username }}님!</template
          >
          <template v-else>코드로 성장하는 공간</template>
        </span>
        <h1 class="hero-title">문제를 해결하고<br />성장하는 개발자 공간</h1>
        <p class="hero-desc">
          다양한 문제를 풀고, 실력을 키우고,<br />AI와 함께 더 빠르게
          성장하세요.
        </p>
        <button class="hero-cta" @click="goProblemList">
          문제 풀러 가기 &nbsp;→
        </button>
      </div>
      <!-- 배경 장식 원 -->
      <div class="deco-circle deco-circle--1" />
      <div class="deco-circle deco-circle--2" />
      <div class="deco-circle deco-circle--3" />

      <div class="hero-image-wrapper">
        <img class="hero-banner-img" :src="bannerImg" alt="Code Place Banner" />
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex"
import bannerImg from "@/assets/code-place-banner.png"

export default {
  name: "HomeHeroSection",
  data() {
    return {
      bannerImg,
    }
  },
  computed: {
    ...mapGetters(["isAuthenticated", "user"]),
  },
  methods: {
    goProblemList() {
      this.$router.push({ name: "problem-list" })
    },
  },
}
</script>

<style scoped lang="less">
.hero-padding {
  width: 100%;
  padding: 20px 0 0;
}

.hero-section {
  background: linear-gradient(135deg, #3a3fa8 0%, #5b64ed 45%, #7f87f5 75%, #b8bcff 100%);
  border-radius: 20px;
  height: 480px;
  display: flex;
  align-items: center;
  padding: 40px 64px;
  position: relative;
  overflow: hidden;
}

.hero-left {
  display: flex;
  flex-direction: column;
  gap: 16px;
  z-index: 1;
  flex: 1;
}

.hero-eyebrow {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
}

.hero-title {
  font-size: 36px;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.3;
  margin: 0;
}

.hero-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.75);
  line-height: 1.6;
  margin: 0;
}

.hero-cta {
  display: inline-flex;
  align-items: center;
  background-color: #ffffff;
  color: #5b64ed;
  font-size: 14px;
  font-weight: 700;
  padding: 12px 24px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  width: fit-content;
  transition: all 0.2s;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);

  &:hover {
    background-color: #f0f0ff;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
  }
}

.hero-image-wrapper {
  position: absolute;
  right: 0;
  top: 0;
  height: 100%;
  width: 48%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 0 20px 20px 0;
}

.hero-banner-img {
  height: 100%;
  width: auto;
  min-width: 100%;
  object-fit: cover;
  object-position: center center;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.12;
  pointer-events: none;

  &--1 {
    width: 320px;
    height: 320px;
    background: #ffffff;
    top: -80px;
    left: -60px;
  }

  &--2 {
    width: 200px;
    height: 200px;
    background: #ffffff;
    bottom: -60px;
    left: 30%;
  }

  &--3 {
    width: 120px;
    height: 120px;
    background: #ffffff;
    top: 20px;
    left: 38%;
    opacity: 0.07;
  }
}
</style>
