<template>
  <error404 v-if="error"></error404>
  <div v-else class="container">
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
import api from '@oj/api'
import SideNavBar from "./SideNavBar.vue";
import UserCard from "./UserCard.vue";
import router from "../../../router";
import Error404 from "../../general/404.vue";

export default {
  components: {Error404, UserCard, SideNavBar},
  name: "user-home",
  data() {
    return {
      profile: {},
      problems: [],
      error: null
    }
  },
  mounted() {
    this.init()
  },
  methods: {
    init() {
      api.getUserInfo(this.username)
        .then(res => {
          this.profile = res.data.data
        })
        .catch(error => {
          this.error = error
        })
    },
  },
  computed: {
    username() {
      let username = '';
      if (this.$route && this.$route.params && typeof this.$route.params.username === 'string') {
        //본인의 username이 아닌 다른 사람의 username을 가져오는 경우
        username = this.$route.params.username;
      } else if (!username && this.$store && this.$store.state.user && this.$store.state.user.profile && this.$store.state.user.profile.user && typeof this.$store.state.user.profile.user.username === 'string') {
        //본인의 username을 가져오는 경우 리디렉션
        router.push({name: 'user-home', params: {username: this.$store.state.user.profile.user.username}})
      } else {
        //로그인이 되어있지 않은 경우
        router.push({name: 'login'})
      }
      return username;
    }
  },
  watch: {
    '$route'(newVal, oldVal) {
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
  width: 1200px;
  margin: 0 auto;
  text-align: center;
  display: flex;

  main {
    width: 83%;
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
