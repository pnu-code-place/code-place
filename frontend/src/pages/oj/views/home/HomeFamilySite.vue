<template>
  <div class="fs-root">
    <div class="fs-header">
      <span class="fs-header-label">FAMILY SITE</span>
      <div class="fs-header-line" />
      <div class="fs-nav-group">
        <button
          type="button"
          class="fs-nav-btn"
          aria-label="이전"
          @click="slidePrev"
        >
          <i class="fas fa-chevron-left" />
        </button>
        <button
          type="button"
          class="fs-nav-btn"
          aria-label="다음"
          @click="slideNext"
        >
          <i class="fas fa-chevron-right" />
        </button>
      </div>
    </div>

    <div class="fs-carousel">
      <div
        ref="track"
        class="fs-track"
        :class="{ 'is-animating': isAnimating }"
        :style="trackStyle"
        @transitionend="onTransitionEnd"
        @mousedown="onDragStart"
        @mousemove="onDragMove"
        @mouseup="onDragEnd"
        @mouseleave="onDragEnd"
        @touchstart="onTouchStart"
        @touchmove="onTouchMove"
        @touchend="onTouchEnd"
      >
        <a
          class="fs-card"
          v-for="site in sites"
          :key="site.title"
          :href="site.url"
          target="_blank"
          rel="noopener noreferrer"
          @click="onCardClick"
          @dragstart.prevent
        >
          <div class="fs-accent" />
          <div class="fs-card-title" v-html="site.title" />
          <div class="fs-card-sub">바로가기 <span class="fs-arrow">→</span></div>
        </a>
      </div>
    </div>
  </div>
</template>

<script>
const DRAG_THRESHOLD_PX = 5

export default {
  name: "HomeFamilySite",
  data() {
    return {
      isAnimating: false,
      isDragging: false,
      dragMoved: false,
      dragStartX: 0,
      translateX: 0,
      transitionDuration: 0,
      animationTimer: null,
      sites: [
        {
          title: "부산대학교<br>AI융합교육원",
          url: "https://swedu.pusan.ac.kr",
        },
        {
          title: "부산대학교<br>학생지원시스템",
          url: "https://onestop.pusan.ac.kr/",
        },
        {
          title: "스마트교육플랫폼<br>PLATO",
          url: "https://plato.pusan.ac.kr",
        },
        {
          title: "온라인강좌<br>인프런",
          url: "https://www.inflearn.com",
        },
        {
          title: "부산대학교<br>SW역량지원시스템",
          url: "https://swcss.pusan.ac.kr/",
        },
        {
          title: "부산대학교<br>AIPMS",
          url: "https://aipms.pusan.ac.kr",
        },
        {
          title: "부산대학교<br>서버관리시스템",
          url: "https://pickle.pusan.ac.kr",
        },
      ],
    }
  },
  computed: {
    trackStyle() {
      return {
        transform: `translateX(${this.translateX}px)`,
        transition:
          this.transitionDuration > 0
            ? `transform ${this.transitionDuration}ms cubic-bezier(0.25, 1, 0.5, 1)`
            : "none",
      }
    },
  },
  beforeDestroy() {
    if (this.animationTimer) clearTimeout(this.animationTimer)
  },
  methods: {
    getCardStep() {
      const track = this.$refs.track
      if (!track) return 0
      const card = track.querySelector(".fs-card")
      if (card) {
        const style = window.getComputedStyle(track)
        const gap = parseFloat(style.gap) || 8
        return card.offsetWidth + gap
      }
      return 0
    },
    slideNext() {
      if (this.isAnimating) return
      const step = this.getCardStep()
      if (!step) return

      this.isAnimating = true
      this.transitionDuration = 280
      this.translateX = -step

      if (this.animationTimer) clearTimeout(this.animationTimer)
      this.animationTimer = setTimeout(() => {
        if (this.isAnimating) {
          this.onTransitionEnd({ target: this.$refs.track })
        }
      }, 320)
    },
    slidePrev() {
      if (this.isAnimating) return
      const step = this.getCardStep()
      if (!step) return

      this.isAnimating = true

      // 1. 마지막 카드를 맨 앞으로 이동
      this.sites.unshift(this.sites.pop())

      // 2. 즉시 -step 위치로 보내어 화면상 위치 유지 (애니메이션 없음)
      this.transitionDuration = 0
      this.translateX = -step

      // 3. DOM 갱신 후 0으로 부드럽게 애니메이션
      this.$nextTick(() => {
        const track = this.$refs.track
        if (track) {
          void track.offsetHeight // force reflow
        }
        requestAnimationFrame(() => {
          this.transitionDuration = 280
          this.translateX = 0

          if (this.animationTimer) clearTimeout(this.animationTimer)
          this.animationTimer = setTimeout(() => {
            if (this.isAnimating) {
              this.onTransitionEnd({ target: this.$refs.track })
            }
          }, 320)
        })
      })
    },
    onTransitionEnd(event) {
      if (event && event.target !== this.$refs.track) return
      if (!this.isAnimating) return

      if (this.animationTimer) {
        clearTimeout(this.animationTimer)
        this.animationTimer = null
      }

      // Next 완료 시 맨 앞 카드를 맨 뒤로 이동
      if (this.translateX < 0) {
        this.sites.push(this.sites.shift())
      }

      this.transitionDuration = 0
      this.translateX = 0
      this.isAnimating = false
    },
    onDragStart(event) {
      if (this.isAnimating) return
      this.isDragging = true
      this.dragMoved = false
      this.dragStartX = event.pageX
    },
    onDragMove(event) {
      if (!this.isDragging) return
      const delta = event.pageX - this.dragStartX
      if (Math.abs(delta) > DRAG_THRESHOLD_PX) {
        this.dragMoved = true
      }
    },
    onDragEnd(event) {
      if (!this.isDragging) return
      this.isDragging = false
      const delta = (event.pageX || 0) - this.dragStartX
      if (delta < -30) {
        this.slideNext()
      } else if (delta > 30) {
        this.slidePrev()
      }
    },
    onTouchStart(event) {
      if (this.isAnimating) return
      if (!event.touches || event.touches.length === 0) return
      this.dragStartX = event.touches[0].pageX
      this.dragMoved = false
    },
    onTouchMove(event) {
      if (!event.touches || event.touches.length === 0) return
      const delta = event.touches[0].pageX - this.dragStartX
      if (Math.abs(delta) > DRAG_THRESHOLD_PX) {
        this.dragMoved = true
      }
    },
    onTouchEnd(event) {
      if (!this.dragMoved) return
      const touch = event.changedTouches && event.changedTouches[0]
      if (!touch) return
      const delta = touch.pageX - this.dragStartX
      if (delta < -30) {
        this.slideNext()
      } else if (delta > 30) {
        this.slidePrev()
      }
    },
    onCardClick(event) {
      if (this.dragMoved) {
        event.preventDefault()
        this.dragMoved = false
      }
    },
  },
}
</script>

