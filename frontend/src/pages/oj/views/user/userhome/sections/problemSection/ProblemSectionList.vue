<template>
  <div>
    <section>
      <div class="problem-tab">
        <header class="problem-tab__header">
          <div class="problem-tab__title">
            <h1 class="main-title">{{ $t("m.Problem_Status") }}</h1>
            <span
              v-if="!isTotalCountLoading && totalCountError === 0"
              class="problem-count-summary"
            >
              {{ problemCountText }}
            </span>
          </div>
          <ul class="query-dropdowns">
            <li>
              <CustomDropdown
                :options="statusOptions"
                @dropdownChange="changeStatus"
                placeholder="Status"
                :default-text="this.$t('m.Is_Solved')"
                :selected="this.query.status"
              ></CustomDropdown>
            </li>
            <li>
              <CustomDropdown
                :options="fieldOptions"
                @dropdownChange="changeField"
                placeholder="Category"
                :default-text="this.$t('m.Field')"
                :selected="this.query.field"
              ></CustomDropdown>
            </li>
            <li>
              <CustomDropdown
                :options="difficultyOptions"
                @dropdownChange="changeDifficulty"
                placeholder="Difficulty"
                :default-text="this.$t('m.Difficulty')"
                :selected="this.query.difficulty"
              ></CustomDropdown>
            </li>
          </ul>
        </header>
      </div>
      <div class="problem-view-switcher">
        <div class="problem-view-tabs" role="tablist">
          <button
            type="button"
            role="tab"
            class="problem-view-tab"
            :class="{ 'problem-view-tab--active': activeView === 'calendar' }"
            :aria-selected="activeView === 'calendar' ? 'true' : 'false'"
            @click="activeView = 'calendar'"
          >
            {{ $t("m.Calendar_View") }}
          </button>
          <button
            type="button"
            role="tab"
            class="problem-view-tab"
            :class="{ 'problem-view-tab--active': activeView === 'all' }"
            :aria-selected="activeView === 'all' ? 'true' : 'false'"
            @click="activeView = 'all'"
          >
            {{ $t("m.Calendar_All_Problems") }}
          </button>
        </div>
      </div>
      <hr />
      <ErrorSign v-if="error !== 0" :code="this.error"></ErrorSign>
      <ProblemSkeleton
        v-else-if="isLoading"
        class="loading-skeleton"
      ></ProblemSkeleton>
      <div v-else class="problem-results">
        <div v-if="activeView === 'calendar'" class="calendar-panel">
          <div class="calendar-toolbar">
            <button
              class="calendar-nav-button"
              type="button"
              @click="moveMonth(-1)"
              :aria-label="$t('m.Calendar_Previous_Month')"
            >
              <font-awesome-icon :icon="['fas', 'chevron-left']" />
            </button>
            <div class="calendar-title">
              <strong>{{ calendarTitle }}</strong>
              <span>{{ calendarProblemCountText }}</span>
            </div>
            <div class="calendar-actions">
              <button
                class="calendar-today-button"
                type="button"
                @click="moveToToday"
              >
                {{ $t("m.Calendar_Today") }}
              </button>
              <button
                class="calendar-nav-button"
                type="button"
                @click="moveMonth(1)"
                :aria-label="$t('m.Calendar_Next_Month')"
              >
                <font-awesome-icon :icon="['fas', 'chevron-right']" />
              </button>
            </div>
          </div>

          <div class="weekday-grid">
            <div
              v-for="weekday in weekdayLabels"
              :key="weekday"
              class="weekday-cell"
            >
              {{ weekday }}
            </div>
          </div>

          <div class="calendar-grid">
            <article
              v-for="day in calendarDays"
              :key="day.key"
              class="calendar-day"
              :class="{
                'calendar-day--muted': !day.isCurrentMonth,
                'calendar-day--today': day.isToday,
                'calendar-day--active': day.problems.length > 0,
                'calendar-day--has-popover':
                  day.problems.length > 0,
              }"
            >
              <div class="calendar-day__top">
                <span class="calendar-day__number">
                  {{ day.date.getDate() }}
                </span>
                <span v-if="day.problems.length" class="calendar-day__count">
                  {{ day.problems.length }}
                </span>
              </div>
              <div class="calendar-day__problems">
                <router-link
                  v-for="problem in visibleProblems(day.problems)"
                  :key="problem.submissionId || `${day.key}-${problem.id}`"
                  class="calendar-problem"
                  :class="problemStatusClass(problem, 'calendar-problem')"
                  :to="{
                    name: 'problem-details',
                    params: { problemID: problem.id },
                  }"
                >
                  <span class="calendar-problem__id">{{ problem.id }}</span>
                  <span class="calendar-problem__title">
                    {{ problem.title }}
                  </span>
                </router-link>
                <button
                  v-if="day.problems.length > maxProblemsPerDay"
                  class="calendar-more"
                  type="button"
                  :aria-label="`${formatCalendarPopoverTitle(day.date)} 전체 풀이 보기`"
                >
                  +{{ day.problems.length - maxProblemsPerDay }}
                </button>
              </div>
              <div
                v-if="day.problems.length > 0"
                class="calendar-popover"
              >
                <div class="calendar-popover__header">
                  <strong>{{ formatCalendarPopoverTitle(day.date) }}</strong>
                  <span>
                    {{
                      $t("m.Calendar_Problem_Count", {
                        count: day.problems.length,
                      })
                    }}
                  </span>
                </div>
                <div class="calendar-popover__items">
                  <router-link
                    v-for="problem in day.problems"
                    :key="problem.submissionId || `${day.key}-${problem.id}`"
                    class="calendar-popover__item"
                    :class="
                      problemStatusClass(problem, 'calendar-popover__item')
                    "
                    :to="{
                      name: 'problem-details',
                      params: { problemID: problem.id },
                    }"
                  >
                    <span class="calendar-popover__item-id">
                      {{ problem.id }}
                    </span>
                    <span class="calendar-popover__item-title">
                      {{ problem.title }}
                    </span>
                  </router-link>
                </div>
              </div>
            </article>
          </div>
        </div>

        <div v-else class="all-problem-list">
          <div
            v-if="displayProblems.length === 0"
            class="all-problem-list__empty"
          >
            {{ $t("m.Calendar_All_Problems_Empty") }}
          </div>
          <div v-else class="all-problem-list__groups">
            <div
              v-for="group in monthlyProblemGroups"
              :key="group.key"
              class="all-problem-month"
            >
              <h2 class="all-problem-month__title">
                <span>{{ group.title }}</span>
                <span class="all-problem-month__count">
                  {{
                    $t("m.Calendar_Problem_Count", {
                      count: group.problems.length,
                    })
                  }}
                </span>
              </h2>
              <div class="all-problem-list__items">
                <router-link
                  v-for="problem in group.problems"
                  :key="`${group.key}-${problem.id}`"
                  class="all-problem-item"
                  :class="problemStatusClass(problem, 'all-problem-item')"
                  :to="{
                    name: 'problem-details',
                    params: { problemID: problem.id },
                  }"
                  :aria-label="problem.title"
                >
                  <span class="all-problem-item__id">{{ problem.id }}</span>
                  <span class="all-problem-item__tooltip">
                    {{ problem.title }}
                  </span>
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import api from "@oj/api"
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome"
import { library } from "@fortawesome/fontawesome-svg-core"
import {
  faChevronLeft,
  faChevronRight,
} from "@fortawesome/free-solid-svg-icons"
import ProblemSkeleton from "./ProblemSkeleton.vue"
import { DIFFICULTY_MAP, FIELD_MAP } from "../../../../../../../utils/constants"
import ErrorSign from "../../../../general/ErrorSign.vue"
import CustomDropdown from "../../../../../components/dropdown/CustomDropdown.vue"
import utils from "../../../../../../../utils/utils"

