<template>
  <nav class="side-nav sticky">
    <ul class="nav-content">
      <router-link :to="{name:'user-dashboard', params: {username:username}}">{{ $t('m.OJ_Status') }}</router-link>
      <router-link :to="{name:'user-problems', params: {username:username}}">{{ $t('m.Problem_Status') }}</router-link>
      <router-link :to="{name:'user-community', params: {username:username}}" :disabled="true" class="disabled">
        {{ $t('m.Community') }}
      </router-link>
    </ul>
  </nav>
</template>

<script>
export default {
  name: "side-nav-bar",
  computed: {
    username() {
      let username = '';

      if (this.$route && this.$route.params && typeof this.$route.params.username === 'string') {
        username = this.$route.params.username;
      }

      if (!username && this.$store && this.$store.state.user && this.$store.state.user.profile && this.$store.state.user.profile.user && typeof this.$store.state.user.profile.user.username === 'string') {
        username = this.$store.state.user.profile.user.username;
      }

      return username;
    }
  },
  methods: {
    logUsername() {
      console.log(this.username)
    }
  }
}
</script>

<style scoped lang="less">

.side-nav {
  width: 17%;
  height: fit-content;
  margin-right: 20px;
  border: 1px solid #dedede;
  border-radius: 7px;
  padding: 10px;

  .nav-content {
    padding: 4px;
    margin: 0;
    display: flex;
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
        background-color: #e6f2ff;
      }
    }

    a.disabled {
      color: #b3b3b3;
      cursor: not-allowed;
    }

    .router-link-active {
      background-color: rgba(34, 33, 72, 0.82);
      color: #e6f2ff;

      &:hover {
        background-color: rgba(34, 33, 72, 0.82);
      }
    }
  }
}

</style>
