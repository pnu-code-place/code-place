<template>
  <div class="ai-panel">
    <div class="ai-panel-header">
      <div class="ai-panel-title">
        <img src="@/assets/images/AIAssistant.svg" alt="" />
        <span>{{ $t("m.AI_Assistant") }}</span>
      </div>
      <button
        type="button"
        class="close-btn"
        :aria-label="$t('m.AI_Assistant_Close')"
        @click="$emit('close')"
      >
        ✕
      </button>
    </div>

    <div class="ai-panel-content">
      <!-- v1: 단계 진행 스테퍼 -->
      <div v-if="!isChatMode && !isAdminRole" class="hint-stepper">
        <div class="step-track">
          <span
            v-for="n in hintLimit"
            :key="n"
            class="step-dot"
            :class="{ done: n <= hintsUsed }"
          ></span>
        </div>
        <span class="step-label">{{ hintsUsed }}/{{ hintLimit }} 단계</span>
      </div>

      <div ref="terminalBody" class="terminal-body">
        <!-- 첫 진입 온보딩 -->
        <div v-if="messages.length === 0" class="ai-empty">
          <div class="ai-empty-avatar">
            <img src="@/assets/images/AIAssistant.svg" alt="AI" />
          </div>
          <p class="ai-empty-title">
            {{
              isChatMode
                ? $t("m.AI_Assistant_Empty_Title")
                : $t("m.AI_Assistant_Hint_Empty_Title")
            }}
          </p>
          <p class="ai-empty-sub">
            {{
              isChatMode
                ? $t("m.AI_Assistant_Empty_Desc")
                : $t("m.AI_Assistant_Hint_Empty_Desc")
            }}
          </p>
        </div>

        <div v-else class="ai-chat">
          <div
            v-for="(msg, i) in renderMessages"
            :key="i"
            class="chat-row"
            :class="{ 'chat-row--user': msg.role === 'user' }"
          >
            <div
              v-if="msg.role === 'user'"
              class="bubble user-bubble"
              v-text="msg.text"
            ></div>

            <template v-else>
              <div class="avatar">
                <img src="@/assets/images/AIAssistant.svg" alt="AI" />
              </div>

              <div
                v-if="msg.thinking"
                class="bubble thinking-bubble"
                v-text="$t('m.AI_Assistant_Thinking')"
              ></div>

              <div
                v-else-if="msg.error"
                class="bubble error"
                v-text="msg.text"
              ></div>

              <div v-else class="bubble hint-bubble">
                <div v-if="msg.parsed.level" class="hint-level-badge">
                  {{ msg.parsed.level }}단계
                </div>

                <template v-if="msg.parsed.sections.length">
                  <div
                    v-for="(sec, si) in msg.parsed.sections"
                    :key="si"
                    class="hint-section"
                    :class="sectionClass(sec.label)"
                  >
                    <div class="hint-section-label">{{ sec.label }}</div>
                    <div class="hint-section-text" v-text="sec.text"></div>
                  </div>
                </template>
                <!-- renderMarkdown 결과는 DOMPurify로 정제됨 -->
                <!-- eslint-disable-next-line vue/no-v-html -->
                <div v-else class="hint-body" v-html="msg.parsed.html"></div>
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- v2: 입력창 -->
      <form
        v-if="isChatMode"
        class="ai-composer"
        @submit.prevent="sendQuestion"
      >
        <textarea
          ref="input"
          v-model="draft"
          class="composer-input"
          rows="1"
          :maxlength="maxQuestionLength"
          :placeholder="$t('m.AI_Assistant_Placeholder')"
          @input="resizeInput"
          @keydown.enter="onEnter"
        ></textarea>
        <div class="composer-actions">
          <button
            type="button"
            class="hint-chip"
            :disabled="isLoading"
            @click="requestHint"
          >
            <i class="far fa-lightbulb"></i>
            {{ $t("m.AI_Assistant_Get_Hint") }}
          </button>
          <span
            v-if="draft.length > maxQuestionLength * 0.8"
            class="char-count"
          >
            {{ draft.length }}/{{ maxQuestionLength }}
          </span>
          <button
            type="submit"
            class="send-btn"
            :disabled="!canSend"
            :aria-label="$t('m.AI_Assistant_Send')"
          >
            <i class="fas fa-arrow-up"></i>
          </button>
        </div>
      </form>

      <!-- v1: 단계별 힌트 요청 -->
      <div v-else class="ai-composer">
        <span class="hint-count">
          {{
            isAdminRole
              ? "남은 횟수 : 무제한 (관리자)"
              : `남은 횟수 : 이 문제에서 ${hintsRemaining}/${hintLimit} 회 더 가능`
          }}
        </span>
        <button
          type="button"
          class="step-hint-btn"
          :disabled="isLoading || hintsExhausted"
          @click="requestStepHint"
        >
          {{
            isLoading
              ? $t("m.AI_Assistant_Thinking")
              : hintsExhausted
                ? $t("m.AI_Assistant_Exhausted")
                : $t("m.AI_Assistant_Get_Step_Hint")
          }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@oj/api"
import { mapGetters } from "vuex"
import { renderMarkdown } from "@/utils/markdown"

// 백엔드 utils.constants.HINT_LIMIT_PER_PROBLEM 과 동일 (v1 전용)
const HINT_LIMIT_PER_PROBLEM = 5

export default {
  emits: ["close"],
  props: {
    problemID: String,
    contestID: [Number, String],
    code: {
      type: String,
      default: "",
    },
  },

  data() {
    return {
      // { role: "user" | "assistant", text, thinking?, error? }
      messages: [],
      draft: "",
      isLoading: false,
      abortController: null,
      // 백엔드 MAX_QUESTION_LENGTH와 동일
      maxQuestionLength: 1000,
      hintLimit: HINT_LIMIT_PER_PROBLEM,
    }
  },

  computed: {
    ...mapGetters(["isAdminRole"]),

    // 대회는 v1(단계별 힌트), 일반 문제는 v2(채팅)
    isChatMode() {
      return !this.contestID
    },

    // v1: 이 문제에서 받은 힌트 수
    hintsUsed() {
      return this.messages.filter(
        (m) => m.role === "assistant" && !m.thinking && !m.error,
      ).length
    },

    hintsRemaining() {
      return Math.max(0, this.hintLimit - this.hintsUsed)
    },

    hintsExhausted() {
      return !this.isAdminRole && this.hintsRemaining <= 0
    },

    canSend() {
      return !this.isLoading && this.draft.trim().length > 0
    },

    // AI 답변은 단계 배지 + 섹션(진단/힌트/점검) 구조로 파싱
    renderMessages() {
      return this.messages.map((m) => ({
        ...m,
        parsed:
          m.role === "assistant" && !m.thinking && !m.error
            ? this.parseHint(m.text)
            : null,
      }))
    },
  },

  methods: {
    // 이전 대화 내역 불러오기
    fetchHistory() {
      if (!this.problemID) return

      api
        .getAIHintHistory(this.problemID, this.contestID)
        .then((res) => {
          // 응답이 늦게 와서 진행 중인 대화를 덮어쓰지 않도록
          if (this.isLoading) return
          const logs = (res.data.data.logs || []).filter(
            (log) => log.hint_content && log.hint_content.trim() !== "",
          )
          this.messages = logs.map((log) => ({
            role: log.role === "user" ? "user" : "assistant",
            text: log.hint_content,
          }))
          this.scrollToBottom()
        })
        .catch((err) => {
          console.error("AI 조교 대화 내역을 불러오지 못했습니다.", err)
        })
    },

    onEnter(e) {
      // 한글 조합 중 Enter, Shift+Enter(줄바꿈)는 전송하지 않음
      if (e.isComposing || e.keyCode === 229 || e.shiftKey) return
      e.preventDefault()
      this.sendQuestion()
    },

    sendQuestion() {
      if (!this.canSend) return
      const question = this.draft.trim()
      this.draft = ""
      this.$nextTick(this.resizeInput)
      this.messages.push({ role: "user", text: question })
      this.streamAnswer(question)
    },

    // v2: 「힌트 받기」는 정해진 질문을 대신 보낸다
    requestHint() {
      if (this.isLoading) return
      const question = this.$t("m.AI_Assistant_Hint_Question")
      this.messages.push({ role: "user", text: question })
      this.streamAnswer(question)
    },

    // v1: 질문 없이 요청하면 백엔드가 다음 단계 힌트를 생성
    requestStepHint() {
      if (this.isLoading || this.hintsExhausted) return
      this.streamAnswer(null)
    },

    async streamAnswer(question) {
      if (!this.problemID) return

      this.abortStream()
      const controller = new AbortController()
      this.abortController = controller
      this.isLoading = true

      // Vue 2 반응성을 위해 error 필드도 미리 선언
      const answer = {
        role: "assistant",
        text: "",
        thinking: true,
        error: false,
      }
      this.messages.push(answer)
      this.scrollToBottom()

      const fail = (message) => {
        answer.thinking = false
        answer.error = true
        answer.text = message || this.$t("m.AI_Assistant_Fetch_Failed")
      }

      try {
        await api.streamProblemLLMHint({
          problemID: this.problemID,
          contestID: this.contestID,
          code: this.code,
          question,
          signal: controller.signal,
          onEvent: (event, payload) => {
            if (event === "chunk") {
              answer.thinking = false
              answer.text += payload.text || ""
            } else if (event === "app-error") {
              fail(payload.message)
            }
            this.scrollToBottom()
          },
        })
        if (answer.thinking) fail()
      } catch {
        if (controller.signal.aborted) return
        fail()
      } finally {
        if (this.abortController === controller) {
          this.abortController = null
          this.isLoading = false
        }
        this.scrollToBottom()
      }
      // v1: 서버에 반영된 힌트 횟수와 맞추기 위해 다시 조회
      if (!this.isChatMode && !answer.error) this.fetchHistory()
    },

    abortStream() {
      if (!this.abortController) return
      this.abortController.abort()
      this.abortController = null
      this.isLoading = false
    },

    resizeInput() {
      const input = this.$refs.input
      if (!input) return
      input.style.height = "auto"
      input.style.height = `${Math.min(input.scrollHeight, 160)}px`
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const terminalBody = this.$refs.terminalBody
        if (!terminalBody) return
        terminalBody.scrollTop = terminalBody.scrollHeight
      })
    },

    // "[N단계]" + "▸ 라벨\n본문" 형식을 구조로 파싱 (스트리밍 중 부분 텍스트도 안전)
    parseHint(text) {
      const result = { level: null, sections: [], html: "" }
      if (!text) return result
      let rest = text
      const lv = rest.match(/^\s*\[(\d+)단계\]\s*/)
      if (lv) {
        result.level = Number(lv[1])
        rest = rest.slice(lv[0].length)
      }
      if (rest.indexOf("▸") !== -1) {
        rest
          .split("▸")
          .map((s) => s.trim())
          .filter((s) => s)
          .forEach((part) => {
            const nl = part.indexOf("\n")
            if (nl === -1) {
              result.sections.push({ label: part.trim(), text: "" })
            } else {
              result.sections.push({
                label: part.slice(0, nl).trim(),
                text: part.slice(nl + 1).trim(),
              })
            }
          })
      } else {
        result.html = renderMarkdown(rest.trim())
      }
      return result
    },

    sectionClass(label) {
      if (label.indexOf("진단") !== -1) return "sec-diagnosis"
      if (label.indexOf("점검") !== -1) return "sec-check"
      return "sec-hint"
    },
  },

  // 패널은 열릴 때마다 새로 마운트되므로, 마운트 시 최신 내역 불러오기
  mounted() {
    this.fetchHistory()
    this.$nextTick(() => this.$refs.input && this.$refs.input.focus())
  },

  beforeDestroy() {
    this.abortStream()
  },

  watch: {
    // 문제 ID가 바뀔 때 상태 초기화 및 새로운 문제 대화 내역 조회
    problemID() {
      this.abortStream()
      this.messages = []
      this.draft = ""
      this.fetchHistory()
    },
  },
}
</script>

