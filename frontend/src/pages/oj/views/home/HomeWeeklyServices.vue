<template>
  <div class="weekly-wrap">
    <div class="section-header">
      <span class="section-title">이주의 추천 문제</span>
      <div class="section-line"></div>
    </div>

    <div class="cards">
      <div
        v-for="(problem, index) in problems"
        :key="problem._id"
        class="card"
        :class="CARD_COLORS[index % 3].cardClass"
        @click="enterProblem(problem._id)"
      >
        <div class="card-meta">
          <span class="badge b-cat">{{ FIELD_MAP[problem.field].value }}</span>
          <span class="badge" :class="difficultyBadgeClass(problem.difficulty)">
            {{ DIFFICULTY_MAP[problem.difficulty].value }}
          </span>
        </div>
        <div class="card-row">
          <p class="card-title">{{ problem.title }}</p>
          <span class="num">{{ String(index + 1).padStart(2, "0") }}</span>
        </div>
        <div class="card-tags">
          <span v-for="tag in problem.tags.slice(0, 2)" :key="tag" class="tag"
            >#{{ tag }}</span
          >
        </div>
        <div class="go-link">풀러가기 <span class="arrow">→</span></div>
      </div>

      <div v-if="problems.length === 0" class="empty-state">
        이번 주 추천 문제가 아직 없어요.
      </div>
    </div>
  </div>
</template>

<script>
import api from "@oj/api"
import { mapActions } from "vuex"
import { FIELD_MAP, DIFFICULTY_MAP } from "../../../../utils/constants"

const CARD_COLORS = [
  { cardClass: "c1" },
  { cardClass: "c2" },
  { cardClass: "c3" },
]

export default {
  name: "HomeWeeklyServices",
  computed: {
    FIELD_MAP() {
      return FIELD_MAP
    },
    DIFFICULTY_MAP() {
      return DIFFICULTY_MAP
    },
    CARD_COLORS() {
      return CARD_COLORS
    },
  },
  data() {
    return {
      problems: [],
    }
  },
  mounted() {
    api.getHomeBonusProblem().then((res) => {
      this.problems = res.data.data.slice(0, 3)
    })
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
  padding: 40px 0 40px;
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #14141f;
  white-space: nowrap;
}

.section-line {
  flex: 1;
  height: 0.5px;
  background: #e0e0e0;
}

.cards {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.card {
  border-radius: 14px;
  padding: 1.1rem 1.1rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 9px;
  cursor: pointer;
  background: #ffffff;
  border: 0.5px solid #e0e0e0;
  border-top-width: 3px;
  transition:
    transform 0.16s,
    border-color 0.16s;

  &:hover {
    transform: translateY(-3px);
  }

  &.c1 {
    border-top-color: #7f77dd;
    &:hover {
      border-color: #7f77dd;
    }
  }
  &.c2 {
    border-top-color: #e24b4a;
    &:hover {
      border-color: #e24b4a;
    }
  }
  &.c3 {
    border-top-color: #1d9e75;
    &:hover {
      border-color: #1d9e75;
    }
  }
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.badge {
  font-size: 10.5px;
  font-weight: 500;
  padding: 3px 9px;
  border-radius: 20px;

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

.card-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}

.card-title {
  font-size: 15px;
  font-weight: 500;
  color: #14141f;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.num {
  font-size: 26px;
  font-weight: 500;
  line-height: 1;
  opacity: 0.07;
  color: #14141f;
  flex-shrink: 0;
}

.card-tags {
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

.go-link {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12.5px;
  font-weight: 500;
  color: #888;
  margin-top: 2px;

  .arrow {
    transition: transform 0.14s;
  }
}

.card:hover .go-link .arrow {
  transform: translateX(3px);
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  color: #aaa;
  font-size: 14px;
  padding: 40px 0;
}
</style>
