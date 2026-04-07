<template>
  <div v-show="visible" class="editor-container">
    <div class="divider" @mousedown="startDrag"></div>

    <div class="editor-bottom">
      <!-- 탭 헤더 -->
      <div class="tab-header">
        <div class="tab-left">
          <span :class="{ active: tab === 'result' }" @click="tab = 'result'"
            >실행 결과</span
          >
          <span :class="{ active: tab === 'ai' }" @click="tab = 'ai'"
            >AI 조교</span
          >
        </div>
        <div class="tab-right-group">
          <div class="tab-right" v-if="tab === 'ai'">
            <span class="hint-count">
              남은 횟수 : [문제: {{ problemHintsRemaining }}/5 · 전체:
              {{ dailyHintsRemaining }}/30]
            </span>
            <button
              class="hint-btn"
              @click="requestHint"
              :disabled="isLoading || hintsExhausted"
            >
              {{
                isLoading
                  ? "생각 중..."
                  : hintsExhausted
                    ? "횟수 초과"
                    : "AI조교 힌트받기"
              }}
            </button>
          </div>
          <button
            type="button"
            class="close-btn"
            aria-label="AI 조교 닫기"
            @click="visible = false"
          >
            ✕
          </button>
        </div>
      </div>

      <!-- 내용 -->
      <div ref="terminalBody" class="terminal-body">
        <!-- AI 조교 탭 -->
        <div v-if="tab === 'ai'" class="ai-chat">
          <div v-if="contestID" class="empty-message">
            AI 조교는 공개 문제에서만 사용할 수 있습니다.
          </div>
          <div v-for="(msg, i) in messages" :key="i" class="chat-row">
            <div class="avatar" :class="{ thinking: msg.thinking }">
              <img src="@/assets/images/AIAssistant.svg" alt="AI" />
            </div>
            <div
              v-if="msg.thinking"
              class="bubble thinking-bubble"
              v-text="'생각 중...'"
            ></div>
            <div
              v-else
              class="bubble"
              :class="{ error: msg.error }"
              v-text="msg.text"
            ></div>
          </div>
        </div>

        <!-- 실행 결과 탭 -->
        <div v-else class="result-message">실행 결과가 여기에 표시됩니다.</div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@oj/api"

export default {
  props: {
    result: Object,
    problemID: String,
    contestID: [Number, String],
  },

  data() {
    return {
      visible: false,
      tab: "ai",
      isDragging: false,
      isLoading: false,
      messages: [],
      eventSource: null,
      hintUsage: {
        date: "",
        dailyCount: 0,
        problems: {},
      },
    }
  },

  computed: {
    problemHintsUsed() {
      return this.hintUsage.problems[this.problemID] || 0
    },
    problemHintsRemaining() {
      return Math.max(0, 5 - this.problemHintsUsed)
    },
    dailyHintsRemaining() {
      return Math.max(0, 30 - this.hintUsage.dailyCount)
    },
    hintsExhausted() {
      return this.problemHintsRemaining <= 0 || this.dailyHintsRemaining <= 0
    },
  },

  methods: {
    loadHintUsage() {
      const today = new Date().toISOString().slice(0, 10)
      const saved = JSON.parse(localStorage.getItem("aiHintUsage") || "{}")
      if (saved.date === today) {
        this.hintUsage = saved
      } else {
        this.hintUsage = { date: today, dailyCount: 0, problems: {} }
        this.saveHintUsage()
      }
    },

    saveHintUsage() {
      localStorage.setItem("aiHintUsage", JSON.stringify(this.hintUsage))
    },

    incrementHintCount() {
      const today = new Date().toISOString().slice(0, 10)
      if (this.hintUsage.date !== today) {
        this.hintUsage = { date: today, dailyCount: 0, problems: {} }
      }
      this.hintUsage.dailyCount += 1
      this.hintUsage.problems[this.problemID] =
        (this.hintUsage.problems[this.problemID] || 0) + 1
      this.saveHintUsage()
    },

    show() {
      this.visible = true
      this.tab = "ai"
      this.scrollToBottom()
    },

    requestHint() {
      if (this.isLoading || !this.problemID || this.hintsExhausted) return
      if (this.contestID) {
        this.messages.push({
          text: "AI 조교는 공개 문제에서만 지원됩니다.",
          error: true,
        })
        this.scrollToBottom()
        return
      }

      this.closeEventSource()
      this.isLoading = true
      this.messages.push({ text: "", thinking: true })
      this.scrollToBottom()
      const thinkingIndex = this.messages.length - 1

      const eventSource = new EventSource(
        api.getProblemLLMHintUrl(this.problemID),
      )
      this.eventSource = eventSource

      eventSource.addEventListener("chunk", (event) => {
        let payload
        try {
          payload = JSON.parse(event.data)
        } catch (error) {
          return
        }

        if (
          this.messages[thinkingIndex] &&
          this.messages[thinkingIndex].thinking
        ) {
          this.messages.splice(thinkingIndex, 1, {
            text: payload.text || "",
            error: false,
          })
          this.scrollToBottom()
          return
        }

        if (this.messages[thinkingIndex]) {
          this.messages[thinkingIndex].text += payload.text || ""
          this.scrollToBottom()
        }
      })

      eventSource.addEventListener("app-error", (event) => {
        let payload
        try {
          payload = JSON.parse(event.data)
        } catch (error) {
          payload = { message: "AI 힌트를 불러오지 못했습니다." }
        }

        this.messages.splice(thinkingIndex, 1, {
          text: payload.message || "AI 힌트를 불러오지 못했습니다.",
          error: true,
        })
        this.scrollToBottom()
        this.isLoading = false
        this.closeEventSource()
      })

      eventSource.addEventListener("done", () => {
        this.incrementHintCount()
        this.isLoading = false
        this.closeEventSource()
      })

      eventSource.onerror = () => {
        if (
          this.messages[thinkingIndex] &&
          this.messages[thinkingIndex].thinking
        ) {
          this.messages.splice(thinkingIndex, 1, {
            text: "AI 힌트를 불러오지 못했습니다.",
            error: true,
          })
          this.scrollToBottom()
        }
        this.isLoading = false
        this.closeEventSource()
      }
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const terminalBody = this.$refs.terminalBody
        if (!terminalBody) return
        terminalBody.scrollTop = terminalBody.scrollHeight
      })
    },

    closeEventSource() {
      if (!this.eventSource) return
      this.eventSource.close()
      this.eventSource = null
    },

    startDrag() {
      this.isDragging = true
    },

    onMouseMove(e) {
      if (!this.isDragging) return

      const parentRect = this.$el.parentElement.getBoundingClientRect()
      const newHeight = parentRect.bottom - e.clientY

      if (newHeight > 120 && newHeight < parentRect.height - 60) {
        this.$el.style.height = `${newHeight}px`
      }
    },

    onMouseUp() {
      this.isDragging = false
    },
  },

  mounted() {
    window.addEventListener("mousemove", this.onMouseMove)
    window.addEventListener("mouseup", this.onMouseUp)
    this.loadHintUsage()
  },

  beforeDestroy() {
    window.removeEventListener("mousemove", this.onMouseMove)
    window.removeEventListener("mouseup", this.onMouseUp)
    this.closeEventSource()
  },
  watch: {
    problemID() {
      this.closeEventSource()
      this.isLoading = false
      this.messages = []
    },
  },
}
</script>

