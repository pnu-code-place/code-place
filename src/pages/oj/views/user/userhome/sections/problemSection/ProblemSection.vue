<template>
  <section id="problem-section">
    <h1>문제풀이</h1>
    <div class="status">
      <div>
        <span class="label">시도한 문제</span>
        <span class="value">{{ tried }}</span>
      </div>
      <div>
        <span class="label">해결한 문제</span>
        <span class="value">{{ problem_info.solved.count }}</span>
      </div>
      <div>
        <span class="label">시도했으나 풀지 못한 문제</span>
        <span class="value">{{ problem_info.failed.count }}</span>
      </div>
      <div>
        <span>상위 {{ problem_info.ranking_percent }}%</span>
      </div>
    </div>
    <div class="problem-tab solved">
      <h2>푼 문제</h2>
      <ul class="solved-problems">
        <li v-for="problem in problem_info.solved.problems" :key="problem.id">
          <problem-badge :problem="problem"></problem-badge>
        </li>
      </ul>
    </div>
    <div class="problem-tab tried">
      <h2>시도했으나 풀지 못한 문제</h2>
      <ul class="tried-problems">
        <li v-for="problem in problem_info.failed.problems" :key="problem.id">
          <problem-badge :problem="problem"></problem-badge>
        </li>
      </ul>
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
  }
}
</script>

<style scoped lang="less">
section {
  border: 1px solid #dedede;
  border-radius: 7px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  padding: 20px;

  .status {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    margin-bottom: 10px;

    div {

    }
  }

  h1 {
    text-align: left;
    margin-bottom: 10px;
  }

  .problem-tab {
    padding: 10px;

    h2 {
      text-align: left;
    }

    ul {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      padding: 0;
      margin: 0;
      list-style: none;
    }
  }
}
</style>
