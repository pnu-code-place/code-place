<template>
  <div class="hero-padding">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Fira+Code:wght@400;500&display=swap" />
    <div class="banner">
      <div class="noise" />
      <div class="grid-lines" />

      <!-- 왼쪽 -->
      <div class="banner-left">
        <div class="eyebrow">
          <span class="eyebrow-dot" />
          부산대학교 공식 코딩 플랫폼
        </div>
        <h1 class="banner-title">
          코드를 배우고,<br />
          문제를 해결하며,<br />
          <span class="accent">함께 성장하는 공간</span>
        </h1>
        <p class="banner-desc">
          알고리즘 문제 풀이부터 실전 코딩테스트, 대회 운영,
          AI 조교 기반 학습 지원까지 제공하는 통합 프로그래밍 교육 플랫폼입니다.
        </p>
        <button class="banner-cta" @click="goProblemList">
          코드플레이스 알아보기 <span class="arrow">→</span>
        </button>
      </div>

      <div class="vline" />

      <!-- 오른쪽 스탯 -->
      <div class="banner-right">
        <div class="stat-cards">
          <div class="stat-card">
            <div class="stat-card-left">
              <div class="stat-card-num">{{ totalProblems }}</div>
              <div class="stat-card-label">// 알고리즘 문제</div>
            </div>
            <div class="stat-card-icon">📋</div>
          </div>
          <div class="stat-card">
            <div class="stat-card-left">
              <div class="stat-card-num">6 TIER</div>
              <div class="stat-card-label">// 새싹 → 다이아몬드</div>
            </div>
            <div class="stat-card-icon">🏆</div>
          </div>
          <div class="stat-card">
            <div class="stat-card-left">
              <div class="stat-card-num">24 / 7</div>
              <div class="stat-card-label">// 실시간 채점 서버</div>
            </div>
            <div class="stat-card-icon">⚡</div>
          </div>
        </div>
        <div class="pnu-tag">PUSAN NATIONAL UNIVERSITY — CODEPLACE</div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex"
import api from "@oj/api"

export default {
  name: "HomeHeroSection",
  data() {
    return {
      totalProblems: "—",
    }
  },
  computed: {
    ...mapGetters(["isAuthenticated", "user", "profile"]),
  },
  mounted() {
    api.getHomeStatistics().then((res) => {
      const d = res.data.data
      const n = d.total_problem_length || 0
      this.totalProblems = n.toLocaleString() + "+"
    }).catch(() => {})
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

.banner {
  width: 100%;
  min-height: 300px;
  border-radius: 20px;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: row;
  align-items: stretch;
  background:
    radial-gradient(ellipse 80% 120% at 10% 50%, #1a0a4e 0%, transparent 60%),
    radial-gradient(ellipse 60% 100% at 90% 20%, #1e3a8a 0%, transparent 55%),
    radial-gradient(ellipse 70% 80% at 60% 90%, #312e81 0%, transparent 60%),
    linear-gradient(135deg, #0f0728 0%, #1a1060 40%, #1e2fa0 100%);

  &::before {
    content: '';
    position: absolute;
    top: -60px; left: -60px;
    width: 340px; height: 340px;
    background: radial-gradient(circle, rgba(139,92,246,0.35) 0%, transparent 70%);
    pointer-events: none;
    z-index: 1;
  }
  &::after {
    content: '';
    position: absolute;
    bottom: -80px; right: 220px;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(59,130,246,0.25) 0%, transparent 70%);
    pointer-events: none;
    z-index: 1;
  }
}

.noise {
  position: absolute;
  inset: 0;
  z-index: 2;
  opacity: 0.04;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  background-size: 180px;
  pointer-events: none;
}

.grid-lines {
  position: absolute;
  inset: 0;
  z-index: 2;
  background-image:
    linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px);
  background-size: 48px 48px;
  pointer-events: none;
}

/* 왼쪽 */
.banner-left {
  flex: 1;
  padding: 52px 56px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  z-index: 5;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: 'Fira Code', monospace;
  font-size: 11px;
  color: rgba(167,139,250,0.9);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  margin-bottom: 18px;
  animation: fadeUp 0.6s ease 0.2s both;
}

.eyebrow-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #a78bfa;
  box-shadow: 0 0 8px #a78bfa;
  flex-shrink: 0;
}

.banner-title {
  font-weight: 900;
  font-size: 42px;
  line-height: 1.2;
  color: #ffffff;
  letter-spacing: -0.03em;
  margin-bottom: 16px;
  animation: fadeUp 0.6s ease 0.35s both;

  .accent {
    background: linear-gradient(90deg, #818cf8, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
}

.banner-desc {
  font-size: 13.5px;
  color: rgba(255,255,255,0.45);
  line-height: 1.85;
  font-weight: 300;
  max-width: 400px;
  margin-bottom: 32px;
  animation: fadeUp 0.6s ease 0.48s both;
}

.banner-cta {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-family: 'Fira Code', monospace;
  font-size: 13px;
  font-weight: 500;
  color: #fff;
  background: rgba(99,102,241,0.9);
  border: 1px solid rgba(129,140,248,0.5);
  padding: 13px 24px;
  border-radius: 8px;
  letter-spacing: 0.04em;
  width: fit-content;
  cursor: pointer;
  transition: background 0.2s, transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 24px rgba(99,102,241,0.4);
  animation: fadeUp 0.6s ease 0.6s both;

  &:hover {
    background: rgba(99,102,241,1);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(99,102,241,0.55);

    .arrow { transform: translateX(4px); }
  }
}

.arrow {
  transition: transform 0.2s;
  display: inline-block;
}

/* 구분선 */
.vline {
  width: 1px;
  align-self: stretch;
  background: linear-gradient(to bottom, transparent, rgba(255,255,255,0.1) 30%, rgba(255,255,255,0.1) 70%, transparent);
  margin: 40px 0;
  flex-shrink: 0;
  position: relative;
  z-index: 5;
}

/* 오른쪽 */
.banner-right {
  width: 380px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-end;
  padding: 52px 52px 52px 0;
  position: relative;
  z-index: 5;
}

.stat-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  animation: fadeLeft 0.7s ease 0.5s both;
}

.stat-card {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  backdrop-filter: blur(10px);
  transition: background 0.2s, border-color 0.2s;

  &:hover {
    background: rgba(255,255,255,0.1);
    border-color: rgba(129,140,248,0.3);
  }
}

.stat-card-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-card-num {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 32px;
  line-height: 1;
  color: #fff;
  letter-spacing: 0.01em;
}

.stat-card-label {
  font-family: 'Fira Code', monospace;
  font-size: 10px;
  color: rgba(255,255,255,0.35);
  letter-spacing: 0.08em;
}

.stat-card-icon {
  font-size: 22px;
  opacity: 0.7;
}

.pnu-tag {
  margin-top: 16px;
  align-self: flex-end;
  font-family: 'Fira Code', monospace;
  font-size: 10px;
  color: rgba(255,255,255,0.2);
  letter-spacing: 0.1em;
  animation: fadeLeft 0.6s ease 0.75s both;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes fadeLeft {
  from { opacity: 0; transform: translateX(16px); }
  to   { opacity: 1; transform: translateX(0); }
}
</style>
