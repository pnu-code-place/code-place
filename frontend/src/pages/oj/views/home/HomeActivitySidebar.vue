<template>
  <div class="sidebar-section">
    <div class="sidebar-card">
      <div class="sidebar-header">
        <span class="sidebar-title">나의 활동</span>
        <span class="sidebar-more" v-if="isAuthenticated" @click="goMyHome">더보기 →</span>
      </div>

      <template v-if="isAuthenticated">
        <div class="stats-row">
          <div class="stat-item">
            <span class="stat-value">{{ profile.accepted_number || 0 }}</span>
            <span class="stat-label">푼 문제</span>
          </div>
          <div class="stat-divider" />
          <div class="stat-item">
            <span class="stat-value">{{ acceptanceRate }}%</span>
            <span class="stat-label">정답률</span>
          </div>
          <div class="stat-divider" />
          <div class="stat-item">
            <span class="stat-value">{{ profile.submission_number || 0 }}</span>
            <span class="stat-label">제출 횟수</span>
          </div>
        </div>

        <div class="score-row">
          <span class="score-label">획득 점수</span>
          <span class="score-value">{{ totalScore }}</span>
        </div>

        <div class="chart-area">
          <p class="chart-title">최근 2주 제출 현황</p>
          <div class="chart-bar-row">
            <div
              class="chart-bar"
              v-for="(bar, i) in activityBars"
              :key="i"
              :class="{ active: bar.active }"
              :style="{ height: bar.pct + '%' }"
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
          <p class="not-logged-desc">로그인하면 나의 활동을<br />확인할 수 있어요.</p>
          <button class="login-btn" @click="openLogin">로그인하기</button>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex"
import api from "@oj/api"

export default {
  name: "HomeActivitySidebar",
  data() {
    return {
      dailyCounts: {},
      totalScore: 0,
    }
  },
  mounted() {
    if (this.isAuthenticated) {
      this.loadData()
    }
  },
  computed: {
    ...mapGetters(["isAuthenticated", "user", "profile"]),
    acceptanceRate() {
      const sub = (this.profile && this.profile.submission_number) || 0
      const acc = (this.profile && this.profile.accepted_number) || 0
      if (!sub) return "0.0"
      return ((acc / sub) * 100).toFixed(1)
    },
    activityBars() {
      const today = new Date()
      const bars = Array.from({ length: 14 }, (_, i) => {
        const d = new Date(today)
        d.setDate(d.getDate() - (13 - i))
        const key = d.getFullYear() + "-" +
          String(d.getMonth() + 1).padStart(2, "0") + "-" +
          String(d.getDate()).padStart(2, "0")
        const label = (d.getMonth() + 1) + "/" + d.getDate()
        return { label, count: this.dailyCounts[key] || 0 }
      })
      const max = Math.max(...bars.map((b) => b.count), 1)
      return bars.map((b) => ({
        label: b.label,
        pct: Math.max((b.count / max) * 100, b.count > 0 ? 8 : 4),
        active: b.count > 0,
      }))
    },
  },
  methods: {
    ...mapActions(["changeModalStatus"]),
    loadData() {
      api.getSubmissionList(0, 200, { myself: "1" }).then((res) => {
        const results = (res.data.data && res.data.data.results) || []
        const counts = {}
        results.forEach((s) => {
          if (!s.create_time) return
          const d = new Date(s.create_time)
          const key = d.getFullYear() + "-" +
            String(d.getMonth() + 1).padStart(2, "0") + "-" +
            String(d.getDate()).padStart(2, "0")
          counts[key] = (counts[key] || 0) + 1
        })
        this.dailyCounts = counts
      }).catch(() => {})

      api.getDashboardInfo(this.user.username).then((res) => {
        const ojStatus = (res.data.data && res.data.data.ojStatus) || {}
        this.totalScore = ojStatus.total_score || 0
      }).catch(() => {
        this.totalScore = (this.profile && this.profile.total_score) || 0
      })
    },
    goMyHome() {
      this.$router.push({
        name: "user-home",
        params: { username: this.user.username },
      })
    },
    openLogin() {
      this.changeModalStatus({ visible: true, mode: "login" })
    },
  },
}
</script>

<style scoped lang="less">
.sidebar-section {
  padding: 16px 0 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  box-sizing: border-box;
}

.sidebar-card {
  background-color: #ffffff;
  border: 1px solid #e5e5ed;
  border-radius: 20px;
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.sidebar-title {
  font-size: 18px;
  font-weight: 700;
  color: #14141f;
}

.sidebar-more {
  font-size: 12px;
  font-weight: 500;
  color: #5b64ed;
  cursor: pointer;

  &:hover {
    text-decoration: underline;
  }
}

.stats-row {
  display: flex;
  align-items: center;
  background-color: #f8f8fc;
  border-radius: 12px;
  padding: 12px 0;
  margin-bottom: 12px;
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
}

.stat-divider {
  width: 1px;
  height: 28px;
  background-color: #e5e5ed;
  flex-shrink: 0;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #14141f;
}

.stat-label {
  font-size: 11px;
  color: #8c8c9e;
}

.score-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background-color: #eeeeff;
  border-radius: 10px;
  margin-bottom: 12px;
}

.score-label {
  font-size: 12px;
  font-weight: 500;
  color: #5b64ed;
}

.score-value {
  font-size: 14px;
  font-weight: 700;
  color: #5b64ed;
}

.chart-area {
  background-color: #f8f8fc;
  border-radius: 10px;
  padding: 10px 10px 8px;
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 60px;
}

.chart-title {
  font-size: 10px;
  color: #a6a6b2;
  margin: 0 0 6px;
}

.chart-bar-row {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  flex: 1;
}

.chart-bar {
  flex: 1;
  background-color: #d8daff;
  border-radius: 3px 3px 0 0;
  min-height: 4px;
  transition: background-color 0.15s;

  &.active {
    background-color: #5b64ed;
    opacity: 0.8;
  }
}

.chart-labels {
  display: flex;
  gap: 3px;
  margin-top: 5px;

  span {
    flex: 1;
    font-size: 8px;
    color: #c0c0d0;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
  }
}

.not-logged-in {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 20px 0;
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
  line-height: 1.6;
}

.login-btn {
  margin-top: 6px;
  padding: 8px 18px;
  background-color: #5b64ed;
  color: #ffffff;
  font-size: 12px;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.15s;

  &:hover {
    background-color: #4a53d4;
  }
}
</style>
