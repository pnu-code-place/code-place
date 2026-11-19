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

    <div v-else-if="status === 'done'" class="result-done">
      <div v-if="cases.length === 0" class="result-message">
        실행할 예제가 없습니다.
      </div>

      <template v-else>
        <!-- 런타임 에러/시간·메모리 초과는 예제 탭 없이 결과만 표시 -->
        <div v-if="!abortedCase" class="case-tabs">
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

          <!-- 런타임 에러: 에러 메시지만 -->
          <div
            v-if="selectedCase.type === 'runtime_error'"
            class="case-section"
          >
            <div class="case-label">에러 메시지</div>
            <pre class="case-code error">{{
              selectedCase.error || "에러 정보가 없습니다."
            }}</pre>
          </div>

          <!-- 시간/메모리 초과: 제약 사항 + 상세 정보만 -->
          <template v-else-if="isLimitExceeded(selectedCase)">
            <div class="case-section">
              <div class="case-label">제약 사항</div>
              <div class="case-code case-stats">
                <span class="stat-label">수행 시간</span>
                <span>{{ formatTime(timeLimit) }}</span>
                <span class="stat-label">메모리</span>
                <span>{{ formatLimitMemory(memoryLimit) }}</span>
              </div>
            </div>

            <div class="case-section">
              <div class="case-label">상세 정보</div>
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
            </div>
          </template>

          <template v-else>
            <div class="case-section">
              <div class="case-label">입력</div>
              <pre class="case-code">{{ selectedCase.input || " " }}</pre>
            </div>

            <div class="case-section">
              <div class="case-label">나의 출력</div>
              <pre class="case-code">{{ selectedCase.output || " " }}</pre>
            </div>

            <div class="case-section">
              <div class="case-label">정답</div>
              <pre class="case-code">{{ selectedCase.expected || " " }}</pre>
            </div>

            <div v-if="hasStat(selectedCase)" class="case-section">
              <div class="case-label">상세 정보</div>
              <div class="case-code case-stats">
                <span class="stat-label">수행 시간</span>
                <span>{{ formatTime(selectedCase.time) }}</span>
                <span class="stat-label">메모리</span>
                <span>{{ formatMemory(selectedCase.memory) }}</span>
              </div>
            </div>
          </template>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { defineComponent } from "vue"

const RESULT_TITLES = {
  accepted: "맞았습니다!",
  wrong_answer: "틀렸습니다",
  time_limit: "시간 초과",
  memory_limit: "메모리 초과",
  runtime_error: "런타임 에러",
}

export default defineComponent({
  props: {
    status: {
      type: String,
      default: "idle",
      validator: (value) => ["idle", "running", "done"].includes(value),
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
    // 실행이 중단된 예제 (런타임 에러, 시간/메모리 초과)
    abortedCase() {
      return this.cases.find(
        (c) => c.type === "runtime_error" || this.isLimitExceeded(c),
      )
    },
    selectedCase() {
      return this.abortedCase || this.cases[this.selectedIndex]
    },
    // 문제의 제한값 (시간: ms, 메모리: MB)
    timeLimit() {
      return this.result.timeLimit
    },
    memoryLimit() {
      return this.result.memoryLimit
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
      if (testCase.type === "time_limit" || testCase.type === "memory_limit") {
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
  padding: 12px 14px;
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

.case-code.error {
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
