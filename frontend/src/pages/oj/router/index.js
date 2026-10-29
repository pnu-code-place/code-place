import Vue from "vue"
import VueRouter from "vue-router"
import routes from "./routes"
import storage from "@/utils/storage"
import { STORAGE_KEY } from "@/utils/constants"
import { sync } from "vuex-router-sync"
import { types, default as store } from "../../../store"

Vue.use(VueRouter)

const originalPush = VueRouter.prototype.push
VueRouter.prototype.push = function push(location, onComplete, onAbort) {
  if (onComplete || onAbort) {
    return originalPush.call(this, location, onComplete, onAbort)
  }
  return originalPush.call(this, location).catch((err) => {
    if (
      VueRouter.isNavigationFailure(
        err,
        VueRouter.NavigationFailureType.aborted,
      )
    ) {
      return err
    }
    return Promise.reject(err)
  })
}

const router = new VueRouter({
  mode: "history",
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { x: 0, y: 0 }
    }
  },
  routes,
})

// 全局身份确认
router.beforeEach((to, from, next) => {
  Vue.prototype.$Loading.start()
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (!storage.get(STORAGE_KEY.AUTHED)) {
      Vue.prototype.$error("Please login first")
      store.commit(types.CHANGE_MODAL_STATUS, { mode: "login", visible: true })
      // 비로그인 상태에서 로그인이 필요한 특정 행위를 했을 떄 그 화면 그대로에서 로그인 팝업이 뜸. 
      if (from.matched.length) {
        Vue.prototype.$Loading.finish()
        next(false)
      } else {
        next({
          name: "home",
        })
      }
    } else {
      next()
    }
  } else {
    next()
  }
})

router.afterEach((to, from, next) => {
  Vue.prototype.$Loading.finish()
})

sync(store, router)

export default router
