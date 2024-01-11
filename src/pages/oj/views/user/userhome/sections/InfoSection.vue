<script>
export default {
  name : 'InfoSection',
  props: {
    profile :{
      type : Object,
      required : true
    }
  },
  methods : {
    // logProps() {
    //   console.log(this.$props);
    // }
}
}
</script>

<template>
  <section>
    <h1>개인 정보</h1>
<!--    <button @click="logProps">prop확인하기</button>-->
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
