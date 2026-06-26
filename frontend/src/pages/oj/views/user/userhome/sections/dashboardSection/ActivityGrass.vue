<template>
  <div class="activity-grass" :style="{ '--activity-cell-size': `${cellSize}px` }">
    <div class="activity-heading">
      <div class="activity-title-copy">
        <h2>연속 해결 {{ currentStreak }}일째</h2>
        <span>
          <svg viewBox="0 0 24 24" focusable="false" aria-hidden="true">
            <path
              d="M7 4h10v2h3v2.5c0 2.6-1.8 4.9-4.3 5.5-.7 1.2-1.8 2-3.2 2.3V19H16v2H8v-2h3.5v-2.7c-1.4-.3-2.5-1.1-3.2-2.3C5.8 13.4 4 11.1 4 8.5V6h3V4Zm0 4H6v.5c0 1.3.7 2.5 1.8 3.2C7.3 10.6 7 9.4 7 8Zm10 0c0 1.4-.3 2.6-.8 3.7 1.1-.7 1.8-1.9 1.8-3.2V8h-1Z"
            />
          </svg>
          최장 {{ longestStreak }}일 연속 문제 해결
        </span>
      </div>
      <div class="activity-summary">
        <span class="summary-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" focusable="false">
            <path
              d="M9.4 16.6 4.8 12l1.8-1.8 2.8 2.8 8-8L19.2 7 9.4 16.6Z"
            />
            <path
              d="M12 22C6.5 22 2 17.5 2 12S6.5 2 12 2c1.9 0 3.7.5 5.2 1.5l-1.5 2.1C14.6 4.9 13.3 4.5 12 4.5 7.9 4.5 4.5 7.9 4.5 12s3.4 7.5 7.5 7.5 7.5-3.4 7.5-7.5c0-.6-.1-1.3-.2-1.9l2.4-.7c.2.8.3 1.7.3 2.6 0 5.5-4.5 10-10 10Z"
            />
          </svg>
        </span>
        <div>
          <strong>{{ totalAccepted }}</strong>
          <span>최근 1년 해결 기록</span>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="activity-state">활동 기록을 불러오는 중입니다.</div>
    <ErrorSign v-else-if="error !== 0" :code="error"></ErrorSign>
    <div v-else class="activity-body">
      <div ref="calendarWrap" class="activity-calendar-wrap">
        <div class="month-row">
          <div class="weekday-label-spacer"></div>
          <div class="month-labels">
            <span
              v-for="month in monthLabels"
              :key="month.key"
              :style="{ gridColumn: month.column }"
            >
              {{ month.label }}
            </span>
          </div>
        </div>
        <div class="activity-calendar">
          <div class="weekday-labels">
            <span>월</span>
            <span>화</span>
            <span>수</span>
            <span>목</span>
            <span>금</span>
            <span>토</span>
            <span>일</span>
          </div>
          <div class="activity-weeks">
            <div
              v-for="(week, weekIndex) in weeks"
              :key="weekIndex"
              class="activity-week"
            >
              <span
                v-for="day in week"
                :key="day.key"
                class="activity-day"
                :class="[
                  day.date ? `level-${activityLevel(day.count)}` : 'empty',
                  { today: day.date === activity.end_date },
                ]"
                :aria-label="day.date ? tooltipContent(day) : '빈 날짜'"
                @mouseenter="showTooltip($event, day)"
                @mousemove="moveTooltip($event)"
                @mouseleave="hideTooltip"
              ></span>
            </div>
          </div>
        </div>
      </div>

      <div class="activity-footer">
        <div class="activity-notes">
          <span v-if="totalAccepted === 0">
            <svg viewBox="0 0 24 24" focusable="false" aria-hidden="true">
              <path
                d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm1 15h-2v-2h2v2Zm0-4h-2V7h2v6Z"
              />
            </svg>
            아직 해결 기록이 없습니다.
          </span>
          <span>
            <svg viewBox="0 0 24 24" focusable="false" aria-hidden="true">
              <path
                d="M7 2h2v2h6V2h2v2h3v18H4V4h3V2Zm11 8H6v10h12V10ZM6 8h12V6H6v2Z"
              />
            </svg>
            매일 오전 {{ activity.day_boundary }} 날짜 변경
          </span>
        </div>
        <div class="activity-legend" aria-label="활동 강도 범례">
          <span>적음</span>
          <span
            v-for="level in legendLevels"
            :key="level"
            class="legend-cell"
            :class="`level-${level}`"
          ></span>
          <span>많음</span>
        </div>
      </div>
    </div>
    <div
      v-if="tooltip.visible"
      class="activity-tooltip"
      :style="{ left: `${tooltip.x}px`, top: `${tooltip.y}px` }"
    >
      {{ tooltip.text }}
    </div>
  </div>
</template>

<script>
import api from "@oj/api"
import ErrorSign from "../../../../general/ErrorSign.vue"

const ACTIVITY_DAYS = 365
const MAX_CELL_SIZE = 14
const MIN_CELL_SIZE = 3
const WEEKDAY_LABEL_WIDTH = 24
const CALENDAR_COLUMN_GAP = 8
const CELL_GAP = 2

