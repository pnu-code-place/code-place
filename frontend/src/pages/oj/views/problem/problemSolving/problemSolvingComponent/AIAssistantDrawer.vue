<template>
  <section
    class="ai-assistant-drawer"
    :class="{ 'dark-theme': isDarkMode }"
    :aria-label="$t('m.AI_Assistant')"
  >
    <!-- 패널 탭 헤더 -->
    <header class="drawer-header">
      <div class="header-tab">
        <span class="header-tab-icon">
          <img src="@/assets/images/AIAssistant.svg" alt="" />
        </span>
        <span class="header-title">{{ $t("m.AI_Assistant") }}</span>
      </div>

      <div class="header-actions">
        <!-- 로컬 전용 가짜 응답 모듈이 있을 때만 표시 -->
        <button
          v-if="mockAvailable"
          type="button"
          class="mock-toggle"
          :class="{ on: mockEnabled }"
          @click="toggleMock"
        >
          Mock {{ mockEnabled ? "ON" : "OFF" }}
        </button>
        <button
          type="button"
          class="header-icon-btn"
          :title="$t('m.AI_Assistant_New_Conversation')"
          :aria-label="$t('m.AI_Assistant_New_Conversation')"
          :disabled="isLoading"
          @click="resetConversation"
        >
          <i class="fas fa-redo-alt"></i>
        </button>
        <button
          type="button"
          class="header-icon-btn"
          :title="$t('m.AI_Assistant_Close')"
          :aria-label="$t('m.AI_Assistant_Close')"
          @click="close"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>
    </header>

    <!-- 대화 영역 -->
    <div ref="chatBody" class="drawer-body" @scroll="onBodyScroll">
      <div v-if="messages.length === 0 && !isLoading" class="empty-state">
        <div class="empty-avatar">
          <img src="@/assets/images/AIAssistant.svg" alt="" />
        </div>
        <p class="empty-title">{{ $t("m.AI_Assistant_Ask_Title") }}</p>
        <!-- 대회: 기존 단계별 힌트 방식 유지 -->
        <template v-if="isContestMode">
          <p class="empty-desc">{{ $t("m.AI_Assistant_Contest_Desc") }}</p>
          <ul class="empty-guide">
            <li>
              <i class="fas fa-lightbulb"></i
              >{{ $t("m.AI_Assistant_Contest_Guide_Approach") }}
            </li>
            <li>
              <i class="fas fa-bug"></i
              >{{ $t("m.AI_Assistant_Contest_Guide_Error") }}
            </li>
            <li>
              <i class="fas fa-stream"></i
              >{{ $t("m.AI_Assistant_Contest_Guide_Algorithm") }}
            </li>
          </ul>
        </template>
        <template v-else>
          <p class="empty-desc">{{ $t("m.AI_Assistant_General_Desc") }}</p>
          <ul class="empty-guide">
            <li>
              <i class="fas fa-lightbulb"></i
              >{{ $t("m.AI_Assistant_General_Guide_Start") }}
            </li>
            <li>
              <i class="fas fa-search"></i
              >{{ $t("m.AI_Assistant_General_Guide_Direction") }}
            </li>
            <li>
              <i class="fas fa-book"></i
              >{{ $t("m.AI_Assistant_General_Guide_Syntax") }}
            </li>
          </ul>
        </template>
      </div>

      <div v-else class="messages-list">
        <div
          v-for="(msg, index) in renderMessages"
          :key="msg.id || index"
          class="message-row"
          :class="msg.role === 'user' ? 'user-turn' : 'assistant-turn'"
        >
          <div
            v-if="msg.role === 'user'"
            class="user-bubble"
            v-text="msg.text"
          ></div>

          <template v-else>
            <div class="assistant-meta">
              <span
                class="assistant-avatar"
                :class="{ thinking: msg.thinking }"
              >
                <img src="@/assets/images/AIAssistant.svg" alt="" />
              </span>
              <span class="sender-name">{{ $t("m.AI_Assistant") }}</span>
              <span
                v-if="msg.parsed && msg.parsed.level"
                class="hint-level-badge"
              >
                {{
                  $t("m.AI_Assistant_Hint_Level", { level: msg.parsed.level })
                }}
              </span>
              <span v-if="msg.timeStr" class="timestamp">{{
                msg.timeStr
              }}</span>
            </div>

            <div v-if="msg.thinking" class="assistant-body thinking-content">
              <span class="typing-dots"><i></i><i></i><i></i></span>
              <span>{{ $t("m.AI_Assistant_Thinking") }}</span>
            </div>

            <div v-else-if="msg.error" class="assistant-body error-content">
              <i class="fas fa-exclamation-circle"></i>
              <span>{{ msg.text }}</span>
            </div>

            <!-- 정답 요구·문제와 무관한 질문 등에 대한 안내 -->
            <div v-else-if="msg.notice" class="assistant-body notice-content">
              <i class="fas fa-info-circle"></i>
              <span>{{ msg.text }}</span>
            </div>

            <!-- 일반 문제: 자유 질문형 답변 (마크다운) -->
            <div
              v-else-if="msg.html !== undefined"
              class="assistant-body markdown-body"
              v-html="msg.html"
            ></div>

            <!-- 대회: 기존 단계별 힌트 형식 -->
            <div v-else class="assistant-body">
              <template v-if="msg.parsed && msg.parsed.sections.length">
                <div
                  v-for="(sec, si) in msg.parsed.sections"
                  :key="si"
                  class="hint-section"
                  :class="sectionClass(sec.label)"
                >
                  <div class="hint-section-title">{{ sec.label }}</div>
                  <div
                    v-if="sec.text"
                    class="hint-section-text"
                    v-text="sec.text"
                  ></div>
                </div>
              </template>
              <div
                v-else
                class="hint-plain-text"
                v-text="msg.parsed ? msg.parsed.body : msg.text"
              ></div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- 입력 영역 -->
    <footer class="drawer-footer">
      <div
        class="input-box"
        :class="{ disabled: isLoading || hintsExhausted }"
        @click="focusInput"
      >
        <textarea
          ref="inputArea"
          v-model="questionInput"
          class="question-textarea"
          rows="1"
          :placeholder="
            hintsExhausted
              ? $t('m.AI_Assistant_Input_Exhausted')
              : $t('m.AI_Assistant_Input_Placeholder')
          "
          :disabled="isLoading || hintsExhausted"
          @keydown="handleKeydown"
          @compositionstart="isComposing = true"
          @compositionend="isComposing = false"
        ></textarea>

        <div class="input-controls">
          <span v-if="isAdminRole && questionLimit" class="usage-text">
            {{ $t("m.AI_Assistant_Admin_Unlimited") }}
          </span>
          <span
            v-else-if="questionLimit"
            class="usage-text"
            :class="{ exhausted: hintsExhausted }"
          >
            {{
              $t("m.AI_Assistant_Remaining", {
                remaining: problemHintsRemaining,
                limit: questionLimit,
              })
            }}
          </span>

          <span
            class="length-counter"
            :class="{ over: inputTooLong }"
            aria-live="polite"
          >
            {{ inputLength }}/{{ maxQuestionLength }}
          </span>

          <button
            type="button"
            class="send-btn"
            :class="{ active: canSend }"
            :disabled="!canSend"
            :title="$t('m.AI_Assistant_Send_Title')"
            :aria-label="$t('m.AI_Assistant_Send_Label')"
            @click.stop="handleSend"
          >
            <i v-if="isLoading" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-arrow-up"></i>
          </button>
        </div>
      </div>
      <p v-if="inputWarning" class="footer-hint warning">{{ inputWarning }}</p>
      <p v-else class="footer-hint">{{ $t("m.AI_Assistant_Shortcut_Hint") }}</p>
    </footer>
  </section>
