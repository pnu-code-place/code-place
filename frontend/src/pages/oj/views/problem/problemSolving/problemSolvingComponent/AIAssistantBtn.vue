<template>
  <button
    type="button"
    class="aiAssistantBtnWrapper"
    :class="{ active, compact }"
    :aria-label="$t('m.AI_Assistant_Name')"
    @click="onClick"
    @mouseenter="showTooltip"
    @mouseleave="tooltipVisible = false"
    @focus="showTooltip"
    @blur="tooltipVisible = false"
    v-if="!$route.params.contestID || (contest && contest.ai_assistant_enabled)"
  >
    <img class="icon" src="@/assets/images/coplee_mini.svg" alt="" />
    <span v-if="!compact">{{ $t("m.AI_Assistant_Name") }}</span>
    <span
      class="btn-tooltip"
      :class="{ visible: tooltipVisible && !active }"
      :style="tooltipStyle"
      role="tooltip"
    >
      {{ $t("m.AI_Assistant_Btn_Tooltip") }}
    </span>
  </button>
</template>

<script>
import { defineComponent } from "vue"

export default defineComponent({
  emits: ["open-ai"],
  props: {
    active: {
      type: Boolean,
      default: false,
    },
    // 좁은 헤더에서 아이콘만 표시
    compact: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      tooltipVisible: false,
      tooltipStyle: {},
    }
  },
  computed: {
    contest() {
      return this.$store.state.contest.contest
    },
  },
  methods: {
    onClick() {
      this.tooltipVisible = false
      this.$emit("open-ai")
    },

    // 편집기 영역에 잘리지 않게 화면 기준 위치로 표시
    showTooltip() {
      const rect = this.$el.getBoundingClientRect()
      this.tooltipStyle = {
        top: `${rect.top - 8}px`,
        left: `${rect.left + rect.width / 2}px`,
      }
      this.tooltipVisible = true
    },
  },
})
</script>

<style scoped lang="less">
.aiAssistantBtnWrapper {
  position: relative;
  font-weight: 700;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: space-evenly;
  border-radius: 10px;
  padding: 4px 12px;
  cursor: pointer;
  transition: width 0.3s;
  border: none;
  background-color: var(--ai-assistant-btn-bg);
  color: var(--ai-assistant-btn-text-color);
  white-space: nowrap;
  i {
    font-size: smaller;
  }

  &.compact {
    padding: 4px 8px;

    .icon {
      margin-right: 0;
    }
  }
}

.aiAssistantBtnWrapper:hover,
.aiAssistantBtnWrapper.active {
  background-color: var(--ai-assistant-btn-hover-bg);
  color: var(--ai-assistant-btn-hover-text-color);
}

.icon {
  width: 24px;
  height: 24px;
  margin-right: 4px;
}

// 버튼 위 가운데 설명
.btn-tooltip {
  position: fixed;
  z-index: 1000;
  padding: 6px 10px;
  border-radius: 8px;
  background-color: var(--ai-assistant-tooltip-bg);
  color: var(--ai-assistant-tooltip-text-color);
  filter: drop-shadow(0 2px 6px var(--ai-assistant-tooltip-shadow));
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  transform: translate(-50%, calc(-100% + 2px));
  transition:
    opacity 0.15s ease,
    transform 0.15s ease;

  &::after {
    content: "";
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 6px solid transparent;
    border-top-color: var(--ai-assistant-tooltip-bg);
  }
}

.btn-tooltip.visible {
  opacity: 1;
  transform: translate(-50%, -100%);
}
</style>
