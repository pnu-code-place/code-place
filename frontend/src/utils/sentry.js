import { init, setContext } from "@sentry/vue"

const SENSITIVE_EXACT_FIELDS = [
  "authorization",
  "cookie",
  "password",
  "token",
  "secret",
  "code",
  "src",
]

const SENSITIVE_SUBSTRINGS = [
  "authorization",
  "cookie",
  "password",
  "token",
  "secret",
  "source_code",
  "sourcecode",
  "spj_code",
  "src",
]

function isSensitiveKey(key) {
  const normalized = String(key).toLowerCase()
  return (
    SENSITIVE_EXACT_FIELDS.indexOf(normalized) !== -1 ||
    SENSITIVE_SUBSTRINGS.some((field) => normalized.indexOf(field) !== -1)
  )
}

function redact(value) {
  if (Array.isArray(value)) {
    return value.map((item) => redact(item))
  }

  if (value && typeof value === "object") {
    return Object.keys(value).reduce((result, key) => {
      result[key] = isSensitiveKey(key) ? "[REDACTED]" : redact(value[key])
      return result
    }, {})
  }

  return value
}

const options = {
  release: process.env.VERSION,
  environment: process.env.SENTRY_ENVIRONMENT,
  beforeSend(event) {
    return redact(event)
  },
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
  if (process.env.USE_SENTRY !== "1" || !process.env.SENTRY_DSN) {
    return
  }

  init({
    Vue,
    dsn: process.env.SENTRY_DSN,
    ...options,
  })

  setContext("app", {
    version: process.env.VERSION,
    location: window.location.href,
  })
}

export function setRequestIdContext(requestId) {
  setContext("request", {
    request_id: requestId,
  })
}
