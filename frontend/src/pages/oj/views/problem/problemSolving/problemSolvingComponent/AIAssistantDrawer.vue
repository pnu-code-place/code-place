<template>
  <section
    class="ai-assistant-drawer"
    :class="{ 'dark-theme': isDarkMode }"
    :aria-label="$t('m.AI_Assistant_Name')"
  >
    <!-- 패널 탭 헤더 -->
    <header class="drawer-header">
      <div class="header-tab">
        <span class="header-tab-icon">
          <img src="@/assets/images/AIAssistant.svg" alt="" />
        </span>
        <span class="header-title">{{ $t("m.AI_Assistant_Name") }}</span>
      </div>

      <div class="header-actions">
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
        <div class="empty-bubble" aria-live="polite">
          <transition name="bubble-swap" mode="out-in">
            <span :key="bubbleIndex">{{ bubbleLines[bubbleIndex] }}</span>
          </transition>
        </div>
        <div class="empty-avatar">
          <img src="@/assets/images/AIAssistant.svg" alt="" />
        </div>
        <p class="empty-title">{{ $t("m.AI_Assistant_Empty_Welcome") }}</p>
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
              <span class="sender-name">{{ $t("m.AI_Assistant_Name") }}</span>
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
              {{ msg.text }}
            </div>

            <div
              v-else
              class="assistant-body markdown-body"
              :class="{ 'stage-hint': msg.parsed }"
              v-html="msg.html"
            ></div>
          </template>
        </div>
      </div>
    </div>

    <!-- 입력 영역 -->
    <footer class="drawer-footer">
      <!-- 대회 단계 힌트 -->
      <div v-if="isContestMode" class="stage-box">
        <span v-if="isAdminRole" class="stage-count">
          {{ $t("m.AI_Assistant_Admin_Unlimited") }}
        </span>
        <span v-else class="stage-count" :class="{ exhausted: hintsExhausted }">
          {{
            $t("m.AI_Assistant_Remaining", {
              remaining: problemHintsRemaining,
              limit: questionLimit,
            })
          }}
        </span>
        <button
          type="button"
          class="hint-btn"
          :disabled="!canSend"
          @click="handleSend"
        >
          <i v-if="isLoading" class="fas fa-spinner fa-spin"></i>
          <i v-else class="fas fa-lightbulb"></i>
          <span>
            {{
              isLoading
                ? $t("m.AI_Assistant_Thinking")
                : hintsExhausted
                  ? $t("m.AI_Assistant_Exhausted")
                  : $t("m.AI_Assistant_Get_Hint")
            }}
          </span>
        </button>
      </div>

      <!-- 일반 문제 자유 질문 -->
      <template v-else>
        <div
          class="input-box"
          :class="{ disabled: isLoading || hintsExhausted }"
          @click="focusInput"
        >
          <textarea
            ref="inputArea"
            :value="questionInput"
            class="question-textarea"
            rows="1"
            :placeholder="
              hintsExhausted
                ? $t('m.AI_Assistant_Input_Exhausted')
                : $t('m.AI_Assistant_Input_Placeholder')
            "
            :disabled="isLoading || hintsExhausted"
            @input="questionInput = $event.target.value"
            @keydown="handleKeydown"
            @compositionstart="isComposing = true"
            @compositionend="isComposing = false"
          ></textarea>

          <div class="input-controls">
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
        <p v-if="inputWarning" class="footer-hint warning">
          {{ inputWarning }}
        </p>
      </template>
    </footer>
  </section>
</template>

<script>
import api from "@oj/api"
import { mapGetters } from "vuex"
import { renderAIMarkdown } from "./aiAssistantMarkdown"
import { aiHintErrorText } from "./aiAssistantErrors"

