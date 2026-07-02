<template>
  <div class="feature-banner-wrap">
    <div class="feature-card">
      <!-- 좌측 copy -->
      <div class="copy">
        <div class="badge-row">
          <span class="badge-new">NEW</span>
          <span class="badge-label">{{ slides[current].label }}</span>
        </div>
        <transition name="txt" mode="out-in">
          <div :key="current" class="copy-body">
            <div class="feature-title">{{ slides[current].title }}</div>
            <div class="feature-desc">{{ slides[current].desc }}</div>
          </div>
        </transition>
        <div class="actions">
          <a
            class="cta-btn"
            :href="slides[current].link"
            target="_blank"
            rel="noopener noreferrer"
            >자세히 알아보기 →</a
          >
          <div class="dots">
            <span
              v-for="(_, i) in slides"
              :key="i"
              class="dot"
              :class="{ active: i === current }"
              @click="jumpTo(i)"
            ></span>
          </div>
        </div>
      </div>

      <!-- 우측 visual -->
      <div class="visual">
        <!-- 아이콘 뱃지 -->
        <div class="icon-badge" :style="{ background: slides[current].iconBg }">
          {{ slides[current].emoji }}
        </div>

        <!-- AI 슬라이드 mockup -->
        <transition name="vis" mode="out-in">
          <div v-if="current === 0" key="ai" class="mockup-wrap">
            <div class="mockup">
              <div class="mock-header">
                <span class="tl" style="background: #ff5f57"></span>
                <span class="tl" style="background: #febc2e"></span>
                <span class="tl" style="background: #28c840"></span>
                <span class="mock-fname">stairs.py</span>
              </div>
              <div class="mock-code">
                <div class="cline">
                  <span class="ln">1</span
                  ><span class="ct" style="color: #4a4660"
                    >n = int(input())</span
                  >
                </div>
                <div class="cline">
                  <span class="ln">2</span
                  ><span class="ct" style="color: #4a4660">dp = [0] * n</span>
                </div>
                <div class="cline">
                  <span class="ln">3</span
                  ><span class="ct" style="color: #4a4660"
                    >for i in range(n):</span
                  >
                </div>
                <div class="cline err">
                  <span class="ln">4</span
                  ><span class="ct" style="color: #c0392b; padding-left: 16px"
                    >dp[i] = ???</span
                  >
                </div>
              </div>
              <div class="hint-bubble">
                <div class="hint-icon">🤖</div>
                <div class="hint-text">
                  <div class="hint-title">AI 조교 힌트</div>
                  <div class="hint-body-text">
                    한 칸/두 칸 전 상태를 떠올려 보세요. dp[i]는 dp[i-1],
                    dp[i-2] 중 무엇과 이어질까요? 💡
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- GitHub 슬라이드 mockup -->
          <div v-else key="hub" class="mockup-wrap">
            <div class="mockup">
              <div class="mock-header">
                <div class="gh-logo">G</div>
                <span class="mock-repo">my-algorithm-solutions</span>
                <span class="mock-branch">main</span>
              </div>
              <div class="mock-files">
                <div class="frow" v-for="f in hubFiles" :key="f">
                  <div class="fcheck">✓</div>
                  <div class="fname">{{ f }}</div>
                  <div class="fext">.py</div>
                </div>
              </div>
              <div class="mock-status">
                <div class="sdot"></div>
                <div class="stext">Accepted → 자동 커밋 완료</div>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "HomeNewFeatureBanner",
  data() {
    return {
      current: 0,
      timer: null,
      hubFiles: ["1000_A+B", "2839_설탕배달", "11726_2xn타일링"],
      slides: [
        {
          label: "AI 학습 도우미",
          title: "AI 조교가 막히는 순간을 딱 맞게 도와드려요",
          desc: "문제를 푸는 도중 막힐 때, AI 조교가 정답을 알려주지 않으면서 방향을 잡아주는 힌트를 실시간으로 제공합니다. 스스로 푸는 힘을 기르며 학습하세요.",
          emoji: "🤖",
          iconBg: "linear-gradient(145deg,#7B6FF0,#5849C9)",
          link: "https://code.pusan.ac.kr/notice/52",
        },
        {
          label: "GitHub 자동 기록",
          title: "해결한 문제가 GitHub에 자동으로 쌓입니다",
          desc: "코드플레이스 허브는 해결한 모든 문제를 GitHub 레포지토리에 자동 업로드하는 크롬 확장 프로그램입니다. 'Accepted' 순간 코드와 문제 요약이 저장되어 포트폴리오가 체계적으로 완성돼요.",
          emoji: "🔗",
          iconBg: "linear-gradient(145deg,#2ECC71,#1A9E55)",
          link: "https://code.pusan.ac.kr/notice/11",
        },
      ],
    }
  },
  mounted() {
    this.timer = setInterval(() => {
      this.current = (this.current + 1) % this.slides.length
    }, 6500)
  },
  beforeDestroy() {
    clearInterval(this.timer)
  },
  methods: {
    jumpTo(i) {
      this.current = i
      clearInterval(this.timer)
      this.timer = setInterval(() => {
        this.current = (this.current + 1) % this.slides.length
      }, 4500)
    },
    goFeature() {},
  },
}
</script>

<style scoped lang="less">
.feature-banner-wrap {
  width: 100%;
  padding: 20px 0 0;
}

/* ─── 카드 ─── */
.feature-card {
  display: flex;
  align-items: stretch;
  height: 240px;
  background: #fff;
  border: 1px solid #efeef6;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(20, 20, 40, 0.04);

  @media (max-width: 768px) {
    height: auto;
    flex-direction: column;
  }
}

