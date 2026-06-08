<template>
  <div class="sidebar-section">
    <div class="sidebar-card">
      <div class="sidebar-header">
        <div class="header-left">
          <span class="sidebar-title">랜덤 문제 추천</span>
        </div>
        <span class="sidebar-more" @click="goRandom">새로고침 ↺</span>
      </div>

      <div v-if="loading" class="skeleton-wrap">
        <div class="sk-badge" />
        <div class="sk-title" />
        <div class="sk-tags" />
        <div class="sk-btn" />
      </div>

      <template v-else-if="problem">
        <div class="problem-body">
          <div class="meta-row">
            <span
              class="field-badge"
              :style="{ backgroundColor: FIELD_MAP[problem.field].boxColor }"
              >{{ FIELD_MAP[problem.field].value }}</span
            >
            <span class="diff-badge" :class="diffClass(problem.difficulty)">{{
              DIFFICULTY_MAP[problem.difficulty].value
            }}</span>
          </div>
          <p class="problem-title">{{ problem.title }}</p>
          <div class="tags-row" v-if="problem.tags && problem.tags.length">
            <span class="tag" v-for="tag in problem.tags.slice(0, 3)" :key="tag"
              >#{{ tag }}</span
            >
          </div>
          <div class="stats-row">
            <div class="stat">
              <span class="stat-val">{{ problem.accepted_number }}</span>
              <span class="stat-label">정답</span>
            </div>
            <div class="stat-divider" />
            <div class="stat">
              <span class="stat-val">{{ problem.submission_number }}</span>
              <span class="stat-label">제출</span>
            </div>
            <div class="stat-divider" />
            <div class="stat">
              <span class="stat-val">{{ successRate }}%</span>
              <span class="stat-label">정답률</span>
            </div>
          </div>
        </div>
        <button class="solve-btn" @click="enterProblem(problem._id)">
          풀러가기 <span class="arrow">→</span>
        </button>
      </template>

      <div v-else class="empty-text">문제를 불러올 수 없어요.</div>
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
    FIELD_MAP() {
      return FIELD_MAP
    },
    DIFFICULTY_MAP() {
      return DIFFICULTY_MAP
    },
    successRate() {
      if (!this.problem || !this.problem.submission_number) return 0
      return Math.round(
        (this.problem.accepted_number / this.problem.submission_number) * 100,
      )
    },
  },
  data() {
    return {
      problem: null,
      loading: true,
    }
  },
  mounted() {
    this.loadTodayProblem()
  },
  methods: {
    ...mapActions(["changeProblemSolvingState"]),
    loadTodayProblem() {
      this.loading = true
      api
        .pickone()
        .then((res) => {
          const problemId = res.data.data
          return api.getProblem(problemId)
        })
        .then((res) => {
          this.problem = res.data.data
          this.loading = false
        })
        .catch(() => {
          this.loading = false
        })
    },
    goRandom() {
      this.loadTodayProblem()
    },
    enterProblem(problemId) {
      this.changeProblemSolvingState(true)
      this.$router.push({
        name: "problem-details",
        params: { problemID: problemId },
      })
    },
    diffClass(difficulty) {
      const map = {
        VeryLow: "diff-easy",
        Low: "diff-easy",
        Mid: "diff-normal",
        High: "diff-hard",
        VeryHigh: "diff-hard",
      }
      return map[difficulty] || "diff-normal"
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
  gap: 16px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sidebar-title {
  font-size: 18px;
  font-weight: 700;
  color: #14141f;
}

.sidebar-more {
  font-size: 12px;
  font-weight: 500;
  color: #9999a6;
  cursor: pointer;
  transition: color 0.15s;

  &:hover {
    color: #5b64ed;
  }
}

.problem-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
}

.meta-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.field-badge {
  font-size: 11px;
  font-weight: 500;
  padding: 3px 9px;
  border-radius: 20px;
  color: #333;
}

.diff-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 20px;

  &.diff-easy {
    background: #eaf3de;
    color: #3b6d11;
  }
  &.diff-normal {
    background: #faeeda;
    color: #854f0b;
  }
  &.diff-hard {
    background: #fcebeb;
    color: #a32d2d;
  }
}

.problem-title {
  font-size: 15px;
  font-weight: 700;
  color: #14141f;
  margin: 0;
  line-height: 1.45;
  word-break: keep-all;
}

.tags-row {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.tag {
  font-size: 11px;
  color: #888;
  background: #f4f4f8;
  padding: 2px 7px;
  border-radius: 4px;
}

.stats-row {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #f8f8fc;
  border-radius: 12px;
  padding: 10px 14px;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  gap: 2px;
}

.stat-val {
  font-size: 15px;
  font-weight: 700;
  color: #5b64ed;
  line-height: 1;
}

.stat-label {
  font-size: 10px;
  color: #b0b0be;
}

.stat-divider {
  width: 1px;
  height: 28px;
  background: #e5e5ed;
  flex-shrink: 0;
}

.solve-btn {
  width: 100%;
  padding: 12px;
  background: #5b64ed;
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: background-color 0.15s;

  &:hover {
    background: #4a52d4;

    .arrow {
      transform: translateX(3px);
    }
  }

  .arrow {
    transition: transform 0.15s;
  }
}

/* skeletons */
.skeleton-wrap {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
}

.sk-badge,
.sk-title,
.sk-tags,
.sk-btn {
  border-radius: 8px;
  background: linear-gradient(90deg, #f0f0f4 25%, #e8e8f0 50%, #f0f0f4 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}

.sk-badge {
  height: 22px;
  width: 80px;
}
.sk-title {
  height: 44px;
}
.sk-tags {
  height: 22px;
  width: 60%;
}
.sk-btn {
  height: 44px;
  margin-top: auto;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.empty-text {
  font-size: 13px;
  color: #9999a6;
  text-align: center;
  padding: 20px 0;
}
</style>
