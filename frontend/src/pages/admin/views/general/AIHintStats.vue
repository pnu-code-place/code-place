<template>
  <div class="view" v-loading="loading">
    <Panel :title="$t('m.AI_Hint_Stats')">
      <div slot="header">
        <el-row type="flex" justify="end" align="middle">
          <span class="range-label" v-if="stats.range.start">
            {{ stats.range.start }} ~ {{ stats.range.end }}
          </span>
          <el-date-picker
            v-model="range"
            type="daterange"
            value-format="yyyy-MM-dd"
            unlink-panels
            :picker-options="pickerOptions"
            :start-placeholder="$t('m.AI_Hint_Start_Date')"
            :end-placeholder="$t('m.AI_Hint_End_Date')"
            @change="scheduleFetch"
            @blur="pickedAt = null"
            @visible-change="(open) => open || (pickedAt = null)"
          />
        </el-row>
      </div>

      <div class="group" v-for="group in summaryGroups" :key="group.title">
        <p class="group-title">{{ group.title }}</p>
        <div class="stat-row">
          <div class="stat-card" v-for="card in group.cards" :key="card.label">
            <p class="stat-value">{{ card.value }}</p>
            <p class="stat-label">{{ card.label }}</p>
            <p class="stat-note">{{ card.note }}</p>
          </div>
        </div>
      </div>
    </Panel>

    <Panel :title="$t('m.AI_Hint_Top_Problems')">
      <el-table :data="stats.top_problems" border :empty-text="$t('m.AI_Hint_Empty')">
        <el-table-column prop="display_id" :label="$t('m.AI_Hint_Problem_ID')" width="120" />
        <el-table-column prop="title" :label="$t('m.AI_Hint_Problem_Title')" />
        <el-table-column prop="turns" :label="$t('m.AI_Hint_Turns')">
          <template slot-scope="scope">
            <div class="cell-bar">
              <span class="cell-bar-track">
                <i :style="{ width: barWidth(scope.row.turns) }"></i>
              </span>
              <b>{{ scope.row.turns }}</b>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="users" :label="$t('m.AI_Hint_Users')" width="120" />
      </el-table>
    </Panel>

    <Panel :title="$t('m.AI_Hint_Contests')">
      <el-table :data="stats.contests" border :empty-text="$t('m.AI_Hint_Empty')">
        <el-table-column prop="title" :label="$t('m.AI_Hint_Contest_Title')" />
        <el-table-column prop="start_date" :label="$t('m.AI_Hint_Contest_Start')" width="120" />
        <el-table-column prop="turns" :label="$t('m.AI_Hint_Card_Contest_Turns')" width="110" />
        <el-table-column prop="users" :label="$t('m.AI_Hint_Users')" width="110" />
        <el-table-column prop="problems" :label="$t('m.AI_Hint_Contest_Problems')" width="130" />
        <el-table-column :label="limitReachedLabel" width="150">
          <template slot-scope="scope">{{ scope.row.limit_reached_rate }}%</template>
        </el-table-column>
      </el-table>
    </Panel>

    <Panel :title="$t('m.AI_Hint_Recent_Questions')">
      <p class="hint-note">
        {{ $t("m.AI_Hint_Recent_Note", { count: stats.recent_questions.length }) }}
      </p>
      <el-table :data="stats.recent_questions" border :empty-text="$t('m.AI_Hint_Empty')">
        <el-table-column prop="created_at" :label="$t('m.AI_Hint_Asked_At')" width="140" />
        <el-table-column :label="$t('m.AI_Hint_Problem')" width="160" show-overflow-tooltip>
          <template slot-scope="scope">{{ scope.row.display_id }} {{ scope.row.title }}</template>
        </el-table-column>
        <el-table-column prop="user" :label="$t('m.AI_Hint_User')" width="100" />
        <el-table-column :label="$t('m.AI_Hint_Question')">
          <template slot-scope="scope">
            <span class="question">{{ scope.row.question }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('m.AI_Hint_Code')" width="100">
          <template slot-scope="scope">{{ scope.row.has_code ? scope.row.language : "-" }}</template>
        </el-table-column>
      </el-table>
    </Panel>
  </div>
</template>

<script>
import api from "../../api.js"

const EMPTY = {
  range: { start: "", end: "", max_range_span_days: 0 },
  practice: {
    turns: 0,
    chat_turns: 0,
    users: 0,
    problems: 0,
    hinted_pairs: 0,
    engaged_pairs: 0,
    adoption_rate: 0,
  },
  contest: { turns: 0, users: 0, contests: 0, limit: 0 },
  top_problems: [],
  contests: [],
  recent_questions: [],
}

const DAY_MS = 24 * 60 * 60 * 1000

export default {
  name: "AIHintStats",
  data() {
    return {
      loading: false,
      requestSeq: 0,
      pickedAt: null,
      // 응답이 실패해도 폭 제한이 풀리면 안 되므로 stats 와 따로 들고 있는다.
      maxRangeSpanDays: 0,
      fetchTimer: null,
      range: [],
      stats: JSON.parse(JSON.stringify(EMPTY)),
    }
  },
  mounted() {
    this.fetch()
  },
  computed: {
    // 백엔드 MAX_RANGE_DAYS 와 같은 폭으로 막는다. 넘겨 고르면 서버가 거절하고
    // 화면이 0으로 비워져 무슨 일이 난 건지 알 수 없다.
    pickerOptions() {
      return {
        disabledDate: (date) => {
          if (date > new Date()) return true
          if (!this.pickedAt || !this.maxRangeMs) return false
          return Math.abs(date - this.pickedAt) > this.maxRangeMs
        },
        onPick: ({ minDate, maxDate }) => {
          this.pickedAt = maxDate ? null : minDate
        },
      }
    },
    maxRangeMs() {
      // 허용 폭은 서버가 계산해 응답에 실어 보낸다. 아직 모르면 폭 검사를 쉰다.
      return this.maxRangeSpanDays * DAY_MS
    },
    maxTopProblemTurns() {
      return Math.max(...this.stats.top_problems.map((p) => p.turns), 1)
    },
    // 응답 전에는 한도를 모르므로 숫자 없는 문구를 쓴다.
    limitReachedLabel() {
      const limit = this.stats.contest.limit
      return limit
        ? this.$t("m.AI_Hint_Limit_Reached_Rate", { limit })
        : this.$t("m.AI_Hint_Limit_Reached_Rate_Plain")
    },
    summaryGroups() {
      const p = this.stats.practice
      const c = this.stats.contest
      const legacy = p.turns - p.chat_turns
      return [
        {
          title: this.$t("m.AI_Hint_Practice"),
          cards: [
            {
              label: this.$t("m.AI_Hint_Card_Turns"),
              value: p.turns,
              // 자유 질문 도입 전 기간까지 조회했을 때만 옛 단계 힌트를 따로 알려 준다.
              note: legacy
                ? this.$t("m.AI_Hint_Card_Turns_Note", { chat: p.chat_turns, legacy })
                : "",
            },
            { label: this.$t("m.AI_Hint_Card_Users"), value: p.users, note: "" },
            { label: this.$t("m.AI_Hint_Card_Problems"), value: p.problems, note: "" },
            {
              label: this.$t("m.AI_Hint_Card_Adoption"),
              value: p.adoption_rate + "%",
              note: this.$t("m.AI_Hint_Card_Adoption_Note", {
                engaged: p.engaged_pairs,
                hinted: p.hinted_pairs,
              }),
            },
          ],
        },
        {
          title: this.$t("m.AI_Hint_Contest"),
          cards: [
            { label: this.$t("m.AI_Hint_Card_Contest_Turns"), value: c.turns, note: "" },
            { label: this.$t("m.AI_Hint_Card_Users"), value: c.users, note: "" },
            { label: this.$t("m.AI_Hint_Card_Contests"), value: c.contests, note: "" },
          ],
        },
      ]
    },
  },
  beforeDestroy() {
    clearTimeout(this.fetchTimer)
  },
  methods: {
    barWidth(turns) {
      return Math.round((100 * turns) / this.maxTopProblemTurns) + "%"
    },
    // 달력을 연달아 바꾸면 요청이 겹친다. 마지막 선택만 실제로 보낸다.
    scheduleFetch() {
      clearTimeout(this.fetchTimer)
      this.fetchTimer = setTimeout(this.fetch, 250)
    },
    fetch() {
      // 느린 응답이 나중에 도착해 최신 결과를 덮어쓰지 않도록 마지막 요청만 반영한다.
      const seq = ++this.requestSeq
      this.loading = true
      const [start, end] = this.range || []
      api
        .getAIHintStats(start, end)
        .then((res) => {
          if (seq !== this.requestSeq) return
          this.stats = res.data.data
          this.maxRangeSpanDays =
            this.stats.range.max_range_span_days || this.maxRangeSpanDays
          this.loading = false
        })
        .catch(() => {
          if (seq !== this.requestSeq) return
          // 실패한 구간의 화면에 이전 구간 숫자가 남아 있으면 오독한다.
          this.stats = JSON.parse(JSON.stringify(EMPTY))
          this.loading = false
        })
    },
  },
}
</script>

<style scoped lang="less">
.group + .group {
  margin-top: 16px;
}

.group-title {
  margin: 0 0 8px;
  color: #5c6773;
  font-weight: 700;
  font-size: 14px;
}

.stat-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.stat-card {
  flex: 1 1 150px;
  padding: 12px;
  border: 1px solid #eeeeee;
  border-radius: 4px;
  text-align: center;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #409eff;
  margin: 0;
}

.stat-label {
  margin: 4px 0 0;
  color: #5c6773;
  font-size: 13px;
}

.stat-note {
  margin: 2px 0 0;
  color: #999999;
  font-size: 11px;
  min-height: 14px;
}

.cell-bar {
  display: flex;
  align-items: center;
  gap: 8px;

  b {
    font-weight: 600;
    font-variant-numeric: tabular-nums;
  }
}

.cell-bar-track {
  flex: 1;
  min-width: 40px;
  max-width: 120px;
  height: 7px;
  border-radius: 4px;
  background: #eef1f5;
  overflow: hidden;

  i {
    display: block;
    height: 100%;
    border-radius: 4px;
    background: #409eff;
  }
}

.question {
  white-space: pre-wrap;
  word-break: break-word;
}

.range-label {
  margin-right: 12px;
  font-size: 12px;
  color: #909399;
  align-self: center;
}

.hint-note {
  margin: 0 0 8px;
  color: #999999;
  font-size: 12px;
}
</style>
