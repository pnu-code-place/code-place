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
          @click="scrollByStep(-1)"
        >
          <i class="fas fa-chevron-left" />
        </button>
        <button
          type="button"
          class="fs-nav-btn"
          aria-label="다음"
          @click="scrollByStep(1)"
        >
          <i class="fas fa-chevron-right" />
        </button>
      </div>
    </div>

    <div class="fs-carousel">
      <div
        ref="track"
        class="fs-track"
        :class="{ 'is-dragging': isDragging }"
        @scroll="onScroll"
        @mousedown="onDragStart"
        @mousemove="onDragMove"
        @mouseup="onDragEnd"
        @mouseleave="onDragEnd"
      >
        <a
          class="fs-card"
          v-for="(site, idx) in infiniteSites"
          :key="site.title + '-' + idx"
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
const DRAG_THRESHOLD_PX = 4

export default {
  name: "HomeFamilySite",
  data() {
    return {
      isDragging: false,
      dragMoved: false,
      dragStartX: 0,
      dragStartScrollLeft: 0,
      scrollResetTimer: null,
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
    // 무한 롤링을 위해 3세트 복제
    infiniteSites() {
      return [...this.sites, ...this.sites, ...this.sites]
    },
  },
  mounted() {
    this.$nextTick(() => {
      this.initScrollPosition()
    })
    window.addEventListener("resize", this.initScrollPosition)
  },
  beforeDestroy() {
    window.removeEventListener("resize", this.initScrollPosition)
    if (this.scrollResetTimer) clearTimeout(this.scrollResetTimer)
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
      return (track.clientWidth - 4 * 8) / 5 + 8
    },
    initScrollPosition() {
      const track = this.$refs.track
      if (!track) return
      const step = this.getCardStep()
      if (!step) return
      const setWidth = this.sites.length * step
      // 가운데 세트 시작점으로 초기 이동
      track.style.scrollBehavior = "auto"
      track.scrollLeft = setWidth
      track.style.scrollBehavior = "smooth"
    },
    onScroll() {
      if (this.isDragging) return
      if (this.scrollResetTimer) clearTimeout(this.scrollResetTimer)
      this.scrollResetTimer = setTimeout(() => {
        this.checkAndResetScroll()
      }, 150)
    },
    checkAndResetScroll() {
      const track = this.$refs.track
      if (!track || this.isDragging) return
      const step = this.getCardStep()
      if (!step) return
      const setWidth = this.sites.length * step

      if (track.scrollLeft < setWidth * 0.4) {
        track.style.scrollBehavior = "auto"
        track.scrollLeft += setWidth
        track.style.scrollBehavior = "smooth"
      } else if (track.scrollLeft > setWidth * 1.8) {
        track.style.scrollBehavior = "auto"
        track.scrollLeft -= setWidth
        track.style.scrollBehavior = "smooth"
      }
    },
    scrollByStep(direction) {
      const track = this.$refs.track
      if (!track) return
      const step = this.getCardStep()
      if (!step) return
      const setWidth = this.sites.length * step

      // 경계면에 너무 가까우면 먼저 가운데 세트로 보정
      if (track.scrollLeft < setWidth * 0.3) {
        track.style.scrollBehavior = "auto"
        track.scrollLeft += setWidth
        track.style.scrollBehavior = "smooth"
      } else if (track.scrollLeft > setWidth * 1.8) {
        track.style.scrollBehavior = "auto"
        track.scrollLeft -= setWidth
        track.style.scrollBehavior = "smooth"
      }

      // 1칸씩 부드럽게 무한 이동
      track.scrollBy({ left: direction * step, behavior: "smooth" })
    },
    onDragStart(event) {
      const track = this.$refs.track
      if (!track) return
      this.isDragging = true
      this.dragMoved = false
      this.dragStartX = event.pageX
      this.dragStartScrollLeft = track.scrollLeft
    },
    onDragMove(event) {
      if (!this.isDragging) return
      const track = this.$refs.track
      if (!track) return
      event.preventDefault()
      const delta = event.pageX - this.dragStartX
      if (Math.abs(delta) > DRAG_THRESHOLD_PX) this.dragMoved = true
      track.scrollLeft = this.dragStartScrollLeft - delta
    },
    onDragEnd() {
      this.isDragging = false
      this.checkAndResetScroll()
    },
    onCardClick(event) {
      // 드래그로 밀었던 경우엔 링크가 열리지 않게 막는다
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
}

.fs-track {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  scroll-snap-type: x proximity;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
  cursor: grab;
  user-select: none;
  scrollbar-width: none;
  padding: 8px 4px 14px;
  margin-top: -6px;
  margin-bottom: -6px;

  &::-webkit-scrollbar {
    display: none;
  }

  &.is-dragging {
    cursor: grabbing;
    scroll-behavior: auto;
  }
}

.fs-card {
  flex: 0 0 auto;
  width: calc((100% - 4 * 8px) / 5);
  scroll-snap-align: start;
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
