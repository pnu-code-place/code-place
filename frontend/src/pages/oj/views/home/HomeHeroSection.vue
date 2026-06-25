<template>
  <div class="hero-padding">
    <div class="banner">
      <div class="glow glow-1" />
      <div class="glow glow-2" />
      <div class="glow glow-3" />
      <div class="grid-overlay" />

      <div class="banner-inner">
        <!-- 상단 -->
        <div class="banner-top">
          <div class="eyebrow">
            <span class="eyebrow-dot" />
            부산대학교 공식 코딩 플랫폼
          </div>
          <span class="wordmark">CODEPLACE</span>
        </div>

        <!-- 중앙 타이틀 -->
        <div class="banner-mid">
          <h1 class="banner-title">
            코드플레이스,<br />
            <span class="accent">실력이 쌓이는 공간</span>
          </h1>
        </div>

        <!-- 하단 -->
        <div class="banner-bottom">
          <p class="banner-desc">
            알고리즘 문제 풀이부터 실전 코딩테스트, 대회 운영, AI 조교 기반 학습
            지원까지 제공하는 통합 프로그래밍 교육 플랫폼입니다.
          </p>
          <a
            class="banner-cta"
            href="https://acei2026.notion.site/Code-Place-304da425d9f780da848ac3def46aac78"
            target="_blank"
            rel="noopener noreferrer"
          >
            코드플레이스 알아보기 <span class="arrow">→</span>
          </a>
        </div>
      </div>
    </div>

    <!-- 통계 카드 -->
    <div class="stat-cards">
      <div class="stat-card">
        <div class="stat-card-left">
          <div class="stat-num">{{ stats.totalProblems }}</div>
          <div class="stat-label">
            <span class="stat-line" />
            전체 문제
          </div>
        </div>
        <span class="stat-icon">
          <svg
            width="27"
            height="27"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <rect x="5" y="4.5" width="14" height="16.5" rx="2.2" />
            <rect x="8.5" y="2.5" width="7" height="4" rx="1.4" />
            <path d="M8.7 11.5h6.6M8.7 15.5h4.4" />
          </svg>
        </span>
      </div>
      <div class="stat-card">
        <div class="stat-card-left">
          <div class="stat-num">{{ stats.acceptedProblems }}</div>
          <div class="stat-label">
            <span class="stat-line" />
            해결된 문제
          </div>
        </div>
        <span class="stat-icon">
          <svg
            width="27"
            height="27"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <circle cx="12" cy="12" r="9" />
            <path d="M8.3 12.4l2.6 2.6 4.8-5.4" />
          </svg>
        </span>
      </div>
      <div class="stat-card">
        <div class="stat-card-left">
          <div class="stat-num">{{ stats.totalContests }}</div>
          <div class="stat-label">
            <span class="stat-line" />
            개최된 대회
          </div>
        </div>
        <span class="stat-icon">
          <svg
            width="27"
            height="27"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M8 4h8v4.5a4 4 0 0 1-8 0V4z" />
            <path d="M8 5.5H5V7a3 3 0 0 0 3 3" />
            <path d="M16 5.5h3V7a3 3 0 0 1-3 3" />
            <path d="M12 12.5v3.5" />
            <path d="M9.2 20h5.6l-.7-3.2H9.9z" />
          </svg>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@oj/api"

export default {
  name: "HomeHeroSection",
  data() {
    return {
      stats: {
        totalProblems: "—",
        acceptedProblems: "—",
        totalContests: "—",
      },
    }
  },
  mounted() {
    api
      .getStatistics()
      .then((res) => {
        const d = res.data.data
        this.stats = {
          totalProblems: (d.total_problem_length || 0).toLocaleString(),
          acceptedProblems: (d.accepted_problem_length || 0).toLocaleString(),
          totalContests: (d.ended_contest_length || 0).toLocaleString(),
        }
      })
      .catch(() => {})
  },
}
</script>

<style scoped lang="less">
@accent: #6d5df0;
@accent-soft: rgba(109, 93, 240, 0.12);

@keyframes cpFloat {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-14px);
  }
}
@keyframes cpFloat2 {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(18px);
  }
}
@keyframes cpPulse {
  0%,
  100% {
    opacity: 0.55;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.06);
  }
}
@keyframes cpDrift {
  0%,
  100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(20px, -16px);
  }
}
@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero-padding {
  width: 100%;
  padding: 20px 0 0;
  display: flex;
  flex-direction: column;
  gap: 22px;

  @media (max-width: 768px) {
    gap: 12px;
  }
}

