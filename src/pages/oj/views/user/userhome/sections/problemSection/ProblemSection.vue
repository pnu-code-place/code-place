<template>
  <section id="problem-section">
    <h1>문제풀이</h1>
    <div class="status">
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
  </section>
</template>

<script>
const problem_info = {
  ranking_percent: 0.3,
  solved: { // 해결한 문제들을 표시합니다.
    count: 4,
    problems: [
      {
        id: 1001,
        title: 'A+B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1002,
        title:
            'A-B',
        submitTime:
            '2021-07-02T08:25:49.443682Z',
        difficulty:
            'easy',
      },
      {
        id: 1003,
        title:
            'A*B',
        submitTime:
            '2021-07-02T08:25:49.443682Z',
        difficulty:
            'easy',
      },
      {
        id: 1004,
        title:
            'A/B',
        submitTime:
            '2021-07-02T08:25:49.443682Z',
        difficulty:
            'easy',
      },
    ],
  },
  failed: { // 시도했으나 풀지 못한 문제들을 표시합니다.
    count: 4,
    problems: [
      {
        id: 1001,
        title: 'A+B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1002,
        title: 'A-B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1003,
        title: 'A*B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1004,
        title: 'A/B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
    ],
  }
}

import ProblemBadge from "./ProblemBadge.vue";

export default {
  name: 'problem-section',
  components: {ProblemBadge},
  data() {
    return {
      problem_info: problem_info,
    }
  },
  methods: {},
  computed: {
    tried() {
      return this.problem_info.failed.count + this.problem_info.solved.count
    },
    ranking_percent() {
      return (this.problem_info.ranking_percent*100).toFixed(1)
    }
  }
}
</script>

<style scoped lang="less">
section {
  border: 1px solid #dedede;
  border-radius: 7px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  padding: 20px;

  h1 {
    text-align: left;
  }

  hr {
    margin-top: 10px;
    border: 1px solid #dedede;
  }

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
        color : #99bbee;
      }
    }
  }

  .problem-tab {
    padding: 10px;

    h2 {
      text-align: left;
      margin-bottom: 10px;
    }

    ul {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      padding: 0;
      margin: 0;
      list-style: none;

      li {
        font-size: 14px;
      }
    }
  }
}
</style>
