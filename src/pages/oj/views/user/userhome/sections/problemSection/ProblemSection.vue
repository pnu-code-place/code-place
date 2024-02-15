<template>
  <section id="problem-section">
    <h1>문제풀이</h1>
    <ProblemSkeleton v-if="isLoading" class="loading">Loading...</ProblemSkeleton>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="!isLoading && !error" class="contents">
      <div class="status" v-if="!isLoading && !error">
        <div class="status-item">
          <span class="label">도전한 문제</span>
          <span class="value">{{ tried }}</span>
        </div>
        <div class="status-item">
          <span class="label">해결한 문제</span>
          <span class="value">{{ problem_info.solved.count }}</span>
        </div>
        <div class="status-item">
          <span class="label">못 푼 문제</span>
          <span class="value">{{ problem_info.failed.count }}</span>
        </div>
        <div class="status-item">
          <span class="score-ratio">상위 {{ ranking_percent }}%</span>
        </div>
      </div>
      <hr/>
      <div class="problem-tab solved">
        <h2>푼 문제</h2>
        <ul v-if="problem_info.solved.count > 0" class="solved-problems">
          <li v-for="problem in problem_info.solved.problems" :key="problem.id">
            <problem-badge :problem="problem"></problem-badge>
          </li>
        </ul>
        <p v-else>맞춘 문제가 없습니다. 한 번 시작해 볼까요?</p>
      </div>
      <hr/>
      <div class="problem-tab tried">
        <h2>시도했으나 풀지 못한 문제</h2>
        <ul v-if="problem_info.failed.count > 0" class="tried-problems">
          <li v-for="problem in problem_info.failed.problems" :key="problem.id">
            <problem-badge :problem="problem"></problem-badge>
          </li>
        </ul>
        <p v-else>시도한 문제가 없습니다. 한 번 시작해 볼까요?</p>
      </div>
    </div>
  </section>
</template>

<script>

import ProblemBadge from "./ProblemBadge.vue";
import api from "@oj/api";
import ProblemSkeleton from "./ProblemSkeleton.vue";

export default {
  name: 'problem-section',
  components: {ProblemSkeleton, ProblemBadge},
  data() {
    return {
      problem_info: {},
      isLoading: true,
      error: null
    }
  },
  methods: {
    init() {
      this.isLoading = true
      api.getUserProblemInfo().then(res => {
        this.problem_info = res.data.data
      }).catch(error =>
          this.error = error
      ).finally(() =>
          this.isLoading = false
      )
    }
  },
  mounted() {
    this.init()
  },
  computed: {
    tried() {
      return this.problem_info.failed.count + this.problem_info.solved.count
    },
    ranking_percent() {
      return (this.problem_info.ranking_percent * 100).toFixed(1)
    }
  }
}
</script>

<style scoped lang="less">
section {
  display: flex;
  flex-direction: column;
  border: 1px solid #dedede;
  border-radius: 7px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  padding: 20px;

  h1 {
    text-align: left;
  }

  hr {
    border: 0.5px solid #dedede;
    margin: 10px 10px 10px 0;
  }

  .contents {
    display: flex;
    flex-direction: column;
    gap: 10px;

    .status {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 50px 25%;

      .status-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;

        .label {
          font-size: 14px;
          font-weight: 500;
          text-decoration: underline;
        }

        .value {
          font-size: 14px;
          font-weight: 700;
        }

        .score-ratio {
          font-size: 14px;
          font-weight: 600;
          color: #99bbee;
        }
      }
    }

    .problem-tab {
      padding: 10px;

      h2 {
        text-align: left;
        margin-bottom: 20px;
      }

      ul {
        display: flex;
        flex-wrap: wrap;
        gap: 13px;
        padding: 0;
        margin: 0;
        list-style: none;

        li {
          font-size: 14px;
          margin-bottom: 10px;
        }
      }
    }
  }
}
</style>
