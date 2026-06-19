// let date = require('moment')().format('YYYYMMDD')
// let commit = require('child_process').execSync('git rev-parse HEAD').toString().slice(0, 5)
// let version = `"${date}-${commit}"`
const sentry = require("./sentry")

let version = JSON.stringify(process.env.APP_VERSION || process.env.VUE_APP_VERSION || "dev")
let useSentry = JSON.stringify(sentry.isSentryEnabled() ? "1" : "0")
let sentryDsn = JSON.stringify(sentry.getSentryDsn())
let sentryEnvironment = JSON.stringify(sentry.getSentryEnvironment())

console.log(`current version is ${version}`)

module.exports = {
  NODE_ENV: '"development"',
  VERSION: version,
  USE_SENTRY: useSentry,
  SENTRY_DSN: sentryDsn,
  SENTRY_ENVIRONMENT: sentryEnvironment,
}
