<template>
  <div class="logo" @click="handleRoute('/')">
    <div>
      <img src="@/assets/code-place-logo.svg" width="30" style="vertical-align:middle;margin-right: 10px"/>
    </div>
    <div class="headerIcon">
      <p class="pnuName">부산대학교</p>
      <p class="systemTitle code">코드플레이스</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LogoButton',
  methods:{
    handleRoute (route) {
      if (route && route.indexOf('admin') < 0) {
        this.$router.push(route)
      } else {
        window.open('/admin/')
      }
    },
  }
}
</script>

<style scoped lang="less">
.logo {
  cursor: pointer;
  float: left;
  margin-left: 4%;
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;

  .headerIcon{
    line-height: normal;
    width: auto;
    text-align: left;
    .pnuName{
      font-size: 14px;
      font-weight: normal;
    }
    .systemTitle{
      font-size: 18px;
      font-weight: bold;
      color: #32306b;
    }
  }
}

</style>