</template>

<script>
import api from "@oj/api"
import { mapGetters } from "vuex"
import { renderAIMarkdown } from "./aiAssistantMarkdown"

// 로컬 전용 가짜 응답 모듈(aiAssistantMock.local.js). 저장소에 포함하지 않으며, 없으면 사용하지 않음
const localMock = (() => {
  if (process.env.NODE_ENV === "production") return null
  const context = require.context(
    "./",
    false,
    /^\.\/aiAssistantMock\.local\.js$/,
  )
  return context.keys().length ? context(context.keys()[0]) : null
})()

// 대회는 기존 5단계 힌트 정책 유지
const CONTEST_HINT_LIMIT = 5
// 일반 문제 질문 횟수. null 이면 제한 없음, 표시 안 함
const GENERAL_QUESTION_LIMIT = null
// 질문 최대 글자수
const MAX_QUESTION_LENGTH = 500

export default {
  name: "AIAssistantDrawer",
  props: {
    visible: {
      type: Boolean,
      default: false,
    },
    problemID: {
      type: String,
      default: "",
    },
    contestID: {
      type: [Number, String],
      default: null,
    },
    code: {
      type: String,
      default: "",
    },
  },
  data() {
    return {
      questionInput: "",
      isLoading: false,
      messages: [],
      eventSource: null,
      problemHintsUsed: 0,
      isComposing: false,
      // 사용자가 위로 스크롤해 읽는 중이면 스트리밍 중에도 강제로 내리지 않음
      stickToBottom: true,
      mockAvailable: !!localMock,
      mockEnabled: !!localMock && localMock.isAIMockEnabled(),
    }
  },
  computed: {
    ...mapGetters(["user", "isAdminRole", "isDarkMode"]),

    username() {
      return (
        (this.user && this.user.username) ||
        this.$t("m.AI_Assistant_Default_Username")
      )
    },

    userAvatar() {
      return (this.user && this.user.avatar) || null
    },

    isContestMode() {
      return !!this.contestID
    },

    questionLimit() {
      return this.isContestMode ? CONTEST_HINT_LIMIT : GENERAL_QUESTION_LIMIT
    },

    maxQuestionLength() {
      return MAX_QUESTION_LENGTH
    },

    problemHintsRemaining() {
      if (!this.questionLimit) return Infinity
      return Math.max(0, this.questionLimit - this.problemHintsUsed)
    },

    hintsExhausted() {
      if (this.isAdminRole) return false
      return this.problemHintsRemaining <= 0
    },

    inputLength() {
      return this.questionInput.trim().length
    },

    inputTooLong() {
      return this.inputLength > MAX_QUESTION_LENGTH
    },

    inputWarning() {
      if (this.inputTooLong) {
        return this.$t("m.AI_Assistant_Too_Long", { max: MAX_QUESTION_LENGTH })
      }
      return ""
    },

    canSend() {
      return (
        !this.hintsExhausted &&
        this.inputLength > 0 &&
        !this.inputTooLong &&
        !this.isLoading
      )
    },

    renderMessages() {
      return this.messages.map((m) => {
        if (m.role === "assistant" && !m.thinking && !m.error && !m.notice) {
          if (this.isContestMode) {
            return { ...m, parsed: this.parseHint(m.text) }
          }
          return { ...m, html: renderAIMarkdown(m.text) }
        }
        return m
      })
    },
  },
  watch: {
    visible(newVal) {
      if (newVal) {
        this.onOpen()
      } else {
        this.closeEventSource()
      }
    },
    problemID() {
      this.closeEventSource()
      this.isLoading = false
      this.messages = []
      this.problemHintsUsed = 0
      if (this.visible) {
        this.fetchHintHistory()
      }
    },
    questionInput() {
      this.$nextTick(this.adjustInputHeight)
    },
  },
  mounted() {
    if (this.visible) {
      this.onOpen()
    }
  },
  beforeDestroy() {
    this.closeEventSource()
  },
  methods: {
    onOpen() {
      this.fetchHintHistory()
      this.$nextTick(() => {
        this.adjustInputHeight()
        this.focusInput()
        this.scrollToBottom(true)
      })
    },

    adjustInputHeight() {
      this.$nextTick(() => {
        const el = this.$refs.inputArea
        if (!el) return

        const minHeight = 22
        const maxHeight = 160

        el.style.height = "auto"
        const scrollHeight = el.scrollHeight || 0
        el.style.height = `${Math.min(Math.max(scrollHeight, minHeight), maxHeight)}px`
        el.style.overflowY = scrollHeight > maxHeight ? "auto" : "hidden"
      })
    },

    close() {
      this.$emit("close")
    },

    toggleMock() {
      this.mockEnabled = !this.mockEnabled
      localMock.setAIMockEnabled(this.mockEnabled)
    },

    focusInput() {
      if (this.$refs.inputArea) {
        this.$refs.inputArea.focus()
      }
    },

    formatTime(date = new Date()) {
      const hours = String(date.getHours()).padStart(2, "0")
      const minutes = String(date.getMinutes()).padStart(2, "0")
      return `${hours}:${minutes}`
    },

    fetchHintHistory() {
      if (!this.problemID || this.contestID) return

      api
        .getAIHintHistory(this.problemID)
        .then((res) => {
          const data = res.data.data
          const logs = (data.logs || []).filter(
            (log) => log.hint_content && log.hint_content.trim() !== "",
          )
          this.problemHintsUsed = logs.length

          // 사용자가 새로 작성한 대화 내역이 없을 때만 히스토리로 초기 세팅
          const userMessages = this.messages.filter((m) => m.role === "user")
          if (userMessages.length === 0) {
            this.messages = logs.reduce((acc, log, idx) => {
              const timeStr = log.created_at
                ? this.formatTime(new Date(log.created_at))
                : ""
              // 질문이 함께 저장된 기록이면 질문-답변 한 쌍으로 표시
              if (log.question) {
                acc.push({
                  id: `history_q_${idx}`,
                  role: "user",
                  sender: this.username,
                  text: log.question,
                  isHistory: true,
                  timeStr,
                })
              }
              acc.push({
                id: `history_${idx}`,
                role: "assistant",
                sender: this.$t("m.AI_Assistant"),
                text: log.hint_content,
                error: false,
                thinking: false,
                notice: false,
                isHistory: true,
                timeStr,
              })
              return acc
            }, [])
          }
          this.scrollToBottom(true)
        })
        .catch((err) => {
          console.error("AI 조교 히스토리 로드 실패:", err)
        })
    },

    resetConversation() {
      if (this.isLoading) return
      this.closeEventSource()
      this.messages = []
      this.questionInput = ""
      this.adjustInputHeight()
      this.fetchHintHistory()
    },

    handleKeydown(e) {
      // 한글 IME 조합 중 Enter는 글자 확정용이므로 전송하지 않음
      if (this.isComposing || e.isComposing || e.keyCode === 229) return
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault()
        this.handleSend()
      }
    },

    handleSend() {
      const text = this.questionInput.trim()
      if (!this.canSend) return

      this.closeEventSource()
      this.isLoading = true
      this.questionInput = ""
      this.adjustInputHeight()

      const userMessage = {
        id: `user_${Date.now()}`,
        role: "user",
        sender: this.username,
        avatar: this.userAvatar,
        text: text,
        timeStr: this.formatTime(),
      }
      this.messages.push(userMessage)

      const assistantMessage = {
        id: `ai_${Date.now()}`,
        role: "assistant",
        sender: this.$t("m.AI_Assistant"),
        text: "",
        thinking: true,
        error: false,
        notice: false,
        timeStr: this.formatTime(),
      }
      this.messages.push(assistantMessage)
      this.scrollToBottom(true)

      const assistantIndex = this.messages.length - 1
      const useMock = this.mockEnabled

      // 실제 SSE 와 가짜 응답 모드가 같은 처리기를 사용
      const handlers = {
        chunk: (payload) => {
          if (this.messages[assistantIndex]) {
            if (this.messages[assistantIndex].thinking) {
              this.messages[assistantIndex].thinking = false
              this.messages[assistantIndex].text = payload.text || ""
            } else {
              this.messages[assistantIndex].text += payload.text || ""
            }
          }
          this.scrollToBottom()
        },
        // 정답 요구·무관한 질문 등에 대한 안내. 백엔드 미구현
        notice: (payload) => {
          if (this.messages[assistantIndex]) {
            this.messages[assistantIndex].thinking = false
            this.messages[assistantIndex].notice = true
            this.messages[assistantIndex].text = payload.message || ""
          }
          this.scrollToBottom()
        },
        "app-error": (payload) => {
          if (this.messages[assistantIndex]) {
            this.messages[assistantIndex].thinking = false
            this.messages[assistantIndex].error = true
            this.messages[assistantIndex].text =
              payload.message || this.$t("m.AI_Assistant_Fetch_Failed")
          }
          this.isLoading = false
          this.closeEventSource()
          this.scrollToBottom()
        },
        done: () => {
          this.isLoading = false
          this.closeEventSource()
          if (!useMock) this.fetchHintHistory()
        },
      }

      if (useMock) {
        this.eventSource = localMock.createMockStream(text, handlers)
        return
      }

      const streamUrl = api.getProblemLLMHintUrl(
        this.problemID,
        this.code,
        this.contestID,
        text,
      )
      const eventSource = new EventSource(streamUrl)
      this.eventSource = eventSource

      const parsePayload = (event) => {
        try {
          return JSON.parse(event.data)
        } catch (error) {
          return null
        }
      }

      eventSource.addEventListener("chunk", (event) => {
        const payload = parsePayload(event)
        if (payload) handlers.chunk(payload)
      })
      eventSource.addEventListener("notice", (event) => {
        handlers.notice(parsePayload(event) || {})
      })
      eventSource.addEventListener("app-error", (event) => {
        handlers["app-error"](parsePayload(event) || {})
      })
      eventSource.addEventListener("done", handlers.done)

      eventSource.onerror = () => {
        if (
          this.messages[assistantIndex] &&
          this.messages[assistantIndex].thinking
        ) {
          this.messages[assistantIndex].thinking = false
          this.messages[assistantIndex].error = true
          this.messages[assistantIndex].text = this.$t(
            "m.AI_Assistant_Fetch_Failed",
          )
        }
        this.isLoading = false
        this.closeEventSource()
        this.scrollToBottom()
      }
    },

    closeEventSource() {
      if (this.eventSource) {
        this.eventSource.close()
        this.eventSource = null
      }
    },

    onBodyScroll() {
      const body = this.$refs.chatBody
      if (!body) return
      this.stickToBottom =
        body.scrollHeight - body.scrollTop - body.clientHeight < 40
    },

    scrollToBottom(force = false) {
      if (force) this.stickToBottom = true
      if (!this.stickToBottom) return
      this.$nextTick(() => {
        const body = this.$refs.chatBody
        if (!body) return
        body.scrollTop = body.scrollHeight
      })
    },

    parseHint(text) {
      const result = { level: null, sections: [], body: "" }
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
        result.body = rest.trim()
      }
      return result
    },

    sectionClass(label) {
      if (label.indexOf("진단") !== -1) return "sec-diagnosis"
      if (label.indexOf("점검") !== -1) return "sec-check"
      return "sec-hint"
    },
  },
}
</script>