const CONTEST_HINT_LIMIT = 5
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
    language: {
      type: String,
      default: "",
    },
  },
  data() {
    return {
      questionInput: "",
      isLoading: false,
      messages: [],
      activeStream: null,
      problemHintsUsed: 0,
      isComposing: false,
      // 위로 스크롤해 읽는 중이면 자동 스크롤 중지
      stickToBottom: true,
      bubbleIndex: 0,
      bubbleTimer: null,
    }
  },
  computed: {
    ...mapGetters(["user", "isAdminRole", "isDarkMode"]),

    isContestMode() {
      return !!this.contestID
    },

    bubbleLines() {
      const keys = this.isContestMode
        ? ["Contest_Bubble_1", "Contest_Bubble_2", "Contest_Bubble_3"]
        : ["Bubble_1", "Bubble_2", "Bubble_3"]
      return keys.map((k) => this.$t(`m.AI_Assistant_Empty_${k}`))
    },

    // 일반 문제는 횟수 제한 없음
    questionLimit() {
      return this.isContestMode ? CONTEST_HINT_LIMIT : null
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
      if (this.hintsExhausted || this.isLoading) return false
      if (this.isContestMode) return true
      return this.inputLength > 0 && !this.inputTooLong
    },

    renderMessages() {
      return this.messages.map((m) => {
        if (m.role === "assistant" && !m.thinking && !m.error) {
          if (this.isContestMode) {
            const parsed = this.parseHint(m.text)
            return {
              ...m,
              parsed,
              html: renderAIMarkdown(this.hintToMarkdown(parsed)),
            }
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
        this.closeStream()
      }
    },
    problemID() {
      this.closeStream()
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
    this.startBubble()
  },
  beforeDestroy() {
    this.closeStream()
    this.stopBubble()
  },
  methods: {
    // 빈 화면 말풍선 문구 순환
    startBubble() {
      this.stopBubble()
      const reduceMotion =
        window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches
      if (reduceMotion) return
      this.bubbleTimer = setInterval(() => {
        this.bubbleIndex = (this.bubbleIndex + 1) % this.bubbleLines.length
      }, 3200)
    },

    stopBubble() {
      if (this.bubbleTimer) {
        clearInterval(this.bubbleTimer)
        this.bubbleTimer = null
      }
    },

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

        const minHeight = 48
        const maxHeight = 200

        el.style.height = "auto"
        const scrollHeight = el.scrollHeight || 0
        el.style.height = `${Math.min(Math.max(scrollHeight, minHeight), maxHeight)}px`
        el.style.overflowY = scrollHeight > maxHeight ? "auto" : "hidden"
      })
    },

    close() {
      this.$emit("close")
    },

    focusInput() {
      if (this.$refs.inputArea) {
        this.$refs.inputArea.focus()
      }
    },

    // 입력창 재활성화 뒤 포커스
    refocusInput() {
      this.$nextTick(() => this.focusInput())
    },

    formatTime(date = new Date()) {
      const hours = String(date.getHours()).padStart(2, "0")
      const minutes = String(date.getMinutes()).padStart(2, "0")
      return `${hours}:${minutes}`
    },

    fetchHintHistory() {
      if (!this.problemID) return

      api
        .getAIHintHistory(this.problemID, this.contestID)
        .then((res) => {
          const data = res.data.data
          const logs = (data.logs || []).filter(
            (log) => log.hint_content && log.hint_content.trim() !== "",
          )
          this.problemHintsUsed = logs.length

          // 이번에 주고받은 대화가 없을 때만 기록으로 채움
          const hasLiveMessages = this.messages.some(
            (m) => !m.id.startsWith("history"),
          )
          if (!hasLiveMessages) {
            this.messages = logs.reduce((acc, log, idx) => {
              const timeStr = log.created_at
                ? this.formatTime(new Date(log.created_at))
                : ""
              if (log.student_question) {
                acc.push({
                  id: `history_q_${idx}`,
                  role: "user",
                  text: log.student_question,
                  timeStr,
                })
              }
              acc.push({
                id: `history_${idx}`,
                role: "assistant",
                text: log.hint_content,
                error: false,
                thinking: false,
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

    handleKeydown(e) {
      // IME 조합 중 Enter 무시
      if (this.isComposing || e.isComposing || e.keyCode === 229) return
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault()
        this.handleSend()
      }
    },

    handleSend() {
      if (!this.canSend) return
      const text = this.questionInput.trim()

      this.closeStream()
      this.isLoading = true

      // 대회는 질문 없이 다음 단계 힌트만 요청
      if (!this.isContestMode) {
        this.questionInput = ""
        this.adjustInputHeight()
        this.messages.push({
          id: `user_${Date.now()}`,
          role: "user",
          text: text,
          timeStr: this.formatTime(),
        })
      }

      const assistantMessage = {
        id: `ai_${Date.now()}`,
        role: "assistant",
        text: "",
        thinking: true,
        error: false,
        timeStr: this.formatTime(),
      }
      this.messages.push(assistantMessage)
      this.scrollToBottom(true)

      const assistantIndex = this.messages.length - 1

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
        "app-error": (payload) => {
          if (this.messages[assistantIndex]) {
            this.messages[assistantIndex].thinking = false
            this.messages[assistantIndex].error = true
            this.messages[assistantIndex].text = aiHintErrorText(this, payload)
          }
          if (payload.error === "problem-limit-exceeded") {
            this.problemHintsUsed = this.questionLimit || this.problemHintsUsed
          }
          this.isLoading = false
          this.closeStream()
          this.refocusInput()
          this.scrollToBottom()
        },
        done: () => {
          this.isLoading = false
          this.closeStream()
          this.refocusInput()
          this.fetchHintHistory()
        },
        // done 없이 연결이 끊긴 경우
        failure: () => {
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
          this.closeStream()
          this.refocusInput()
          this.scrollToBottom()
        },
      }

      // 일반 문제 자유 질문
      if (!this.isContestMode) {
        this.activeStream = api.chatAIHint(
          {
            problemID: this.problemID,
            question: text,
            code: this.code,
            language: this.language,
          },
          handlers,
        )
        return
      }

      // 대회 5단계 힌트
      this.activeStream = api.stageAIHint(
        {
          problemID: this.problemID,
          code: this.code,
          contestID: this.contestID,
        },
        handlers,
      )
    },

    closeStream() {
      if (this.activeStream) {
        this.activeStream.close()
        this.activeStream = null
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

    // 단계 힌트 구역을 번호 이모지 제목과 본문으로 변환
    hintToMarkdown(parsed) {
      if (!parsed.sections.length) return parsed.body
      const keycaps = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
      return parsed.sections
        .map((sec, i) => {
          const title = `### ${keycaps[i] || `${i + 1}.`} ${sec.label}`
          return sec.text ? `${title}\n\n${sec.text}` : title
        })
        .join("\n\n")
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
  gap: 7px;
  min-width: 0;
}

.header-tab-icon {
  width: 22px;
  height: 22px;
  flex: 0 0 auto;
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
}

.header-title {
  font-size: 15px;
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

.empty-bubble {
  position: relative;
  max-width: 240px;
  margin-bottom: 14px;
  padding: 9px 14px;
  border-radius: 14px;
  background-color: var(--ai-assistant-subtle-bg);
  color: var(--ai-assistant-bubble-text-color);
  font-size: 13px;
  line-height: 1.5;
  word-break: keep-all;

  &::after {
    content: "";
    position: absolute;
    left: 50%;
    bottom: -6px;
    width: 12px;
    height: 12px;
    background-color: var(--ai-assistant-subtle-bg);
    border-radius: 2px;
    transform: translateX(-50%) rotate(45deg);
  }
}

.bubble-swap-enter-active,
.bubble-swap-leave-active {
  transition:
    opacity 0.25s ease,
    transform 0.25s ease;
}

.bubble-swap-enter {
  opacity: 0;
  transform: translateY(4px);
}

.bubble-swap-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.empty-avatar {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background-color: var(--ai-assistant-avatar-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
  animation: bob 3s ease-in-out infinite;

  img {
    width: 34px;
    height: 34px;
    filter: var(--ai-assistant-avatar-icon-filter);
  }
}

.empty-title {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
}

@keyframes bob {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .empty-avatar {
    animation: none;
  }
}

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

  // 대회는 답변만 이어지므로 답변 사이를 선으로 구분
  &.assistant-turn + &.assistant-turn {
    margin-top: 8px;
    padding-top: 24px;
    border-top: 1px solid var(--border-color);
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
  width: 26px;
  height: 26px;
  border-radius: 7px;
  background-color: var(--ai-assistant-avatar-bg);
  display: inline-flex;
  align-items: center;
  justify-content: center;

  img {
    width: 17px;
    height: 17px;
    filter: var(--ai-assistant-avatar-icon-filter);
  }

  &.thinking {
    animation: pulse 1.4s infinite ease-in-out;
  }
}

.sender-name {
  font-size: 14px;
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
  color: var(--ai-assistant-subtle-text-color);
}

/* 자유 질문형 답변 (마크다운) */
.markdown-body {
  // 전역 마크다운 스타일 덮어씀
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
    margin: 14px 0 4px;
    font-size: 14px;
    font-weight: 700;

    &:first-child {
      margin-top: 0;
    }
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

  // 대회 단계 힌트, 구역 간격
  &.stage-hint {
    /deep/ h4 {
      margin: 20px 0 6px;
      font-size: 15px;

      &:first-child {
        margin-top: 2px;
      }
    }

    /deep/ p {
      line-height: 1.75;
    }
  }

  // 긴 수식 가로 스크롤
  /deep/ .katex-display {
    margin: 8px 0;
    overflow-x: auto;
    overflow-y: hidden;
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

  // 언어 이름은 코드 위 머리줄에 표시
  /deep/ .code-lang {
    display: block;
    padding: 4px 12px;
    border-bottom: 1px solid var(--border-color);
    font-size: 10.5px;
    line-height: 1.6;
    text-align: right;
    color: var(--ai-assistant-muted-text-color);
    user-select: none;
  }

  /deep/ pre {
    margin: 0;
    padding: 10px 12px;
    border: none;
    border-radius: 0;
    overflow-x: auto;

    // 스크롤할 때 뜨는 가로 스크롤바가 마지막 줄을 가리지 않게 아래 여백
    padding-bottom: 16px;
    background: transparent;
    white-space: pre;
    word-break: normal;
    overflow-wrap: normal;

    // 코드 강조 기본 스타일의 안쪽 스크롤 끄기, 바깥 pre 만 스크롤
    code {
      display: inline;
      overflow: visible;
      padding: 0;
      border-radius: 0;
      background: transparent;
      font-size: 12.5px;
      line-height: 1.55;
    }
  }
}

/* 코드 강조 색, VS Code 기본 테마 색 */
.markdown-body {
  /deep/ .hljs {
    color: #1f1f1f;
  }
  /deep/ .hljs-keyword,
  /deep/ .hljs-literal,
  /deep/ .hljs-selector-tag {
    color: #0000ff;
  }
  /deep/ .hljs-meta,
  /deep/ .hljs-meta .hljs-keyword {
    color: #af00db;
  }
  /deep/ .hljs-built_in,
  /deep/ .hljs-title,
  /deep/ .hljs-title.function_,
  /deep/ .hljs-function .hljs-title {
    color: #795e26;
  }
  /deep/ .hljs-type,
  /deep/ .hljs-class .hljs-title,
  /deep/ .hljs-title.class_ {
    color: #267f99;
  }
  /deep/ .hljs-params,
  /deep/ .hljs-variable,
  /deep/ .hljs-attr,
  /deep/ .hljs-property {
    color: #001080;
  }
  /deep/ .hljs-string,
  /deep/ .hljs-meta .hljs-string {
    color: #a31515;
  }
  /deep/ .hljs-number {
    color: #098658;
  }
  /deep/ .hljs-comment {
    color: #008000;
    font-style: normal;
  }
  /deep/ .hljs-operator,
  /deep/ .hljs-punctuation {
    color: #1f1f1f;
  }
}

.dark-theme .markdown-body {
  /deep/ .hljs {
    color: #d4d4d4;
  }
  /deep/ .hljs-keyword,
  /deep/ .hljs-literal,
  /deep/ .hljs-selector-tag {
    color: #569cd6;
  }
  /deep/ .hljs-meta,
  /deep/ .hljs-meta .hljs-keyword {
    color: #c586c0;
  }
  /deep/ .hljs-built_in,
  /deep/ .hljs-title,
  /deep/ .hljs-title.function_,
  /deep/ .hljs-function .hljs-title {
    color: #dcdcaa;
  }
  /deep/ .hljs-type,
  /deep/ .hljs-class .hljs-title,
  /deep/ .hljs-title.class_ {
    color: #4ec9b0;
  }
  /deep/ .hljs-params,
  /deep/ .hljs-variable,
  /deep/ .hljs-attr,
  /deep/ .hljs-property {
    color: #9cdcfe;
  }
  /deep/ .hljs-string,
  /deep/ .hljs-meta .hljs-string {
    color: #ce9178;
  }
  /deep/ .hljs-number {
    color: #b5cea8;
  }
  /deep/ .hljs-comment {
    color: #6a9955;
    font-style: normal;
  }
  /deep/ .hljs-operator,
  /deep/ .hljs-punctuation {
    color: #d4d4d4;
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

/* 대회 단계 힌트 */
.stage-box {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 2px 0;
}

.stage-count {
  flex: 0 0 auto;
  padding: 7px 12px;
  border-radius: 999px;
  background-color: var(--ai-assistant-subtle-bg);
  color: var(--ai-assistant-subtle-text-color);
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
  user-select: none;

  &.exhausted {
    color: var(--ai-assistant-error-text-color);
  }
}

.hint-btn {
  flex: 1 1 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 11px 16px;
  border: none;
  border-radius: 10px;
  background-color: var(--submission-primary-btn-bg);
  color: var(--submission-primary-btn-text-color);
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
  cursor: pointer;
  transition: background-color 0.15s;

  i {
    font-size: 12px;
  }

  &:hover:not(:disabled) {
    background-color: var(--submission-primary-btn-hover-bg);
  }

  &:disabled {
    background-color: var(--ai-assistant-subtle-bg);
    color: var(--ai-assistant-muted-text-color);
    cursor: not-allowed;
  }
}

.input-box {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 12px 10px 14px;
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
  min-height: 48px;
  max-height: 200px;
  padding: 0;
  border: none;
  outline: none;
  resize: none;
  overflow-y: hidden;
  background: transparent;
  color: inherit;
  font-family: inherit;
  font-size: 14px;
  line-height: 24px;

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