.banner {
  width: 100%;
  height: 340px;
  border-radius: 22px;
  overflow: hidden;
  position: relative;
  background: #0a0a1f;
  box-shadow: 0 8px 20px rgba(20, 14, 60, 0.2);

  @media (max-width: 768px) {
    height: auto;
    min-height: 240px;
    border-radius: 16px;
  }
}

/* 글로우 오브 */
.glow {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
}

.glow-1 {
  width: 520px;
  height: 520px;
  left: -120px;
  top: -200px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.4), transparent 62%);
  filter: blur(40px);
  animation: cpDrift 16s ease-in-out infinite;
}

.glow-2 {
  width: 440px;
  height: 440px;
  right: -100px;
  bottom: -200px;
  background: radial-gradient(
    circle,
    rgba(139, 92, 246, 0.36),
    transparent 62%
  );
  filter: blur(40px);
  animation: cpFloat2 13s ease-in-out infinite;
}

.glow-3 {
  width: 280px;
  height: 280px;
  left: 42%;
  top: -120px;
  background: radial-gradient(
    circle,
    rgba(56, 189, 248, 0.22),
    transparent 64%
  );
  filter: blur(46px);
  animation: cpFloat 11s ease-in-out infinite;
}

/* 내부 레이아웃 */
.banner-inner {
  position: relative;
  z-index: 5;
  box-sizing: border-box;
  padding: 36px 52px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;

  @media (max-width: 768px) {
    padding: 24px 20px;
    gap: 20px;
  }
}

/* 상단 */
.banner-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  animation: fadeUp 0.5s ease 0.1s both;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: #d3cdff;
}

.eyebrow-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #8b7cff;
  box-shadow: 0 0 12px #8b7cff;
  flex-shrink: 0;
  animation: cpPulse 2.4s ease-in-out infinite;
}

.wordmark {
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.2em;
  color: rgba(160, 165, 220, 0.42);
  font-family: "JetBrains Mono", "Fira Code", monospace;

  @media (max-width: 768px) {
    display: none;
  }
}

/* 중앙 타이틀 */
.banner-mid {
  animation: fadeUp 0.6s ease 0.25s both;
}

.banner-title {
  margin: 0;
  font-size: 44px;
  font-weight: 800;
  line-height: 1.15;
  letter-spacing: -0.035em;
  color: #fff;

  @media (max-width: 1024px) { font-size: 34px; }
  @media (max-width: 768px)  { font-size: 26px; }

  .accent {
    background-image: linear-gradient(100deg, #8fb4ff, #c4b5fd, #67e8f9);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    color: transparent;
    display: inline-block;
  }
}

/* 하단 */
.banner-bottom {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: flex-end;
  gap: 28px;
  animation: fadeUp 0.6s ease 0.4s both;

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}

.banner-desc {
  margin: 0;
  max-width: 560px;
  font-size: 14px;
  line-height: 1.7;
  font-weight: 400;
  color: rgba(208, 212, 242, 0.72);

  @media (max-width: 768px) {
    font-size: 13px;
  }
}

.banner-cta {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  border-radius: 999px;
  background: #fff;
  color: #171636;
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
  box-shadow: 0 14px 34px rgba(120, 110, 255, 0.35);
  transition:
    transform 0.18s ease,
    filter 0.18s ease;
  white-space: nowrap;

  &:hover {
    transform: translateY(-2px);
    filter: brightness(1.05);
  }

  @media (max-width: 768px) {
    width: 100%;
    justify-content: center;
    padding: 12px 20px;
  }
}

.arrow {
  font-size: 16px;
}

/* 통계 카드 */
.stat-cards {
  display: flex;
  gap: 22px;

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 12px;
  }
}

.stat-card {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28px 30px;
  border-radius: 18px;
  background: #fff;
  border: 1px solid rgba(22, 24, 60, 0.07);
  box-shadow: 0 12px 30px rgba(40, 42, 95, 0.08);

  @media (max-width: 768px) {
    padding: 20px 22px;
  }
}

.stat-card-left {
  display: flex;
  flex-direction: column;
}

.stat-num {
  font-size: 44px;
  font-weight: 800;
  letter-spacing: -0.025em;
  color: #171a3c;
  line-height: 1;

  @media (max-width: 768px) {
    font-size: 32px;
  }
}

.stat-label {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-top: 15px;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.01em;
  color: #737899;
}

.stat-line {
  width: 16px;
  height: 2px;
  border-radius: 2px;
  background: @accent;
  flex-shrink: 0;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: @accent-soft;
  color: @accent;
  flex-shrink: 0;
}
</style>