library.add(faChevronLeft, faChevronRight)

export default {
  name: "problem-section-list",
  components: { CustomDropdown, ErrorSign, ProblemSkeleton, FontAwesomeIcon },
  data() {
    const now = new Date()
    const today = new Date(
      now.getFullYear(),
      now.getMonth(),
      now.getDate(),
      now.getHours() - 6,
      now.getMinutes(),
      now.getSeconds(),
      now.getMilliseconds()
    )
    return {
      isLoading: true,
      isTotalCountLoading: true,
      error: 0,
      totalCountError: 0,
      calendarDate: new Date(today.getFullYear(), today.getMonth(), 1),
      maxProblemsPerDay: 2,
      activeView: "calendar",
      query: {
        field: "",
        difficulty: "",
        status: "",
      },
      fieldOptions: [],
      difficultyOptions: [],
      statusOptions: [
        {
          id: "All",
          name: this.$t("m.All"),
        },
        {
          id: "Solved",
          name: this.$t("m.Solved_Problems"),
        },
        {
          id: "Failed",
          name: this.$t("m.Failed_Problems"),
        },
      ],
      problem_list: [],
      totalProblemCount: 0,
    }
  },
  methods: {
    init() {
      this.initQuery()
      this.optionInit()
      this.requestTotalCount()
      this.requestData()
    },
    initQuery() {
      this.query.field = this.$route.query.field || ""
      this.query.difficulty = this.$route.query.difficulty || ""
      this.query.status = this.$route.query.status || ""
    },
    optionInit() {
      this.difficultyOptions = Object.keys(DIFFICULTY_MAP).map((key) => ({
        id: key,
        name: DIFFICULTY_MAP[key].value,
      }))
      this.difficultyOptions.unshift({ id: "All", name: this.$t("m.All") })
      this.fieldOptions = Object.keys(FIELD_MAP).map((key) => ({
        id: key,
        name: FIELD_MAP[key].value,
      }))
      this.fieldOptions.unshift({ id: "All", name: this.$t("m.All") })
    },
    requestData() {
      this.isLoading = true
      this.error = 0
      this.problem_list = []
      api
        .getUserProblemInfo(this.username, utils.filterEmptyValue(this.query))
        .then((res) => {
          this.problem_list = res.data.data
          this.syncCalendarToResult()
        })
        .catch((error) => {
          this.error = error.response ? error.response.status : 500
        })
        .finally(() => (this.isLoading = false))
    },
    requestTotalCount() {
      this.isTotalCountLoading = true
      this.totalCountError = 0
      api
        .getUserProblemInfo(this.username, {})
        .then((res) => {
          this.totalProblemCount = this.getUniqueProblemCount(res.data.data)
        })
        .catch((error) => {
          this.totalCountError = error.response ? error.response.status : 500
        })
        .finally(() => (this.isTotalCountLoading = false))
    },
    changeField(newVal) {
      this.query.field = newVal
      this.pushRouter()
    },
    changeStatus(newVal) {
      this.query.status = newVal
      this.pushRouter()
    },
    changeDifficulty(newVal) {
      this.query.difficulty = newVal
      this.pushRouter()
    },
    pushRouter() {
      this.$router.push({
        name: "user-problems",
        params: { username: this.username },
        query: utils.filterEmptyValue(this.query),
      }).catch(() => {})
    },
    moveMonth(amount) {
      this.calendarDate = new Date(
        this.calendarDate.getFullYear(),
        this.calendarDate.getMonth() + amount,
        1
      )
    },
    moveToToday() {
      const today = this.getServiceDate(new Date())
      this.calendarDate = new Date(today.getFullYear(), today.getMonth(), 1)
    },
    visibleProblems(problems) {
      return problems.slice(0, this.maxProblemsPerDay)
    },
    problemStatusClass(problem, blockName) {
      if (problem.status === 0) {
        return `${blockName}--accepted`
      }
      if (problem.status !== undefined && problem.status !== null) {
        return `${blockName}--failed`
      }
      if (this.query.status === "Solved") {
        return `${blockName}--accepted`
      }
      if (this.query.status === "Failed") {
        return `${blockName}--failed`
      }
      return `${blockName}--unknown`
    },
    syncCalendarToResult() {
      if (this.problem_list.length > 0) {
        const latestDate = this.getProblemServiceDate(this.problem_list[0])
        this.calendarDate = new Date(
          latestDate.getFullYear(),
          latestDate.getMonth(),
          1
        )
      }
    },
    getProblemServiceDate(problem) {
      return this.getServiceDate(new Date(problem.submitTime))
    },
    getServiceDate(date) {
      return new Date(
        date.getFullYear(),
        date.getMonth(),
        date.getDate(),
        date.getHours() - 6,
        date.getMinutes(),
        date.getSeconds(),
        date.getMilliseconds()
      )
    },
    formatMonthKey(date) {
      return `${date.getFullYear()}-${`${date.getMonth() + 1}`.padStart(2, "0")}`
    },
    formatDateKey(date) {
      const year = date.getFullYear()
      const month = `${date.getMonth() + 1}`.padStart(2, "0")
      const day = `${date.getDate()}`.padStart(2, "0")
      return `${year}-${month}-${day}`
    },
    createDisplayProblem(problem) {
      const serviceDate = this.getProblemServiceDate(problem)
      return {
        ...problem,
        serviceDate,
        serviceDateKey: this.formatDateKey(serviceDate),
        serviceMonthKey: this.formatMonthKey(serviceDate),
      }
    },
    getProblemIdentity(problem) {
      return problem.id
    },
    getUniqueProblemCount(problems) {
      return new Set(problems.map((problem) => this.getProblemIdentity(problem)))
        .size
    },
    getUniqueDisplayProblems(getGroupKey) {
      const seen = {}
      return this.displayProblems.filter((problem) => {
        const groupKey = getGroupKey(problem)
        const problemKey = this.getProblemIdentity(problem)
        if (!seen[groupKey]) {
          seen[groupKey] = {}
        }
        if (seen[groupKey][problemKey]) {
          return false
        }
        seen[groupKey][problemKey] = true
        return true
      })
    },
    formatCalendarPopoverTitle(date) {
      return `${date.getMonth() + 1}월 ${date.getDate()}일`
    },
  },
  mounted() {
    this.init()
  },
  watch: {
    $route() {
      this.initQuery()
      this.requestData()
    },
    username() {
      this.requestTotalCount()
    },
  },
  computed: {
    calendarTitle() {
      const year = this.calendarDate.getFullYear()
      const month = this.calendarDate.getMonth() + 1
      return this.$t("m.Calendar_Month_Title", { year, month })
    },
    problemCountText() {
      return this.$t("m.Calendar_Problem_Count", {
        count: this.totalProblemCount,
      })
    },
    calendarProblemCountText() {
      return this.$t("m.Calendar_Month_Problem_Count", {
        count: this.currentCalendarMonthProblems.length,
      })
    },
    weekdayLabels() {
      return [
        this.$t("m.Calendar_Weekday_Sun"),
        this.$t("m.Calendar_Weekday_Mon"),
        this.$t("m.Calendar_Weekday_Tue"),
        this.$t("m.Calendar_Weekday_Wed"),
        this.$t("m.Calendar_Weekday_Thu"),
        this.$t("m.Calendar_Weekday_Fri"),
        this.$t("m.Calendar_Weekday_Sat"),
      ]
    },
    problemsByDate() {
      return this.uniqueDailyProblems.reduce((acc, problem) => {
        const key = problem.serviceDateKey
        if (!acc[key]) {
          acc[key] = []
        }
        acc[key].push(problem)
        return acc
      }, {})
    },
    currentCalendarMonthProblems() {
      const year = this.calendarDate.getFullYear()
      const month = this.calendarDate.getMonth()
      return this.uniqueDailyProblems.filter((problem) => {
        const submitDate = problem.serviceDate
        return (
          submitDate.getFullYear() === year && submitDate.getMonth() === month
        )
      })
    },
    sortedProblems() {
      return this.problem_list
        .slice()
        .sort((a, b) => new Date(b.submitTime) - new Date(a.submitTime))
    },
    displayProblems() {
      return this.sortedProblems.map((problem) =>
        this.createDisplayProblem(problem)
      )
    },
    uniqueDailyProblems() {
      return this.getUniqueDisplayProblems((problem) => problem.serviceDateKey)
    },
    uniqueMonthlyProblems() {
      return this.getUniqueDisplayProblems((problem) => problem.serviceMonthKey)
    },
    monthlyProblemGroups() {
      const groups = []
      const groupMap = {}
      this.uniqueMonthlyProblems.forEach((problem) => {
        const submitDate = problem.serviceDate
        const key = problem.serviceMonthKey
        if (!groupMap[key]) {
          groupMap[key] = {
            key,
            title: this.$t("m.Calendar_Month_Title", {
              year: submitDate.getFullYear(),
              month: submitDate.getMonth() + 1,
            }),
            problems: [],
          }
          groups.push(groupMap[key])
        }
        groupMap[key].problems.push(problem)
      })
      return groups
    },
    calendarDays() {
      const year = this.calendarDate.getFullYear()
      const month = this.calendarDate.getMonth()
      const firstDay = new Date(year, month, 1)
      const startDate = new Date(firstDay)
      startDate.setDate(firstDay.getDate() - firstDay.getDay())

      const todayKey = this.formatDateKey(this.getServiceDate(new Date()))
      const days = []
      for (let index = 0; index < 42; index += 1) {
        const date = new Date(startDate)
        date.setDate(startDate.getDate() + index)
        const key = this.formatDateKey(date)
        days.push({
          key,
          date,
          isCurrentMonth: date.getMonth() === month,
          isToday: key === todayKey,
          problems: this.problemsByDate[key] || [],
        })
      }
      return days
    },
    username() {
      let username = ""
      if (
        this.$route &&
        this.$route.params &&
        typeof this.$route.params.username === "string"
      ) {
        username = this.$route.params.username
      }
      if (
        !username &&
        this.$store &&
        this.$store.state.user &&
        this.$store.state.user.profile &&
        this.$store.state.user.profile.user &&
        typeof this.$store.state.user.profile.user.username === "string"
      ) {
        username = this.$store.state.user.profile.user.username
      }
      return username
    },
  },
}
</script>

