"use strict"

function isSentryEnabled(nodeEnv = process.env.NODE_ENV) {
  const enabled = (process.env.USE_SENTRY || (nodeEnv === "production" ? "1" : "0")) === "1"
  return enabled && Boolean(getSentryDsn())
}

function getSentryDsn() {
  return process.env.SENTRY_DSN_FRONTEND || ""
}

function getSentryEnvironment(nodeEnv = process.env.NODE_ENV) {
  return process.env.SENTRY_ENVIRONMENT || nodeEnv || "development"
}

function isSentryUploadEnabled(nodeEnv = process.env.NODE_ENV) {
  return (
    isSentryEnabled(nodeEnv) &&
    Boolean(process.env.SENTRY_AUTH_TOKEN) &&
    Boolean(process.env.APP_VERSION || process.env.VUE_APP_VERSION)
  )
}

function assertSentryUploadConfig(nodeEnv = process.env.NODE_ENV) {
  const requested = (process.env.USE_SENTRY || (nodeEnv === "production" ? "1" : "0")) === "1"
  if (!requested) {
    return
  }

  const required = {
    SENTRY_DSN_FRONTEND: getSentryDsn(),
    SENTRY_AUTH_TOKEN: process.env.SENTRY_AUTH_TOKEN,
    APP_VERSION: process.env.APP_VERSION || process.env.VUE_APP_VERSION,
  }
  const missing = Object.keys(required).filter((name) => !required[name])
  if (missing.length) {
    throw new Error(`Missing Sentry build configuration: ${missing.join(", ")}`)
  }
}

module.exports = {
  assertSentryUploadConfig,
  getSentryEnvironment,
  getSentryDsn,
  isSentryEnabled,
  isSentryUploadEnabled,
}
