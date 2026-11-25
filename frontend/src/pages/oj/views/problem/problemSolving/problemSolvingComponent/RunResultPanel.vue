<template>
  <div class="run-result">
    <div v-if="status === 'idle'" class="result-message">
      실행 결과가 여기에 표시됩니다.
    </div>

    <div v-else-if="status === 'running'" class="result-message running">
      <span>
        코드를 실행하고 있습니다<span class="loading-dots"
          ><span>.</span><span>.</span><span>.</span></span
        >
      </span>
    </div>

    <div
      v-else-if="status === 'error'"
      class="result-message error"
      role="alert"
    >
      {{ result.message }}
    </div>

    <div v-else-if="status === 'done'" class="result-done">
      <div v-if="result.compileError" class="case-detail">
        <div class="case-title error">컴파일 에러</div>
        <div class="case-section">
          <div class="case-label">컴파일 메시지</div>
          <RunResultCodeBlock label="컴파일 메시지" :text="result.compileError">
            <pre class="case-code error">{{ result.compileError }}</pre>
          </RunResultCodeBlock>
        </div>
      </div>
      <div v-else-if="cases.length === 0" class="result-message">
        실행할 예제가 없습니다.
      </div>

      <template v-else>
        <!-- 모든 예제 결과를 탭으로 보여주고, 처음 실패한 예제를 자동 선택 -->
        <div class="case-tabs">
          <button
            v-for="(testCase, index) in cases"
            :key="index"
            type="button"
            :class="['case-tab', { active: index === selectedIndex }]"
            @click="selectedIndex = index"
          >
            <span :class="['case-dot', caseTone(testCase)]"></span>
            예제 {{ index + 1 }}
          </button>
        </div>

        <div v-if="selectedCase" class="case-detail">
          <div :class="['case-title', caseTone(selectedCase)]">
            {{ titleOf(selectedCase) }}
          </div>

          <!-- 시간/메모리 초과: 제약 사항 + 상세 정보만 -->
          <template v-if="isLimitExceeded(selectedCase)">
            <div class="case-section">
              <div class="case-label">제약 사항</div>
              <RunResultCodeBlock label="제약 사항" :text="limitCopyText">
                <div class="case-code case-stats">
                  <span class="stat-label">수행 시간</span>
                  <span>{{ formatTime(timeLimit) }}</span>
                  <span class="stat-label">메모리</span>
                  <span>{{ formatLimitMemory(memoryLimit) }}</span>
                </div>
              </RunResultCodeBlock>
            </div>

            <div class="case-section">
              <div class="case-label">상세 정보</div>
              <RunResultCodeBlock label="상세 정보" :text="usageCopyText">
                <div class="case-code case-stats">
                  <span class="stat-label">수행 시간</span>
                  <span
                    :class="{
                      exceeded: selectedCase.type === 'time_limit',
                    }"
                    >{{ formatTime(selectedCase.time) }}</span
                  >
                  <span class="stat-label">메모리</span>
                  <span
                    :class="{
                      exceeded: selectedCase.type === 'memory_limit',
                    }"
                    >{{ formatMemory(selectedCase.memory) }}</span
                  >
                </div>
              </RunResultCodeBlock>
            </div>
          </template>

          <div
            v-else-if="selectedCase.type === 'output_limit'"
            class="result-message"
          >
            출력량이 너무 많아 실행이 중단되었습니다.
          </div>

          <div
            v-else-if="
              ['runtime_error', 'system_error'].includes(selectedCase.type)
            "
            class="case-section"
          >
            <div class="case-label">에러 메시지</div>
            <RunResultCodeBlock
              label="에러 메시지"
              :text="selectedCase.error || '에러 정보가 없습니다.'"
            >
              <pre class="case-code error">{{
                selectedCase.error || "에러 정보가 없습니다."
              }}</pre>
            </RunResultCodeBlock>
          </div>

          <template v-else>
            <div class="case-section">
              <div class="case-label">입력</div>
              <RunResultCodeBlock label="입력" :text="selectedCase.input || ''">
                <pre class="case-code">{{ selectedCase.input || " " }}</pre>
              </RunResultCodeBlock>
            </div>

            <div class="case-section">
              <div class="case-label">
                나의 출력{{
                  selectedCase.outputTruncated ? " (일부만 표시)" : ""
                }}
              </div>
              <RunResultCodeBlock
                label="나의 출력"
                :text="selectedCase.output || ''"
              >
                <pre class="case-code">{{ selectedCase.output || " " }}</pre>
              </RunResultCodeBlock>
            </div>

            <div class="case-section">
              <div class="case-label">정답</div>
              <RunResultCodeBlock
                label="정답"
                :text="selectedCase.expected || ''"
              >
                <pre class="case-code">{{ selectedCase.expected || " " }}</pre>
              </RunResultCodeBlock>
            </div>

            <div v-if="hasStat(selectedCase)" class="case-section">
              <div class="case-label">상세 정보</div>
              <RunResultCodeBlock label="상세 정보" :text="usageCopyText">
                <div class="case-code case-stats">
                  <span class="stat-label">수행 시간</span>
                  <span>{{ formatTime(selectedCase.time) }}</span>
                  <span class="stat-label">메모리</span>
                  <span>{{ formatMemory(selectedCase.memory) }}</span>
                </div>
              </RunResultCodeBlock>
            </div>
          </template>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { defineComponent } from "vue"
import RunResultCodeBlock from "./RunResultCodeBlock.vue"

const RESULT_TITLES = {
  accepted: "맞았습니다!",
  wrong_answer: "틀렸습니다",
  time_limit: "시간 초과",
  memory_limit: "메모리 초과",
  output_limit: "출력 초과",
  runtime_error: "런타임 에러",
  system_error: "실행 오류",
}

