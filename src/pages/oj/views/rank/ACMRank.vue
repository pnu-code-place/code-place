<template>
  <div class="acm-rank">
    <h1>{{ $t('m.Top_Users') }}</h1>
    <div class="main-contents">
      <header class="routers">
        <router-link class="" to="user-rank">{{ $t('m.User_Rank') }}</router-link>
        <router-link class="" to="soaring-rank">{{ $t('m.Today_User') }}</router-link>
        <router-link class="" to="major-rank">{{ $t('m.Major_Rank') }}</router-link>
      </header>
      <div class="acm-rank__contents">
        <router-view></router-view>
      </div>
    </div>
  </div>
</template>

<script>

export default {}
</script>

<style scoped lang="less">
.acm-rank {
  width: 1200px;
  h1 {
    font-size: 18px;
    margin: 0 0 25px;
  }

  header {
    width: 100%;
    display: flex;
    justify-content: space-between;

    a {
      font-size: 15px;
      width: 100%;
      text-align: center;
      padding: 12px;
      color: #fff;
      font-weight: 500;
      border: 1px solid #dedede;
      border-radius: 10px 10px 0 0;
      background-color: #495060;
    }

    .router-link-active {
      background-color: #fff;
      color: #495060;
      border-bottom: 0;
    }
  }

  .acm-rank__contents {
    display: flex;
    justify-content: space-between;
    border-color: #dedede;
    border-style: solid;
    border-width: 0 1px 1px 1px;
    gap: 30px;
  }
}
</style>