<style scoped lang="less">
.ai-assistant-drawer {
  width: 100%;
  height: 100%;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: var(--ps-content-color);
  border: 1px solid var(--border-color);
  border-radius: 7px;
  overflow: hidden;
  color: var(--ai-assistant-bubble-text-color);
}

/* 헤더 */
.drawer-header {
  flex: 0 0 auto;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 6px 0 12px;
  border-bottom: 1px solid var(--border-color);
  background: var(--ai-assistant-header-bg);
  user-select: none;
}

.header-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

.header-tab-icon {
  width: 20px;
  height: 20px;
  flex: 0 0 auto;
  border-radius: 5px;
  background-color: var(--ai-assistant-avatar-bg);
  display: inline-flex;
  align-items: center;
  justify-content: center;

  img {
    width: 13px;
    height: 13px;
    filter: var(--ai-assistant-avatar-icon-filter);
  }
}

.header-title {
  font-size: 14px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}

.mock-toggle {
  height: 22px;
  margin-right: 4px;
  padding: 0 8px;
  border: 1px dashed var(--ai-assistant-close-text-color);
  border-radius: 11px;
  background: transparent;
  color: var(--ai-assistant-muted-text-color);
  font-size: 10.5px;
  font-weight: 700;
  cursor: pointer;

  &.on {
    border-style: solid;
    border-color: var(--point-color, #5b64ed);
    color: var(--point-color, #5b64ed);
  }
}

.header-icon-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--ai-assistant-close-text-color);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  cursor: pointer;
  transition:
    background-color 0.15s,
    color 0.15s;

  &:hover:not(:disabled) {
    background-color: var(--ai-assistant-close-hover-bg);
    color: var(--ai-assistant-close-hover-text-color);
  }

  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
}

