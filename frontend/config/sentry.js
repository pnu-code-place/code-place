"use strict"

function isSentryEnabled(nodeEnv = process.env.NODE_ENV) {
  return (process.env.USE_SENTRY || (nodeEnv === "production" ? "1" : "0")) === "1"
}

function getSentryDsn() {
  return (
    process.env.SENTRY_DSN ||
    "https://143814aaa2d6e0b4550b2e5effefe90d@o4511586463776768.ingest.us.sentry.io/4511586483634176"
  )
}

function getSentryEnvironment(nodeEnv = process.env.NODE_ENV) {
  return process.env.SENTRY_ENVIRONMENT || nodeEnv || "development"
}

module.exports = {
  getSentryEnvironment,
  getSentryDsn,
  isSentryEnabled,
}
