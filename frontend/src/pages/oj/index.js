import "core-js/stable"
import "regenerator-runtime/runtime"
import Vue from "vue"
import App from "./App.vue"
import router from "./router"
import store from "@/store"
import i18n from "@/i18n"
import VueClipboard from "vue-clipboard2"
import VueAnalytics from "vue-analytics"
import { GOOGLE_ANALYTICS_ID } from "@/utils/constants"

import iView from "iview"
import "iview/dist/styles/iview.css"

import Panel from "@oj/components/Panel.vue"
import VerticalMenu from "@oj/components/verticalMenu/verticalMenu.vue"
import VerticalMenuItem from "@oj/components/verticalMenu/verticalMenu-item.vue"
import "@/styles/index.less"

import highlight from "@/plugins/highlight"
import katex from "@/plugins/katex"
import filters from "@/utils/filters.js"

import ECharts from "vue-echarts"
import "@/utils/echarts"
import { initSentry } from "@/utils/sentry"

const legacyPanelTag = "Panel"

// register global utility filters.
Object.keys(filters).forEach((key) => {
  Vue.filter(key, filters[key])
})

Vue.config.productionTip = false
Vue.use(iView, {
  i18n: (key, value) => i18n.t(key, value),
})

Vue.use(VueClipboard)
Vue.use(highlight)
Vue.use(katex)
Vue.use(VueAnalytics, {
  id: GOOGLE_ANALYTICS_ID,
  router,
})

Vue.component("ECharts", ECharts)
Vue.component(VerticalMenu.name, VerticalMenu)
Vue.component(VerticalMenuItem.name, VerticalMenuItem)
Vue.component(legacyPanelTag, Panel)

// 注册全局消息提示
Vue.prototype.$Message.config({
  duration: 2,
})
Vue.prototype.$error = (s) => Vue.prototype.$Message.error(s)
Vue.prototype.$info = (s) => Vue.prototype.$Message.info(s)
Vue.prototype.$success = (s) => Vue.prototype.$Message.success(s)

initSentry(Vue)

const app = new Vue(Vue.util.extend({ router, store, i18n }, App))

router.onReady(() => {
  app.$mount("#app")
})
