<template>
  <div class="sidebar-section">
    <div class="sidebar-card">
      <div class="sidebar-header">
        <span class="sidebar-title">이번 주 인기 문제</span>
        <span class="sidebar-more" @click="goProblemList">더보기 →</span>
      </div>

      <div v-if="loading" class="skeleton-list">
        <div class="skeleton-item" v-for="i in 3" :key="i" />
      </div>

      <template v-else-if="problems.length > 0">
        <div
          class="problem-item"
          v-for="(problem, index) in problems"
          :key="problem._id"
          @click="enterProblem(problem._id)"
        >
          <span class="rank-num" :class="rankClass(index)">{{ index + 1 }}</span>
          <div class="problem-info">
            <span class="problem-title">{{ problem.title }}</span>
            <div class="problem-meta">
              <span class="field-badge" :style="{ backgroundColor: FIELD_MAP[problem.field].boxColor }">
                {{ FIELD_MAP[problem.field].value }}
              </span>
              <span class="difficulty-text" :style="{ color: DIFFICULTY_MAP[problem.difficulty].textColor }">
                {{ DIFFICULTY_MAP[problem.difficulty].value }}
              </span>
            </div>
          </div>
          <div class="problem-stat">
            <span class="stat-num">{{ problem.accepted }}</span>
            <span class="stat-sub">풀이</span>
          </div>
        </div>
      </template>

      <div v-else class="empty-text">이번 주 데이터가 없어요.</div>
    </div>
  </div>
</template>

<script>
import api from "@oj/api"
import { mapActions } from "vuex"
import { FIELD_MAP, DIFFICULTY_MAP } from "../../../../utils/constants"

export default {
  name: "HomeActivitySidebar",
  computed: {
    FIELD_MAP() { return FIELD_MAP },
    DIFFICULTY_MAP() { return DIFFICULTY_MAP },
  },
  data() {
    return {
      problems: [],
      loading: true,
    }
  },
  mounted() {
    api.getWeeklyTopProblems().then((res) => {
      this.problems = res.data.data || []
      this.loading = false
    }).catch(() => {
      this.loading = false
    })
  },
  methods: {
    ...mapActions(["changeProblemSolvingState"]),
    enterProblem(problemId) {
      this.changeProblemSolvingState(true)
      this.$router.push({ name: "problem-details", params: { problemID: problemId } })
    },
    goProblemList() {
      this.$router.push({ name: "problem-list" })
    },
    rankClass(index) {
      if (index === 0) return "rank-gold"
      if (index === 1) return "rank-silver"
      if (index === 2) return "rank-bronze"
      return ""
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

.problem-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 6px;
  border-radius: 10px;
  margin: 0 -6px;
  cursor: pointer;
  transition: background-color 0.15s;

  & + & {
    border-top: 1px solid #f4f4f8;
  }

  &:hover {
    background-color: #f8f8fc;

    .problem-title {
      color: #5b64ed;
    }
  }
}

.rank-num {
  width: 24px;
  height: 24px;
  border-radius: 7px;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: #f4f4f8;
  color: #9999a6;

  &.rank-gold   { background: #fff8e6; color: #d97706; }
  &.rank-silver { background: #f4f4f8; color: #6b7280; }
  &.rank-bronze { background: #fdf3ee; color: #b45309; }
}

.problem-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.problem-title {
  font-size: 13px;
  font-weight: 600;
  color: #14141f;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  transition: color 0.15s;
}

.problem-meta {
  display: flex;
  align-items: center;
  gap: 6px;
}

.field-badge {
  font-size: 10px;
  font-weight: 500;
  padding: 2px 7px;
  border-radius: 20px;
  color: #333;
}

.difficulty-text {
  font-size: 10px;
  font-weight: 500;
}

.problem-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.stat-num {
  font-size: 15px;
  font-weight: 700;
  color: #5b64ed;
  line-height: 1.1;
}

.stat-sub {
  font-size: 9px;
  color: #b0b0be;
}

.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-item {
  height: 52px;
  border-radius: 10px;
  background: linear-gradient(90deg, #f0f0f4 25%, #e8e8f0 50%, #f0f0f4 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}

.empty-text {
  font-size: 13px;
  color: #9999a6;
  text-align: center;
  padding: 20px 0;
}

@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
