<template>
  <div v-show="visible" class="editor-container">
    <div class="divider" @mousedown="startDrag"></div>

    <div class="editor-bottom">
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
            <span class="hint-count" v-if="isAdminRole">
              남은 횟수 : 무제한 (관리자)
            </span>

            <span class="hint-count" v-else>
              남은 횟수 : 이 문제에서 {{ problemHintsRemaining }}/5 회 더 가능
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

      <div ref="terminalBody" class="terminal-body">
        <div v-if="tab === 'ai'" class="ai-chat">
          <div v-for="(msg, i) in messages" :key="i" class="chat-row">
            <div class="avatar" :class="{ thinking: msg.thinking }">
              <img src="@/assets/images/AIAssistant.svg" alt="AI" />
            </div>

            <div v-if="msg.thinking" class="bubble thinking-bubble">
              생각 중...
            </div>

            <div
              v-else
              class="bubble"
              :class="{ error: msg.error }"
              v-text="msg.text"
            ></div>
          </div>
        </div>

        <div v-else class="result-message">실행 결과가 여기에 표시됩니다.</div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@oj/api"
import { mapGetters } from "vuex" // 스토어에서 관리자 여부를 가져오기 위해 추가

export default {
  props: {
    result: Object,
    problemID: String,
    contestID: [Number, String],
    code: {
      type: String,
      default: "",
    },
  },

  data() {
    return {
      visible: false,
      tab: "ai",
      isDragging: false,
      isLoading: false,
      messages: [],
      eventSource: null,

      // DB에서 가져온 사용 횟수를 담을 변수
      problemHintsUsed: 0,
    }
  },

  computed: {
    // Vuex Store에 있는 Admin Role 확인
    ...mapGetters(["isAdminRole"]),

    problemHintsRemaining() {
      return Math.max(0, 5 - this.problemHintsUsed)
    },

    hintsExhausted() {
      if (this.isAdminRole) return false // 관리자는 소진 개념이 없음
      return this.problemHintsRemaining <= 0
    },
  },

  methods: {
    // 백엔드 API에서 이전 대화 내역 및 현재 횟수를 불러오는 핵심 함수
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

          // 이전 로그들을 messages 배열에 세팅
          this.messages = logs.map((log) => ({
            text: log.hint_content,
            error: false,
            isHistory: true,
          }))

          this.scrollToBottom()
        })
        .catch((err) => {
          console.error("AI 조교 히스토리를 불러오지 못했습니다.", err)
        })
    },

    show() {
      this.visible = true
      this.tab = "ai"
      // 패널이 열릴 때마다 최신 내역 및 카운트 불러오기
      this.fetchHintHistory()
    },

    requestHint() {
      if (this.isLoading || !this.problemID || this.hintsExhausted) return

      this.closeEventSource()
      this.isLoading = true
      this.messages.push({ text: "", thinking: true })
      this.scrollToBottom()
      const thinkingIndex = this.messages.length - 1

      const eventSource = new EventSource(
        api.getProblemLLMHintUrl(this.problemID, this.code, this.contestID),
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
        } else if (this.messages[thinkingIndex]) {
          this.messages[thinkingIndex].text += payload.text || ""
        }
        this.scrollToBottom()
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
        this.isLoading = false
        this.closeEventSource()
        // 답변 생성이 끝났으므로 DB에 반영된 최신 횟수 및 내역을 다시 받아옵니다.
        this.fetchHintHistory()
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
      const minPanelHeight = 120
      const minEditorHeight = 220
      const newHeight = parentRect.bottom - e.clientY
      if (
        newHeight > minPanelHeight &&
        newHeight < parentRect.height - minEditorHeight
      ) {
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
    // 페이지 마운트 시에도 내역 불러오기
    if (this.visible) {
      this.fetchHintHistory()
    }
  },

  beforeDestroy() {
    window.removeEventListener("mousemove", this.onMouseMove)
    window.removeEventListener("mouseup", this.onMouseUp)
    this.closeEventSource()
  },

  watch: {
    // 문제 ID가 바뀔 때 상태 초기화 및 새로운 문제 히스토리 조회
    problemID() {
      this.closeEventSource()
      this.isLoading = false
      this.messages = []
      this.problemHintsUsed = 0
      if (this.visible) {
        this.fetchHintHistory()
      }
    },
  },
}
</script>

<style scoped>
/* 기존 스타일 그대로 유지 (생략 없이 사용하세요) */
.editor-container {
  position: relative;
  height: 260px;
  display: flex;
  flex-direction: column;
  flex: 0 0 auto;
  z-index: 10;
}

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

.editor-bottom {
  flex: 1;
  border-top: 1px solid var(--ai-assistant-border-color);
  background: var(--ai-assistant-panel-bg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

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

.terminal-body {
  padding: 16px;
  overflow-y: auto;
  flex: 1;
}

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

.result-message {
  color: var(--ai-assistant-muted-text-color);
  font-size: 14px;
}

.empty-message {
  color: var(--ai-assistant-muted-text-color);
  font-size: 14px;
}
</style>
