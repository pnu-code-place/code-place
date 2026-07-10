<script>
import moment from "moment"
import { JUDGE_STATUS } from "../../../../utils/constants"

export default {
  name: "SubmissionListItem",
  props: {
    contestID: {
      type: [String, Number],
      default: "",
    },
    item: {
      type: Object,
      default: () => {},
    },
  },
  computed: {
    submit_time() {
      const submittedAt = moment.utc(this.item.create_time).local()
      const now = moment()
      if (submittedAt.isSame(now, "day")) {
        return `오늘 ${submittedAt.format("HH:mm:ss")}`
      }
      if (submittedAt.isSame(now.clone().subtract(1, "day"), "day")) {
        return `어제 ${submittedAt.format("HH:mm:ss")}`
      }
      return submittedAt.format("YYYY-MM-DD HH:mm:ss")
    },
    problemID() {
      return this.item.problem_id || this.item.problem
    },
    resultDisplay() {
      return this.$t(
        "m." + JUDGE_STATUS[this.item.result].name.replace(/ /g, "_"),
      )
    },
    statusClass() {
      const result = Number(this.item.result)
      const statusMap = {
        "-2": "status-compile-error",
        "-1": "status-wrong-answer",
        0: "status-accepted",
        1: "status-time-limit",
        2: "status-time-limit",
        3: "status-memory-limit",
        4: "status-runtime-error",
        5: "status-system-error",
        6: "status-pending",
        7: "status-judging",
        8: "status-partial",
        9: "status-submitting",
      }
      return statusMap[result] || "status-unknown"
    },
    memory() {
      if (
        this.item.statistic_info.memory_cost === null ||
        this.item.statistic_info.memory_cost === undefined
      ) {
        return "--"
      } else {
        return this.getMemory(this.item.statistic_info.memory_cost)
      }
    },
    running_time() {
      if (
        this.item.statistic_info.time_cost === null ||
        this.item.statistic_info.time_cost === undefined
      ) {
        return "--"
      } else {
        return this.item.statistic_info.time_cost + "ms"
      }
    },
  },
  methods: {
    goStatus() {
      this.$router.push("/status/" + this.item.id)
    },
    goProblem() {
      if (this.contestID) {
        this.$router.push({
          name: "contest-problem-details",
          params: {
            problemID: this.problemID,
            contestID: this.contestID,
          },
        })
      } else {
        this.$router.push({
          name: "problem-details",
          params: { problemID: this.problemID },
        })
      }
    },
    goUser() {
      this.$router.push({
        name: "user-home",
        params: { username: this.item.username },
      })
    },
    getMemory(memory_cost) {
      if (memory_cost > 1024 * 1024 * 1024) {
        return (memory_cost / 1024 / 1024 / 1024).toFixed(1) + "GB"
      } else if (memory_cost > 1024 * 1024) {
        return (memory_cost / 1024 / 1024).toFixed(1) + "MB"
      } else if (memory_cost > 1024) {
        return (memory_cost / 1024).toFixed(1) + "KB"
      } else {
        return memory_cost + "B"
      }
    },
  },
}
</script>

<template>
  <tr @click="goStatus">
    <td class="submitted-at">{{ this.submit_time }}</td>
    <td>
      <button class="problem-link problem-id-link" @click.stop="goProblem">
        {{ problemID }}번
      </button>
    </td>
    <td class="user-cell">
      <div class="user-wrapper">
        <img class="avatar" :src="item.user_avatar" />
        <button class="name-wrapper" @click.stop="goUser">
          {{ item.username }}
        </button>
      </div>
    </td>
    <td class="result-cell">
      <button
        class="status-badge"
        :class="statusClass"
        :aria-label="`제출 결과: ${resultDisplay}`"
        :title="resultDisplay"
        @click.stop="goStatus"
      >
        {{ resultDisplay }}
      </button>
    </td>
    <td class="language-cell">{{ item.language }}</td>
    <td class="numeric">{{ this.running_time }}</td>
    <td class="numeric">{{ this.memory }}</td>
  </tr>
</template>

<style scoped lang="less">
tr {
  cursor: pointer;
  transition: background-color 0.15s ease;
}

tr:hover {
  background-color: #fafbff;
}

td {
  color: #4f5b6f;
  font-size: 14px;
  line-height: 1.35;
  padding: 10px 16px;
  border-bottom: 1px solid #eef1f5;
  vertical-align: middle;
}

.problem-link,
.name-wrapper {
  border: 0;
  background: transparent;
  color: #5661f6;
  cursor: pointer;
  font: inherit;
  padding: 0;
  text-align: left;
}

.problem-link:hover,
.name-wrapper:hover {
  color: #3942d8;
  text-decoration: underline;
}

.problem-id-link {
  font-weight: 700;
  white-space: nowrap;
}

.result-cell {
  text-align: center;
}

.language-cell {
  text-align: center;
}

.user-cell {
  min-width: 150px;
}

.user-wrapper {
  display: flex;
  align-items: center;
  min-width: 0;
}

.name-wrapper {
  display: block;
  margin-left: 7px;
  max-width: 110px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 88px;
  height: 20px;
  padding: 0 8px;
  color: var(--status-ink);
  font-size: 12px;
  font-weight: 700;
  line-height: 1;
  letter-spacing: 0;
  cursor: pointer;
  border: 0;
  border-radius: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  background: var(--status-bg);
  transition:
    background-color 0.15s ease,
    color 0.15s ease;
}

.status-badge:hover {
  background: var(--status-bg-hover);
}

.status-badge:focus-visible {
  outline: 2px solid var(--status-focus);
  outline-offset: 2px;
}

.status-accepted {
  --status-ink: #216e4e;
  --status-bg: #eef8f1;
  --status-bg-hover: #e4f3e9;
  --status-focus: rgba(33, 110, 78, 0.2);
}

.status-wrong-answer {
  --status-ink: #7f5f01;
  --status-bg: #fff7e0;
  --status-bg-hover: #fff2c7;
  --status-focus: rgba(127, 95, 1, 0.2);
}

.status-time-limit,
.status-memory-limit,
.status-partial {
  --status-ink: #9e4c00;
  --status-bg: #fff3e8;
  --status-bg-hover: #ffe9d3;
  --status-focus: rgba(158, 76, 0, 0.2);
}

.status-runtime-error,
.status-compile-error {
  --status-ink: #ae2e24;
  --status-bg: #fff1f0;
  --status-bg-hover: #ffe7e5;
  --status-focus: rgba(174, 46, 36, 0.2);
}

.status-system-error {
  --status-ink: #5d1f1a;
  --status-bg: #f8eeee;
  --status-bg-hover: #f3e3e3;
  --status-focus: rgba(93, 31, 26, 0.2);
}

.status-pending,
.status-judging,
.status-submitting {
  --status-ink: #1558bc;
  --status-bg: #f0f6ff;
  --status-bg-hover: #e6f0ff;
  --status-focus: rgba(21, 88, 188, 0.2);
}

.status-unknown {
  --status-ink: #4f5b6f;
  --status-bg: #f8fafc;
  --status-bg-hover: #f1f5f9;
  --status-focus: rgba(105, 115, 134, 0.2);
}

.numeric {
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.submitted-at {
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

@avatar-radius: 50%;

.avatar {
  flex: none;
  width: 24px;
  height: 24px;
  border-radius: @avatar-radius;
  box-shadow: 0 0 0 1px #e6e9f0;
  object-fit: cover;
}
</style>
