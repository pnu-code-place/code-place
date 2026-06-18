import moment from "moment"
import types from "../types"
import api from "@oj/api"
import { CONTEST_STATUS, USER_TYPE, CONTEST_TYPE } from "@/utils/constants"

function getClientTick() {
  if (typeof window !== "undefined" && window.performance) {
    return window.performance.now()
  }
  return Date.now()
}

const state = {
  now: moment(),
  nowBase: moment(),
  clientNowBase: getClientTick(),
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

function formatDuration(seconds) {
  let duration = Math.max(parseInt(seconds, 10), 0)
  const sec = duration % 60
  duration = parseInt(duration / 60, 10)
  const min = duration % 60
  duration = parseInt(duration / 60, 10)
  const hours = duration % 24
  duration = parseInt(duration / 24, 10)
  const days = duration

  let result = ""
  if (days > 0) result += days + "일 "
  if (hours > 0) result += hours + "시간 "
  if (min > 0) result += min + "분 "
  if (sec > 0) result += sec + "초"

  return result || "0초"
}

function getElapsedServerNow(state) {
  return moment(state.nowBase).add(getClientTick() - state.clientNowBase, "ms")
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
  OIContestRealTimePermission: (state, getters) => {
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
    return moment(state.contest.start_time)
  },
  contestEndTime: (state) => {
    return moment(state.contest.end_time)
  },
  countdown: (state, getters) => {
    if (getters.contestStatus === CONTEST_STATUS.NOT_START) {
      return (
        "시작까지 " +
        formatDuration(getters.contestStartTime.diff(state.now, "seconds")) +
        " 전"
      )
    } else if (getters.contestStatus === CONTEST_STATUS.UNDERWAY) {
      return (
        "종료까지 " +
        formatDuration(getters.contestEndTime.diff(state.now, "seconds")) +
        " 전"
      )
    } else {
      return "종료"
    }
  },
  countdownParts: (state, getters) => {
    let totalSeconds
    let label
    let status

    if (getters.contestStatus === CONTEST_STATUS.NOT_START) {
      totalSeconds = Math.max(
        getters.contestStartTime.diff(state.now, "seconds"),
        0,
      )
      label = "시작까지"
      status = "waiting"
    } else if (getters.contestStatus === CONTEST_STATUS.UNDERWAY) {
      totalSeconds = Math.max(
        getters.contestEndTime.diff(state.now, "seconds"),
        0,
      )
      label = "종료까지"
      status = "running"
    } else {
      return { days: 0, hours: 0, minutes: 0, seconds: 0, label: "종료", status: "ended", totalSeconds: 0 }
    }

    let rem = totalSeconds
    const days = Math.floor(rem / 86400)
    rem %= 86400
    const hours = Math.floor(rem / 3600)
    rem %= 3600
    const minutes = Math.floor(rem / 60)
    const seconds = rem % 60

    return { days, hours, minutes, seconds, label, status, totalSeconds }
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
    state.nowBase = moment(payload.now)
    state.clientNowBase = getClientTick()
    state.now = moment(state.nowBase)
  },
  [types.NOW_ADD_1S](state) {
    state.now = getElapsedServerNow(state)
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
        (err) => {
          commit(types.CHANGE_CONTEST_PROBLEMS, { contestProblems: [] })
          reject(err)
        },
      )
    })
  },
  getContestAccess({ commit, rootState }) {
    return new Promise((resolve) => {
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