function formatDate(date) {
  const year = date.getFullYear()
  const month = `${date.getMonth() + 1}`.padStart(2, "0")
  const day = `${date.getDate()}`.padStart(2, "0")
  return `${year}-${month}-${day}`
}

function parseLocalDate(dateString) {
  const [year, month, day] = dateString.split("-").map(Number)
  return new Date(year, month - 1, day)
}

function addDays(date, days) {
  const nextDate = new Date(date)
  nextDate.setDate(nextDate.getDate() + days)
  return nextDate
}

export default {
  name: "activity-grass",
  components: {
    ErrorSign,
  },
  data() {
    return {
      isLoading: true,
      error: 0,
      activity: {
        start_date: "",
        end_date: "",
        total: 0,
        max_count: 0,
        current_streak: 0,
        longest_streak: 0,
        day_boundary: "06:00 UTC+9",
        days: [],
      },
      legendLevels: [0, 1, 2, 3, 4],
      tooltip: {
        visible: false,
        text: "",
        x: 0,
        y: 0,
      },
      cellSize: MAX_CELL_SIZE,
      resizeObserver: null,
    }
  },
  computed: {
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
    totalAccepted() {
      return this.activity.total || 0
    },
    countByDate() {
      return this.activity.days.reduce((map, day) => {
        map[day.date] = day.count
        return map
      }, {})
    },
    currentStreak() {
      return this.activity.current_streak || 0
    },
    longestStreak() {
      return this.activity.longest_streak || 0
    },
    weeks() {
      if (!this.activity.start_date || !this.activity.end_date) {
        return []
      }

      const startDate = parseLocalDate(this.activity.start_date)
      const endDate = parseLocalDate(this.activity.end_date)
      const firstCalendarDate = new Date(startDate)
      const daysFromMonday = (startDate.getDay() + 6) % 7
      firstCalendarDate.setDate(startDate.getDate() - daysFromMonday)

      const weeks = []
      let currentDate = firstCalendarDate

      while (currentDate <= endDate) {
        const week = []
        for (let weekday = 0; weekday < 7; weekday += 1) {
          const dateKey = formatDate(currentDate)
          const isInRange = currentDate >= startDate && currentDate <= endDate
          week.push({
            key: `${dateKey}-${weekday}`,
            date: isInRange ? dateKey : "",
            count: isInRange ? this.countByDate[dateKey] || 0 : 0,
          })
          currentDate = addDays(currentDate, 1)
        }
        weeks.push(week)
      }

      return weeks
    },
    monthLabels() {
      const labels = []
      const seenMonths = {}
      this.weeks.forEach((week, index) => {
        week.forEach((day) => {
          if (!day.date) {
            return
          }
          const date = parseLocalDate(day.date)
          const month = date.getMonth()
          const monthKey = `${date.getFullYear()}-${month}`
          const isFirstVisibleDate = day.date === this.activity.start_date
          if (seenMonths[monthKey] || (!isFirstVisibleDate && date.getDate() !== 1)) {
            return
          }
          seenMonths[monthKey] = true
          labels.push({
            key: monthKey,
            label: `${month + 1}월`,
            column: `${index + 1}`,
          })
        })
      })
      return labels
    },
  },
  watch: {
    username() {
      this.fetchActivity()
    },
    weeks() {
      this.$nextTick(this.updateCellSize)
    },
  },
  mounted() {
    this.fetchActivity()
    this.$nextTick(() => {
      this.updateCellSize()
      if (typeof ResizeObserver !== "undefined") {
        this.resizeObserver = new ResizeObserver(this.updateCellSize)
        this.resizeObserver.observe(this.$el)
      } else {
        window.addEventListener("resize", this.updateCellSize)
      }
    })
  },
  beforeDestroy() {
    if (this.resizeObserver) {
      this.resizeObserver.disconnect()
    } else {
      window.removeEventListener("resize", this.updateCellSize)
    }
  },
  methods: {
    fetchActivity() {
      if (!this.username) {
        this.isLoading = false
        return
      }

      this.isLoading = true
      this.error = 0
      api
        .getUserActivity(this.username, ACTIVITY_DAYS)
        .then((res) => {
          this.activity = res.data.data
          this.isLoading = false
          this.$nextTick(this.updateCellSize)
        })
        .catch((err) => {
          this.isLoading = false
          this.error = err.response ? err.response.status : 500
        })
    },
    activityLevel(count) {
      if (count <= 0) {
        return 0
      }
      if (count === 1) {
        return 1
      }
      if (count <= 3) {
        return 2
      }
      if (count <= 6) {
        return 3
      }
      return 4
    },
    tooltipContent(day) {
      return `${day.date}: 해결 ${day.count}개`
    },
    showTooltip(event, day) {
      if (!day.date) {
        return
      }
      this.tooltip.text = this.tooltipContent(day)
      this.tooltip.visible = true
      this.moveTooltip(event)
    },
    moveTooltip(event) {
      if (!this.tooltip.visible) {
        return
      }
      this.tooltip.x = event.clientX + 12
      this.tooltip.y = event.clientY - 34
    },
    hideTooltip() {
      this.tooltip.visible = false
    },
    updateCellSize() {
      const calendarWrap = this.$refs.calendarWrap
      if (!calendarWrap) {
        return
      }

      const weekCount = this.weeks.length || 53
      const availableWidth =
        calendarWrap.clientWidth - WEEKDAY_LABEL_WIDTH - CALENDAR_COLUMN_GAP
      const totalGapWidth = Math.max(weekCount - 1, 0) * CELL_GAP
      const fittedSize = Math.floor((availableWidth - totalGapWidth) / weekCount)
      this.cellSize = Math.max(MIN_CELL_SIZE, Math.min(MAX_CELL_SIZE, fittedSize))
    },
  },
}
</script>

