<template>
  <div class="timer">
    <div class="timerIconWrapper">
      <Icon type="ios-stopwatch-outline" color="#4E4E4E" size="22" style="cursor: pointer"></Icon>
    </div>
    <p> 00:00:00 </p>
  </div>
</template>

<script>

export default {
  name: "ProblemTimer",
  mounted () {

  },
  methods: {

  },

}
</script>

<style lang="less" scoped>
.timer{
  margin-top: 2px;
  display: flex;
  justify-content: space-evenly;
  margin-bottom: 2px;
  width: 100px;
  border-radius: 7px;
  text-align: center;
  .timerIconWrapper{
    text-align: center;
    display: flex;
    align-items: center;
  }
}
//.timer:hover{
//  background-color: #e6e6e6;
//}
</style>
