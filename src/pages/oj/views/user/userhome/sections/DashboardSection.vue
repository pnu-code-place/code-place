<script>
export default {
  name: "dashboard-section"
}
</script>

<template>
  <section>
    <h1>OJ 통계</h1>
  </section>
</template>

<style scoped lang="less">
section {
  border : 1px solid #dedede;
  border-radius: 7px;
  transition : all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  padding : 10px;
  h1 {
    text-align : left;
    margin-bottom: 10px;
  }
}
</style>
