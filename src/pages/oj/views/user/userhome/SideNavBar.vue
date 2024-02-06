<template>
  <nav class="side-nav sticky">
    <ul class="nav-content">
      <router-link :to="{name:'user-home'}">{{ $t('m.OJ_Status') }}</router-link>
      <router-link :to="{name:'user-problems'}">{{ $t('m.Problem_Status') }}</router-link>
      <router-link :to="{name:'user-community'}" :disabled="true" class="disabled">{{ $t('m.Community') }}</router-link>
      <router-link :to="{name:'user-setting'}">{{ $t('m.User_Setting') }}</router-link>
      <router-link :to="{name:'user-achievements'}">{{ $t('m.Achievement') }}</router-link>
    </ul>
  </nav>
</template>

<script>
export default {
  name: "side-nav-bar"
}
</script>

<style scoped lang="less">

.side-nav {
  width: 18%;
  height: fit-content;
  margin-right: 20px;
  border: 1px solid #dedede;
  border-radius: 7px;
  padding: 10px;

  .nav-content {
    padding: 4px;
    margin: 0;
    display : flex;
    flex-direction: column;
    gap: 10px;

    a {
      display: block;
      text-decoration: none;
      padding: 10px;
      font-size: 16px;
      cursor: pointer;
      font-weight: bold;
      color: #495060;
      border-radius: 5px;

      &:hover {
        background-color: #f5f5f5;
      }
    }

    a.disabled {
      color: #b3b3b3;
      cursor: not-allowed;
    }
    .router-link-exact-active {
      background-color: #e6f2ff;
      color: #0078ff;
    }
  }
}

</style>
