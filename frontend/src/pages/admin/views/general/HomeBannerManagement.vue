<template>
  <div style="padding: 30px;">
    <section style="display: flex; justify-content: space-between;">
      <h1 class="title">{{$t('m.Home_Banner_Management')}}</h1>
      <span class="alert-description" style="display: flex; gap: 10px; align-items: center;">
        <img src="@/assets/information_icon.svg" width="17px" />
        배너 활성화는 최대 5개까지 가능합니다.
      </span>
    </section>
  </div>
</template>

<script>
  export default {
    name: 'home-banner-management',
  }
</script>

<style lang="less" scoped>
.title {
  margin: 0;
  color: #333;
  font-size: 18px;
  font-weight: 300;
}
.alert-description {
  color: #666;
  font-size: 18px;
  font-weight: 500;
}
</style>