<style scoped>
.ai-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* 코드 작성 헤더(container-header)와 같은 높이/모양 */
.ai-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex: 0 0 auto;
  height: 50px;
  padding: 0 10px 0 20px;
  margin-bottom: 10px;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background-color: var(--ps-content-color);
}

.ai-panel-title {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  font-size: medium;
  font-weight: bold;
}

.ai-panel-title img {
  width: 18px;
  height: 18px;
  filter: var(--ai-assistant-avatar-icon-filter);
}

.close-btn {
  color: var(--ai-assistant-close-text-color);
  font-size: 13px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  border: none;
  background: transparent;
}

.close-btn:hover {
  background-color: var(--ai-assistant-close-hover-bg);
  color: var(--ai-assistant-close-hover-text-color);
}

.ai-panel-content {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background: var(--ai-assistant-panel-bg);
  overflow: hidden;
}

.terminal-body {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 16px;
  overflow-y: auto;
}

/* 입력창 */
.ai-composer {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 0 12px 12px;
  padding: 10px 10px 8px 12px;
  border: 1px solid var(--ai-assistant-header-border-color);
  border-radius: 10px;
  background: var(--ai-assistant-header-bg);
  transition: border-color 0.15s;
}

.ai-composer:focus-within {
  border-color: var(--ai-assistant-focus-border-color);
}