/* ─── 좌측 copy ─── */
.copy {
  flex: 1;
  min-width: 0;
  padding: 40px 44px;
  display: flex;
  flex-direction: column;
  justify-content: center;

  @media (max-width: 768px) {
    padding: 28px 24px 20px;
  }
}

.badge-row {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-bottom: 8px;
}

.badge-new {
  background: #f26646;
  color: #fff;
  font-size: 11px;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 999px;
  letter-spacing: 0.5px;
}

.badge-label {
  font-size: 12px;
  font-weight: 600;
  color: #9c98ae;
}

.feature-title {
  font-size: 22px;
  font-weight: 800;
  color: #2e2a47;
  letter-spacing: -0.7px;
  line-height: 1.25;

  @media (max-width: 1100px) {
    font-size: 24px;
  }
  @media (max-width: 768px) {
    font-size: 21px;
  }
}

.feature-desc {
  font-size: 13px;
  font-weight: 500;
  color: #6e6a85;
  margin-top: 8px;
  line-height: 1.65;
  height: 72px;
  overflow: hidden;

  @media (max-width: 768px) {
    height: auto;
  }
}

.actions {
  display: flex;
  align-items: center;
  gap: 18px;
}

.cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #fff;
  color: #6c5ce7;
  font-size: 12px;
  font-weight: 800;
  padding: 12px 20px;
  border-radius: 13px;
  border: none;
  cursor: pointer;
  box-shadow: 0 10px 18px rgba(108, 92, 231, 0.3);
  transition: transform 0.15s;

  &:hover {
    transform: translateY(-1px);
  }
}

.dots {
  display: flex;
  gap: 8px;
  align-items: center;

  .dot {
    height: 8px;
    border-radius: 999px;
    cursor: pointer;
    transition: all 0.2s;
    background: #d8d3ef;
    width: 8px;

    &.active {
      width: 22px;
      background: #6c5ce7;
    }
  }
}

/* ─── 우측 visual ─── */
.visual {
  width: 400px;
  flex: none;
  position: relative;
  background: linear-gradient(150deg, #f0eefc, #e7e3fa);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;

  @media (max-width: 768px) {
    width: 100%;
    min-height: 240px;
  }
}

.icon-badge {
  position: absolute;
  left: 22px;
  top: 22px;
  width: 34px;
  height: 34px;
  border-radius: 11px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  box-shadow: 0 8px 16px rgba(108, 92, 231, 0.28);
  z-index: 2;
}

.mockup-wrap {
  transform: scale(0.82);
  transform-origin: center;
}

/* ─── 공통 mockup 윈도우 ─── */
.mockup {
  width: 300px;
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 16px 34px rgba(60, 50, 110, 0.16);
  overflow: hidden;
}

.mock-header {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 11px 15px;
  background: #1e2229;
}

.tl {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  flex-shrink: 0;
}

.mock-fname {
  margin-left: 6px;
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.6);
}

/* ─── 코드 영역 ─── */
.mock-code {
  padding: 14px 15px 10px;
  background: #fff;
}

.cline {
  display: flex;
  gap: 10px;
  font-size: 11px;
  font-weight: 600;
  font-family: "SF Mono", ui-monospace, monospace;
  line-height: 1.7;

  &.err {
    background: rgba(192, 57, 43, 0.06);
  }
}

.ln {
  color: #c4c0d6;
  width: 14px;
  text-align: right;
  flex-shrink: 0;
}

/* ─── 힌트 버블 ─── */
.hint-bubble {
  margin: 4px 14px 16px;
  background: linear-gradient(135deg, #f0eefc, #e9e4fb);
  border: 1px solid #ded8f6;
  border-radius: 13px;
  padding: 12px 13px;
  display: flex;
  gap: 10px;
}

.hint-icon {
  width: 26px;
  height: 26px;
  flex-shrink: 0;
  border-radius: 8px;
  background: linear-gradient(145deg, #7b6ff0, #5849c9);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
}

.hint-text {
  .hint-title {
    font-size: 11px;
    font-weight: 800;
    color: #3730a3;
    margin-bottom: 2px;
  }
  .hint-body-text {
    font-size: 10.5px;
    font-weight: 500;
    color: #4338ca;
    line-height: 1.5;
  }
}

/* ─── GitHub 헤더 ─── */
.gh-logo {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #fff;
  color: #1e2229;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 800;
  flex-shrink: 0;
}

.mock-repo {
  flex: 1;
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mock-branch {
  font-size: 10px;
  font-weight: 700;
  color: #9d8ef5;
  background: rgba(157, 142, 245, 0.15);
  padding: 2px 8px;
  border-radius: 999px;
  flex-shrink: 0;
}

/* ─── 파일 목록 ─── */
.mock-files {
  background: #fff;
}

.frow {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 9px 12px;
  border-bottom: 1px solid #f1eff8;

  .fcheck {
    width: 18px;
    height: 18px;
    flex-shrink: 0;
    border-radius: 5px;
    background: #e4f7ec;
    color: #15a35e;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 800;
  }

  .fname {
    flex: 1;
    font-size: 12px;
    font-weight: 600;
    color: #4a4660;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .fext {
    font-size: 10px;
    font-weight: 600;
    color: #9c98ae;
  }
}

.mock-status {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 11px 13px;
  background: #f7f6fd;

  .sdot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #22c26b;
    flex-shrink: 0;
  }

  .stext {
    font-size: 11px;
    font-weight: 700;
    color: #15a35e;
  }
}

/* ─── 트랜지션 ─── */
.txt-enter-active,
.txt-leave-active {
  transition: opacity 0.4s ease;
}
.txt-enter,
.txt-leave-to {
  opacity: 0;
}

.vis-enter-active,
.vis-leave-active {
  transition: opacity 0.45s ease;
}
.vis-enter,
.vis-leave-to {
  opacity: 0;
}
</style>
