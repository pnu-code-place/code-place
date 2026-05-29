<template>
  <div class="logo" @click="handleRoute('/')">
    <div>
      <img
        src="@/assets/code-place-logo.svg"
        width="32"
        style="vertical-align: middle; margin-right: 10px"
      />
    </div>
    <div class="headerIcon">
      <p class="pnuName">부산대학교</p>
      <p class="systemTitle code">코드플레이스</p>
    </div>
  </div>
</template>

<script>
export default {
  name: "LogoButton",
  methods: {
    handleRoute(route) {
      if (route && route.indexOf("admin") < 0) {
        this.$router.push(route)
      } else {
        window.open("/admin/")
      }
    },
  },
}
</script>

<style scoped lang="less">
.logo {
  cursor: pointer;
  float: left;
  margin: 0 12px;
  height: var(--header-height);
  display: flex;
  justify-content: space-between;
  align-items: center;

  .headerIcon {
    line-height: 1.15;
    width: auto;
    text-align: left;
    p {
      margin: 0;
    }
    .pnuName {
      font-size: 14.5px;
      font-weight: normal;
    }
    .systemTitle {
      font-size: 19px;
      font-weight: bold;
      color: #5b64ed;
    }
  }
}
</style>
