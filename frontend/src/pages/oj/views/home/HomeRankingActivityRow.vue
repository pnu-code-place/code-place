<template>
  <div class="row-padding">
    <!-- 랭킹 -->
    <div class="card ranking-card">
      <div class="card-header">
        <span class="card-header-title">랭킹</span>
        <div class="rank-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.value"
            class="tab-btn"
            :class="{ active: activeTab === tab.value }"
            @click="activeTab = tab.value"
          >
            {{ tab.label }}
          </button>
        </div>
        <span class="card-header-more" @click="goRanking">더보기 &gt;</span>
      </div>
      <div class="rank-list">
        <div v-if="rankLoading" class="skeleton-list">
          <div class="skeleton-item" v-for="i in 5" :key="i" />
        </div>
        <template v-else-if="rankingItems.length > 0">
          <div
            class="rank-row"
            v-for="(user, index) in rankingItems.slice(0, 5)"
            :key="user.username"
            @click="goUser(user.username)"
          >
            <span class="rank-medal" v-if="index < 3">{{ medals[index] }}</span>
            <span class="rank-number" v-else>{{ index + 1 }}</span>
            <img class="rank-avatar" :src="user.avatar" :alt="user.username" />
            <span class="rank-name">{{ user.username }}</span>
            <span class="rank-score">{{ user.total_score }}</span>
          </div>
        </template>
        <div v-else class="empty-text">랭킹 데이터가 없습니다.</div>
      </div>
    </div>

    <!-- 나의 활동 -->
    <div class="card activity-card">
      <div class="card-header">
        <span class="card-header-title">나의 활동</span>
        <span class="card-header-more" v-if="isAuthenticated" @click="goMyHome">더보기 &gt;</span>
      </div>

      <template v-if="isAuthenticated">
        <div class="stats-row">
          <div class="stat-item">
            <span class="stat-label">푼 문제</span>
            <span class="stat-value">{{ profile.accepted_number || 0 }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">정답률</span>
            <span class="stat-value">{{ acceptanceRate }}%</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">획득한 점수</span>
            <span class="stat-value">{{ profile.total_score || 0 }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">제출 횟수</span>
            <span class="stat-value">{{ profile.submission_number || 0 }}</span>
          </div>
        </div>
        <div class="chart-area">
          <div class="chart-bar-row">
            <div
              class="chart-bar"
              v-for="(bar, i) in activityBars"
              :key="i"
              :style="{ height: bar.height + 'px' }"
            />
          </div>
          <div class="chart-labels">
            <span v-for="(bar, i) in activityBars" :key="i">{{ bar.label }}</span>
          </div>
        </div>
      </template>

      <template v-else>
        <div class="not-logged-in">
          <p class="not-logged-title">로그인이 필요합니다</p>
          <p class="not-logged-desc">로그인하면 나의 활동을 확인할 수 있어요.</p>
          <button class="login-btn" @click="openLogin">로그인하기</button>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import api from "@oj/api"
import { mapGetters, mapActions } from "vuex"

export default {
  name: "HomeRankingActivityRow",
  data() {
    return {
      rankLoading: false,
      rankingItems: [],
      medals: ["🥇", "🥈", "🥉"],
      activeTab: "all",
      tabs: [
        { label: "전체", value: "all" },
        { label: "주간", value: "weekly" },
        { label: "월간", value: "monthly" },
      ],
    }
  },
  mounted() {
    this.loadRanking()
  },
  computed: {
    ...mapGetters(["profile", "isAuthenticated", "user"]),
    acceptanceRate() {
      const sub = this.profile.submission_number || 0
      const acc = this.profile.accepted_number || 0
      if (!sub) return "0.0"
      return ((acc / sub) * 100).toFixed(1)
    },
    activityBars() {
      const today = new Date()
      return Array.from({ length: 7 }, (_, i) => {
        const d = new Date(today)
        d.setDate(d.getDate() - (6 - i))
        const label = `${d.getMonth() + 1}/${d.getDate()}`
        const height = Math.floor(Math.random() * 40) + 10
        return { label, height }
      })
    },
  },
  methods: {
    ...mapActions(["changeModalStatus"]),
    loadRanking() {
      this.rankLoading = true
      api.getHomeRealTimeRanking().then(
        (res) => {
          this.rankLoading = false
          this.rankingItems = res.data.data || []
        },
        () => {
          this.rankLoading = false
        },
      )
    },
    goRanking() {
      this.$router.push({ name: "acm-rank" })
    },
    goUser(username) {
      this.$router.push({ name: "user-home", params: { username } })
    },
    goMyHome() {
      this.$router.push({ name: "user-home", params: { username: this.user.username } })
    },
    openLogin() {
      this.changeModalStatus({ visible: true, mode: "login" })
    },
  },
}
</script>

<style scoped lang="less">
.row-padding {
  width: 100%;
  padding: 20px 0 0;
  display: flex;
  gap: 20px;
}

.card {
  background-color: #ffffff;
  border: 1px solid #e5e5ed;
  border-radius: 16px;
  padding: 20px 24px;
  height: 280px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow: hidden;
}

.ranking-card {
  flex: 1 1 0;
}

.activity-card {
  flex: 0 0 380px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.card-header-title {
  font-size: 14px;
  font-weight: 700;
  color: #14141f;
}

.rank-tabs {
  display: flex;
  gap: 4px;
}

.tab-btn {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  background-color: #f5f5f7;
  color: #737385;
  transition: all 0.15s;

  &.active {
    background-color: #5b64ed;
    color: #ffffff;
  }

  &:hover:not(.active) {
    background-color: #ebebf2;
  }
}

.card-header-more {
  font-size: 12px;
  color: #5b64ed;
  cursor: pointer;
  margin-left: auto;

  &:hover {
    text-decoration: underline;
  }
}

.rank-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow: hidden;
  flex: 1;
}

.rank-row {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 2px 0;

  &:hover .rank-name {
    color: #5b64ed;
  }
}

.rank-medal {
  font-size: 18px;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}

.rank-number {
  font-size: 13px;
  color: #9999a6;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}

.rank-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  flex-shrink: 0;
  object-fit: cover;
}

.rank-name {
  font-size: 13px;
  font-weight: 500;
  color: #333345;
  flex: 1;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  transition: color 0.15s;
}

.rank-score {
  font-size: 14px;
  font-weight: 600;
  color: #14141f;
  flex-shrink: 0;
}

/* 나의 활동 */
.stats-row {
  display: flex;
  flex-shrink: 0;
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-label {
  font-size: 11px;
  color: #8c8c9e;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #14141f;
}

.chart-area {
  background-color: #f8f8fe;
  border-radius: 10px;
  flex: 1;
  padding: 12px 12px 8px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  overflow: hidden;
}

.chart-bar-row {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  flex: 1;
}

.chart-bar {
  flex: 1;
  background-color: #5b64ed;
  border-radius: 4px 4px 0 0;
  opacity: 0.6;
  min-height: 4px;
}

.chart-labels {
  display: flex;
  gap: 8px;
  margin-top: 6px;

  span {
    flex: 1;
    font-size: 10px;
    color: #a6a6b2;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
  }
}

.not-logged-in {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  text-align: center;
}

.not-logged-title {
  font-size: 14px;
  font-weight: 600;
  color: #333345;
  margin: 0;
}

.not-logged-desc {
  font-size: 12px;
  color: #8c8c9e;
  margin: 0;
}

.login-btn {
  margin-top: 8px;
  padding: 8px 20px;
  background-color: #5b64ed;
  color: #ffffff;
  font-size: 13px;
  font-weight: 600;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background-color: #4a53d4;
  }
}

.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.skeleton-item {
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(90deg, #f0f0f4 25%, #e8e8f0 50%, #f0f0f4 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}

.empty-text {
  font-size: 13px;
  color: #9999a6;
  text-align: center;
  margin-top: 20px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