<style scoped lang="less">
.fs-root {
  padding: 40px 0 0;
}

.fs-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.fs-header-label {
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.1em;
  color: #9999a6;
  white-space: nowrap;
}

.fs-header-line {
  height: 1px;
  flex: 1;
  background-color: #e5e5ed;
}

.fs-nav-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.fs-nav-btn {
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(91, 100, 237, 0.2);
  border-radius: 50%;
  background: #fff;
  color: var(--point-color, #5b64ed);
  cursor: pointer;
  font-size: 10px;
  box-shadow: 0 1px 4px rgba(91, 100, 237, 0.1);
  transition: all 0.15s ease;

  &:hover:not(:disabled) {
    background: rgba(91, 100, 237, 0.08);
    border-color: rgba(91, 100, 237, 0.35);
    transform: scale(1.05);
  }

  &:disabled {
    opacity: 0.35;
    cursor: not-allowed;
    box-shadow: none;
  }
}

.fs-carousel {
  position: relative;
  overflow: hidden;
  padding: 8px 4px 14px;
  margin-top: -6px;
  margin-bottom: -6px;
}

.fs-track {
  display: flex;
  gap: 8px;
  user-select: none;
  cursor: grab;

  &.is-animating {
    pointer-events: none;
  }
}

.fs-card {
  flex: 0 0 calc((100% - 4 * 8px) / 5);
  width: calc((100% - 4 * 8px) / 5);
  box-sizing: border-box;
  border-radius: 12px;
  padding: 12px 14px;
  cursor: pointer;
  text-decoration: none;
  display: flex;
  flex-direction: column;
  gap: 5px;
  background-color: rgba(91, 100, 237, 0.045);
  border: 1px solid rgba(91, 100, 237, 0.12);
  transition:
    transform 0.16s ease,
    box-shadow 0.16s ease,
    background-color 0.16s ease,
    border-color 0.16s ease;

  &:hover {
    transform: translateY(-2px);
    background-color: rgba(91, 100, 237, 0.08);
    box-shadow: 0 6px 18px rgba(91, 100, 237, 0.12);
    border-color: rgba(91, 100, 237, 0.25);

    .fs-arrow {
      transform: translateX(2px);
    }
  }

  @media (max-width: 768px) {
    flex: 0 0 calc((100% - 8px) / 2);
    width: calc((100% - 8px) / 2);
  }
}

.fs-accent {
  width: 20px;
  height: 2px;
  border-radius: 2px;
  background-color: var(--point-color, #5b64ed);
  margin-bottom: 2px;
}

.fs-card-title {
  font-size: 11.5px;
  font-weight: 700;
  line-height: 1.5;
  color: #2d3561;
}

.fs-card-sub {
  font-size: 10px;
  color: rgba(91, 100, 237, 0.75);
  display: flex;
  align-items: center;
  gap: 2px;
}

.fs-arrow {
  display: inline-block;
  transition: transform 0.14s;
}
</style>
