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
  }
}
</script>

<template>
  <Tooltip delay=0 :content="problem.title">
    <router-link :to="{name : 'problem-details', params : {problemId:problem.id}}">
      {{problem.id}}
    </router-link>
  </Tooltip>
</template>

<style scoped lang="less">
a {
  padding: 8px;
  font-size: 13px;
  border : 1px solid #cfe2ff;
  border-radius: 5px;
}

a:hover {
  background-color: #e6f2ff;
}
</style>
