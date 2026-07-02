<template>
  <div class="contest-problem-navigator">
    <div class="navigator-panel">
      <div class="navigator-problems" :aria-busy="loading">
        <div
          v-if="loading && problems.length === 0"
          class="navigator-skeleton-list"
          aria-hidden="true"
        >
          <div
            v-for="index in skeletonCount"
            :key="`contest-problem-nav-skeleton-${index}`"
            class="navigator-skeleton-item"
          >
            <span class="navigator-skeleton-number"></span>
            <span class="navigator-skeleton-dot"></span>
          </div>
        </div>
        <button
          v-else
          v-for="(problem, index) in problems"
          :key="`contest-problem-nav-${problem._id}`"
          type="button"
          class="navigator-problem-button"
          :class="[
            getProblemStatusClass(problem),
            { active: String(problem._id) === String(problemID) },
          ]"
          :disabled="loading"
          :aria-label="getProblemTitle(problem)"
          @blur="hideTooltip"
          @click="navigate(problem, $event)"
          @focus="showTooltip(problem, index, $event)"
          @mouseenter="showTooltip(problem, index, $event)"
          @mouseleave="hideTooltip"
        >
          <span class="problem-number">{{ index + 1 }}</span>
          <span
            class="problem-status-dot"
            aria-hidden="true"
          ></span>
        </button>
      </div>
    </div>
    <div
      v-if="hoveredProblem"
      class="navigator-tooltip"
      :class="getProblemStatusClass(hoveredProblem)"
      :style="tooltipStyle"
    >
      <span class="tooltip-title">{{ hoveredProblem.title }}</span>
      <span class="tooltip-status">
        {{ getProblemStatusText(hoveredProblem) }}
      </span>
    </div>
  </div>
</template>

<script>
export default {
  name: "ContestProblemNavigator",
  props: {
    contestID: {
      type: [Number, String],
      required: true,
    },
    problemID: {
      type: [Number, String],
      required: true,
    },
    problems: {
      type: Array,
      default: () => [],
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      hoveredProblem: null,
      hoveredIndex: -1,
      tooltipTop: 0,
      skeletonCount: 8,
    }
  },
  computed: {
    currentIndex() {
      return this.problems.findIndex(
        (problem) => String(problem._id) === String(this.problemID),
      )
    },
    tooltipStyle() {
      return {
        top: `${this.tooltipTop}px`,
      }
    },
  },
  methods: {
    getProblemState(problem) {
      if (!problem) {
        return null
      }
      if (problem.mine_submission_state) {
        return problem.mine_submission_state
      }
      if (problem.my_status === 0) {
        return "Accepted"
      }
      if (problem.my_status === 8) {
        return "Partially_Accepted"
      }
      if (problem.my_status !== null && problem.my_status !== undefined) {
        return "Failed"
      }
      return null
    },
    getProblemStatusClass(problem) {
      const state = this.getProblemState(problem)
      if (state === "Accepted") {
        return "status-accepted"
      }
      if (state === "Partially_Accepted") {
        return "status-partial"
      }
      if (state === "Failed") {
        return "status-failed"
      }
      return ""
    },
    getProblemStatusText(problem) {
      const state = this.getProblemState(problem)
      if (state === "Accepted") {
        return "정답"
      }
      if (state === "Partially_Accepted") {
        return "부분 정답"
      }
      if (state === "Failed") {
        return "오답"
      }
      return "미제출"
    },
    getProblemTitle(problem) {
      const state = this.getProblemState(problem)
      if (!state) {
        return problem.title
      }
      const statusText = {
        Accepted: "정답",
        Partially_Accepted: "부분 정답",
        Failed: "오답",
      }[state]
      return `${problem.title} - ${statusText}`
    },
    showTooltip(problem, index, event) {
      if (!problem || !event || !event.currentTarget) {
        return
      }
      const target = event.currentTarget
      const targetRect = target.getBoundingClientRect()
      const rootRect = this.$el.getBoundingClientRect()
      this.hoveredProblem = problem
      this.hoveredIndex = index
      this.tooltipTop = targetRect.top - rootRect.top + targetRect.height / 2
    },
    hideTooltip() {
      this.hoveredProblem = null
      this.hoveredIndex = -1
    },
    navigate(problem, event) {
      if (!problem || this.loading) {
        return
      }
      if (event && event.currentTarget) {
        event.currentTarget.blur()
      }
      this.$emit("navigate", problem._id)
    },
  },
}
</script>

<style scoped lang="less">
.contest-problem-navigator {
  --navigator-bg: #f8fafc;
  --navigator-bg-hover: #eef2f7;
  --navigator-border: rgba(148, 163, 184, 0.24);
  --navigator-text: #475569;
  --navigator-text-strong: #0f172a;
  --navigator-muted: #94a3b8;
  --navigator-number-bg: rgba(255, 255, 255, 0.82);
  --navigator-number-border: rgba(148, 163, 184, 0.28);
  --navigator-active-bg: #2563eb;
  --navigator-active-text: #ffffff;
  --navigator-tooltip-bg: #ffffff;
  --navigator-tooltip-border: rgba(148, 163, 184, 0.22);
  --navigator-tooltip-shadow: 0 8px 22px rgba(15, 23, 42, 0.1);
  --navigator-accepted: #6f9f84;
  --navigator-partial: #a98d62;
  --navigator-failed: #aa7777;

  position: relative;
  z-index: 20;
  width: 60px;
  height: 100%;
}

