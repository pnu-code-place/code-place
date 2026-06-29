<template>
  <div class="flex-container">
    <section id="main" class="submission-panel">
      <div class="submission-content">
        <header class="submission-toolbar">
          <h1>{{ title }}</h1>
          <div class="filter">
            <details
              ref="statusFilter"
              class="status-filter"
              :class="{ active: formFilter.result !== '' }"
            >
              <summary>
                <span class="control-kicker">{{
                  $t("m.Submission_State")
                }}</span>
                <strong>{{ selectedStatusLabel }}</strong>
                <svg
                  class="summary-caret"
                  viewBox="0 0 16 16"
                  aria-hidden="true"
                >
                  <path d="M4 6l4 4 4-4" />
                </svg>
              </summary>
              <div class="status-popover">
                <button
                  class="status-option"
                  :class="{ selected: formFilter.result === '' }"
                  type="button"
                  @click="selectResult('')"
                >
                  {{ $t("m.All") }}
                </button>
                <button
                  v-for="status in Object.keys(JUDGE_STATUS)"
                  :key="status"
                  class="status-option"
                  :class="{ selected: formFilter.result === status }"
                  type="button"
                  @click="selectResult(status)"
                >
                  {{ getJudgeStatusLabel(status) }}
                </button>
              </div>
            </details>

            <label class="mine-toggle">
              <input
                v-model="formFilter.myself"
                type="checkbox"
                @change="handleQueryChange"
              />
              <span class="toggle-track"></span>
              <span class="toggle-label">{{ $t("m.Mine") }}</span>
            </label>

            <label class="search-control">
              <svg
                class="search-icon"
                viewBox="0 0 16 16"
                aria-hidden="true"
              >
                <circle cx="7" cy="7" r="4" />
                <path d="M10.5 10.5L13 13" />
              </svg>
              <input
                v-model="formFilter.username"
                :placeholder="$t('m.Search_Submitter')"
                type="search"
                @keydown.enter="handleQueryChange"
              />
            </label>
          </div>
        </header>

        <div class="table-panel">
          <SubmissionTable
            :contest-id="contestID"
            :data="submissions"
            :loading="loadingTable"
          ></SubmissionTable>
        </div>

        <footer class="pagination-footer">
          <span class="total-count">총 {{ total }}개 제출</span>
          <nav class="pagination" aria-label="pagination">
            <button
              class="page-button"
              type="button"
              :disabled="page <= 1"
              @click="goPage(page - 1)"
            >
              ‹
            </button>
            <button
              v-for="pageItem in visiblePages"
              :key="pageItem.key"
              class="page-button"
              :class="{ active: pageItem.page === page }"
              type="button"
              :disabled="pageItem.ellipsis"
              @click="!pageItem.ellipsis && goPage(pageItem.page)"
            >
              {{ pageItem.label }}
            </button>
            <button
              class="page-button"
              type="button"
              :disabled="page >= totalPages"
              @click="goPage(page + 1)"
            >
              ›
            </button>
          </nav>
        </footer>
      </div>
    </section>
  </div>
</template>

<script>
import { mapGetters } from "vuex"
import api from "@oj/api"
import { JUDGE_STATUS } from "@/utils/constants"
import utils from "@/utils/utils"
import SubmissionTable from "./SubmissionTable.vue"

