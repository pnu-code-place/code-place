<template>
  <section id="problem-section">
    <h1>{{ $t('m.Problem_Status') }}</h1>
    <ProblemSkeleton v-if="isLoading" class="loading"></ProblemSkeleton>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="!isLoading && !error" class="contents">
      <div class="status" v-if="!isLoading && !error">
        <div class="status-item">
          <span class="label">{{ $t('m.Tried_Problems') }}</span>
          <span class="value">{{ tried }}</span>
        </div>
        <div class="status-item">
          <span class="label">{{ $t('m.Solved_Problems') }}</span>
          <span class="value">{{ problem_info.solved.count }}</span>
        </div>
        <div class="status-item">
          <span class="label">{{ $t('m.Failed_Problems') }}</span>
          <span class="value">{{ problem_info.failed.count }}</span>
        </div>
        <div class="status-item">
          <span class="score-ratio">{{ $t('m.TOP') }} {{ ranking_percent }}%</span>
        </div>
      </div>
      <hr/>
      <div class="problem-tab solved">
        <h2>{{ $t('m.Solved_Problems') }}</h2>
        <ul v-if="problem_info.solved.count > 0" class="solved-problems">
          <li v-for="problem in problem_info.solved.problems" :key="problem.id">
            <problem-badge :problem="problem"></problem-badge>
          </li>
        </ul>
        <p v-else>{{ $t('m.There_Is_No_Problem_You_Solved') }}
          <router-link :to="{name:'problem-list'}">{{ $t('m.Lets_Get_Started') }}</router-link>
        </p>
      </div>
      <hr/>
      <div class="problem-tab tried">
        <h2>{{ $t('m.Failed_Problems') }}</h2>
        <ul v-if="problem_info.failed.count > 0" class="tried-problems">
          <li v-for="problem in problem_info.failed.problems" :key="problem.id">
            <problem-badge :problem="problem"></problem-badge>
          </li>
        </ul>
        <p v-else>{{ $t('m.There_Is_No_Problem_You_Tried') }}
          <router-link :to="{name:'problem-list'}">{{ $t('m.Lets_Get_Started') }}</router-link>
        </p>
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
      api.getUserProblemInfo(this.username).then(res => {
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
    },
    username() {
      let username = '';

      if (this.$route && this.$route.params && typeof this.$route.params.username === 'string') {
        username = this.$route.params.username;
      }

      if (!username && this.$store && this.$store.state.user && this.$store.state.user.profile && this.$store.state.user.profile.user && typeof this.$store.state.user.profile.user.username === 'string') {
        username = this.$store.state.user.profile.user.username;
      }

      return username;
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