/* 대화 영역 */
.drawer-body {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 16px 14px;

  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background-color: var(--ai-assistant-header-border-color);
    border-radius: 6px;
  }
}

/* 빈 상태 */
.empty-state {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 16px 8px;
  user-select: none;
}

.empty-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background-color: var(--ai-assistant-avatar-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;

  img {
    width: 26px;
    height: 26px;
    filter: var(--ai-assistant-avatar-icon-filter);
  }
}

.empty-title {
  margin: 0 0 6px;
  font-size: 15px;
  font-weight: 700;
}

.empty-desc {
  margin: 0;
  max-width: 280px;
  font-size: 13px;
  line-height: 1.55;
  color: var(--ai-assistant-muted-text-color);
  word-break: keep-all;
}

.empty-guide {
  list-style: none;
  margin: 18px 0 0;
  padding: 0;
  width: 100%;
  max-width: 260px;
  display: flex;
  flex-direction: column;
  gap: 6px;

  li {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    font-size: 12.5px;
    color: var(--ai-assistant-subtle-text-color);
    text-align: left;
  }

  i {
    width: 14px;
    font-size: 12px;
    color: var(--ai-assistant-tab-active-color);
    text-align: center;
  }
}

/* 메시지 */
.messages-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-row {
  display: flex;
  flex-direction: column;
  min-width: 0;

  &.user-turn {
    align-items: flex-end;
  }

  &.assistant-turn {
    align-items: stretch;
  }
}

