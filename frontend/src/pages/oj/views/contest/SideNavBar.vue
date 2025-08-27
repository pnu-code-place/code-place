<template>
  <nav v-show="showMenu" class="side-nav sticky">
    <ul class="nav-content">
      <router-link :to="{ name: 'contest-overview' }">
        <Icon type="home"></Icon> {{ $t("m.Contest_Overview") }}
      </router-link>
      <router-link :to="{ name: 'contest-announcement-list' }">
        <Icon type="chatbubble-working"></Icon> {{ $t("m.Announcements") }}
      </router-link>
      <router-link :to="{ name: 'contest-problem-list' }">
        <Icon type="ios-photos"></Icon> {{ $t("m.Problems") }}
      </router-link>
      <router-link
        :to="{ name: 'contest-rank' }"
        v-if="OIContestRealTimePermission"
      >
        <Icon type="stats-bars"></Icon> {{ $t("m.Rankings") }}
      </router-link>
    </ul>
  </nav>
</template>

<script>
import SideNavBar from "./SideNavBar.vue"
import moment from "moment"
import { mapState, mapGetters, mapActions } from "vuex"
import { types } from "@/store"
import time from "@/utils/time"

export default {
  name: "side-nav-bar",
  data() {
    return {
      btnLoading: false,
      contestID: "",
    }
  },
  mounted() {
    this.contestID = this.$route.params.contestID
  },
  methods: {
    handleRoute(route) {
      this.$router.push(route)
    },
  },
  computed: {
    ...mapState({
      showMenu: (state) => state.contest.itemVisible.menu,
    }),
    ...mapGetters([
      "contestRuleType",
      "isContestAdmin",
      "OIContestRealTimePermission",
    ]),
    showAdminHelper() {
      return this.isContestAdmin && this.contestRuleType === "ACM"
    },
  },
}
</script>

<style scoped lang="less">
.side-nav {
  flex: none;
  width: 200px;
  height: fit-content;
  margin-right: 20px;
  background-color: var(--box-background-color);
  border: 1px solid #e9ece9;
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
