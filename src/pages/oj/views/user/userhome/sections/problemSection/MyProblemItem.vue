<script>
export default {
  props: ['problem'],
  name : 'MyProblemItem',
  computed: {
    submitTime() {
      // 2021-07-02T08:25:49.443682Z -> 2021-07-02 08:25:49
      const date = new Date(this.problem.submitTime);
      const year = date.getFullYear();
      const month = date.getMonth() + 1;
      const day = date.getDate();
      const hour = date.getHours();
      const minute = date.getMinutes();
      const second = date.getSeconds();
      return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
    }
  },
  methods: {
    logDate() {
      console.log(this.problem.submitTime);
    }
  }
}
</script>

<template>
  <li class="problem-item">
    <button @click="logDate">log date</button>
    <router-link :to="{ name: 'ProblemDetail', params: { problemId: problem.id } }">
      <div class="id">{{problem.id}}</div>
      <div class="field">필드아이콘</div>
      <div class="title">{{problem.title}}</div>
      <div class="difficulty">난이도뱃지</div>
      <div class="submit-date">{{problem.submitTime}}</div>
    </router-link>
  </li>
</template>

<style scoped lang="less">
li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  border-bottom: 1px solid #dedede;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  &:hover {
    background-color: #f5f5f5;
  }
  .problem-id {
    width: 10%;
    text-align: center;
  }
  .problem-field {
    width: 20%;
    text-align: center;
  }
  .problem-title {
    width: 50%;
    text-align: center;
  }
  .problem-difficulty {
    width: 10%;
    text-align: center;
  }
  .problem-solved {
    width: 10%;
    text-align: center;
  }
}
</style>
