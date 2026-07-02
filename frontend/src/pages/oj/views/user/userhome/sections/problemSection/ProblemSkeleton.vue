<script>
export default {
  name: "ProblemSkeleton",
  computed: {
    calendarDays() {
      return Array.from({ length: 42 }, (_, index) => index)
    },
    weekdays() {
      return Array.from({ length: 7 }, (_, index) => index)
    },
    problemItems() {
      return Array.from({ length: 12 }, (_, index) => index)
    },
  },
}
</script>

<template>
  <div class="problem-skeleton">
    <div class="problem-skeleton__calendar">
      <div class="problem-skeleton__toolbar">
        <span class="skeleton-block skeleton-button"></span>
        <div class="problem-skeleton__title">
          <span class="skeleton-block skeleton-title"></span>
          <span class="skeleton-block skeleton-subtitle"></span>
        </div>
        <div class="problem-skeleton__actions">
          <span class="skeleton-block skeleton-today"></span>
          <span class="skeleton-block skeleton-button"></span>
        </div>
      </div>

      <div class="problem-skeleton__weekdays">
        <span
          v-for="weekday in weekdays"
          :key="weekday"
          class="skeleton-block skeleton-weekday"
        ></span>
      </div>

      <div class="problem-skeleton__days">
        <div
          v-for="day in calendarDays"
          :key="day"
          class="problem-skeleton__day"
        >
          <span class="skeleton-block skeleton-day-number"></span>
          <span
            v-if="day === 24"
            class="skeleton-block skeleton-problem skeleton-problem--wide"
          ></span>
          <span
            v-if="day === 24"
            class="skeleton-block skeleton-problem"
          ></span>
          <span
            v-if="day === 17 || day === 31"
            class="skeleton-block skeleton-problem skeleton-problem--short"
          ></span>
        </div>
      </div>
    </div>

    <div class="problem-skeleton__list">
      <div class="problem-skeleton__list-header">
        <span class="skeleton-block skeleton-list-title"></span>
        <span class="skeleton-block skeleton-list-count"></span>
      </div>
      <div class="problem-skeleton__items">
        <span
          v-for="problem in problemItems"
          :key="problem"
          class="skeleton-block skeleton-list-item"
        ></span>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
@keyframes skeleton-loading {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: -100% 0;
  }
}

.problem-skeleton {
  display: grid;
  gap: 24px;
  width: 100%;
}

.skeleton-block {
  display: block;
  border-radius: 6px;
  background: linear-gradient(90deg, #eef2f7 25%, #f8fafc 37%, #eef2f7 63%);
  background-size: 400% 100%;
  animation: skeleton-loading 1.35s ease-in-out infinite;
}

.problem-skeleton__calendar {
  display: grid;
  gap: 14px;
}

.problem-skeleton__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.problem-skeleton__title {
  display: grid;
  justify-items: center;
  gap: 6px;
}

.problem-skeleton__actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.skeleton-button {
  width: 36px;
  height: 36px;
}

.skeleton-today {
  width: 58px;
  height: 36px;
}

.skeleton-title {
  width: 116px;
  height: 22px;
}

.skeleton-subtitle {
  width: 64px;
  height: 14px;
}

.problem-skeleton__weekdays,
.problem-skeleton__days {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
}

.problem-skeleton__weekdays,
.problem-skeleton__days {
  gap: 8px;
}

.skeleton-weekday {
  width: 24px;
  height: 14px;
  margin-left: 8px;
}

.problem-skeleton__day {
  height: 128px;
  border: 1px solid #e5eaf2;
  border-radius: 8px;
  background: #fbfcfe;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow: hidden;
}

.skeleton-day-number {
  width: 22px;
  height: 16px;
  margin-bottom: 6px;
}

.skeleton-problem {
  width: 54%;
  height: 24px;
}

.skeleton-problem--wide {
  width: 86%;
}

.skeleton-problem--short {
  width: 42%;
}

.problem-skeleton__list {
  display: grid;
  gap: 12px;
  padding: 18px;
  border: 1px solid #e5eaf2;
  border-radius: 8px;
  background: #ffffff;
}

.problem-skeleton__list-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
}

.skeleton-list-title {
  width: 132px;
  height: 24px;
}

.skeleton-list-count {
  width: 58px;
  height: 14px;
}

.problem-skeleton__items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skeleton-list-item {
  width: 64px;
  height: 35px;
}

@media (max-width: 960px) {
  .problem-skeleton__toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .problem-skeleton__title {
    justify-items: start;
  }

  .problem-skeleton__actions {
    justify-content: space-between;
  }

  .problem-skeleton__day {
    height: 104px;
    padding: 8px;
  }
}

@media (max-width: 680px) {
  .problem-skeleton__weekdays,
  .problem-skeleton__days {
    gap: 4px;
  }

  .skeleton-weekday {
    margin: 0 auto;
  }

  .problem-skeleton__day {
    height: 78px;
    border-radius: 6px;
    padding: 5px;
  }

  .skeleton-problem {
    height: 20px;
    width: 100%;
  }
}
</style>