export default defineComponent({
  components: { RunResultCodeBlock },
  props: {
    status: {
      type: String,
      default: "idle",
      validator: (value) =>
        ["idle", "running", "done", "error"].includes(value),
    },
    result: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      selectedIndex: 0,
    }
  },
  computed: {
    cases() {
      return this.result.cases || []
    },
    selectedCase() {
      return this.cases[this.selectedIndex]
    },
    // 문제의 제한값 (시간: ms, 메모리: MB)
    timeLimit() {
      return this.result.timeLimit
    },
    memoryLimit() {
      return this.result.memoryLimit
    },
    limitCopyText() {
      return this.statsText(
        this.formatTime(this.timeLimit),
        this.formatLimitMemory(this.memoryLimit),
      )
    },
    usageCopyText() {
      const testCase = this.selectedCase || {}
      return this.statsText(
        this.formatTime(testCase.time),
        this.formatMemory(testCase.memory),
      )
    },
  },
  watch: {
    result() {
      const failedIndex = this.cases.findIndex((c) => c.type !== "accepted")
      this.selectedIndex = failedIndex === -1 ? 0 : failedIndex
    },
  },
  methods: {
    caseTone(testCase) {
      if (testCase.type === "accepted") return "success"
      if (this.isLimitExceeded(testCase) || testCase.type === "output_limit") {
        return "warning"
      }
      return "error"
    },
    titleOf(testCase) {
      return RESULT_TITLES[testCase.type] || RESULT_TITLES.wrong_answer
    },
    isLimitExceeded(testCase) {
      return testCase.type === "time_limit" || testCase.type === "memory_limit"
    },
    hasStat(testCase) {
      return testCase.time != null || testCase.memory != null
    },
    formatTime(time) {
      return time != null ? `${time}ms` : "-"
    },
    statsText(time, memory) {
      return `수행 시간: ${time}\n메모리: ${memory}`
    },
    formatLimitMemory(memoryMB) {
      return memoryMB != null ? `${memoryMB}MB` : "-"
    },
    formatMemory(memory) {
      if (memory == null) return "-"
      if (memory >= 1024) return `${Math.round(memory / 1024)}MB`
      return `${memory}KB`
    },
  },
})
</script>

<style scoped>
.result-message {
  padding: 8px 0;
  color: var(--ps-content-text-color);
  font-size: 13px;
  line-height: 1.6;
}

.result-message.running {
  display: flex;
  align-items: center;
  gap: 8px;
}

.result-message.error {
  color: var(--run-result-error-color);
}

.loading-dots span:nth-child(2) {
  animation: dot-2 1.2s steps(1) infinite;
}

.loading-dots span:nth-child(3) {
  animation: dot-3 1.2s steps(1) infinite;
}

@keyframes dot-2 {
  0% {
    visibility: hidden;
  }
  33% {
    visibility: visible;
  }
}

@keyframes dot-3 {
  0% {
    visibility: hidden;
  }
  66% {
    visibility: visible;
  }
}

.result-done {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 예제 탭 */
.case-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.case-tab {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border: 1px solid var(--ps-content-pre-border-color);
  border-radius: 6px;
  background-color: var(--ps-content-color);
  color: var(--ps-content-text-color);
  font-size: 13px;
  cursor: pointer;
  transition:
    background-color 0.15s,
    border-color 0.15s;
}

.case-tab:hover {
  background-color: var(--ps-content-pre-background-color);
}

.case-tab.active {
  background-color: var(--ps-content-pre-background-color);
  color: var(--ps-content-title-color);
  font-weight: 600;
}

.case-tab:focus-visible {
  outline: 2px solid var(--ps-content-text-color);
  outline-offset: 2px;
}

.case-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* 결과 톤 */
.case-dot.success {
  background-color: var(--run-result-success-color);
}

.case-dot.warning {
  background-color: var(--run-result-warning-color);
}

.case-dot.error {
  background-color: var(--run-result-error-color);
}

.case-title.success {
  color: var(--run-result-success-color);
}

.case-title.warning {
  color: var(--run-result-warning-color);
}

.case-title.error {
  color: var(--run-result-error-color);
}

/* 예제 상세 */
.case-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.case-title {
  font-size: 16px;
  font-weight: 600;
}

.case-label {
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--ps-content-text-color);
}

/* 코드 박스 */
.case-code {
  margin: 0;
  padding: 12px 48px 12px 14px;
  border: 1px solid var(--ps-content-pre-border-color);
  border-radius: 6px;
  max-height: none;
  overflow: visible;
  background-color: var(--ps-content-pre-background-color);
  color: var(--ps-content-code-text-color);
  font-size: 14px;
  font-family:
    "JetBrains Mono", "Noto Sans KR", "Apple SD Gothic Neo", "Menlo", "Monaco",
    "Consolas", monospace;
  font-variant-ligatures: none;
  line-height: 1.5;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

/* 에러 메시지는 길이를 자르지 않고 영역 높이만 제한해 스크롤 */
.case-code.error {
  max-height: 320px;
  overflow: auto;
  color: var(--run-result-error-color);
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.case-stats {
  display: grid;
  grid-template-columns: max-content 1fr;
  column-gap: 24px;
  row-gap: 8px;
  font-size: 13px;
  font-variant-numeric: tabular-nums;
  white-space: normal;
}

.exceeded {
  color: var(--run-result-error-color);
  font-weight: 700;
}

.stat-label {
  font-family: "Noto Sans KR", "Apple SD Gothic Neo", sans-serif;
}
</style>
