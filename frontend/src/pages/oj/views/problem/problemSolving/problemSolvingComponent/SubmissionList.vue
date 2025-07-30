<template>
  <div class="submission-list-container" :class="themeClass">
    <div class="submission-table-wrapper">
      <table class="submission-table">
        <thead>
          <tr>
            <th></th>
            <th>결과</th>
            <th>언어</th>
            <th>실행 시간</th>
            <th>메모리</th>
            <th>제출 일자</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(submission, idx) in submissions">
            <!-- 메인 행 -->
            <tr
              :key="submission.id"
              @click="selectSubmission(submission)"
              :class="{ selected: selectedSubmissionId === submission.id }"
            >
              <td>{{ submissions.length - idx }}</td>
              <td class="status-cell">
                <span
                  class="status-dot"
                  :style="{
                    backgroundColor: judgeStatus[submission.result].color,
                  }"
                />
                <span class="status">{{
                  judgeStatus[submission.result].name
                }}</span>
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
            </tr>

            <!-- 드롭다운 행 -->
            <tr
              v-if="selectedSubmissionId === submission.id"
              :key="`dropdown-${submission.id}`"
              class="dropdown-row"
            >
              <td colspan="6" class="dropdown-cell">
                <div class="dropdown-content">
                  <SubmissionErrorDropdown
                    v-if="submission.result !== 0"
                    :submission="submission"
                    :isDarkMode="isDarkMode"
                  />
                  <SubmissionAcceptedDropdown
                    v-else
                    :submission="submission"
                    :isDarkMode="isDarkMode"
                  />
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import api from "@oj/api";
import {
  JUDGE_STATUS,
  LANGUAGE_COLOR,
} from "../../../../../../utils/constants";
import SubmissionErrorDropdown from "./SubmissionErrorDropdown.vue";
import SubmissionAcceptedDropdown from "./SubmissionAcceptedDropdown.vue";

const BYTES_IN_KB = 1024;
const BYTES_IN_MB = BYTES_IN_KB * 1024;
const BYTES_IN_GB = BYTES_IN_MB * 1024;

export default {
  name: "SubmissionList",
  components: {
    SubmissionErrorDropdown,
    SubmissionAcceptedDropdown,
  },
  props: {
    problemID: {
      type: String,
      required: true,
    },
    contestID: {
      type: String,
      default: null,
    },
    isDarkMode: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      submissions: [],
      selectedSubmissionId: null,
      judgeStatus: JUDGE_STATUS,
    };
  },
  computed: {
    themeClass() {
      return this.isDarkMode ? "dark-theme" : "light-theme";
    },
  },
  mounted() {
    this.getSubmissionList();
  },
  methods: {
    async getSubmissionList() {
      try {
        const params = {
          myself: "1",
          problem_id: this.problemID,
        };
        const res = await api.getSubmissionList(0, 100, params);
        this.submissions = res.data.data.results;
      } catch (error) {
        console.error("Failed to fetch submission list:", error);
      }
    },

    async selectSubmission(submission) {
      if (this.selectedSubmissionId === submission.id) {
        this.selectedSubmissionId = null;
        return;
      }

      this.selectedSubmissionId = submission.id;

      if (!submission.code) {
        await this.fetchSubmissionDetails(submission);
      }

      this.$emit("submissionSelected", submission);
    },

    async fetchSubmissionDetails(submission) {
      try {
        const res = await api.getSubmission(submission.id);
        const { code, first_failed_tc_io } = res.data.data;

        this.$set(submission, "code", code);
        this.$set(submission, "first_failed_tc_io", first_failed_tc_io);
      } catch (error) {
        console.error("Failed to fetch submission details:", error);
      }
    },

    formatTime(timestamp) {
      return new Date(timestamp).toLocaleDateString();
    },

    formatTimeCost(time) {
      return time != null ? `${time} ms` : "N/A";
    },

    formatMemoryCost(memory) {
      if (memory == null) return "N/A";

      if (memory < BYTES_IN_MB) {
        return `${Math.round(memory / BYTES_IN_KB)} KB`;
      }
      if (memory < BYTES_IN_GB) {
        return `${(memory / BYTES_IN_MB).toFixed(2)} MB`;
      }
      return `${(memory / BYTES_IN_GB).toFixed(2)} GB`;
    },

    getLanguageStyle(language) {
      const colorConfig = LANGUAGE_COLOR[language];
      if (!colorConfig) return {};

      const themeConfig = this.isDarkMode
        ? colorConfig.darkTheme
        : colorConfig.lightTheme;
      return {
        backgroundColor: themeConfig.color,
        color: themeConfig.textColor,
      };
    },
  },
};
</script>

<style scoped lang="less">
.light-theme {
  --border-color: #e0e0e0;
  --th-color: #3a3a4a;
  --row-hover-bg: #f5f6fa;
  --text-color: #222;
  --dropdown-border: #e0e0e0;
}

.dark-theme {
  --border-color: #3a3a4a;
  --th-color: #e6e6e6;
  --row-hover-bg: #2f3542;
  --text-color: #e6e6e6;
  --dropdown-border: #3a3a4a;
}

.submission-list-container {
  height: 100%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-color);
  padding: 14px 16px;
  color: var(--text-color);
}

.submission-table-wrapper {
  width: 100%;
  overflow-x: auto;
}

.submission-table {
  width: 100%;
  border-collapse: collapse;

  th,
  td {
    text-align: start;
    vertical-align: middle;
    padding: 12px 0;
    font-size: 14px;

    &:first-child {
      min-width: 20px;
      max-width: 40px;
    }
  }

  th {
    border-bottom: 1px solid var(--border-color);
    font-weight: 700;
    color: var(--th-color);
    background: var(--bg-color);
  }

  tbody tr {
    transition: background 0.2s;
    cursor: pointer;

    &.selected {
      background: var(--row-hover-bg);
      transition: background 0.5s;
    }

    &.dropdown-row {
      cursor: default !important;
    }
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

.dropdown-cell {
  padding: 10px !important;
  border-bottom: 1px solid var(--dropdown-border);
}

.dropdown-content {
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
