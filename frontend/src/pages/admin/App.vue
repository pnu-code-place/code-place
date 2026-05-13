<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: "app",
  components: {},
}
</script>

<style lang="less">
body {
  margin: 0;
  padding: 0;
  font-family:
    "Noto Sans KR", "Apple SD Gothic Neo", "Helvetica Neue", Helvetica, Arial,
    sans-serif;
  font-size: 14px;
  -webkit-font-smoothing: antialiased;
  background-color: #324157;
}

#app {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 100%;
}
</style>