export default {
  name: "submissionList",
  components: {
    SubmissionTable,
  },
  data() {
    return {
      formFilter: {
        myself: false,
        result: "",
        username: "",
      },
      loadingTable: false,
      submissions: [],
      total: 30,
      limit: 18,
      page: 1,
      contestID: "",
      problemID: "",
      routeName: "",
      JUDGE_STATUS: {},
    }
  },
  mounted() {
    this.init()
    this.JUDGE_STATUS = Object.assign({}, JUDGE_STATUS)
    // 去除submitting的状态 和 两个
    delete this.JUDGE_STATUS["9"]
    delete this.JUDGE_STATUS["2"]
  },
  methods: {
    init() {
      this.contestID = this.$route.params.contestID
      let query = this.$route.query
      this.problemID = query.problemID
      this.formFilter.myself = query.myself === "1"
      this.formFilter.result = query.result || ""
      this.formFilter.username = query.username || ""
      this.page = parseInt(query.page) || 1
      if (this.page < 1) {
        this.page = 1
      }
      this.routeName = this.$route.name
      this.getSubmissions()
    },
    buildQuery() {
      return {
        myself: this.formFilter.myself === true ? "1" : "0",
        result: this.formFilter.result,
        username: this.formFilter.username,
        page: this.page,
      }
    },
    getSubmissions() {
      let params = this.buildQuery()
      params.contest_id = this.contestID
      params.problem_id = this.problemID
      let offset = (this.page - 1) * this.limit
      let func = this.contestID
        ? "getContestSubmissionList"
        : "getSubmissionList"
      this.loadingTable = true
      api[func](offset, this.limit, params)
        .then((res) => {
          let data = res.data.data
          for (let v of data.results) {
            v.loading = false
          }
          this.loadingTable = false
          this.submissions = data.results
          this.total = data.total
        })
        .catch(() => {
          this.loadingTable = false
        })
    },
    // 改变route， 通过监听route变化请求数据，这样可以产生route history， 用户返回时就会保存之前的状态
    changeRoute() {
      let query = utils.filterEmptyValue(this.buildQuery())
      query.contestID = this.contestID
      query.problemID = this.problemID
      let routeName = query.contestID
        ? "contest-submission-list"
        : "submission-list"
      this.$router.push({
        name: routeName,
        query: utils.filterEmptyValue(query),
      })
    },
    goRoute(route) {
      this.$router.push(route)
    },
    selectResult(status) {
      this.page = 1
      this.formFilter.result = status
      if (this.$refs.statusFilter) {
        this.$refs.statusFilter.removeAttribute("open")
      }
      this.changeRoute()
    },
    handleQueryChange() {
      this.page = 1
      this.changeRoute()
    },
    getJudgeStatusLabel(status) {
      return this.$i18n.t(
        "m." + JUDGE_STATUS[status].name.replace(/ /g, "_"),
      )
    },
    goPage(page) {
      if (page < 1 || page > this.totalPages || page === this.page) {
        return
      }
      this.page = page
      this.changeRoute()
    },
  },
  computed: {
    ...mapGetters(["isAuthenticated"]),
    totalPages() {
      return Math.max(Math.ceil(this.total / this.limit), 1)
    },
    selectedStatusLabel() {
      if (this.formFilter.result === "") {
        return this.$i18n.t("m.All")
      }
      return this.getJudgeStatusLabel(this.formFilter.result)
    },
    visiblePages() {
      const pages = []
      const addPage = (page) => {
        pages.push({
          key: `page-${page}`,
          label: page,
          page,
          ellipsis: false,
        })
      }
      const addEllipsis = (key) => {
        pages.push({
          key,
          label: "...",
          page: null,
          ellipsis: true,
        })
      }

      if (this.totalPages <= 7) {
        for (let page = 1; page <= this.totalPages; page++) {
          addPage(page)
        }
        return pages
      }

      addPage(1)
      if (this.page > 4) {
        addEllipsis("start-ellipsis")
      }

      const start = Math.max(2, this.page - 1)
      const end = Math.min(this.totalPages - 1, this.page + 1)
      for (let page = start; page <= end; page++) {
        addPage(page)
      }

      if (this.page < this.totalPages - 3) {
        addEllipsis("end-ellipsis")
      }
      addPage(this.totalPages)
      return pages
    },
    title() {
      if (!this.contestID) {
        return this.$i18n.t("m.Status")
      } else if (this.problemID) {
        return this.$i18n.t("m.Problem_Submissions")
      } else {
        return this.$i18n.t("m.Submissions")
      }
    },
  },
  watch: {
    $route(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.init()
      }
    },
    isAuthenticated() {
      this.init()
    },
  },
}
</script>

<style scoped lang="less">
.flex-container {
  width: 100%;
  margin: 0;
  background: #ffffff;

  #main {
    flex: auto;
  }
}

.submission-panel {
  overflow: visible;
  background: #ffffff;
  border: 0;
  border-radius: 0;
}

.submission-content {
  width: 100%;
  max-width: var(--global-width);
  margin: 0 auto;
  padding: 0 32px;
}

