<template>
  <div class="container">
    <side-nav-bar></side-nav-bar>
    <main>
      <user-card :profile="profile"></user-card>
      <keep-alive>
        <router-view></router-view>
      </keep-alive>
    </main>
  </div>
</template>
<script>
import time from '@/utils/time'
import api from '@oj/api'
import SideNavBar from "./SideNavBar.vue";
import UserCard from "./UserCard.vue";

export default {
  components: {UserCard, SideNavBar},
  name: "user-home",

  data() {
    return {
      profile: {},
      problems: [],
    }
  },
  mounted() {
    this.init()
  },
  methods: {
    init() {
      api.getUserInfo(this.username).then(res => {
        // this.changeDomTitle({title: res.data.data.user.username})
        this.profile = res.data.data
        // this.getSolvedProblems()
        let registerTime = time.utcToLocal(this.profile.user.create_time, 'YYYY-MM-D')
        // console.log('The guy registered at ' + registerTime + '.')
      })
    },
  },
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
  watch: {
    '$route' (newVal, oldVal) {
      if (newVal !== oldVal) {
        this.init()
      }
    }
  }
}
</script>

<style lang="less" scoped>

.container {
  position: relative;
  width: 100%;
  margin: 0 auto;
  text-align: center;
  display: flex;

  main {
    width: 80%;
    gap: 30px;
    display: flex;
    flex-direction: column;
  }

  p {
    margin-top: 8px;
    margin-bottom: 8px;
  }

  .emphasis {
    font-size: 20px;
    font-weight: 600;
  }

  #split {
    margin: 20px auto;
    width: 90%;
  }

  #problems {
    margin-top: 40px;
    padding-left: 30px;
    padding-right: 30px;
    font-size: 18px;

    .btns {
      margin-top: 15px;

      .problem-btn {
        display: inline-block;
        margin: 5px;
      }
    }
  }
}
</style>
