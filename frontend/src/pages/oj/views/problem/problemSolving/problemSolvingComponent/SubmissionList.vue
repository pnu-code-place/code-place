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
            <th>제출 시간</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(submission, idx) in submissions"
            :key="submission.id"
            @click="selectSubmission(submission)"
            :class="{ selected: selectedSubmissionId === submission.id }"
          >
            <td>{{ submissions.length - idx }}</td>
            <td>
              <span
                class="status-dot"
                :style="{ backgroundColor: judgeStatus[submission.result].color }"
              ></span>
              <span class="status">{{ judgeStatus[submission.result].name }}</span>
            </td>
            <td>
              <span
                class="pill"
                :style="{
                  backgroundColor: getLanguageColor(submission.language).color,
                  color: getLanguageColor(submission.language).textColor
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
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import api from '@oj/api'
import { JUDGE_STATUS, LANGUAGE_COLOR } from '../../../../../../utils/constants'

export default {
  name: 'SubmissionList',
  props: {
    problemID: String,
    contestID: String,
    theme: {
      type: Boolean,
    }
  },
  data() {
    return {
      submissions: [],
      selectedSubmissionId: null,
      judgeStatus: JUDGE_STATUS,
      languageColor: LANGUAGE_COLOR,
    }
  },
  computed: {
    themeClass() {
      return this.theme ? 'dark-theme' : 'light-theme'
    }
  },
  mounted() {
    this.getSubmissionList()
  },
  methods: {
    getSubmissionList() {
      const params = {
        myself: '1',
        problem_id: this.problemID,
      }
      api['getSubmissionList'](0, 100, params).then(res => {
        // TODO: 최대 100개의 제출만 가져오도록 해놓았는데, 추후 페이지네이션을 고려해야 할 것 같습니다.
        this.submissions = res.data.data.results
      })
    },
    selectSubmission(submission) {
      this.selectedSubmissionId = submission.id
      this.$emit('submissionSelected', submission)
    },
    formatTime(timestamp) {
      const date = new Date(timestamp)
      return date.toLocaleDateString()
    },
    formatTimeCost(time) {
      if (time == null) return 'N/A'
      return `${time} ms`
    },
    formatMemoryCost(memory) {
      if (memory == null) return 'N/A'
      if (memory < 1024 * 1024) return `${(memory / 1024).toFixed(0)} KB`
      if (memory < 1024 * 1024 * 1024) return `${(memory / 1024 / 1024).toFixed(2)} MB`
      return `${(memory / 1024 / 1024 / 1024).toFixed(2)} GB`
    },
    getLanguageColor(language) {
      return (this.theme ? this.languageColor[language].darkTheme : this.languageColor[language].lightTheme)
    }
  }
}
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

.submission-table tr.selected,
.submission-table tr:hover {
  background: var(--row-hover-bg);
  transition: background 0.5s;
}
</style>