.navigator-panel {
  width: 60px;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 8px 7px 8px 5px;
  border-right: 1px solid var(--navigator-border);
  background: var(--navigator-bg);
  color: var(--navigator-text);
  overflow: visible;
  transition:
    background 0.2s ease,
    border-color 0.2s ease;
}

:root.dark.problem .contest-problem-navigator {
  --navigator-bg: #111827;
  --navigator-bg-hover: rgba(255, 255, 255, 0.06);
  --navigator-border: rgba(255, 255, 255, 0.07);
  --navigator-text: rgba(226, 232, 240, 0.8);
  --navigator-text-strong: #f8fafc;
  --navigator-muted: #94a3b8;
  --navigator-number-bg: rgba(255, 255, 255, 0.05);
  --navigator-number-border: rgba(255, 255, 255, 0.08);
  --navigator-active-bg: #3b82f6;
  --navigator-active-text: #ffffff;
  --navigator-tooltip-bg: #172033;
  --navigator-tooltip-border: rgba(255, 255, 255, 0.08);
  --navigator-tooltip-shadow: 0 10px 26px rgba(2, 6, 23, 0.36);
  --navigator-accepted: #86ad98;
  --navigator-partial: #b9a06f;
  --navigator-failed: #bc8b8b;
}

.navigator-problems {
  min-height: 0;
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  gap: 5px;
  overflow-x: hidden;
  overflow-y: auto;
  padding: 2px 0;
}

.navigator-problems::-webkit-scrollbar {
  width: 3px;
}

.navigator-problems::-webkit-scrollbar-thumb {
  background: var(--navigator-border);
  border-radius: 0;
}

.navigator-problem-button {
  position: relative;
  flex: 0 0 34px;
  display: grid;
  grid-template-columns: 38px 7px;
  align-items: center;
  gap: 2px;
  width: 48px;
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  color: var(--navigator-text);
  cursor: pointer;
  transition:
    background 0.16s ease,
    color 0.16s ease;
}

.navigator-skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.navigator-skeleton-item {
  flex: 0 0 34px;
  display: grid;
  grid-template-columns: 38px 7px;
  align-items: center;
  gap: 2px;
  width: 48px;
}

.navigator-skeleton-number {
  width: 28px;
  height: 28px;
  justify-self: center;
  border-radius: 999px;
  background: var(--navigator-number-bg);
}

.navigator-skeleton-dot {
  width: 5px;
  height: 5px;
  border-radius: 999px;
  background: var(--navigator-muted);
  opacity: 0.45;
}

.navigator-problem-button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.navigator-problem-button:not(:disabled):hover .problem-number {
  background: var(--navigator-bg-hover);
  border-color: transparent;
  color: var(--navigator-text-strong);
}

.navigator-problem-button.active .problem-number {
  border-color: transparent;
  background: var(--navigator-active-bg);
  color: var(--navigator-active-text);
}

.navigator-problem-button:focus {
  outline: none;
}

.navigator-problem-button:focus-visible .problem-number {
  outline: 2px solid var(--navigator-active-bg);
  outline-offset: 2px;
}

.problem-number {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: var(--navigator-number-bg);
  border: 1px solid var(--navigator-number-border);
  color: var(--navigator-text);
  justify-self: center;
  font-size: 12px;
  font-weight: 700;
  line-height: 1;
  transition:
    background 0.16s ease,
    border-color 0.16s ease,
    color 0.16s ease,
    transform 0.16s ease;
}

.problem-status-dot {
  width: 5px;
  height: 5px;
  border-radius: 999px;
  background: var(--navigator-muted);
  opacity: 0.72;
}

.navigator-problem-button.status-accepted .problem-status-dot {
  background: var(--navigator-accepted);
}

.navigator-problem-button.status-partial .problem-status-dot {
  background: var(--navigator-partial);
}

.navigator-problem-button.status-failed .problem-status-dot {
  background: var(--navigator-failed);
}

.navigator-tooltip {
  position: absolute;
  left: 56px;
  z-index: 30;
  width: max-content;
  min-width: 120px;
  max-width: min(360px, calc(100vw - 96px));
  max-height: 160px;
  display: flex;
  flex-direction: column;
  gap: 5px;
  align-items: flex-start;
  justify-content: center;
  overflow: hidden;
  padding: 9px 11px 8px;
  border: 1px solid var(--navigator-tooltip-border);
  border-radius: 6px;
  background: var(--navigator-tooltip-bg);
  box-shadow: var(--navigator-tooltip-shadow);
  color: var(--navigator-text-strong);
  pointer-events: none;
  transform: translate(4px, -50%);
}

.navigator-tooltip::before {
  position: absolute;
  top: 50%;
  left: -4px;
  width: 7px;
  height: 7px;
  border-left: 1px solid var(--navigator-tooltip-border);
  border-bottom: 1px solid var(--navigator-tooltip-border);
  background: var(--navigator-tooltip-bg);
  content: "";
  transform: translateY(-50%) rotate(45deg);
}

.tooltip-title {
  display: -webkit-box;
  max-width: 100%;
  overflow: hidden;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0;
  line-height: 1.35;
  white-space: normal;
  word-break: break-word;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 4;
}

.tooltip-status {
  color: var(--navigator-muted);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0;
  line-height: 1;
  white-space: nowrap;
}

.navigator-tooltip.status-accepted .tooltip-status {
  color: var(--navigator-accepted);
}

.navigator-tooltip.status-partial .tooltip-status {
  color: var(--navigator-partial);
}

.navigator-tooltip.status-failed .tooltip-status {
  color: var(--navigator-failed);
}
</style>
