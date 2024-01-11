<script>

import MyProblemItem from "./MyProblemItem.vue";

export default {
  components: {
    MyProblemItem,
  },
  props: {
    problems: {
      type: Array,
      required: true,
    },
    title: {
      type: String,
      required: true,
    }
  },
}

</script>

<template>
<div class="problem-list">
  <h2>{{title}}</h2>
  <div class="problem-items">
    <my-problem-item v-for="problem in problems" :key="problem.id" :problem="problem" />
  </div>
</div>
</template>

<style scoped lang="less">

</style>
