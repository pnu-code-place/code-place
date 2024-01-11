<script>
export default {
  name : 'CommunitySection',
  props: {
    actions: {
      type : Object,
      required : true
    }
  }
}
</script>

<template>
  <section>
    <h1>커뮤니티</h1>
    <div class="subsection">njj</div>
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
