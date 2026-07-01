<template>
  <div class="weekly-wrap">
    <div class="outer-card">
      <div class="section-header">
        <span class="section-title">이번주의 보너스 문제</span>
        <span class="double-badge">
          해결하면 점수를 2배로 받을 수 있어요
        </span>
      </div>

      <div class="cards">
        <div
          v-for="(problem, index) in problems"
          :key="problem._id"
          class="card"
          @click="enterProblem(problem._id)"
        >
          <div class="card-top">
            <div class="card-meta">
              <span class="badge b-bonus">점수 2배</span>
              <span class="badge b-cat">{{
                (FIELD_MAP[problem.field] || {}).value
              }}</span>
              <span
                class="badge"
                :class="difficultyBadgeClass(problem.difficulty)"
              >
                {{ (DIFFICULTY_MAP[problem.difficulty] || {}).value }}
              </span>
            </div>
            <span class="num">{{ String(index + 1).padStart(2, "0") }}</span>
          </div>
          <p class="card-title">{{ problem.title }}</p>
          <div class="card-tags">
            <span
              v-for="tag in (problem.tags || []).slice(0, 2)"
              :key="tag"
              class="tag"
              >#{{ tag }}</span
            >
          </div>
          <div class="go-link">풀러가기 <span class="arrow">→</span></div>
        </div>

        <div v-if="problems.length === 0" class="empty-state">
          이번 주 보너스 문제가 없습니다.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@oj/api"
import { mapActions } from "vuex"
import { FIELD_MAP, DIFFICULTY_MAP } from "../../../../utils/constants"

export default {
  name: "HomeWeeklyServices",
  computed: {
    FIELD_MAP() {
      return FIELD_MAP
    },
    DIFFICULTY_MAP() {
      return DIFFICULTY_MAP
    },
  },
  data() {
    return {
      problems: [],
    }
  },
  mounted() {
    api
      .getHomeBonusProblem()
      .then((res) => {
        this.problems = (res.data.data || []).slice(0, 3)
      })
      .catch(() => {})
  },
  methods: {
    ...mapActions(["changeProblemSolvingState"]),
    enterProblem(problemId) {
      this.changeProblemSolvingState(true)
      this.$router.push({
        name: "problem-details",
        params: { problemID: problemId },
      })
    },
    goMoreProblems() {
      this.$router.push({ name: "problem-list" })
    },
    difficultyBadgeClass(difficulty) {
      const map = {
        VeryLow: "b-easy",
        Low: "b-easy",
        Mid: "b-normal",
        High: "b-hard",
        VeryHigh: "b-hard",
      }
      return map[difficulty] || "b-normal"
    },
  },
}
</script>

<style scoped lang="less">
.weekly-wrap {
  width: 100%;
  padding: 40px 0;
}

.outer-card {
  background: #ffffff;
  border: 1px solid #e5e5ed;
  border-radius: 20px;
  padding: 20px 28px;
  display: flex;
  flex-direction: column;
  gap: 4px;

  @media (max-width: 768px) {
    padding: 16px 16px;
  }
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #14141f;
  flex: 1;
}

.double-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 500;
  color: #aaa;
  padding: 4px 12px;
  white-space: nowrap;
}

.more-link {
  font-size: 13px;
  font-weight: 500;
  color: #5b64ed;
  cursor: pointer;
  white-space: nowrap;

  &:hover {
    text-decoration: underline;
  }
}

.cards {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.card {
  border-radius: 16px;
  padding: 20px 20px 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  cursor: pointer;
  background: #ffffff;
  border: 1px solid #f2e2bb;
  transition:
    transform 0.16s,
    box-shadow 0.16s;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(245, 158, 11, 0.18);
  }
}

.card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.badge {
  font-size: 11px;
  font-weight: 500;
  padding: 3px 10px;
  border-radius: 99px;

  &.b-bonus {
    background: #f59e0b;
    color: #fff;
    font-weight: 700;
  }
  &.b-cat {
    background: #eeedfe;
    color: #3c3489;
  }
  &.b-hard {
    background: #fcebeb;
    color: #a32d2d;
  }
  &.b-normal {
    background: #faeeda;
    color: #854f0b;
  }
  &.b-easy {
    background: #eaf3de;
    color: #3b6d11;
  }
}

.num {
  font-size: 36px;
  font-weight: 700;
  line-height: 1;
  color: #14141f;
  opacity: 0.07;
  flex-shrink: 0;
  letter-spacing: -0.02em;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  color: #14141f;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag {
  font-size: 11px;
  color: #6b6b80;
  background: #f2f2f8;
  padding: 3px 9px;
  border-radius: 99px;
}

.go-link {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 600;
  color: #5b64ed;
  margin-top: 4px;

  .arrow {
    transition: transform 0.14s;
  }
}

.card:hover .go-link .arrow {
  transform: translateX(3px);
}

.empty-state {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: #aaa;
  font-size: 14px;
  padding: 40px 0;
}
</style>
