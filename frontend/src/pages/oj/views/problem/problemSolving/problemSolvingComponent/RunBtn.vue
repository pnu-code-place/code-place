<template>
  <button
    v-if="!$route.params.contestID || (contest && contest.sample_run_enabled)"
    type="button"
    class="runBtnWrapper"
    :disabled="isRunning"
    :aria-busy="String(isRunning)"
    @click="runCode"
  >
    <span>{{ isRunning ? "실행 중" : "실행" }}</span>
  </button>
</template>

<script>
import { defineComponent } from "vue"

export default defineComponent({
  emits: ["create-run"],
  props: {
    isRunning: Boolean,
  },
  computed: {
    contest() {
      return this.$store.state.contest.contest
    },
  },
  methods: {
    runCode() {
      if (!this.isRunning) {
        this.$emit("create-run")
      }
    },
  },
})
</script>

<style scoped lang="less">
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

.runBtnWrapper:focus-visible {
  outline: 2px solid var(--submission-primary-btn-bg);
  outline-offset: 2px;
}

.runBtnWrapper:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