.submission-toolbar {
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

.filter {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
}

.status-filter {
  position: relative;

  summary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    height: 36px;
    padding: 0 12px;
    color: #303747;
    font-size: 14px;
    list-style: none;
    background: #f6f7fb;
    border: 1px solid transparent;
    border-radius: 999px;
    cursor: pointer;
    user-select: none;

    &::-webkit-details-marker {
      display: none;
    }

    &:hover {
      background: #eef1ff;
    }
  }

  &[open] summary,
  &.active summary {
    color: #5661f6;
    background: #eef1ff;
    border-color: rgba(86, 97, 246, 0.18);
  }

  &.active .control-kicker,
  &.active .summary-caret,
  &[open] .control-kicker,
  &[open] .summary-caret {
    color: #5661f6;
  }

  strong {
    font-weight: 800;
  }
}

.control-kicker {
  color: #8a94a6;
  font-size: 13px;
  font-weight: 700;
}

.summary-caret {
  flex: none;
  width: 14px;
  height: 14px;
  color: #8a94a6;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}

.status-popover {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  z-index: 20;
  display: grid;
  grid-template-columns: repeat(2, minmax(104px, 1fr));
  gap: 6px;
  width: 250px;
  padding: 8px;
  background: #ffffff;
  border: 1px solid #e6e9f0;
  border-radius: 10px;
  box-shadow: 0 16px 40px rgba(30, 41, 59, 0.12);
}

.status-option {
  height: 32px;
  padding: 0 10px;
  color: #596579;
  font-size: 13px;
  font-weight: 700;
  text-align: left;
  background: transparent;
  border: 0;
  border-radius: 7px;
  cursor: pointer;

  &:hover,
  &.selected {
    color: #5661f6;
    background: #f3f5ff;
  }
}

.mine-toggle {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  height: 36px;
  padding: 0 4px 0 10px;
  color: #4f5b6f;
  font-size: 14px;
  font-weight: 700;
  background: #f6f7fb;
  border-radius: 999px;
  cursor: pointer;

  input {
    position: absolute;
    opacity: 0;
    pointer-events: none;
  }

  input:checked + .toggle-track {
    background: #5661f6;
  }

  input:checked + .toggle-track::after {
    transform: translateX(14px);
  }
}

.toggle-track {
  position: relative;
  width: 34px;
  height: 20px;
  background: #d8dde8;
  border-radius: 999px;
  transition: background-color 0.15s ease;
}

.toggle-track::after {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 14px;
  height: 14px;
  content: "";
  background: #ffffff;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.2);
  transition: transform 0.15s ease;
}

.toggle-label {
  padding-right: 8px;
}

.search-control {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  width: 198px;
  height: 36px;
  padding: 0 12px;
  color: #8a94a6;
  background: #f6f7fb;
  border-radius: 999px;

  &:focus-within {
    color: #5661f6;
    background: #eef1ff;
    box-shadow: inset 0 0 0 1px rgba(86, 97, 246, 0.18);
  }

  input {
    width: 100%;
    min-width: 0;
    color: #303747;
    font-size: 14px;
    background: transparent;
    border: 0;
    outline: none;
  }
}

.search-icon {
  flex: none;
  width: 15px;
  height: 15px;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}

.table-panel {
  background: #ffffff;
}

.pagination-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 56px;
  padding: 10px 0 12px;
  background: #ffffff;
}

.total-count {
  color: #8a94a6;
  font-size: 14px;
  font-weight: 600;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px;
  background: #f6f7fb;
  border-radius: 999px;
}

.page-button {
  min-width: 30px;
  height: 30px;
  padding: 0 10px;
  color: #697386;
  font-size: 14px;
  font-weight: 700;
  background: transparent;
  border: 0;
  border-radius: 999px;
  cursor: pointer;

  &:hover:not(:disabled),
  &.active {
    color: #ffffff;
    background: #5661f6;
    box-shadow: 0 6px 16px rgba(86, 97, 246, 0.22);
  }

  &:disabled {
    color: #bdc4d0;
    cursor: not-allowed;
    background: transparent;
  }
}

@media (max-width: 960px) {
  .submission-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .filter {
    justify-content: flex-start;
  }

  .pagination-footer {
    align-items: flex-start;
    flex-direction: column;
    gap: 10px;
  }
}
</style>
