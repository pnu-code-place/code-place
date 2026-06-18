// let date = require('moment')().format('YYYYMMDD')
// let commit = require('child_process').execSync('git rev-parse HEAD').toString().slice(0, 5)
// let version = `"${date}-${commit}"`
let version = JSON.stringify(process.env.VUE_APP_VERSION || "dev")
let useSentry = JSON.stringify(
  process.env.USE_SENTRY || (process.env.NODE_ENV === "production" ? "1" : "0"),
)
let sentryDsn = JSON.stringify(
  process.env.SENTRY_DSN ||
    "https://143814aaa2d6e0b4550b2e5effefe90d@o4511586463776768.ingest.us.sentry.io/4511586483634176",
)

console.log(`current version is ${version}`)

module.exports = {
  NODE_ENV: '"development"',
  VERSION: version,
  USE_SENTRY: useSentry,
  SENTRY_DSN: sentryDsn,
}