<style scoped lang="less">
section {
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border: 1px solid #e6e8ee;
  border-radius: 8px;
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.06);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  padding: 24px;

  .problem-tab__header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 20px;
  }

  .problem-tab__title {
    display: flex;
    align-items: baseline;
    gap: 12px;
    min-width: 0;
  }

  .problem-count-summary {
    color: #6b7280;
    font-size: 13px;
    font-weight: 700;
    white-space: nowrap;
  }

  .problem-view-switcher {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-top: 18px;
  }

  .problem-view-tabs {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px;
    border: 1px solid #e5eaf2;
    border-radius: 8px;
    background: #f8fafc;
  }

  .problem-view-tab {
    min-width: 96px;
    height: 34px;
    border: 0;
    border-radius: 6px;
    background: transparent;
    color: #64748b;
    cursor: pointer;
    font-size: 13px;
    font-weight: 700;
    padding: 0 14px;
    transition: background-color 0.15s ease, color 0.15s ease,
      box-shadow 0.15s ease;

    &:hover {
      color: #1f2937;
    }
  }

  .problem-view-tab--active {
    background: #ffffff;
    color: #111827;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.12);
  }

  h1 {
    text-align: left;
    margin: 0;
    color: #111827;
    font-size: 24px;
    line-height: 1.25;
  }

  .query-dropdowns {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: flex-end;
    margin: 0;
    padding: 0;

    li {
      display: flex;
      align-items: center;
      gap: 10px;

      span {
        white-space: nowrap;
        font-size: 1rem;
        font-weight: 500;
      }
    }
  }

  hr {
    border: 0;
    border-top: 1px solid #edf0f5;
    margin: 22px 0;
  }

  .problem-results {
    display: grid;
    gap: 0;
  }

  .calendar-panel {
    display: grid;
    gap: 14px;
  }

  .calendar-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
  }

  .calendar-title {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    color: #111827;

    strong {
      font-size: 18px;
      line-height: 1.3;
    }

    span {
      color: #6b7280;
      font-size: 12px;
    }
  }

  .calendar-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .calendar-nav-button,
  .calendar-today-button {
    height: 36px;
    border: 1px solid #dbe1ea;
    background: #ffffff;
    color: #1f2937;
    border-radius: 6px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.15s ease, border-color 0.15s ease,
      color 0.15s ease;

    &:hover {
      background: #f3f6fb;
      border-color: #c9d3e2;
    }
  }

  .calendar-nav-button {
    width: 36px;
    font-size: 13px;
    line-height: 0;
  }

  .calendar-today-button {
    padding: 0 14px;
    font-size: 13px;
    font-weight: 600;
  }

  .weekday-grid,
  .calendar-grid {
    display: grid;
    grid-template-columns: repeat(7, minmax(0, 1fr));
  }

  .weekday-grid {
    gap: 8px;
  }

  .weekday-cell {
    color: #64748b;
    font-size: 12px;
    font-weight: 700;
    text-align: left;
    text-transform: uppercase;
    padding: 0 8px;
  }

  .calendar-grid {
    gap: 8px;
  }

  .calendar-day {
    position: relative;
    height: 128px;
    border: 1px solid #e5eaf2;
    border-radius: 8px;
    background: #fbfcfe;
    padding: 10px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    min-width: 0;
    overflow: visible;
  }

  .calendar-day--muted {
    background: #f7f8fb;
    color: #9aa4b2;
  }

  .calendar-day--active {
    background: #ffffff;
    border-color: #cdd9ee;
  }

  .calendar-day--has-popover:hover,
  .calendar-day--has-popover:focus-within {
    z-index: 30;

    .calendar-popover {
      opacity: 1;
      pointer-events: auto;
      transform: translate(-50%, -2px);
      visibility: visible;
    }
  }

  .calendar-day--today {
    border-color: #2563eb;
    box-shadow: inset 0 0 0 1px rgba(37, 99, 235, 0.2);
  }

  .calendar-day__top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 22px;
  }

  .calendar-day__number {
    font-size: 13px;
    font-weight: 700;
    color: #334155;
  }

  .calendar-day__count {
    min-width: 22px;
    height: 22px;
    border-radius: 999px;
    background: #1d4ed8;
    color: #ffffff;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 700;
    padding: 0 7px;
  }

  .calendar-day__problems {
    display: flex;
    flex-direction: column;
    gap: 5px;
    min-width: 0;
    overflow: hidden;
  }

  .calendar-problem {
    display: flex;
    align-items: center;
    gap: 5px;
    min-width: 0;
    height: 24px;
    padding: 0 7px;
    border-radius: 5px;
    text-decoration: none;
    font-size: 12px;
    line-height: 1;

    &:hover {
      filter: brightness(0.98);
    }
  }

  .calendar-problem--accepted {
    background: #e7f8ef;
    color: #166534;
  }

  .calendar-problem--failed {
    background: #fff1f2;
    color: #9f1239;
  }

  .calendar-problem--unknown {
    background: #f1f5f9;
    color: #475569;
  }

  .calendar-problem__id {
    font-weight: 800;
    flex: 0 0 auto;
  }

  .calendar-problem__title {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    min-width: 0;
  }

  .calendar-more {
    align-self: flex-start;
    border: 0;
    border-radius: 999px;
    background: #f3f6fb;
    color: #64748b;
    display: inline-flex;
    align-items: center;
    cursor: pointer;
    height: 20px;
    font-size: 12px;
    font-weight: 700;
    line-height: 1;
    padding: 0 7px;

    &:hover {
      background: #e8edf5;
      color: #334155;
    }
  }

  .calendar-popover {
    position: absolute;
    top: calc(100% - 8px);
    left: 50%;
    width: 240px;
    max-width: calc(100vw - 48px);
    z-index: 40;
    border: 1px solid #d7dde7;
    border-radius: 7px;
    background: #ffffff;
    box-shadow: 0 14px 34px rgba(15, 23, 42, 0.18);
    opacity: 0;
    overflow: hidden;
    pointer-events: none;
    transform: translate(-50%, 4px);
    transition: opacity 0.12s ease, transform 0.12s ease,
      visibility 0.12s ease;
    visibility: hidden;
  }

  .calendar-popover__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 9px 10px;
    border-bottom: 1px solid #edf0f5;
    color: #111827;

    strong {
      font-size: 13px;
      line-height: 1.2;
    }

    span {
      color: #6b7280;
      font-size: 11px;
      font-weight: 700;
      white-space: nowrap;
    }
  }

  .calendar-popover__items {
    display: grid;
    gap: 5px;
    max-height: 240px;
    overflow-y: auto;
    padding: 8px;
  }

  .calendar-popover__item {
    display: flex;
    align-items: center;
    gap: 6px;
    min-width: 0;
    border-radius: 5px;
    padding: 6px 7px;
    text-decoration: none;
    transition: background-color 0.12s ease, color 0.12s ease,
      filter 0.12s ease;

    &:hover {
      filter: brightness(0.97);
    }
  }

  .calendar-popover__item--accepted {
    background: #e7f8ef;
    color: #166534;
  }

  .calendar-popover__item--failed {
    background: #fff1f2;
    color: #9f1239;
  }

  .calendar-popover__item--unknown {
    background: #f1f5f9;
    color: #475569;
  }

  .calendar-popover__item-id {
    flex: 0 0 auto;
    font-size: 12px;
    font-weight: 800;
  }

  .calendar-popover__item-title {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 12px;
    font-weight: 500;
  }

  .all-problem-list {
    display: grid;
    gap: 16px;
  }

  .all-problem-list__empty {
    border: 1px dashed #d7deea;
    border-radius: 8px;
    color: #64748b;
    font-size: 14px;
    padding: 18px;
    text-align: center;
  }

  .all-problem-list__groups {
    display: grid;
    gap: 16px;
  }

  .all-problem-month {
    display: grid;
    grid-template-columns: 150px minmax(0, 1fr);
    align-items: start;
    column-gap: 24px;
    padding: 14px 0;
    border-top: 1px solid #edf0f5;

    &:first-child {
      border-top: 0;
      padding-top: 0;
    }

    &:last-child {
      padding-bottom: 0;
    }
  }

  .all-problem-month__title {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 3px;
    margin: 0;
    color: #111827;
    font-size: 15px;
    font-weight: 800;
    line-height: 1.3;
    white-space: nowrap;
  }

  .all-problem-month__count {
    color: #6b7280;
    font-size: 12px;
    font-weight: 700;
  }

  .all-problem-list__items {
    display: flex;
    flex-wrap: wrap;
    gap: 7px 12px;
  }

  .all-problem-item {
    position: relative;
    display: inline-flex;
    align-items: center;
    min-width: 58px;
    justify-content: center;
    color: #1f2937;
    border: 1px solid #d7dde7;
    border-radius: 5px;
    background: #ffffff;
    padding: 5px 8px;
    text-decoration: none;
    transition: background-color 0.15s ease, border-color 0.15s ease,
      color 0.15s ease;

    &:hover {
      background: #f8fafc;
      border-color: #b8c2d1;

      .all-problem-item__tooltip {
        opacity: 1;
        transform: translate(-50%, -4px);
        visibility: visible;
      }
    }
  }

  .all-problem-item--accepted {
    color: #1f6b4f;
    border-color: #b8dccb;
    background: #fbfefc;
  }

  .all-problem-item--failed {
    color: #b42318;
    border-color: #f1b8b3;
    background: #fff7f6;
  }

  .all-problem-item--unknown {
    color: #475569;
    border-color: #cbd5e1;
    background: #f8fafc;
  }

  .all-problem-item__id {
    color: currentColor;
    font-size: 1rem;
    font-weight: 800;
  }

  .all-problem-item__tooltip {
    position: absolute;
    bottom: calc(100% + 8px);
    left: 50%;
    z-index: 20;
    max-width: 240px;
    padding: 7px 9px;
    border: 1px solid #d7dde7;
    border-radius: 6px;
    background: #111827;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.16);
    color: #ffffff;
    font-size: 12px;
    font-weight: 700;
    line-height: 1.35;
    opacity: 0;
    pointer-events: none;
    text-align: center;
    transform: translate(-50%, 0);
    transition: opacity 0.12s ease, transform 0.12s ease,
      visibility 0.12s ease;
    visibility: hidden;
    white-space: normal;
    width: max-content;
  }
}

