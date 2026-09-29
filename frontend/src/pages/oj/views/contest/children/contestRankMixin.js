import ScreenFull from "@admin/components/ScreenFull.vue"
import { mapGetters, mapState } from "vuex"
import { types } from "@/store"
import { CONTEST_STATUS } from "@/utils/constants"

export default {
  components: {
    ScreenFull,
  },
  computed: {
    ...mapGetters(["isContestAdmin"]),
    ...mapState({
      contest: (state) => state.contest.contest,
      contestProblems: (state) => state.contest.contestProblems,
    }),
    showChart: {
      get() {
        return this.$store.state.contest.itemVisible.chart
      },
      set(value) {
        this.$store.commit(types.CHANGE_CONTEST_ITEM_VISIBLE, { chart: value })
      },
    },
    showMenu: {
      get() {
        return this.$store.state.contest.itemVisible.menu
      },
      set(value) {
        this.$store.commit(types.CHANGE_CONTEST_ITEM_VISIBLE, { menu: value })
        this.$nextTick(() => {
          if (this.showChart) {
            this.$refs.chart.resize()
          }
          this.$refs.tableRank.handleResize()
        })
      },
    },

    forceUpdate: {
      get() {
        return this.$store.state.contest.forceUpdate
      },
      set(value) {
        this.$store.commit(types.CHANGE_RANK_FORCE_UPDATE, { value: value })
      },
    },
    limit: {
      get() {
        return this.$store.state.contest.rankLimit
      },
      set(value) {
        this.$store.commit(types.CHANGE_CONTEST_RANK_LIMIT, {
          rankLimit: value,
        })
      },
    },
    refreshDisabled() {
      return this.contest.status === CONTEST_STATUS.ENDED
    },
  },
  beforeDestroy() {
    clearInterval(this.refreshFunc)
  },
}
