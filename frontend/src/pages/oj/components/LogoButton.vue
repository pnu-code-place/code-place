<template>
  <div class="logo" @click="handleRoute('/')">
    <div>
      <img src="@/assets/pojLogo.png" width="48" style="vertical-align:middle;margin-right: 10px"/>
    </div>
    <div class="headerIcon">
      <p class="pnuName">부산대학교</p>
      <p class="systemTitle">코딩역량강화플랫폼</p>
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

<style lang="less">
.logo {
  cursor: pointer;
  float: left;
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
