<template>
  <main v-if="route_name === 'contest-problem-details'" style="width: 100%">
    <router-view></router-view>
  </main>
  <main v-else>
    <side-nav-bar></side-nav-bar>
    <div id="contest-content">
      <transition name="fadeInUp">
        <router-view></router-view>
      </transition>
    </div>
  </main>
</template>

<script>
import SideNavBar from "./SideNavBar.vue"
import moment from "moment"
import api from "@oj/api"
import { mapState, mapGetters, mapActions } from "vuex"
import { types } from "@/store"
import { CONTEST_STATUS_REVERSE, CONTEST_STATUS } from "@/utils/constants"
import time from "@/utils/time"

export default {
  components: { SideNavBar },
  name: "ContestDetail",
  data() {
    return {
      CONTEST_STATUS: CONTEST_STATUS,
      route_name: "",
      btnLoading: false,
      contestID: "",
      contestPassword: "",
      columns: [
        {
          title: this.$i18n.t("m.StartAt"),
          render: (h, params) => {
            return h("span", time.utcToLocal(params.row.start_time))
          },
        },
        {
          title: this.$i18n.t("m.EndAt"),
          render: (h, params) => {
            return h("span", time.utcToLocal(params.row.end_time))
          },
        },
        {
          title: this.$i18n.t("m.ContestType"),
          render: (h, params) => {
            return h(
              "span",
              this.$i18n.t(
                "m." + params.row.contest_type
                  ? params.row.contest_type.replace(" ", "_")
                  : "",
              ),
            )
          },
        },
        {
          title: this.$i18n.t("m.Rule"),
          render: (h, params) => {
            return h("span", this.$i18n.t("m." + params.row.rule_type))
          },
        },
        {
          title: this.$i18n.t("m.Creator"),
          render: (h, data) => {
            return h("span", data.row.created_by.username)
          },
        },
      ],
    }
  },
  mounted() {
    this.contestID = this.$route.params.contestID
    this.route_name = this.$route.name
    this.$store.dispatch("getContest").then((res) => {
      this.changeDomTitle({ title: res.data.data.title })
      let data = res.data.data
      let endTime = moment(data.end_time)
      if (endTime.isAfter(moment(data.now))) {
        this.timer = setInterval(() => {
          this.$store.commit(types.NOW_ADD_1S)
        }, 1000)
      }
    })
  },
  methods: {
    ...mapActions(["changeDomTitle"]),
    handleRoute(route) {
      this.$router.push(route)
    },
    checkPassword() {
      if (this.contestPassword === "") {
        this.$error("Password can't be empty")
        return
      }
      this.btnLoading = true
      api.checkContestPassword(this.contestID, this.contestPassword).then(
        (res) => {
          this.$success("Succeeded")
          this.$store.commit(types.CONTEST_ACCESS, { access: true })
          this.btnLoading = false
        },
        (res) => {
          this.btnLoading = false
        },
      )
    },
  },
  computed: {
    ...mapState({
      showMenu: (state) => state.contest.itemVisible.menu,
      contest: (state) => state.contest.contest,
      contest_table: (state) => [state.contest.contest],
      now: (state) => state.contest.now,
    }),
    ...mapGetters([
      "contestMenuDisabled",
      "contestRuleType",
      "contestStatus",
      "countdown",
      "isContestAdmin",
      "OIContestRealTimePermission",
      "passwordFormVisible",
    ]),
    countdownColor() {
      if (this.contestStatus) {
        return CONTEST_STATUS_REVERSE[this.contestStatus].color
      }
    },
    showAdminHelper() {
      return this.isContestAdmin && this.contestRuleType === "ACM"
    },
  },
  watch: {
    $route(newVal) {
      this.route_name = newVal.name
      this.contestID = newVal.params.contestID
      this.changeDomTitle({ title: this.contest.title })
    },
  },
  beforeDestroy() {
    clearInterval(this.timer)
    this.$store.commit(types.CLEAR_CONTEST)
  },
}
</script>

<style scoped lang="less">
main {
  width: var(--global-width);
  display: flex;
  gap: 10px;

  #contest-content {
    flex: 1 auto;
  }
}
</style>
