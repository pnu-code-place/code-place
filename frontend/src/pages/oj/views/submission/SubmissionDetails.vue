<template>
  <main class="submission-detail">
    <section class="submission-detail__content">
      <header class="submission-detail__toolbar">
        <h1>{{ $t("m.Status") }}</h1>
        <label
          v-if="submission.can_unshare"
          class="share-toggle"
          :class="{ active: submission.shared, loading: shareUpdating }"
        >
          <span class="share-toggle__label">제출 공개</span>
          <input
            :checked="submission.shared"
            :disabled="shareUpdating"
            type="checkbox"
            @change="shareSubmission($event.target.checked)"
          />
          <span class="share-toggle__track"></span>
        </label>
      </header>

      <section class="summary-panel">
        <div class="result-heading">
          <div>
            <h2 :style="{ color: status.color }">
              {{ $t("m." + status.statusName.replace(/ /g, "_")) }}
            </h2>
            <p>#{{ submission.id || $route.params.id }}</p>
          </div>
        </div>

        <pre v-if="isCE" class="compile-error">{{
          submission.statistic_info.err_info
        }}</pre>

        <div v-else class="metric-grid">
          <div class="metric-item">
            <span>{{ $t("m.Time") }}</span>
            <strong>{{
              submission.statistic_info.time_cost | submissionTime
            }}</strong>
          </div>
          <div class="metric-item">
            <span>{{ $t("m.Memory") }}</span>
            <strong>{{
              submission.statistic_info.memory_cost | submissionMemory
            }}</strong>
          </div>
          <div class="metric-item">
            <span>{{ $t("m.Lang") }}</span>
            <strong>{{ submission.language }}</strong>
          </div>
          <div class="metric-item">
            <span>{{ $t("m.Submission_Table_Author") }}</span>
            <strong>{{ submission.username }}</strong>
          </div>
        </div>
      </section>

      <section v-if="hasInfoTable && !isCE" class="detail-section">
        <div class="section-header">
          <h2>채점 결과</h2>
        </div>
        <div class="case-table-wrap">
          <table class="case-table">
            <thead>
              <tr>
                <th>{{ $t("m.ID") }}</th>
                <th>{{ $t("m.Status") }}</th>
                <th>{{ $t("m.Memory") }}</th>
                <th>{{ $t("m.Time") }}</th>
                <th v-if="hasScoreColumn">{{ $t("m.Score") }}</th>
                <th v-if="isAdminRole">{{ $t("m.Real_Time") }}</th>
                <th v-if="isAdminRole">{{ $t("m.Signal") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in submission.info.data" :key="index">
                <td>{{ index + 1 }}</td>
                <td>
                  <span class="case-status" :style="caseStatusStyle(row)">
                    {{ caseStatusText(row) }}
                  </span>
                </td>
                <td>{{ formatMemory(row.memory) }}</td>
                <td>{{ formatTime(row.cpu_time) }}</td>
                <td v-if="hasScoreColumn">{{ row.score }}</td>
                <td v-if="isAdminRole">{{ formatTime(row.real_time) }}</td>
                <td v-if="isAdminRole">{{ row.signal }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="detail-section code-section">
        <div class="section-header">
          <h2>제출 코드</h2>
          <span>{{ submission.language }}</span>
        </div>
        <div class="code-block-shell">
          <button
            v-clipboard:copy="submission.code"
            v-clipboard:success="onCopy"
            v-clipboard:error="onCopyError"
            class="copy-code-button"
            type="button"
            title="코드 복사"
            aria-label="코드 복사"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <rect x="9" y="9" width="10" height="10" rx="2"></rect>
              <path d="M5 15V7a2 2 0 0 1 2-2h8"></path>
            </svg>
          </button>
          <Highlight
            :code="submission.code"
            :language="submission.language"
            :border-color="status.color"
          ></Highlight>
        </div>
      </section>
    </section>
  </main>
</template>

<script>
import api from "@oj/api"
import { JUDGE_STATUS } from "@/utils/constants"
import utils from "@/utils/utils"
import Highlight from "@/pages/oj/components/Highlight"

export default {
  name: "submissionDetails",
  components: {
    Highlight,
  },
  data() {
    return {
      submission: {
        result: "0",
        code: "",
        info: {
          data: [],
        },
        statistic_info: {
          time_cost: "",
          memory_cost: "",
        },
      },
      loading: false,
      shareUpdating: false,
    }
  },
  mounted() {
    this.getSubmission()
  },
  methods: {
    getSubmission() {
      this.loading = true
      return api.getSubmission(this.$route.params.id).then(
        (res) => {
          this.loading = false
          this.submission = res.data.data
        },
        () => {
          this.loading = false
        },
      )
    },
    shareSubmission(shared) {
      if (this.shareUpdating || shared === this.submission.shared) {
        return
      }
      const previousShared = this.submission.shared
      this.shareUpdating = true
      let data = { id: this.submission.id, shared: shared }
      api.updateSubmission(data).then(
        () => {
          this.submission.shared = shared
          this.getSubmission().then(() => {
            this.shareUpdating = false
            this.$success(this.$i18n.t("m.Succeeded"))
          })
        },
        () => {
          this.shareUpdating = false
          this.submission.shared = previousShared
          this.$error("제출 공개 상태 변경에 실패했습니다.")
        },
      )
    },
    onCopy() {
      this.$success("코드를 복사했습니다.")
    },
    onCopyError() {
      this.$error("코드 복사에 실패했습니다.")
    },
    formatMemory(memory) {
      return utils.submissionMemoryFormat(memory)
    },
    formatTime(time) {
      return utils.submissionTimeFormat(time)
    },
    caseStatusText(row) {
      const judgeStatus = JUDGE_STATUS[row.result]
      if (!judgeStatus) {
        return "-"
      }
      return this.$i18n.t("m." + judgeStatus.name.replace(/ /g, "_"))
    },
    caseStatusStyle(row) {
      const judgeStatus = JUDGE_STATUS[row.result]
      if (!judgeStatus) {
        return {}
      }
      return {
        "--case-status-color": judgeStatus.color,
      }
    },
  },
  computed: {
    status() {
      const judgeStatus =
        JUDGE_STATUS[this.submission.result] ||
        JUDGE_STATUS[String(this.submission.result)] ||
        JUDGE_STATUS["0"]
      return {
        type: judgeStatus.type,
        statusName: judgeStatus.name,
        color: judgeStatus.color,
      }
    },
    isCE() {
      return Number(this.submission.result) === -2
    },
    isAdminRole() {
      return this.$store.getters.isAdminRole
    },
    hasInfoTable() {
      return (
        this.submission.info &&
        Array.isArray(this.submission.info.data) &&
        this.submission.info.data.length > 0
      )
    },
    hasScoreColumn() {
      return (
        this.hasInfoTable && this.submission.info.data[0].score !== undefined
      )
    },
  },
}
</script>

<style scoped lang="less">
.submission-detail {
  width: 100%;
  background: #ffffff;
}

.submission-detail__content {
  width: 100%;
  max-width: var(--global-width);
  margin: 0 auto;
  padding: 0 32px 36px;
}

.submission-detail__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 16px 0;
  border-bottom: 1px solid #eef1f5;

  h1 {
    margin: 0;
    color: #303747;
    font-size: 20px;
    font-weight: 700;
    line-height: 1.3;
  }
}

.share-toggle {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  height: 36px;
  padding: 0 5px 0 13px;
  color: #697386;
  font-size: 14px;
  font-weight: 800;
  background: #f6f7fb;
  border-radius: 999px;
  cursor: pointer;
  user-select: none;

  &.active {
    color: #5661f6;
    background: #eef1ff;
  }

  &.loading {
    cursor: wait;
    opacity: 0.72;
  }

  input {
    position: absolute;
    opacity: 0;
    pointer-events: none;
  }

  input:checked + .share-toggle__track {
    background: #5661f6;
  }

  input:checked + .share-toggle__track::after {
    transform: translateX(16px);
  }
}

.share-toggle__label {
  white-space: nowrap;
}

.share-toggle__track {
  position: relative;
  width: 38px;
  height: 22px;
  background: #d8dde8;
  border-radius: 999px;
  transition: background-color 0.15s ease;

  &::after {
    position: absolute;
    top: 3px;
    left: 3px;
    width: 16px;
    height: 16px;
    content: "";
    background: #ffffff;
    border-radius: 50%;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.2);
    transition: transform 0.15s ease;
  }
}

.summary-panel {
  display: grid;
  grid-template-columns: minmax(220px, 0.8fr) minmax(0, 1.2fr);
  gap: 18px;
  padding: 18px 0;
  border-bottom: 1px solid #eef1f5;
}

.result-heading {
  display: flex;
  align-items: center;
  gap: 12px;

  h2 {
    margin: 0;
    color: #303747;
    font-size: 22px;
    font-weight: 800;
    line-height: 1.2;
  }

  p {
    margin: 5px 0 0;
    color: #8a94a6;
    font-size: 13px;
    font-weight: 700;
  }
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}

.metric-item {
  min-width: 0;
  padding: 10px 12px;
  background: #f6f7fb;
  border-radius: 8px;

  span {
    display: block;
    color: #8a94a6;
    font-size: 12px;
    font-weight: 800;
  }

  strong {
    display: block;
    margin-top: 4px;
    overflow: hidden;
    color: #303747;
    font-size: 14px;
    font-weight: 800;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.compile-error {
  min-width: 0;
  max-height: 240px;
  padding: 14px;
  overflow: auto;
  color: #ae2e24;
  white-space: pre-wrap;
  word-break: break-word;
  background: #fff1f0;
  border: 1px solid #ffe0dd;
  border-radius: 8px;
}

.detail-section {
  padding-top: 18px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;

  h2 {
    margin: 0;
    color: #303747;
    font-size: 16px;
    font-weight: 800;
  }

  span {
    color: #8a94a6;
    font-size: 13px;
    font-weight: 800;
  }
}

.case-table-wrap {
  overflow-x: auto;
}

.case-table {
  width: 100%;
  min-width: 620px;
  border-spacing: 0;
  border-collapse: separate;

  th {
    padding: 10px 16px;
    color: #697386;
    font-size: 13px;
    font-weight: 700;
    text-align: left;
    white-space: nowrap;
    background: #f7f8fb;
    border-bottom: 1px solid #e6e9f0;
  }

  td {
    padding: 10px 16px;
    color: #4f5b6f;
    font-size: 14px;
    border-bottom: 1px solid #eef1f5;
  }
}

.case-status {
  display: inline-flex;
  align-items: center;
  height: 24px;
  padding: 0 8px;
  color: var(--case-status-color);
  font-size: 12px;
  font-weight: 800;
  background: #f6f7fb;
  border-radius: 6px;
  white-space: nowrap;
}

.code-section {
  padding-bottom: 12px;
}

.copy-code-button {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  color: #697386;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid #dfe4ee;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);

  svg {
    width: 16px;
    height: 16px;
    stroke: currentColor;
    stroke-width: 1.9;
    stroke-linecap: round;
    stroke-linejoin: round;
    fill: none;
  }

  &:hover {
    color: #5661f6;
    border-color: #cbd1ff;
    background: #f7f8ff;
  }
}

.code-block-shell {
  position: relative;
  overflow: hidden;
  background: #f7f8fb;
  border: 1px solid #e1e6ef;
  border-radius: 8px;
}

.code-block-shell /deep/ pre {
  max-height: 640px;
  margin: 0;
  overflow: auto;
  color: #263042;
  background: #f7f8fb !important;
}

.code-block-shell /deep/ code {
  display: block;
  min-width: max-content;
  padding: 18px 20px !important;
  color: #263042;
  font-size: 13px !important;
  line-height: 1.65;
  background: transparent !important;
  border-left-width: 0 !important;
}

.code-block-shell /deep/ pre::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

.code-block-shell /deep/ pre::-webkit-scrollbar-track {
  background: #eef1f6;
}

.code-block-shell /deep/ pre::-webkit-scrollbar-thumb {
  background: #c9d1de;
  border: 2px solid #eef1f6;
  border-radius: 999px;
}

pre {
  border: none;
  background: none;
}

@media (max-width: 960px) {
  .submission-detail__content {
    padding: 0 18px 30px;
  }

  .summary-panel {
    grid-template-columns: 1fr;
  }

  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .submission-detail__toolbar,
  .section-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .metric-grid {
    grid-template-columns: 1fr;
  }
}
</style>
