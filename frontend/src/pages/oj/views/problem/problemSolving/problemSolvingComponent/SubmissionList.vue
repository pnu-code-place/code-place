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
            <tr
              :key="submission.id"
              @click="selectSubmission(submission)"
              :class="{ selected: selectedSubmissionId === submission.id }"
            >
              <td>{{ submissions.length - idx }}</td>
              <td>
                <span
                  class="status-dot"
                  :style="{
                    backgroundColor: judgeStatus[submission.result].color,
                  }"
                ></span>
                <span class="status">{{
                  judgeStatus[submission.result].name
                }}</span>
              </td>
              <td>
                <span
                  class="pill"
                  :style="{
                    backgroundColor: getLanguageColor(submission.language)
                      .color,
                    color: getLanguageColor(submission.language).textColor,
                  }"
                  >{{ submission.language }}</span
                >
              </td>
              <td>
                <i class="ivu-icon ivu-icon-ios-speedometer-outline"></i>
                {{ formatTimeCost(submission.statistic_info.time_cost) }}
              </td>
              <td>
                <i class="ivu-icon ivu-icon-ios-pulse"></i>
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
                    :theme.sync="theme"
                  />
                  <SubmissionAcceptedDropdown
                    v-if="submission.result === 0"
                    :submission="submission"
                    :theme.sync="theme"
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
import CodeHighlight from "./CodeHighlight.vue";
import SubmissionErrorDropdown from "./SubmissionErrorDropdown.vue";
import SubmissionAcceptedDropdown from "./SubmissionAcceptedDropdown.vue";

export default {
  name: "SubmissionList",
  props: {
    problemID: String,
    contestID: String,
    theme: {
      type: Boolean,
    },
  },
  components: {
    CodeHighlight,
    SubmissionErrorDropdown,
    SubmissionAcceptedDropdown,
  },
  data() {
    return {
      submissions: [],
      selectedSubmissionId: null,
      judgeStatus: JUDGE_STATUS,
      languageColor: LANGUAGE_COLOR,
    };
  },
  computed: {
    themeClass() {
      return this.theme ? "dark-theme" : "light-theme";
    },
  },
  mounted() {
    this.getSubmissionList();
  },
  methods: {
    getSubmissionList() {
      const params = {
        myself: "1",
        problem_id: this.problemID,
      };
      api["getSubmissionList"](0, 100, params).then((res) => {
        this.submissions = res.data.data.results;
        console.log(this.submissions);
      });
    },
    async selectSubmission(submission) {
      if (this.selectedSubmissionId === submission.id) {
        this.selectedSubmissionId = null;
        return;
      }

      this.selectedSubmissionId = submission.id;
      if (!submission.code) {
        const res = await api.getSubmission(submission.id);
        this.$set(submission, "code", res.data.data.code);
      }
      this.$emit("submissionSelected", submission);
    },
    formatTime(timestamp) {
      const date = new Date(timestamp);
      return date.toLocaleDateString();
    },
    formatTimeCost(time) {
      if (time == null) return "N/A";
      return `${time} ms`;
    },
    formatMemoryCost(memory) {
      if (memory == null) return "N/A";
      if (memory < 1024 * 1024) return `${(memory / 1024).toFixed(0)} KB`;
      if (memory < 1024 * 1024 * 1024)
        return `${(memory / 1024 / 1024).toFixed(2)} MB`;
      return `${(memory / 1024 / 1024 / 1024).toFixed(2)} GB`;
    },
    getLanguageColor(language) {
      return this.theme
        ? this.languageColor[language].darkTheme
        : this.languageColor[language].lightTheme;
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
}

.dark-theme {
  --border-color: #3a3a4a;
  --th-color: #e6e6e6;
  --row-hover-bg: #2f3542;
  --text-color: #e6e6e6;
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

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 2px;
}

.status {
  font-weight: bold;
}

.pill {
  display: inline-flex;
  align-items: center;
  padding: 5px 10px;
  border-radius: 5px;
  font-size: 10.5px;
  font-weight: bold;
}

.submission-table-wrapper {
  width: 100%;
  overflow-x: auto;
}

.submission-table {
  width: 100%;
  border-collapse: collapse;
}

.submission-table th,
.submission-table td {
  text-align: start;
  vertical-align: middle;
  padding: 12px 0;
  font-size: 14px;
}

.submission-table th:first-child,
.submission-table td:first-child {
  min-width: 20px;
  max-width: 40px;
}

.submission-table th {
  border-bottom: 1px solid var(--border-color);
  font-weight: 700;
  color: var(--th-color);
  background: var(--bg-color);
}

.submission-table tr {
  transition: background 0.2s;
  cursor: pointer;
}

.submission-table tr.selected {
  background: var(--row-hover-bg);
  transition: background 0.5s;
}

/* 드롭다운 스타일 */
.dropdown-row {
  cursor: default !important;
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