.composer-input {
  width: 100%;
  min-height: 22px;
  max-height: 160px;
  resize: none;
  border: none;
  outline: none;
  background: transparent;
  color: var(--ai-assistant-bubble-text-color);
  font-family: inherit;
  font-size: 14px;
  line-height: 1.55;
}

.composer-input::placeholder {
  color: var(--ai-assistant-muted-text-color);
}

.composer-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.hint-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border: 1px solid var(--ai-assistant-header-border-color);
  border-radius: 99px;
  background: transparent;
  color: var(--ai-assistant-subtle-text-color);
  font-size: 12px;
  cursor: pointer;
  white-space: nowrap;
}

.hint-chip:hover:not(:disabled) {
  border-color: var(--ai-assistant-focus-border-color);
  color: var(--ai-assistant-bubble-text-color);
}

.hint-chip:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* v1: 단계 진행 스테퍼 */
.hint-stepper {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 0 0 auto;
  padding: 12px 16px 0;
}

.step-track {
  display: flex;
  gap: 4px;
  flex: 1;
}

.step-dot {
  flex: 1;
  height: 4px;
  border-radius: 2px;
  background: var(--ai-assistant-header-border-color);
}

.step-dot.done {
  background: var(--ai-assistant-send-bg);
}

.step-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--ai-assistant-subtle-text-color);
  white-space: nowrap;
}

