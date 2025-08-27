import types from "../types"
import api from "@oj/api"
import storage from "@/utils/storage"
import i18n from "@/i18n"
import { STORAGE_KEY, USER_TYPE, PROBLEM_PERMISSION } from "@/utils/constants"

const state = {
  profile: {},
  isProblemSolving: false,
  isDarkMode: false,
}

const getters = {
  user: (state) => state.profile.user || {},
  profile: (state) => state.profile,
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
    if (profile.language) {
      i18n.locale = profile.language
    }
    storage.set(STORAGE_KEY.AUTHED, !!profile.user)
  },
}

const actions = {
  getProfile({ commit }) {
    api.getUserInfo().then((res) => {
      commit(types.CHANGE_PROFILE, {
        profile: res.data.data || {},
      })
    })
  },
  clearProfile({ commit }) {
    commit(types.CHANGE_PROFILE, {
      profile: {},
    })
    storage.clear()
  },
  changeProblemSolvingState({ commit, state }, payload) {
    state.isProblemSolving = payload
  },
  changeProblemSolvingTheme({ commit, state }, payload) {
    state.isDarkMode = payload
  },
}

export default {
  state,
  getters,
  actions,
  mutations,
}
