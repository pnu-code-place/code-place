<template>
  <error404 v-if="this.cardError"></error404>
  <div v-else class="container">
    <side-nav-bar></side-nav-bar>
    <main>
      <div class="user-home-header">
        <user-card
          :profile="profile"
          :oj-status="this.ojStatus"
          :loading="this.cardLoading || this.statusLoading"
        ></user-card>
      </div>
      <keep-alive>
        <router-view></router-view>
      </keep-alive>
    </main>
  </div>
</template>
<script>
import api from "@oj/api"
import SideNavBar from "./SideNavBar.vue"
import UserCard from "./UserCard.vue"
import router from "../../../router"
import Error404 from "../../general/404.vue"
import OjSummary from "./OJSummary.vue"

export default {
  components: { OjSummary, Error404, UserCard, SideNavBar },
  name: "user-home",
  data() {
    return {
      profile: {},
      ojStatus: {},

      cardError: null,
      statusError: null,

      cardLoading: false,
      statusLoading: false,
    }
  },
  mounted() {
    this.init()
  },
  methods: {
    init() {
      this.statusLoading = true
      this.cardLoading = true
      api
        .getUserInfo(this.username)
        .then((res) => {
          this.profile = res.data.data
          this.cardLoading = false
        })
        .catch((error) => {
          this.cardError = error
        })
      api
        .getDashboardInfo(this.username)
        .then((res) => {
          this.ojStatus = res.data.data.ojStatus
          this.statusLoading = false
        })
        .catch((error) => {
          this.statusError = error
        })
    },
  },
  computed: {
    username() {
      let username = ""
      if (
        this.$route &&
        this.$route.params &&
        typeof this.$route.params.username === "string"
      ) {
        //본인의 username이 아닌 다른 사람의 username을 가져오는 경우
        username = this.$route.params.username
      } else if (
        !username &&
        this.$store &&
        this.$store.state.user &&
        this.$store.state.user.profile &&
        this.$store.state.user.profile.user &&
        typeof this.$store.state.user.profile.user.username === "string"
      ) {
        //본인의 username을 가져오는 경우 리디렉션
        router.push({
          name: "user-home",
          params: { username: this.$store.state.user.profile.user.username },
        })
      } else {
        //로그인이 되어있지 않은 경우
        console.log("76")
        router.push({ name: "login" })
      }
      return username
    },
    error() {
      return this.statusError || this.cardError
    },
    loading() {
      return this.statusLoading || this.cardLoading
    },
  },
  watch: {
    $route(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.init()
      }
    },
  },
}
</script>

<style lang="less" scoped>
.container {
  position: relative;
  width: var(--global-width);
  margin: 0 auto;
  text-align: center;
  display: flex;

  main {
    width: 83%;
    gap: 30px;
    display: flex;
    flex-direction: column;

    .user-home-header {
      display: flex;
      gap: 30px;

      .status-wrapper {
        flex: 1;
      }

      .card-wrapper {
        flex: 1;
      }
    }
  }

  p {
    margin: 8px 0;
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
    padding: 0 30px;
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
