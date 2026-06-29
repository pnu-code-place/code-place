<template>
  <div class="ongoing-section">
    <div class="ongoing-card">
      <div class="section-header">
        <p class="section-title">진행 중인 대회</p>
        <span class="more-link" @click="goContestList">더보기 →</span>
      </div>

      <!-- 빈 상태 -->
      <div v-if="!loading && contests.length === 0 && upcomingContests.length === 0" class="empty-state">
        <img
          class="empty-illust"
          src="@/assets/images/contest-empty-calendar.svg"
          alt=""
        />
        <div class="empty-text">
          <p class="empty-title">현재 진행 중인 콘테스트가 없어요</p>
          <p class="empty-desc">
            다음 대회를 준비하는 동안, 추천 문제를 풀며<br />
            실력을 키워보는 건 어때요?
          </p>
          <div class="empty-actions">
            <button class="empty-btn-primary" @click="goProblemList">
              추천 문제 풀러가기 →
            </button>
            <span class="empty-btn-text" @click="goContestHistory">
              이전 대회 보기
            </span>
          </div>
        </div>
      </div>

      <!-- 대회 목록 (진행중 + 개최 예정 가로 나열) -->
      <div class="contest-list-wrap" v-else>
        <!-- 좌측 화살표 -->
        <div v-if="totalContests >= 3" class="scroll-arrow arrow-left" :class="{ visible: !scrolledToStart }">
          <svg width="16" height="28" viewBox="0 0 16 28" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M11 4L4 14l7 10"/>
          </svg>
        </div>
        <!-- 우측 화살표 -->
        <div v-if="totalContests >= 3" class="scroll-arrow arrow-right" :class="{ visible: !scrolledToEnd }">
          <svg width="16" height="28" viewBox="0 0 16 28" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 4l7 10-7 10"/>
          </svg>
        </div>
        <div
          class="contest-list"
          :class="{ 'is-scrollable': totalContests >= 3 }"
          ref="contestList"
          @mousedown="onDragStart"
          @scroll="onScroll"
        >
        <div
          class="contest-card"
          v-for="contest in contests"
          :key="contest.id"
          @click="goContest(contest)"
        >
          <div class="card-main">
            <div class="card-icon">
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#fff"
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
            </div>
            <div class="card-info">
              <div class="badge-row">
                <span class="badge-underway">● 진행중</span>
                <span class="badge-dday">{{ ddayShort(contest) }}</span>
              </div>
              <p class="card-title">{{ contest.title }}</p>
              <p class="card-date">
                {{ formatDate(contest.start_time) }} ~
                {{ formatDate(contest.end_time) }}
              </p>
            </div>
          </div>
          <div class="card-bottom">
            <div class="progress-bar">
              <div
                class="progress-fill"
                :style="{ width: progressWidth(contest) + '%' }"
              />
            </div>
            <span class="timer-badge">
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <circle cx="12" cy="12" r="9" />
                <path d="M12 7v5l3 3" />
              </svg>
              {{ timerLabel(contest) }}
            </span>
          </div>
        </div>
        <div
          class="contest-card upcoming"
          v-for="contest in upcomingContests"
          :key="'upcoming-' + contest.id"
          @click="goContest(contest)"
        >
          <div class="card-main">
            <div class="card-icon upcoming-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="3"/>
                <path d="M16 2v4M8 2v4M3 10h18"/>
                <path d="M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01"/>
              </svg>
            </div>
            <div class="card-info">
              <div class="badge-row">
                <span class="badge-upcoming">● 개최 예정</span>
                <span class="badge-dday">D-{{ daysUntilStart(contest) }}</span>
              </div>
              <p class="card-title">{{ contest.title }}</p>
              <p class="card-date">
                {{ formatDate(contest.start_time) }} ~
                {{ formatDate(contest.end_time) }}
              </p>
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@oj/api"

const DAY_NAMES = ["일", "월", "화", "수", "목", "금", "토"]

