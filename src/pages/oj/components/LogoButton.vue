<template>
  <div class="logo" @click="handleRoute('/')">
    <img src="@/assets/pnu.png" width="70" height="70"/>
    <div class="headerIcon">
      <p class="pnuName">부산대학교</p>
      <p class="systemTitle">온라인 저지 시스템</p>
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
      color: #255AA4;
    }
  }
}
</style>
