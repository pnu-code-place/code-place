import { init, setContext } from "@sentry/vue"

const SENTRY_DSN =
  "https://143814aaa2d6e0b4550b2e5effefe90d@o4511586463776768.ingest.us.sentry.io/4511586483634176"

const options = {
  release: process.env.VERSION,
  environment: process.env.SENTRY_ENVIRONMENT,
  denyUrls: [
    // Chrome extensions
    /extensions\//i,
    /^chrome:\/\//i,
    // Firefox extensions
    /^resource:\/\//i,
    // Ignore Google flakiness
    /\/(gtm|ga|analytics)\.js/i,
  ],
  dataCollection: {
    userInfo: false,
    httpBodies: [],
  },
}

export function initSentry(Vue) {
  if (process.env.USE_SENTRY !== "1") {
    return
  }

  init({
    Vue,
    dsn: process.env.SENTRY_DSN || SENTRY_DSN,
    ...options,
  })

  setContext("app", {
    version: process.env.VERSION,
    location: window.location.href,
  })
}