@media (max-width: 960px) {
  section {
    .problem-tab__header,
    .calendar-toolbar {
      flex-direction: column;
      align-items: stretch;
    }

    .calendar-title {
      align-items: flex-start;
    }

    .query-dropdowns {
      justify-content: flex-start;
    }

    .problem-view-switcher {
      align-items: stretch;
      flex-direction: column;
    }

    .problem-view-tab {
      flex: 1;
    }

    .calendar-actions {
      justify-content: space-between;
    }

    .all-problem-month {
      grid-template-columns: 1fr;
      row-gap: 6px;
    }

    .calendar-day {
      height: 104px;
      padding: 8px;
    }

    .calendar-problem__title {
      display: none;
    }
  }
}

@media (max-width: 680px) {
  section {
    padding: 16px;

    .weekday-grid,
    .calendar-grid {
      gap: 4px;
    }

    .weekday-cell {
      padding: 0 2px;
      font-size: 10px;
      text-align: center;
    }

    .calendar-day {
      height: 78px;
      border-radius: 6px;
      padding: 5px;
    }

    .calendar-day__count {
      min-width: 18px;
      height: 18px;
      font-size: 10px;
      padding: 0 5px;
    }

    .calendar-problem {
      height: 20px;
      justify-content: center;
      padding: 0 4px;
    }
  }
}
</style>
