<script>

// const problem = {
//   id : 1001,
//   title: 'A+B',
//   submitTime: '2021-07-02T08:25:49.443682Z',
//   difficulty: 'easy',
// }
export default {
  props: ['problem'],
  name : 'problem-badge',
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
  methods : {
    // goProblem() {
    //   this.$router.push({name : 'problem-details', params : {problemId : problem.id}})
    // }
  }
}
</script>

<template>
    <router-link :to="{name : 'problem-details', params : {problemId:problem.id}}">
      {{problem.id}}
    </router-link>
<!--    <span @click="goProblem">{{problem.title}}</span>-->
</template>

<style scoped lang="less">
</style>
