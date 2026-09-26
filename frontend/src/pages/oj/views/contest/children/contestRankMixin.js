import ScreenFull from "@admin/components/ScreenFull.vue"
import { mapGetters, mapState } from "vuex"
import { types } from "@/store"
import { CONTEST_STATUS } from "@/utils/constants"

const RANK_REFRESH_INTERVAL_MS = 2000
const RANK_REFRESH_JITTER_MS = 500

export default {
  components: {
    ScreenFull,
  },
  data() {
    return {
      refreshFunc: null,
      rankRequestInFlight: false,
    }
  },
  computed: {
    ...mapGetters(["isContestAdmin", "contestStatus"]),
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
      return this.contestStatus === CONTEST_STATUS.ENDED
    },
  },
  mounted() {
    document.addEventListener("visibilitychange", this.handleRankVisibilityChange)
  },
  methods: {
    startRankPolling() {
      this.stopRankPolling()
      if (this.refreshDisabled || document.hidden) return

      const jitter = Math.floor(Math.random() * (RANK_REFRESH_JITTER_MS + 1))
      this.refreshFunc = setTimeout(
        this.pollContestRank,
        RANK_REFRESH_INTERVAL_MS + jitter,
      )
    },
    stopRankPolling() {
      if (this.refreshFunc !== null) {
        clearTimeout(this.refreshFunc)
        this.refreshFunc = null
      }
    },
    pollContestRank() {
      this.stopRankPolling()
      if (this.refreshDisabled || document.hidden) return

      Promise.resolve(this.updateContestData({ silent: true })).finally(() => {
        this.startRankPolling()
      })
    },
    handleRankVisibilityChange() {
      if (document.hidden || this.refreshDisabled) {
        this.stopRankPolling()
        return
      }

      this.pollContestRank()
    },
  },
  beforeDestroy() {
    this.stopRankPolling()
    document.removeEventListener(
      "visibilitychange",
      this.handleRankVisibilityChange,
    )
  },
}
