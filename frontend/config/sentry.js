"use strict"

function isSentryEnabled(nodeEnv = process.env.NODE_ENV) {
  const enabled = (process.env.USE_SENTRY || (nodeEnv === "production" ? "1" : "0")) === "1"
  return enabled && Boolean(getSentryDsn())
}

function getSentryDsn() {
  return process.env.SENTRY_DSN || ""
}

function getSentryEnvironment(nodeEnv = process.env.NODE_ENV) {
  return process.env.SENTRY_ENVIRONMENT || nodeEnv || "development"
}

module.exports = {
  getSentryEnvironment,
  getSentryDsn,
  isSentryEnabled,
}
