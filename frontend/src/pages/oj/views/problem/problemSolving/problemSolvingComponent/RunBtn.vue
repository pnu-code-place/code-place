<template>
  <div class="runBtnGroup">
    <!-- TODO: 실행 API 연동 후 제거 (테스트용 결과 선택) -->
    <select
      v-model="mockType"
      class="mockSelect"
      :disabled="isRunning"
      aria-label="예시 실행 결과 선택"
    >
      <option value="mixed">섞어서</option>
      <option value="accepted">맞았습니다</option>
      <option value="wrong_answer">틀렸습니다</option>
      <option value="time_limit">시간 초과</option>
      <option value="memory_limit">메모리 초과</option>
      <option value="runtime_error">런타임 에러</option>
    </select>
    <button
      type="button"
      class="runBtnWrapper"
      :disabled="isRunning"
      :aria-busy="String(isRunning)"
      @click="runCode"
    >
      <span>{{ isRunning ? "실행 중" : "실행" }}</span>
    </button>
  </div>
</template>

<script>
import { defineComponent } from "vue"

export default defineComponent({
  emits: ["create-run"],
  props: {
    isRunning: Boolean,
  },
  data() {
    return {
      mockType: "mixed",
    }
  },
  methods: {
    runCode() {
      if (!this.isRunning) {
        this.$emit("create-run", this.mockType)
      }
    },
  },
})
</script>

<style scoped lang="less">
.runBtnGroup {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mockSelect {
  font-size: 13px;
  font-weight: 650;
  height: 34px;
  padding: 0 8px;
  border-radius: 7px;
  border: 1px solid var(--border-color);
  background-color: var(--ps-content-color);
  color: var(--ps-content-title-color);
  cursor: pointer;
}

.runBtnWrapper {
  font-weight: 700;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: space-evenly;
  border-radius: 10px;
  padding: 5px 11px;
  cursor: pointer;
  transition: background-color 0.15s;
  border: 1px solid var(--border-color);
  background-color: var(--ps-content-color);
  color: var(--ps-content-text-color);
}

.runBtnWrapper:hover:not(:disabled) {
  background-color: var(--header-btn-color);
}

.runBtnWrapper:focus-visible,
.mockSelect:focus-visible {
  outline: 2px solid var(--submission-primary-btn-bg);
  outline-offset: 2px;
}

.runBtnWrapper:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
