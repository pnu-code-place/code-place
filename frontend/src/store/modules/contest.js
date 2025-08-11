import moment from "moment"
import types from "../types"
import api from "@oj/api"
import { CONTEST_STATUS, USER_TYPE, CONTEST_TYPE } from "@/utils/constants"

const state = {
  now: moment(),
  access: false,
  rankLimit: 30,
  forceUpdate: false,
  contest: {
    created_by: {},
    contest_type: CONTEST_TYPE.PUBLIC,
  },
  contestProblems: [],
  itemVisible: {
    menu: true,
    chart: true,
    realName: false,
  },
}

const getters = {
  // contest 是否加载完成
  contestLoaded: (state) => {
    return !!state.contest.status
  },
  contestStatus: (state, getters) => {
    if (!getters.contestLoaded) return null
    let startTime = moment(state.contest.start_time)
    let endTime = moment(state.contest.end_time)
    let now = state.now

    if (startTime > now) {
      return CONTEST_STATUS.NOT_START
    } else if (endTime < now) {
      return CONTEST_STATUS.ENDED
    } else {
      return CONTEST_STATUS.UNDERWAY
    }
  },
  contestRuleType: (state) => {
    return state.contest.rule_type || null
  },
  isContestAdmin: (state, getters, _, rootGetters) => {
    return (
      rootGetters.isAuthenticated &&
      (state.contest.created_by.id === rootGetters.user.id ||
        rootGetters.user.admin_type === USER_TYPE.SUPER_ADMIN)
    )
  },
  contestMenuDisabled: (state, getters) => {
    if (getters.isContestAdmin) return false
    if (state.contest.contest_type === CONTEST_TYPE.PUBLIC) {
      return getters.contestStatus === CONTEST_STATUS.NOT_START
    }
    return !state.access
  },
  OIContestRealTimePermission: (state, getters, _, rootGetters) => {
    if (
      getters.contestRuleType === "ACM" ||
      getters.contestStatus === CONTEST_STATUS.ENDED
    ) {
      return true
    }
    return state.contest.real_time_rank === true || getters.isContestAdmin
  },
  problemSubmitDisabled: (state, getters, _, rootGetters) => {
    if (getters.contestStatus === CONTEST_STATUS.ENDED) {
      return true
    } else if (getters.contestStatus === CONTEST_STATUS.NOT_START) {
      return !getters.isContestAdmin
    }
    return !rootGetters.isAuthenticated
  },
  passwordFormVisible: (state, getters) => {
    return (
      state.contest.contest_type !== CONTEST_TYPE.PUBLIC &&
      !state.access &&
      !getters.isContestAdmin
    )
  },
  contestStartTime: (state) => {
    const date = new Date(state.contest.start_time)

    return new Date(date.getTime() - date.getTimezoneOffset() * 60 * 1000)
  },
  contestEndTime: (state) => {
    const date = new Date(state.contest.end_time)

    return new Date(date.getTime() - date.getTimezoneOffset() * 60 * 1000)
  },
  countdown: (state, getters) => {
    if (getters.contestStatus === CONTEST_STATUS.NOT_START) {
      const offset = getters.contestStartTime.getTimezoneOffset() * 60 * 1000
      let duration = getters.contestStartTime - new Date() + offset

      duration = parseInt(duration / 1000)
      const sec = duration % 60
      duration = parseInt(duration / 60)
      const min = duration % 60
      duration = parseInt(duration / 60)
      const hours = duration % 24
      duration = parseInt(duration / 24)
      const days = duration

      let result = ""
      if (days > 0) result += days + "일 "
      if (hours > 0) result += hours + "시간 "
      if (min > 0) result += min + "분 "
      if (sec > 0) result += sec + "초"

      return "시작까지 " + result + " 전"
    } else if (getters.contestStatus === CONTEST_STATUS.UNDERWAY) {
      const offset = getters.contestEndTime.getTimezoneOffset() * 60 * 1000
      let duration = getters.contestEndTime - new Date() + offset

      duration = parseInt(duration / 1000)
      const sec = duration % 60
      duration = parseInt(duration / 60)
      const min = duration % 60
      duration = parseInt(duration / 60)
      const hours = duration % 24
      duration = parseInt(duration / 24)
      const days = duration

      let result = ""
      if (days > 0) result += days + "일 "
      if (hours > 0) result += hours + "시간 "
      if (min > 0) result += min + "분 "
      if (sec > 0) result += sec + "초"

      console.log(days, hours, min, sec)

      return "종료까지 " + result + " 전"
    } else {
      return "종료"
    }
  },
}

const mutations = {
  [types.CHANGE_CONTEST](state, payload) {
    state.contest = payload.contest
  },
  [types.CHANGE_CONTEST_ITEM_VISIBLE](state, payload) {
    state.itemVisible = { ...state.itemVisible, ...payload }
  },
  [types.CHANGE_RANK_FORCE_UPDATE](state, payload) {
    state.forceUpdate = payload.value
  },
  [types.CHANGE_CONTEST_PROBLEMS](state, payload) {
    state.contestProblems = payload.contestProblems
  },
  [types.CHANGE_CONTEST_RANK_LIMIT](state, payload) {
    state.rankLimit = payload.rankLimit
  },
  [types.CONTEST_ACCESS](state, payload) {
    state.access = payload.access
  },
  [types.CLEAR_CONTEST](state) {
    state.contest = { created_by: {} }
    state.contestProblems = []
    state.access = false
    state.itemVisible = {
      menu: true,
      chart: true,
      realName: false,
    }
    state.forceUpdate = false
  },
  [types.NOW](state, payload) {
    state.now = payload.now
  },
  [types.NOW_ADD_1S](state) {
    state.now = moment(state.now.add(1, "s"))
  },
}

const actions = {
  getContest({ commit, rootState, dispatch }) {
    return new Promise((resolve, reject) => {
      api.getContest(rootState.route.params.contestID).then(
        (res) => {
          resolve(res)
          let contest = res.data.data
          commit(types.CHANGE_CONTEST, { contest: contest })
          commit(types.NOW, { now: moment(contest.now) })
          if (contest.contest_type === CONTEST_TYPE.PRIVATE) {
            dispatch("getContestAccess")
          }
        },
        (err) => {
          reject(err)
        },
      )
    })
  },
  getContestProblems({ commit, rootState }, keyword) {
    return new Promise((resolve, reject) => {
      api.getContestProblemList(rootState.route.params.contestID, keyword).then(
        (res) => {
          res.data.data.sort((a, b) => {
            if (a._id === b._id) {
              return 0
            } else if (a._id > b._id) {
              return 1
            }
            return -1
          })
          commit(types.CHANGE_CONTEST_PROBLEMS, {
            contestProblems: res.data.data,
          })
          resolve(res)
        },
        () => {
          commit(types.CHANGE_CONTEST_PROBLEMS, { contestProblems: [] })
        },
      )
    })
  },
  getContestAccess({ commit, rootState }) {
    return new Promise((resolve, reject) => {
      api
        .getContestAccess(rootState.route.params.contestID)
        .then((res) => {
          commit(types.CONTEST_ACCESS, { access: res.data.data.access })
          resolve(res)
        })
        .catch()
    })
  },
}

export default {
  state,
  mutations,
  getters,
  actions,
}