export default {
  name: "HomeOngoingContests",
  data() {
    return {
      contests: [],
      upcomingContests: [],
      loading: true,
      now: Date.now(),
      timer: null,
      scrolledToStart: true,
      scrolledToEnd: false,
      drag: {
        active: false,
        startX: 0,
        scrollLeft: 0,
        moved: false,
        lastX: 0,
        velocity: 0,
        lastTime: 0,
        rafId: null,
      },
    }
  },
  computed: {
    totalContests() {
      return this.contests.length + this.upcomingContests.length
    },
  },
  mounted() {
    api.getUnderwayContestList().then(
      (res) => {
        this.contests = (res.data.data || []).slice(0, 6)
        this.loading = false
      },
      () => {
        this.loading = false
      },
    )
    api.getNotStartedContestList().then((res) => {
      const now = Date.now()
      const sevenDays = 7 * 24 * 60 * 60 * 1000
      this.upcomingContests = (res.data.data || [])
        .filter((c) => {
          const start = new Date(c.start_time).getTime()
          return start - now <= sevenDays
        })
        .slice(0, 3)
    }).catch(() => {})
    this.timer = setInterval(() => {
      this.now = Date.now()
    }, 1000)
  },
  beforeDestroy() {
    clearInterval(this.timer)
    document.removeEventListener("mousemove", this._onDragMove)
    document.removeEventListener("mouseup", this._onDragEnd)
  },
  methods: {
    formatDate(dateStr) {
      if (!dateStr) return ""
      const d = new Date(dateStr)
      const day = DAY_NAMES[d.getDay()]
      return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, "0")}.${String(d.getDate()).padStart(2, "0")} (${day}) ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`
    },
    progressWidth(contest) {
      const start = new Date(contest.start_time).getTime()
      const end = new Date(contest.end_time).getTime()
      const elapsed = this.now - start
      const total = end - start
      return Math.min(100, Math.max(0, (elapsed / total) * 100))
    },
    daysLeft(contest) {
      const end = new Date(contest.end_time).getTime()
      const diff = end - this.now
      return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
    },
    daysUntilStart(contest) {
      const start = new Date(contest.start_time).getTime()
      const diff = start - this.now
      return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
    },
    ddayShort(contest) {
      const end = new Date(contest.end_time).getTime()
      const diff = end - this.now
      if (diff <= 0) return "종료"
      const days = Math.ceil(diff / (1000 * 60 * 60 * 24))
      return days === 0 ? "오늘 종료" : `${days}일 남음`
    },
    timerLabel(contest) {
      const end = new Date(contest.end_time).getTime()
      const diff = end - this.now
      if (diff <= 0) return "00:00:00"
      const totalSec = Math.floor(diff / 1000)
      const h = String(Math.floor(totalSec / 3600)).padStart(2, "0")
      const m = String(Math.floor((totalSec % 3600) / 60)).padStart(2, "0")
      const s = String(totalSec % 60).padStart(2, "0")
      return `${h}:${m}:${s}`
    },
    goContestList() {
      this.$router.push({ name: "contest-list" })
    },
    goContestHistory() {
      this.$router.push({ name: "contest-history-list" })
    },
    goProblemList() {
      this.$router.push({ name: "problem-list" })
    },
    goContest(contest) {
      if (this.drag.moved) return
      this.$router.push({
        name: "contest-overview",
        params: { contestID: contest.id },
      })
    },
    onScroll() {
      const el = this.$refs.contestList
      if (!el) return
      const max = el.scrollWidth - el.clientWidth
      this.scrolledToStart = el.scrollLeft <= 4
      this.scrolledToEnd = el.scrollLeft >= max - 4
    },
    onDragStart(e) {
      if (this.totalContests < 3) return
      const el = this.$refs.contestList
      if (this.drag.rafId) cancelAnimationFrame(this.drag.rafId)
      this.drag.active = true
      this.drag.moved = false
      this.drag.startX = e.clientX
      this.drag.lastX = e.clientX
      this.drag.scrollLeft = el.scrollLeft
      this.drag.velocity = 0
      this.drag.lastTime = performance.now()
      el.style.cursor = "grabbing"
      el.style.userSelect = "none"

      this._onDragMove = (ev) => {
        if (!this.drag.active) return
        const now = performance.now()
        const dt = now - this.drag.lastTime
        const dist = ev.clientX - this.drag.startX
        if (Math.abs(dist) > 4) this.drag.moved = true
        this.drag.velocity = (ev.clientX - this.drag.lastX) / (dt || 1)
        this.drag.lastX = ev.clientX
        this.drag.lastTime = now
        el.scrollLeft = this.drag.scrollLeft - dist
      }
      this._onDragEnd = () => {
        this.drag.active = false
        el.style.cursor = ""
        el.style.userSelect = ""
        document.removeEventListener("mousemove", this._onDragMove)
        document.removeEventListener("mouseup", this._onDragEnd)
        // 관성 스크롤
        let velocity = -this.drag.velocity * 15
        const inertia = () => {
          if (Math.abs(velocity) < 0.3) {
            setTimeout(() => { this.drag.moved = false }, 0)
            return
          }
          el.scrollLeft += velocity
          velocity *= 0.88
          this.drag.rafId = requestAnimationFrame(inertia)
        }
        this.drag.rafId = requestAnimationFrame(inertia)
      }
      document.addEventListener("mousemove", this._onDragMove)
      document.addEventListener("mouseup", this._onDragEnd)
    },
  },
}
</script>

<style scoped lang="less">
.ongoing-section {
  width: 100%;
  padding: 40px 0 0;
}

.ongoing-card {
  background-color: #ffffff;
  border: 1px solid #e5e5ed;
  border-radius: 20px;
  padding: 20px 28px 20px;
  overflow: visible;

  @media (max-width: 768px) {
    padding: 16px 16px;
  }
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #14141f;
  margin: 0;
}

.more-link {
  font-size: 13px;
  font-weight: 500;
  color: #5b64ed;
  cursor: pointer;

  &:hover {
    text-decoration: underline;
  }
}

/* 대회 목록 래퍼 */
.contest-list-wrap {
  position: relative;
}

/* 대회 목록 */
.contest-list {
  display: flex;
  flex-direction: row;
  gap: 12px;

  &.is-scrollable {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    cursor: grab;
    user-select: none;
    scrollbar-width: none;
    &::-webkit-scrollbar { display: none; }

    .contest-card {
      flex: 0 0 320px;

      @media (max-width: 768px) {
        flex: 0 0 280px;
      }
    }
  }

  @media (max-width: 768px) {
    &:not(.is-scrollable) {
      flex-direction: column;
    }
  }
}

/* 드래그 방향 유도 화살표 */
.scroll-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.4s;
  color: #c8c8de;

  svg {
    filter: drop-shadow(0 0 4px rgba(255, 255, 255, 1));
  }

  &.visible {
    opacity: 1;
  }

  &.arrow-left {
    left: -20px;
  }

  &.arrow-right {
    right: -20px;
  }
}

.contest-card {
  background: #ffffff;
  border: 1px solid #ebebf6;
  border-radius: 16px;
  padding: 20px 24px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition:
    box-shadow 0.2s,
    transform 0.2s;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(91, 100, 237, 0.1);
  }
}

.card-main {
  display: flex;
  align-items: flex-start;
  gap: 18px;
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: #6d5df0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
  overflow: hidden;
  flex: 1;
}

.badge-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.badge-underway {
  font-size: 11px;
  font-weight: 600;
  color: #16a34a;
  background-color: #dcfce7;
  border-radius: 99px;
  padding: 2px 8px;
}

.badge-dday {
  font-size: 11px;
  font-weight: 600;
  color: #59596b;
  background-color: #f0f0f6;
  border-radius: 99px;
  padding: 2px 8px;
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  color: #14141f;
  margin: 0;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.card-date {
  font-size: 12px;
  color: #9999a6;
  margin: 0;
}

.card-bottom {
  display: flex;
  align-items: center;
  gap: 14px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background-color: #ebebf6;
  border-radius: 99px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6d5df0, #8b7cff);
  border-radius: 99px;
  transition: width 0.5s;
}

.timer-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  font-weight: 700;
  color: #6d5df0;
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
}

.contest-card.upcoming {
  background: #faf9ff;
  border-color: #e8e5ff;
}

.upcoming-icon {
  background: #a89af0 !important;
}

.badge-upcoming {
  font-size: 11px;
  font-weight: 600;
  color: #7c6fe0;
  background-color: #ede9ff;
  border-radius: 99px;
  padding: 2px 8px;
}

/* 빈 상태 */
.empty-state {
  background-color: #f2f2fa;
  border-radius: 16px;
  padding: 32px 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 28px;

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 28px 20px;
    gap: 16px;
  }
}

.empty-illust {
  width: 100px;
  height: 100px;
  flex-shrink: 0;
  object-fit: contain;
}

.empty-text {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.empty-title {
  font-size: 18px;
  font-weight: 700;
  color: #14141f;
  margin: 0;
}

.empty-desc {
  font-size: 13px;
  color: #59596b;
  margin: 0;
  line-height: 1.65;
}

.empty-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 6px;
}

.empty-btn-primary {
  display: inline-flex;
  align-items: center;
  padding: 11px 22px;
  border-radius: 12px;
  background: #6d5df0;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: background 0.15s;

  &:hover {
    background: #5b4dd4;
  }
}

.empty-btn-text {
  font-size: 13px;
  font-weight: 500;
  color: #9999a6;
  cursor: pointer;

  &:hover {
    color: #6d5df0;
  }
}
</style>