/* v1: 힌트 요청 버튼 */
.hint-count {
  font-size: 12px;
  color: var(--ai-assistant-subtle-text-color);
}

.step-hint-btn {
  width: 100%;
  padding: 9px 14px;
  border: none;
  border-radius: 7px;
  background: var(--ai-assistant-send-bg);
  color: var(--ai-assistant-send-text-color);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.step-hint-btn:hover:not(:disabled) {
  background: var(--ai-assistant-send-hover-bg);
}

.step-hint-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.char-count {
  font-size: 11px;
  color: var(--ai-assistant-muted-text-color);
}

.send-btn {
  margin-left: auto;
  width: 30px;
  height: 30px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 50%;
  background: var(--ai-assistant-send-bg);
  color: var(--ai-assistant-send-text-color);
  font-size: 13px;
  cursor: pointer;
}

.send-btn:hover:not(:disabled) {
  background: var(--ai-assistant-send-hover-bg);
}

.send-btn:disabled {
  background: var(--ai-assistant-header-border-color);
  color: var(--ai-assistant-muted-text-color);
  cursor: not-allowed;
}

.ai-chat {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.chat-row--user {
  justify-content: flex-end;
}

.avatar {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  background-color: var(--ai-assistant-avatar-bg);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 7px;
}

.avatar img {
  width: 100%;
  height: 100%;
  filter: var(--ai-assistant-avatar-icon-filter);
}

.bubble {
  background: var(--ai-assistant-bubble-bg);
  border-radius: 0 12px 12px 12px;
  padding: 8px 12px;
  font-size: 14px;
  color: var(--ai-assistant-bubble-text-color);
  line-height: 1.6;
  max-width: 85%;
  white-space: pre-wrap;
  word-break: break-word;
}

.user-bubble {
  border-radius: 14px;
}

/* AI 답변은 말풍선 없이 본문처럼 표시 (아바타 높이에 맞춰 첫 줄 정렬) */
.hint-bubble,
.thinking-bubble,
.bubble.error {
  background: transparent;
  padding: 5px 0 0;
  border-radius: 0;
  max-width: none;
  flex: 1;
  min-width: 0;
}

.bubble.error {
  color: var(--ai-assistant-error-text-color);
}

.thinking-bubble {
  color: var(--ai-assistant-thinking-text-color);
  font-style: italic;
}

/* 첫 진입 온보딩 */
.ai-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 6px;
  padding: 16px 24px 8px;
}

.ai-empty-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: var(--ai-assistant-avatar-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 11px;
  margin-bottom: 2px;
}

.ai-empty-avatar img {
  width: 100%;
  height: 100%;
  filter: var(--ai-assistant-avatar-icon-filter);
}

.ai-empty-title {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  color: var(--ai-assistant-bubble-text-color);
}

.ai-empty-sub {
  margin: 0;
  max-width: 340px;
  font-size: 12.5px;
  line-height: 1.6;
  color: var(--ai-assistant-subtle-text-color);
}

/* 힌트 말풍선: 구조 요소 사이 여백이 pre-wrap으로 빈 줄처럼 보이지 않도록 normal */
.hint-bubble {
  white-space: normal;
}

/* 단계 배지 */
.hint-level-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  color: var(--ai-assistant-send-text-color);
  background: var(--ai-assistant-send-bg);
  padding: 2px 10px;
  border-radius: 99px;
  margin-bottom: 10px;
}