.user-bubble {
  max-width: 85%;
  padding: 8px 12px;
  border-radius: 14px 14px 4px 14px;
  background-color: var(--ai-assistant-subtle-bg);
  color: var(--ai-assistant-bubble-text-color);
  font-size: 13.5px;
  line-height: 1.55;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.assistant-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 12px;
  user-select: none;
}

.assistant-avatar {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  background-color: var(--ai-assistant-avatar-bg);
  display: inline-flex;
  align-items: center;
  justify-content: center;

  img {
    width: 14px;
    height: 14px;
    filter: var(--ai-assistant-avatar-icon-filter);
  }

  &.thinking {
    animation: pulse 1.4s infinite ease-in-out;
  }
}

.sender-name {
  font-weight: 700;
}

.hint-level-badge {
  padding: 1px 7px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  background-color: var(--ai-assistant-subtle-bg);
  color: var(--ai-assistant-tab-active-color);
}

.timestamp {
  margin-left: auto;
  font-size: 11px;
  color: var(--ai-assistant-muted-text-color);
}

.assistant-body {
  font-size: 13.5px;
  line-height: 1.65;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.hint-plain-text,
.hint-section-text {
  white-space: pre-wrap;
}

.hint-section {
  padding: 2px 0 2px 12px;
  border-left: 3px solid var(--ai-assistant-tab-active-color);

  & + & {
    margin-top: 12px;
  }

  &.sec-diagnosis {
    border-left-color: #e67e22;
  }
  &.sec-check {
    border-left-color: #27ae60;
  }
}

.hint-section-title {
  margin-bottom: 2px;
  font-size: 12.5px;
  font-weight: 700;
  color: var(--ai-assistant-muted-text-color);
}

.thinking-content {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--ai-assistant-thinking-text-color);
}

