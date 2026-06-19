import { setRequestIdContext } from "@/utils/sentry"

const REQUEST_ID_HEADER = "X-Request-ID"
const RESPONSE_REQUEST_ID_HEADER = "x-request-id"

function randomHex(length) {
  if (window.crypto && window.crypto.getRandomValues) {
    const values = new Uint8Array(Math.ceil(length / 2))
    window.crypto.getRandomValues(values)
    return Array.from(values)
      .map((value) => value.toString(16).padStart(2, "0"))
      .join("")
      .slice(0, length)
  }

  return Math.random().toString(16).slice(2, 2 + length).padEnd(length, "0")
}

function createRequestId() {
  return `cp-${Date.now().toString(36)}-${randomHex(16)}`
}

function rememberRequestId(requestId) {
  if (!requestId) {
    return
  }

  setRequestIdContext(requestId)
}

function responseRequestId(response) {
  return (
    response &&
    response.headers &&
    (response.headers[RESPONSE_REQUEST_ID_HEADER] || response.headers[REQUEST_ID_HEADER])
  )
}

export function configureAxiosRequestId(axios) {
  if (axios.__codeplaceRequestIdConfigured) {
    return
  }
  axios.__codeplaceRequestIdConfigured = true

  axios.interceptors.request.use((config) => {
    const requestId = createRequestId()
    config.headers = config.headers || {}
    config.headers[REQUEST_ID_HEADER] = requestId
    config.metadata = {
      ...(config.metadata || {}),
      requestId,
    }
    rememberRequestId(requestId)
    return config
  })

  axios.interceptors.response.use(
    (response) => {
      const requestId =
        responseRequestId(response) ||
        (response.config && response.config.metadata && response.config.metadata.requestId)
      response.requestId = requestId
      rememberRequestId(requestId)
      return response
    },
    (error) => {
      const requestId =
        responseRequestId(error.response) ||
        (error.config && error.config.metadata && error.config.metadata.requestId)
      error.requestId = requestId
      rememberRequestId(requestId)
      return Promise.reject(error)
    },
  )
}