<style scoped lang="less">
.activity-grass {
  --activity-cell-gap: 2px;
  --activity-week-label-width: 24px;

  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 2px 0 6px;
}

.activity-heading {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  padding: 0 10px;
}

.activity-title-copy {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.activity-heading h2 {
  text-align: left;
  font-size: 24px;
  font-weight: 800;
  line-height: 1.25;
  margin: 0;
  color: #111827;
}

.activity-title-copy span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: #6b7280;
  font-size: 13px;
  font-weight: 700;
  line-height: 1.2;
}

.activity-title-copy span svg {
  width: 14px;
  height: 14px;
  flex: 0 0 14px;
  fill: #9aa3b2;
}

.activity-summary {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #6b7280;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  padding-top: 4px;
}

.activity-summary > div {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.summary-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  color: #17945f;
}

.summary-icon svg {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

.activity-summary strong {
  color: #111827;
  font-size: 28px;
  font-weight: 800;
  line-height: 1;
}

.activity-summary span:not(.summary-icon) {
  color: #6f7787;
  line-height: 1.2;
}

.activity-legend {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #7b8190;
  font-size: 12px;
  line-height: 10px;
  white-space: nowrap;
}

.legend-cell {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  display: block;
}

.activity-state {
  min-height: 110px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  font-size: 14px;
}

.activity-body {
  min-width: 0;
}

.activity-calendar-wrap {
  overflow-x: hidden;
  padding: 2px 10px 10px;
}

.activity-calendar {
  display: flex;
  gap: 8px;
  width: 100%;
}

.month-row {
  display: flex;
  gap: 8px;
  width: 100%;
}

.weekday-label-spacer {
  width: var(--activity-week-label-width);
  flex-shrink: 0;
}

.month-labels {
  display: grid;
  grid-auto-columns: var(--activity-cell-size);
  grid-auto-flow: column;
  gap: var(--activity-cell-gap);
  flex: 1 1 auto;
  margin-bottom: 8px;
  color: #7b8190;
  font-size: 12px;
  font-weight: 600;
  line-height: 1;
  min-width: 0;
  text-align: left;
  white-space: nowrap;
}

.weekday-labels {
  display: grid;
  grid-template-rows: repeat(7, var(--activity-cell-size));
  gap: var(--activity-cell-gap);
  color: #7b8190;
  font-size: 11px;
  font-weight: 600;
  line-height: var(--activity-cell-size);
  text-align: right;
  width: var(--activity-week-label-width);
  flex-shrink: 0;
}

.activity-weeks {
  display: flex;
  gap: var(--activity-cell-gap);
  flex: 1 1 auto;
  min-width: 0;
}

.activity-week {
  display: grid;
  grid-template-rows: repeat(7, var(--activity-cell-size));
  gap: var(--activity-cell-gap);
  flex: 0 0 var(--activity-cell-size);
}

.activity-day {
  width: var(--activity-cell-size);
  height: var(--activity-cell-size);
  border-radius: 2px;
  display: block;
  transition:
    transform 0.12s ease;
}

.activity-day:hover {
  transform: scale(1.15);
}

.activity-day.empty {
  background: transparent;
}

.level-0 {
  background-color: #eef1f5;
}

.level-1 {
  background-color: #b9ead1;
}

.level-2 {
  background-color: #68d391;
}

.level-3 {
  background-color: #2f9e66;
}

.level-4 {
  background-color: #166342;
}

.activity-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  padding: 0 10px;
}

.activity-notes {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  color: #7c8493;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.25;
  text-align: left;
}

.activity-notes span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.activity-notes svg {
  width: 13px;
  height: 13px;
  flex: 0 0 13px;
  fill: #a0a8b6;
}

.activity-tooltip {
  position: fixed;
  z-index: 3000;
  pointer-events: none;
  padding: 7px 9px;
  color: #fff;
  background: rgba(17, 24, 39, 0.94);
  border-radius: 4px;
  box-shadow: 0 6px 16px rgba(17, 24, 39, 0.18);
  font-size: 12px;
  font-weight: 700;
  line-height: 1.2;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .activity-grass {
    gap: 14px;
  }

  .activity-heading,
  .activity-footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .activity-heading {
    gap: 12px;
  }

  .activity-summary {
    padding-top: 0;
  }
}
</style>
