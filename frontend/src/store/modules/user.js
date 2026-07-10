import types from "../types"
import api from "@oj/api"
import storage from "@/utils/storage"
import i18n from "@/i18n"
import { STORAGE_KEY, USER_TYPE, PROBLEM_PERMISSION } from "@/utils/constants"

const state = {
  profile: {},
  profileResolved: false,
  isProblemSolving: false,
  isDarkMode: false,
}

const getters = {
  user: (state) => state.profile.user || {},
  profile: (state) => state.profile,
  profileResolved: (state) => state.profileResolved,
  isProblemSolving: (state) => state.isProblemSolving,
  isAuthenticated: (state, getters) => {
    return !!getters.user.id
  },
  isDarkMode: (state) => state.isDarkMode,
  isAdminRole: (state, getters) => {
    return (
      getters.user.admin_type === USER_TYPE.ADMIN ||
      getters.user.admin_type === USER_TYPE.SUPER_ADMIN
    )
  },
  isSuperAdmin: (state, getters) => {
    return getters.user.admin_type === USER_TYPE.SUPER_ADMIN
  },
  hasProblemPermission: (state, getters) => {
    return getters.user.problem_permission !== PROBLEM_PERMISSION.NONE
  },
}

const mutations = {
  [types.CHANGE_PROFILE](state, { profile }) {
    state.profile = profile
    state.profileResolved = true
    if (profile.language) {
      i18n.locale = profile.language
    }
    storage.set(STORAGE_KEY.AUTHED, !!profile.user)
  },
  resolveProfile(state) {
    state.profileResolved = true
  },
  [types.CHANGE_PROBLEM_SOLVING_STATE](state, payload) {
    state.isProblemSolving = payload
  },
  [types.CHANGE_PROBLEM_SOLVING_THEME](state, payload) {
    state.isDarkMode = payload
  },
}

const actions = {
  getProfile({ commit }) {
    return api.getUserInfo().then(
      (res) => {
        commit(types.CHANGE_PROFILE, {
          profile: res.data.data || {},
        })
      },
      (error) => {
        const message = getProfileErrorMessage(error)
        if (message.startsWith("Please login")) {
          commit(types.CHANGE_PROFILE, {
            profile: {},
          })
          return
        }
        commit("resolveProfile")
      },
    )
  },
  clearProfile({ commit }) {
    commit(types.CHANGE_PROFILE, {
      profile: {},
    })
    storage.clear()
  },
  changeProblemSolvingState({ commit }, payload) {
    commit(types.CHANGE_PROBLEM_SOLVING_STATE, payload)
  },
  changeProblemSolvingTheme({ commit }, payload) {
    commit(types.CHANGE_PROBLEM_SOLVING_THEME, payload)
  },
}

function getProfileErrorMessage(error) {
  const data =
    (error && error.data) ||
    (error && error.response && error.response.data) ||
    {}
  return typeof data.data === "string" ? data.data : ""
}

export default {
  state,
  getters,
  actions,
  mutations,
}
