import "core-js/stable"
import "regenerator-runtime/runtime"
import Vue from "vue"
import App from "./App.vue"
import store from "@/store"
import i18n from "@/i18n"
import Element from "element-ui"
import "element-ui/lib/theme-chalk/index.css"

import filters from "@/utils/filters"
import router from "./router"
import { GOOGLE_ANALYTICS_ID } from "@/utils/constants"
import VueAnalytics from "vue-analytics"
import katex from "@/plugins/katex"

import iView from "iview"
import "iview/dist/styles/iview.css"

import Panel from "./components/Panel.vue"
import IconBtn from "./components/btn/IconBtn.vue"
import Save from "./components/btn/Save.vue"
import Cancel from "./components/btn/Cancel.vue"
import "./style.less"

import ECharts from "vue-echarts"
import "@/utils/echarts"
import { initSentry } from "@/utils/sentry"
import { initClientErrorReporter } from "@/utils/client_error_reporter"

const legacyPanelTag = "Panel"
const legacySaveTag = "Save"
const legacyCancelTag = "Cancel"

// register global utility filters.
Object.keys(filters).forEach((key) => {
  Vue.filter(key, filters[key])
})

Vue.use(VueAnalytics, {
  id: GOOGLE_ANALYTICS_ID,
  router,
})
Vue.use(iView)
Vue.use(katex)
Vue.component(IconBtn.name, IconBtn)
Vue.component(legacyPanelTag, Panel)
Vue.component(legacySaveTag, Save)
Vue.component(legacyCancelTag, Cancel)
Vue.component("ECharts", ECharts)

Vue.use(Element, {
  i18n: (key, value) => i18n.t(key, value),
})

Vue.prototype.$error = (msg) => {
  Vue.prototype.$message({ message: msg, type: "error" })
}

Vue.prototype.$warning = (msg) => {
  Vue.prototype.$message({ message: msg, type: "warning" })
}

Vue.prototype.$success = (msg) => {
  if (!msg) {
    Vue.prototype.$message({ message: "Succeeded", type: "success" })
  } else {
    Vue.prototype.$message({ message: msg, type: "success" })
  }
}

initSentry(Vue)
initClientErrorReporter(Vue, { surface: "admin", router })

new Vue(Vue.util.extend({ router, store, i18n }, App)).$mount("#app")
