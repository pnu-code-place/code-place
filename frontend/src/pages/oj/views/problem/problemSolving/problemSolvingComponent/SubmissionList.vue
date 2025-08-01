<template>
  <div class="submission-list-container" :class="themeClass">
    <div class="submission-table-wrapper">
      <table class="submission-table">
        <thead>
          <tr>
            <th>No.</th>
            <th>결과</th>
            <th>언어</th>
            <th>실행 시간</th>
            <th>메모리</th>
            <th>제출 일자 {{ this.lastSubmissionId || "no" }}</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(submission, idx) in submissions">
            <!-- 메인 행 -->
            <tr
              :key="submission.id"
              @click="selectSubmission(submission)"
              class="submission-row"
              :class="{
                selected: internalSelectedSubmissionId === submission.id,
              }"
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
              <td>
                <Icon
                  v-if="internalSelectedSubmissionId !== submission.id"
                  type="ios-arrow-down"
                />
                <Icon v-else type="ios-arrow-up" class="rotate-icon" />
              </td>
            </tr>

            <!-- 드롭다운 행 -->
            <tr
              v-if="internalSelectedSubmissionId === submission.id"
              :key="`dropdown-${submission.id}`"
              class="dropdown-row"
            >
              <td colspan="7" class="dropdown-cell">
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
    lastSubmissionId: {
      type: String,
      default: null,
    },
  },
  data() {
    return {
      submissions: [],
      internalSelectedSubmissionId: null,
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
  watch: {
    async lastSubmissionId(newId, oldId) {
      // 값이 실제로 변경되었을 때만 실행
      if (newId !== oldId && newId) {
        try {
          console.log("Last submission ID changed:", newId);
          // 1. 제출 목록 새로고침
          await this.getSubmissionList();

          // 2. DOM 업데이트 완료 대기
          await this.$nextTick();

          // 3. 해당 제출을 선택
          this.selectSubmissionById(newId);
        } catch (error) {
          console.error("Failed to process lastSubmissionId change:", error);
          this.internalSelectedSubmissionId = null;
        }
      }
    },
  },
  methods: {
    async getSubmissionList() {
      try {
        console.log("Fetching submission list for problem ID:", this.problemID);
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

    selectSubmissionById(submissionId) {
      console.log("Selecting submission by ID:", submissionId);
      const submission = this.submissions.find(
        (sub) => sub.id === submissionId
      );
      if (submission) {
        console.log("Selecting submission:", submission);
        this.selectSubmission(submission);
      } else {
        console.warn("Submission not found for ID:", submissionId);
        this.internalSelectedSubmissionId = null;
      }
    },

    async selectSubmission(submission) {
      if (this.internalSelectedSubmissionId === submission.id) {
        this.internalSelectedSubmissionId = null;
        return;
      }

      this.internalSelectedSubmissionId = submission.id;

      // 코드가 없는 경우에만 상세 정보 fetch
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
    padding: 12px 14px;
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
    padding: 0 12px;
    cursor: pointer;

    &.selected {
      background: var(--row-hover-bg);
      transition: background 0.5s;
    }

    &.dropdown-row {
      cursor: default !important;
    }
  }

  .submission-row:hover {
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

.dropdown-cell {
  padding: 10px !important;
  border-bottom: 1px solid var(--dropdown-border);
}

.dropdown-content {
  animation: slideDown 0.8s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
