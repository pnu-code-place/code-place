<template>
  <div class="row-padding">
    <!-- 공지사항 -->
    <div class="card notice-card">
      <div class="card-header">
        <span class="card-header-title">공지사항</span>
        <span class="card-header-more" @click="goNotice">더보기 &gt;</span>
      </div>
      <div class="notice-list">
        <div v-if="loading" class="skeleton-list">
          <div class="skeleton-item" v-for="i in 5" :key="i" />
        </div>
        <template v-else-if="announcements.length > 0">
          <div
            class="notice-row"
            v-for="(item, idx) in announcements.slice(0, 5)"
            :key="idx"
            @click="goNotice"
          >
            <span class="notice-dot" />
            <span class="notice-title">{{ item.title }}</span>
            <span class="notice-date">{{ formatDate(item.create_time) }}</span>
          </div>
        </template>
        <div v-else class="empty-text">공지사항이 없습니다.</div>
      </div>
    </div>

    <!-- 추천 문제 -->
    <div class="card problem-card">
      <div class="card-header">
        <span class="card-header-title">추천 문제</span>
        <span class="card-header-more" @click="goProblemList">더보기 &gt;</span>
      </div>
      <div class="problem-list">
        <div v-if="problemLoading" class="skeleton-list">
          <div class="skeleton-item" v-for="i in 5" :key="i" />
        </div>
        <template v-else-if="problems.length > 0">
          <div
            class="problem-row"
            v-for="(problem, idx) in problems.slice(0, 5)"
            :key="idx"
            @click="goProblem(problem._id)"
          >
            <span class="problem-title">{{ problem.title }}</span>
            <span
              class="difficulty-badge"
              :class="getDifficultyClass(problem.difficulty)"
            >{{ getDifficultyLabel(problem.difficulty) }}</span>
            <span class="success-rate" v-if="problem.submission_number > 0">
              성공률 {{ getSuccessRate(problem) }}%
            </span>
          </div>
        </template>
        <div v-else class="empty-text">추천 문제가 없습니다.</div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@oj/api"
import { mapActions } from "vuex"

export default {
  name: "HomeNoticeProblemRow",
  data() {
    return {
      loading: false,
      problemLoading: false,
      announcements: [],
      problems: [],
    }
  },
  mounted() {
    this.loadAnnouncements()
    this.loadProblems()
  },
  methods: {
    ...mapActions(["changeProblemSolvingState"]),
    loadAnnouncements() {
      this.loading = true
      api.getAnnouncementList(0, 5).then(
        (res) => {
          this.loading = false
          this.announcements = res.data.data.results || []
        },
        () => {
          this.loading = false
        },
      )
    },
    loadProblems() {
      this.problemLoading = true
      api.getHomeBonusProblem().then(
        (res) => {
          this.problemLoading = false
          this.problems = res.data.data || []
        },
        () => {
          this.problemLoading = false
        },
      )
    },
    formatDate(dateStr) {
      if (!dateStr) return ""
      const d = new Date(dateStr)
      return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, "0")}.${String(d.getDate()).padStart(2, "0")}`
    },
    getDifficultyLabel(difficulty) {
      const map = {
        VeryLow: "쉬움",
        Low: "쉬움",
        Mid: "중간",
        High: "어려움",
        VeryHigh: "어려움",
      }
      return map[difficulty] || difficulty
    },
    getDifficultyClass(difficulty) {
      if (difficulty === "VeryLow" || difficulty === "Low") return "easy"
      if (difficulty === "High" || difficulty === "VeryHigh") return "hard"
      return "mid"
    },
    getSuccessRate(problem) {
      if (!problem.submission_number) return 0
      return ((problem.accepted_number / problem.submission_number) * 100).toFixed(1)
    },
    goNotice() {
      this.$router.push({ name: "notice" })
    },
    goProblemList() {
      this.$router.push({ name: "problem-list" })
    },
    goProblem(id) {
      this.changeProblemSolvingState(true)
      this.$router.push({ name: "problem-details", params: { problemID: id } })
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
  height: 260px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.card-header-title {
  font-size: 14px;
  font-weight: 700;
  color: #14141f;
}

.card-header-more {
  font-size: 12px;
  color: #5b64ed;
  cursor: pointer;

  &:hover {
    text-decoration: underline;
  }
}

.notice-list,
.problem-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow: hidden;
  flex: 1;
}

.notice-row {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  overflow: hidden;

  &:hover .notice-title {
    color: #5b64ed;
  }
}

.notice-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #5b64ed;
  flex-shrink: 0;
}

.notice-title {
  font-size: 13px;
  color: #333345;
  flex: 1;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  transition: color 0.15s;
}

.notice-date {
  font-size: 11px;
  color: #9999a6;
  flex-shrink: 0;
}

.problem-row {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  overflow: hidden;

  &:hover .problem-title {
    color: #5b64ed;
  }
}

.problem-title {
  font-size: 13px;
  color: #333345;
  flex: 1;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  transition: color 0.15s;
}

.difficulty-badge {
  font-size: 11px;
  font-weight: 500;
  padding: 3px 8px;
  border-radius: 99px;
  flex-shrink: 0;

  &.easy {
    background-color: #e0faeb;
    color: #1aa666;
  }

  &.mid {
    background-color: #fff7de;
    color: #cc8c0d;
  }

  &.hard {
    background-color: #ffebeb;
    color: #d93333;
  }
}

.success-rate {
  font-size: 12px;
  color: #8c8c9e;
  flex-shrink: 0;
}

.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.skeleton-item {
  height: 20px;
  border-radius: 6px;
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
