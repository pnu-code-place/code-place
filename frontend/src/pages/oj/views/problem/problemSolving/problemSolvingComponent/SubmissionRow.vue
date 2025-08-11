<template>
  <tr
    class="submission-row"
    :class="{ selected: isSelected }"
    @click="$emit('click')"
  >
    <td>{{ index }}</td>
    <td class="status-cell">
      <span
        class="status-dot"
        :style="{ backgroundColor: judgeStatus[submission.result].color }"
      />
      <span class="status">{{ judgeStatus[submission.result].name }}</span>
    </td>
    <td>
      <span
        class="language-pill"
        :style="getLanguageStyle(submission.language)"
      >
        {{ submission.language }}
      </span>
    </td>
    <td>
      <Icon type="ios-speedometer-outline" />
      {{ formatTimeCost(submission.statistic_info.time_cost) }}
    </td>
    <td>
      <Icon type="ios-pulse" />
      {{ formatMemoryCost(submission.statistic_info.memory_cost) }}
    </td>
    <td>{{ formatTime(submission.create_time) }}</td>
    <td>
      <Icon
        :type="isSelected ? 'ios-arrow-up' : 'ios-arrow-down'"
        :class="{ 'rotate-icon': isSelected }"
      />
    </td>
  </tr>
</template>

<script>
import { JUDGE_STATUS, LANGUAGE_COLOR } from "../../../../../../utils/constants"

const BYTES_IN_KB = 1024
const BYTES_IN_MB = BYTES_IN_KB * 1024
const BYTES_IN_GB = BYTES_IN_MB * 1024

export default {
  name: "SubmissionRow",
  props: {
    submission: {
      type: Object,
      required: true,
    },
    index: {
      type: Number,
      required: true,
    },
    isSelected: {
      type: Boolean,
      default: false,
    },
    isDarkMode: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      judgeStatus: JUDGE_STATUS,
    }
  },
  methods: {
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleDateString()
    },

    formatTimeCost(time) {
      return time != null ? `${time} ms` : "N/A"
    },

    formatMemoryCost(memory) {
      if (memory == null) return "N/A"

      if (memory < BYTES_IN_MB) {
        return `${Math.round(memory / BYTES_IN_KB)} KB`
      }
      if (memory < BYTES_IN_GB) {
        return `${(memory / BYTES_IN_MB).toFixed(2)} MB`
      }
      return `${(memory / BYTES_IN_GB).toFixed(2)} GB`
    },

    getLanguageStyle(language) {
      const colorConfig = LANGUAGE_COLOR[language]
      if (!colorConfig) return {}

      const themeConfig = this.isDarkMode
        ? colorConfig.darkTheme
        : colorConfig.lightTheme
      return {
        backgroundColor: themeConfig.color,
        color: themeConfig.textColor,
      }
    },
  },
}
</script>

<style scoped lang="less">
.submission-row {
  transition: background 0.2s;
  padding: 0 12px;
  cursor: pointer;

  td {
    text-align: start;
    vertical-align: middle;
    padding: 12px 14px;
    font-size: 14px;

    &:first-child {
      min-width: 20px;
      max-width: 40px;
    }
  }

  &.selected {
    background: var(--row-hover-bg);
    transition: background 0.5s;
  }

  &:hover {
    background: var(--row-hover-bg);
  }
}

.status-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status {
  font-weight: bold;
}

.language-pill {
  display: inline-flex;
  align-items: center;
  padding: 5px 10px;
  border-radius: 5px;
  font-size: 10.5px;
  font-weight: bold;
}
</style>