<style scoped>
.editor-container {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 260px;
  display: flex;
  flex-direction: column;
  z-index: 10;
}

/* 구분선 */
.divider {
  height: 6px;
  cursor: row-resize;
  background-color: transparent;
  position: relative;
  flex-shrink: 0;
}

.divider::after {
  content: "";
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 3px;
  background: #ccc;
  border-radius: 2px;
}

/* 하단 패널 */
.editor-bottom {
  flex: 1;
  border-top: 1px solid var(--ai-assistant-border-color);
  background: var(--ai-assistant-panel-bg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 탭 헤더 */
.tab-header {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0 16px;
  border-bottom: 1px solid var(--ai-assistant-header-border-color);
  background: var(--ai-assistant-header-bg);
  flex-shrink: 0;
  height: 42px;
}

.tab-left {
  display: flex;
  gap: 4px;
  height: 100%;
}

.tab-left span {
  cursor: pointer;
  color: var(--ai-assistant-tab-text-color);
  font-size: 14px;
  padding: 0 10px;
  display: flex;
  align-items: center;
  border-bottom: 2px solid transparent;
}

.tab-left span.active {
  color: var(--ai-assistant-tab-active-color);
  border-bottom: 2px solid var(--ai-assistant-tab-active-color);
  font-weight: 600;
}

.tab-right-group {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 10px;
}

.tab-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.hint-count {
  font-size: 12px;
  color: var(--ai-assistant-subtle-text-color);
  white-space: nowrap;
}

.hint-btn {
  background-color: var(--ai-assistant-subtle-bg);
  color: var(--ai-assistant-tab-active-color);
  border: none;
  border-radius: 4px;
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.hint-btn:hover:not(:disabled) {
  background-color: var(--ai-assistant-subtle-hover-bg);
}

.hint-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.close-btn {
  margin-left: 0;
  color: var(--ai-assistant-close-text-color);
  font-size: 12px;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  border: none;
  background: transparent;
}

.close-btn:hover {
  background-color: var(--ai-assistant-close-hover-bg);
  color: var(--ai-assistant-close-hover-text-color);
}

/* 내용 영역 */
.terminal-body {
  padding: 16px;
  overflow-y: auto;
  flex: 1;
}

/* AI 채팅 */
.ai-chat {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chat-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.avatar {
  width: 52px;
  height: 52px;
  flex-shrink: 0;
  background-color: var(--ai-assistant-avatar-bg);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
}

.avatar img {
  width: 100%;
  height: 100%;
  filter: var(--ai-assistant-avatar-icon-filter);
}

.bubble {
  background: var(--ai-assistant-bubble-bg);
  border-radius: 0 12px 12px 12px;
  padding: 12px 16px;
  font-size: 14px;
  color: var(--ai-assistant-bubble-text-color);
  line-height: 1.6;
  max-width: 85%;
  white-space: pre-wrap;
}

.bubble.error {
  color: var(--ai-assistant-error-text-color);
}

.thinking-bubble {
  background: var(--ai-assistant-thinking-bg);
  color: var(--ai-assistant-thinking-text-color);
  font-style: italic;
}

/* 실행 결과 */
.result-message {
  color: var(--ai-assistant-muted-text-color);
  font-size: 14px;
}

.empty-message {
  color: var(--ai-assistant-muted-text-color);
  font-size: 14px;
}
</style>
