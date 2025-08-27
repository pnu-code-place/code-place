<template>
  <div class="submission-list-container" :class="themeClass">
    <div class="submission-table-wrapper">
      <table class="submission-table">
        <colgroup>
          <col style="width: 5%" />
          <col style="width: 20%" />
          <col style="width: 10%" />
          <col style="width: 15%" />
          <col style="width: 15%" />
          <col style="width: 10%" />
          <col style="width: 5%" />
        </colgroup>
        <thead>
          <tr>
            <th>No.</th>
            <th>결과</th>
            <th>언어</th>
            <th>실행 시간</th>
            <th>메모리</th>
            <th>제출 일자</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(submission, idx) in submissions">
            <SubmissionRow
              :key="submission.id"
              :submission="submission"
              :index="submissions.length - idx"
              :isSelected="selectedSubmissionId === submission.id"
              :isDarkMode="isDarkMode"
              @click="handleSubmissionClick(submission)"
            />

            <SubmissionDropdown
              v-if="selectedSubmissionId === submission.id"
              :key="`dropdown-${submission.id}`"
              :submission="submission"
              :contestID="contestID"
              :isDarkMode="isDarkMode"
            />
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import api from "@oj/api"
import SubmissionRow from "./SubmissionRow.vue"
import SubmissionDropdown from "./SubmissionDropdown.vue"

export default {
  name: "SubmissionList",
  components: {
    SubmissionRow,
    SubmissionDropdown,
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
      selectedSubmissionId: null,
    }
  },
  computed: {
    themeClass() {
      return this.isDarkMode ? "dark-theme" : "light-theme"
    },
  },
  mounted() {
    this.fetchSubmissions()
  },
  watch: {
    async lastSubmissionId(newId, oldId) {
      if (newId !== oldId && newId) {
        try {
          await this.fetchSubmissions()
          await this.$nextTick()
          this.selectSubmissionById(newId)
        } catch (error) {
          console.error("Failed to process lastSubmissionId change:", error)
          this.selectedSubmissionId = null
        }
      }
    },
  },
  methods: {
    async fetchSubmissions() {
      try {
        console.log("Contest ID:", this.contestID)
        const params = {
          myself: "1",
          problem_id: this.problemID,
          ...(this.contestID && { contest_id: this.contestID }),
        }
        const res = await api.getSubmissionList(0, 100, params)
        this.submissions = res.data.data.results
      } catch (error) {
        console.error("Failed to fetch submission list:", error)
      }
    },

    selectSubmissionById(submissionId) {
      const submission = this.submissions.find((sub) => sub.id === submissionId)
      if (submission) {
        this.handleSubmissionClick(submission)
      } else {
        console.warn("Submission not found for ID:", submissionId)
        this.selectedSubmissionId = null
      }
    },

    async handleSubmissionClick(submission) {
      if (this.selectedSubmissionId === submission.id) {
        this.selectedSubmissionId = null
        return
      }

      this.selectedSubmissionId = submission.id

      if (!submission.code) {
        await this.fetchSubmissionDetails(submission)
      }

      this.$emit("submissionSelected", submission)
    },

    async fetchSubmissionDetails(submission) {
      try {
        const res = await api.getSubmission(submission.id)
        const { code, first_failed_tc_io } = res.data.data

        this.$set(submission, "code", code)
        this.$set(submission, "first_failed_tc_io", first_failed_tc_io)
      } catch (error) {
        console.error("Failed to fetch submission details:", error)
      }
    },
  },
}
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
  overflow-x: auto;
  min-width: 0;

  &::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  &::-webkit-scrollbar-track {
    background: var(--dropdown-bg);
    border-radius: 4px;
  }
  &::-webkit-scrollbar-thumb {
    background-color: var(--border-color);
    border-radius: 4px;
    border: 2px solid var(--dropdown-bg);
  }
}

.submission-table {
  width: 100%;
  min-width: 500px;
  border-collapse: collapse;
  table-layout: fixed;

  th {
    text-align: start;
    vertical-align: middle;
    padding: 12px 14px;
    font-size: 14px;
    border-bottom: 1px solid var(--border-color);
    font-weight: 700;
    color: var(--th-color);
    background: var(--bg-color);

    &:first-child {
      min-width: 20px;
      max-width: 40px;
    }
  }
}
</style>
