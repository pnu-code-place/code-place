import Vue from 'vue'
import Vuex from 'vuex'
import user from './modules/user'
import contest from './modules/contest'
import api from '@oj/api'
import types from './types'
import storage from "../utils/storage";

Vue.use(Vuex)
const debug = process.env.NODE_ENV !== 'production'

const rootState = {
  website: {},
  modalStatus: {
    mode: 'login', // or 'register',
    visible: false
  },
}

const rootGetters = {
  'website'(state) {
    return state.website
  },
  'modalStatus'(state) {
    return state.modalStatus
  },
  'removedPopupId'(state) {
    console.log("removedPopupId")
    if (storage.get('removedPopup') === null ) {
      storage.set('removedPopup', [])
    }
    return storage.get('removedPopup').map(popup => popup.id)
    // return state.removed_popup.map(popup => popup.id)
  }
}

const rootMutations = {
  [types.UPDATE_WEBSITE_CONF](state, payload) {
    state.website = payload.websiteConfig
  },
  [types.CHANGE_MODAL_STATUS](state, {mode, visible}) {
    if (mode !== undefined) {
      state.modalStatus.mode = mode
    }
    if (visible !== undefined) {
      state.modalStatus.visible = visible
    }
  },
  removePopup(state, payload) {
    if (storage.get('removedPopup') === null ) {
      storage.set('removedPopup', [])
    }
    const removedPopup = storage.get('removedPopup')
    removedPopup.push({removedDay : new Date().getDay() ,id : payload})
    storage.set('removedPopup', removedPopup)
    // state.removed_popup.push({removedDay: new Date().getDay(), id: payload})
  },
  refreshPopup(state) {
    if (storage.get('removedPopup') === null ) {
      storage.set('removedPopup', [])
    }
    let filtered = storage.get('removedPopup')
    filtered = filtered.filter(popup => popup.removedDay === new Date().getDay())
    storage.set('removedPopup', filtered)
    // state.removed_popup = state.removed_popup.filter(popup => popup.removedDay !== new Date().getDay())
  }
}

const rootActions = {
  getWebsiteConfig({commit}) {
    api.getWebsiteConf().then(res => {
      commit(types.UPDATE_WEBSITE_CONF, {
        websiteConfig: res.data.data
      })
    })
  },
  changeModalStatus({commit}, payload) {
    commit(types.CHANGE_MODAL_STATUS, payload)
  },
  changeDomTitle({commit, state}, payload) {
    if (payload && payload.title) {
      window.document.title = state.website.website_name_shortcut + ' | ' + payload.title
    } else {
      window.document.title = state.website.website_name_shortcut + ' | ' + state.route.meta.title
    }
  }
}

export default new Vuex.Store({
  modules: {
    user,
    contest
  },
  state: rootState,
  getters: rootGetters,
  mutations: rootMutations,
  actions: rootActions,
  strict: debug,
})

export {types}