/* 힌트 섹션 (진단 / 힌트 / 점검 포인트) */
.hint-section {
  margin-bottom: 12px;
}

.hint-section:last-child {
  margin-bottom: 0;
}

.hint-section-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.02em;
  margin-bottom: 4px;
  color: var(--ai-assistant-subtle-text-color);
}

.hint-section-text {
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}

/* 점검 포인트 = 강조 콜아웃 */
.sec-check {
  background: var(--ai-assistant-callout-bg);
  border-left: 3px solid var(--ai-assistant-callout-border-color);
  padding: 8px 12px;
  border-radius: 0 8px 8px 0;
}

/* 마크다운 답변 (v-html 내용이라 /deep/ 필요) */
.hint-body {
  font-size: 14px;
  line-height: 1.65;
  overflow-wrap: anywhere;
}

.hint-body /deep/ > :first-child {
  margin-top: 0;
}

.hint-body /deep/ > :last-child {
  margin-bottom: 0;
}

.hint-body /deep/ p {
  margin: 0 0 10px;
}

.hint-body /deep/ h2,
.hint-body /deep/ h3 {
  margin: 16px 0 8px;
  font-weight: 700;
  line-height: 1.4;
  color: var(--ai-assistant-bubble-text-color);
}

.hint-body /deep/ h2 {
  font-size: 15px;
}

.hint-body /deep/ h3 {
  font-size: 14px;
}

.hint-body /deep/ ul,
.hint-body /deep/ ol {
  margin: 0 0 10px;
  padding-left: 20px;
}

.hint-body /deep/ ul {
  list-style: disc;
}

.hint-body /deep/ ol {
  list-style: decimal;
}

.hint-body /deep/ li {
  margin: 2px 0;
}

.hint-body /deep/ strong {
  font-weight: 700;
}

.hint-body /deep/ code {
  padding: 1px 5px;
  border-radius: 4px;
  background: var(--ai-assistant-bubble-bg);
  font-family: "Menlo", "Consolas", monospace;
  font-size: 12.5px;
}

.hint-body /deep/ pre {
  margin: 0 0 10px;
  padding: 10px 12px;
  border: 1px solid var(--ai-assistant-header-border-color);
  border-radius: 8px;
  background: var(--ai-assistant-bubble-bg);
  overflow-x: auto;
}

.hint-body /deep/ pre code {
  padding: 0;
  background: transparent;
  font-size: 12.5px;
  line-height: 1.55;
  white-space: pre;
}

.hint-body /deep/ blockquote {
  margin: 0 0 10px;
  padding-left: 10px;
  border-left: 3px solid var(--ai-assistant-callout-border-color);
  color: var(--ai-assistant-subtle-text-color);
}

.hint-body /deep/ hr {
  margin: 12px 0;
  border: none;
  border-top: 1px solid var(--ai-assistant-header-border-color);
}
</style>
