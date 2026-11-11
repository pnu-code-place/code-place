// 서버 오류 코드를 화면 문구 키로 변환, 모르는 코드는 서버 문구 사용
const AI_HINT_ERROR_KEYS = {
  "ai-hint-busy": "m.AI_Assistant_Error_Busy",
  "ai-hint-throttled": "m.AI_Assistant_Error_Throttled",
  "problem-limit-exceeded": "m.AI_Assistant_Error_Limit",
  "llm-hint-unavailable": "m.AI_Assistant_Error_Unavailable",
}

export function aiHintErrorText(vm, payload) {
  const key = payload && AI_HINT_ERROR_KEYS[payload.error]
  if (key) return vm.$t(key, { wait: payload.wait })
  return (payload && payload.message) || vm.$t("m.AI_Assistant_Fetch_Failed")
}
