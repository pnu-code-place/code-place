<template>
  <div class="ongoing-section">
    <div class="ongoing-card">
      <div class="section-header">
        <p class="section-title">진행 중인 콘테스트</p>
        <span class="more-link" @click="goContestList">더보기 →</span>
      </div>
      <div v-if="!loading && contests.length === 0" class="empty-state">
        <div class="empty-card" @click="goContestHistory">
          <img class="empty-illust" src="@/assets/images/contest-empty-calendar.svg" alt="" />
          <div class="empty-text">
            <p class="empty-title">현재 진행 중인 콘테스트가 없어요 🐯</p>
            <p class="empty-desc">
              다음 콘테스트를 기대해주세요!<br />이전 콘테스트에 참여해보는 것도 좋아요.
            </p>
            <span class="empty-btn">이전 콘테스트 보기 →</span>
          </div>
        </div>
        <div class="empty-card" @click="goProblemList">
          <div class="empty-text">
            <p class="empty-title">추천 문제로 실력 향상하기 💪</p>
            <p class="empty-desc">
              콘테스트가 없어도 문제 풀기는 계속!<br />추천 문제를 풀고 실력을
              키워보세요.
            </p>
            <span class="empty-btn">추천 문제 풀러가기 →</span>
          </div>
          <img class="empty-illust" src="@/assets/images/contest-empty-clipboard.svg" alt="" />
        </div>
      </div>
      <div class="contest-cards" v-else>
        <div
          class="contest-card"
          v-for="contest in contests"
          :key="contest.id"
          @click="goContest(contest)"
        >
          <div class="card-top">
            <div
              class="card-icon"
              :style="{ backgroundColor: iconBg(contest) }"
            >
              <Icon :type="iconType(contest)" size="22" color="#ffffff" />
            </div>
            <div class="card-info">
              <span class="badge-underway">진행중</span>
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
            <span
              class="dday-badge"
              :class="{ 'dday-urgent': daysLeft(contest) === 0 }"
            >
              {{ ddayLabel(contest) }}
            </span>
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
      loading: true,
      now: Date.now(),
      timer: null,
    }
  },
  mounted() {
    api.getUnderwayContestList().then(
      (res) => {
        this.contests = (res.data.data || []).slice(0, 3)
        this.loading = false
      },
      () => {
        this.loading = false
      },
    )
    this.timer = setInterval(() => {
      this.now = Date.now()
    }, 1000)
  },
  beforeDestroy() {
    clearInterval(this.timer)
  },
  methods: {
    formatDate(dateStr) {
      if (!dateStr) return ""
      const d = new Date(dateStr)
      const day = DAY_NAMES[d.getDay()]
      return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, "0")}.${String(d.getDate()).padStart(2, "0")} (${day})`
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
    ddayLabel(contest) {
      const end = new Date(contest.end_time).getTime()
      const diff = end - this.now
      if (diff <= 0) return "종료"
      if (diff < 24 * 60 * 60 * 1000) {
        const h = String(Math.floor(diff / 3600000)).padStart(2, "0")
        const m = String(Math.floor((diff % 3600000) / 60000)).padStart(2, "0")
        const s = String(Math.floor((diff % 60000) / 1000)).padStart(2, "0")
        return `${h}:${m}:${s}`
      }
      return `D-${this.daysLeft(contest)}`
    },
    iconType(contest) {
      if (contest.rule_type === "OI") return "ios-pulse"
      return "trophy"
    },
    iconBg(contest) {
      const colors = ["#7b6ef5", "#f5a230", "#34c175"]
      return colors[contest.id % colors.length]
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
      this.$router.push({
        name: "contest-details",
        params: { contestID: contest.id },
      })
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
  padding: 12px 28px;
  padding-bottom: 20px;
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

.contest-cards {
  display: flex;
  gap: 16px;
}

.contest-card {
  flex: 1;
  background-color: #f8f8fc;
  border: 1px solid #f0f0f6;
  border-radius: 16px;
  padding: 20px 24px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 20px;
  transition:
    transform 0.2s,
    box-shadow 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.07);
  }
}

.card-top {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow: hidden;
}

.badge-underway {
  font-size: 11px;
  font-weight: 600;
  color: #16a34a;
  background-color: #dcfce7;
  border-radius: 99px;
  padding: 2px 8px;
  width: fit-content;
}

.card-title {
  font-size: 15px;
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
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background-color: #f0f0f6;
  border-radius: 99px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #5b64ed;
  border-radius: 99px;
  transition: width 0.5s;
}

.empty-state {
  display: flex;
  gap: 16px;
}

.empty-card {
  flex: 1;
  background-color: #eeeaff;
  border-radius: 20px;
  padding: 28px 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  cursor: pointer;
  transition: background-color 0.15s;

  &:hover {
    background-color: #e5e0ff;
  }

  &:first-child {
    flex: 1.4;
    background-color: #ffffff;
    border: 1.5px solid #e5e5ed;

    &:hover {
      background-color: #f8f7ff;
    }
  }
}

.empty-illust {
  width: 110px;
  height: 110px;
  flex-shrink: 0;
  object-fit: contain;
  filter: drop-shadow(0 6px 14px rgba(91, 100, 237, 0.22));
}

.empty-text {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.empty-title {
  font-size: 16px;
  font-weight: 700;
  color: #14141f;
  margin: 0;
  line-height: 1.4;
}

.empty-desc {
  font-size: 13px;
  color: #59596b;
  margin: 0;
  line-height: 1.65;
}

.empty-btn {
  display: inline-block;
  margin-top: 4px;
  font-size: 13px;
  font-weight: 600;
  color: #5b64ed;
  background-color: #ffffff;
  border: 1.5px solid #c9caff;
  border-radius: 99px;
  padding: 7px 16px;
  width: fit-content;
  cursor: pointer;
  transition: background-color 0.15s;

  .empty-card:hover & {
    background-color: #f5f3ff;
  }
}

.dday-badge {
  font-size: 13px;
  font-weight: 700;
  color: #5b64ed;
  background-color: #eeeaff;
  border-radius: 8px;
  padding: 4px 10px;
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;

  &.dday-urgent {
    color: #dc2626;
    background-color: #fee2e2;
  }
}
</style>
