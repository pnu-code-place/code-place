const CLIENT_ERROR_ENDPOINT = "/api/client_error"
const MAX_MESSAGE_LENGTH = 300

function cleanField(value) {
  if (value === undefined || value === null) {
    return ""
  }
  return String(value).replace(/[\r\n]+/g, " ").trim().slice(0, MAX_MESSAGE_LENGTH)
}

function currentRequestId() {
  return cleanField(window.__CODEPLACE_LAST_REQUEST_ID__)
}

function currentRoute(router) {
  if (router && router.currentRoute && router.currentRoute.path) {
    return router.currentRoute.path
  }
  return window.location.pathname
}

function reportClientError(payload) {
  const requestId = currentRequestId()
  const body = JSON.stringify({
    ...payload,
    request_id: requestId,
    release: process.env.VERSION,
  })
  const headers = {
    "Content-Type": "application/json",
  }
  if (requestId) {
    headers["X-Request-ID"] = requestId
  }

  if (navigator.sendBeacon) {
    const blob = new Blob([body], { type: "application/json" })
    if (navigator.sendBeacon(CLIENT_ERROR_ENDPOINT, blob)) {
      return
    }
  }

  window.fetch(CLIENT_ERROR_ENDPOINT, {
    method: "POST",
    headers,
    body,
    credentials: "same-origin",
    keepalive: true,
  }).catch(() => {})
}

function errorMessage(error) {
  if (!error) {
    return "unknown"
  }
  if (error.message) {
    return error.message
  }
  return error.reason || error.toString()
}

export function initClientErrorReporter(Vue, { surface = "unknown", router } = {}) {
  const previousErrorHandler = Vue.config.errorHandler

  Vue.config.errorHandler = (error, vm, info) => {
    reportClientError({
      surface,
      error_type: "vue",
      message: cleanField(errorMessage(error)),
      route: cleanField(currentRoute(router)),
      component: cleanField(vm && vm.$options && (vm.$options.name || vm.$options._componentTag)),
      info: cleanField(info),
    })

    if (previousErrorHandler) {
      previousErrorHandler.call(Vue.config, error, vm, info)
    } else {
      console.error(error)
    }
  }

  if (window.__CODEPLACE_CLIENT_ERROR_REPORTER_READY__) {
    return
  }
  window.__CODEPLACE_CLIENT_ERROR_REPORTER_READY__ = true

  window.addEventListener("error", (event) => {
    reportClientError({
      surface,
      error_type: "window_error",
      message: cleanField(errorMessage(event.error) || event.message),
      route: cleanField(currentRoute(router)),
    })
  })

  window.addEventListener("unhandledrejection", (event) => {
    reportClientError({
      surface,
      error_type: "unhandled_rejection",
      message: cleanField(errorMessage(event.reason)),
      route: cleanField(currentRoute(router)),
    })
  })
}