.typing-dots {
  display: inline-flex;
  gap: 3px;

  i {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background-color: currentColor;
    animation: typing 1.2s infinite ease-in-out;

    &:nth-child(2) {
      animation-delay: 0.15s;
    }
    &:nth-child(3) {
      animation-delay: 0.3s;
    }
  }
}

.error-content {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  background-color: rgba(192, 57, 43, 0.08);
  color: var(--ai-assistant-error-text-color);

  i {
    margin-top: 4px;
  }
}

.notice-content {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  background-color: var(--ai-assistant-subtle-bg);
  color: var(--ai-assistant-subtle-text-color);

  i {
    margin-top: 4px;
    color: var(--ai-assistant-tab-active-color);
  }
}

/* 자유 질문형 답변 (마크다운) */
.markdown-body {
  // 전역 마크다운 스타일(styles/markdown.less)의 글자 크기·점선 테두리를 덮어씀
  /deep/ p,
  /deep/ ul,
  /deep/ ol {
    font-size: inherit;
    line-height: inherit;
  }

  /deep/ p {
    margin: 0;

    & + p,
    & + ul,
    & + ol,
    & + .code-block,
    & + h4 {
      margin-top: 8px;
    }
  }

  /deep/ h4 {
    margin: 12px 0 4px;
    font-size: 13.5px;
    font-weight: 700;
  }

  /deep/ ul,
  /deep/ ol {
    margin: 6px 0 0;
    padding-left: 20px;

    & + p {
      margin-top: 8px;
    }
  }

  /deep/ li + li {
    margin-top: 2px;
  }

  /deep/ ul li {
    list-style: disc;
  }

  /deep/ ol li {
    list-style: decimal;
  }

  /deep/ strong {
    font-weight: 700;
  }

  /deep/ em {
    font-style: italic;
  }

  /deep/ a {
    color: var(--point-color, #5b64ed);
    text-decoration: underline;
    word-break: break-all;
  }

  /deep/ li > ul,
  /deep/ li > ol {
    margin-top: 2px;
  }

  /deep/ ul ul li {
    list-style: circle;
  }

  /deep/ blockquote {
    margin: 8px 0;
    padding: 2px 0 2px 10px;
    border-left: 3px solid var(--border-color);
    color: var(--ai-assistant-muted-text-color);
  }

  /deep/ hr {
    margin: 12px 0;
    border: none;
    border-top: 1px solid var(--border-color);
  }

  /deep/ .table-wrap {
    margin: 8px 0;
    overflow-x: auto;
  }

  /deep/ table {
    border-collapse: collapse;
    font-size: 12.5px;
    white-space: nowrap;
  }

  /deep/ th,
  /deep/ td {
    padding: 5px 10px;
    border: 1px solid var(--border-color);
    text-align: left;
  }

  /deep/ th {
    font-weight: 700;
    background-color: var(--ai-assistant-subtle-bg);
  }

  /deep/ code {
    padding: 1px 5px;
    border-radius: 4px;
    background-color: var(--ai-assistant-subtle-bg);
    font-family: "JetBrains Mono", "Menlo", "Monaco", "Consolas", monospace;
    font-size: 12.5px;
  }

  /deep/ .code-block {
    position: relative;
    margin: 8px 0;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    background-color: var(--ai-assistant-thinking-bg);
    overflow: hidden;

    & + p {
      margin-top: 8px;
    }
  }

  /deep/ .code-lang {
    position: absolute;
    top: 4px;
    right: 8px;
    font-size: 10.5px;
    color: var(--ai-assistant-muted-text-color);
    user-select: none;
  }

  /deep/ pre {
    margin: 0;
    padding: 10px 12px;
    border: none;
    border-radius: 0;
    overflow-x: auto;
    background: transparent;
    white-space: pre;
    word-break: normal;
    overflow-wrap: normal;

    code {
      padding: 0;
      border-radius: 0;
      background: transparent;
      font-size: 12.5px;
      line-height: 1.55;
    }
  }
}

/* 다크 모드: 전역 코드 강조 테마(밝은 테마) 색을 덮어씀 */
.dark-theme .markdown-body {
  /deep/ .hljs {
    color: #d4d4d4;
  }
  /deep/ .hljs-keyword,
  /deep/ .hljs-built_in,
  /deep/ .hljs-meta {
    color: #c586c0;
  }
  /deep/ .hljs-string {
    color: #ce9178;
  }
  /deep/ .hljs-number,
  /deep/ .hljs-literal {
    color: #b5cea8;
  }
  /deep/ .hljs-comment {
    color: #6a9955;
  }
  /deep/ .hljs-title,
  /deep/ .hljs-function {
    color: #dcdcaa;
  }
  /deep/ .hljs-type,
  /deep/ .hljs-class {
    color: #4ec9b0;
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes typing {
  0%,
  80%,
  100% {
    opacity: 0.3;
    transform: translateY(0);
  }
  40% {
    opacity: 1;
    transform: translateY(-2px);
  }
}

/* 입력 영역 */
.drawer-footer {
  flex: 0 0 auto;
  padding: 0 12px 10px;
}

.input-box {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px 10px 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background-color: var(--ps-content-color);
  cursor: text;
  transition:
    border-color 0.15s,
    box-shadow 0.15s;

  &:focus-within {
    border-color: var(--submission-primary-btn-bg);
    box-shadow: 0 0 0 1px var(--submission-primary-btn-bg);
  }

  &.disabled {
    background-color: var(--ai-assistant-thinking-bg);
    cursor: default;
  }
}

.question-textarea {
  display: block;
  width: 100%;
  min-height: 22px;
  max-height: 160px;
  padding: 0;
  border: none;
  outline: none;
  resize: none;
  overflow-y: hidden;
  background: transparent;
  color: inherit;
  font-family: inherit;
  font-size: 13.5px;
  line-height: 22px;

  &::placeholder {
    color: var(--ai-assistant-muted-text-color);
    opacity: 0.8;
  }

  &:disabled {
    cursor: not-allowed;
  }

  &::-webkit-scrollbar {
    width: 4px;
  }
  &::-webkit-scrollbar-thumb {
    background-color: var(--ai-assistant-header-border-color);
    border-radius: 4px;
  }
}

.input-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.usage-text {
  font-size: 11.5px;
  color: var(--ai-assistant-muted-text-color);
  white-space: nowrap;
  user-select: none;

  &.exhausted {
    color: var(--ai-assistant-error-text-color);
  }
}

.length-counter {
  margin-left: auto;
  font-size: 11px;
  color: var(--ai-assistant-muted-text-color);
  white-space: nowrap;
  user-select: none;
  font-variant-numeric: tabular-nums;

  &.over {
    color: var(--ai-assistant-error-text-color);
    font-weight: 600;
  }
}

.send-btn {
  width: 28px;
  height: 28px;
  flex: 0 0 auto;
  border: none;
  border-radius: 8px;
  background-color: var(--ai-assistant-subtle-bg);
  color: var(--ai-assistant-muted-text-color);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  cursor: not-allowed;
  transition:
    background-color 0.15s,
    color 0.15s;

  &.active {
    background-color: var(--submission-primary-btn-bg);
    color: var(--submission-primary-btn-text-color);
    cursor: pointer;

    &:hover {
      background-color: var(--submission-primary-btn-hover-bg);
    }
  }
}

.footer-hint {
  margin: 6px 0 0;
  text-align: center;
  font-size: 11px;
  color: var(--ai-assistant-muted-text-color);
  opacity: 0.8;
  user-select: none;

  &.warning {
    color: var(--ai-assistant-error-text-color);
    opacity: 1;
  }
}
</style>
