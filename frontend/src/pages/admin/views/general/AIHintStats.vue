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

      <div class="stat-row">
        <div class="stat-card" v-for="card in summaryCards" :key="card.label">
            <p class="stat-value">{{ card.value }}</p>
            <p class="stat-label">{{ card.label }}</p>
            <p class="stat-note">{{ card.note }}</p>
        </div>
      </div>
    </Panel>

    <Panel :title="$t('m.AI_Hint_Usage_Trend')">
      <el-row :gutter="12">
        <el-col :span="14">
          <div class="chart-title">{{ $t("m.AI_Hint_Monthly") }}</div>
          <ECharts :option="monthlyOption" class="chart" />
        </el-col>
        <el-col :span="10">
          <div class="chart-title">{{ $t("m.AI_Hint_Hourly") }}</div>
          <ECharts :option="hourlyOption" class="chart" />
        </el-col>
      </el-row>
    </Panel>

    <Panel :title="$t('m.AI_Hint_Depth')">
      <el-row :gutter="12">
        <el-col :span="14">
          <div class="chart-title">{{ $t("m.AI_Hint_Turn_Distribution") }}</div>
          <ECharts :option="depthOption" class="chart" />
        </el-col>
        <el-col :span="10">
          <div class="depth-summary">
            <p>
              {{ $t("m.AI_Hint_Avg_Turns") }}
              <b>{{ depth.avg_turns }}</b>
            </p>
            <p>
              {{ $t("m.AI_Hint_Single_Turn_Rate") }}
              <b>{{ depth.single_turn_rate }}%</b>
            </p>
            <p>
              {{ limitReachedLabel }}
              <b>{{ depth.limit_reached_rate }}%</b>
            </p>
          </div>
        </el-col>
      </el-row>
    </Panel>

    <Panel :title="$t('m.AI_Hint_Quality')">
      <el-row :gutter="12">
        <el-col :span="12">
          <p>
            {{ $t("m.AI_Hint_Label_Rate") }}
            <b>{{ quality.label_rate }}%</b>
            <span class="hint-note">{{ $t("m.AI_Hint_Label_Note") }}</span>
          </p>
        </el-col>
        <el-col :span="12">
          <p>{{ $t("m.AI_Hint_Length") }}</p>
          <div class="range">
            <span class="range-track">
              <i :style="{ width: lengthScale.p90 + '%' }"></i>
              <em class="range-tick" :style="{ left: lengthScale.p50 + '%' }"></em>
              <em class="range-tick" :style="{ left: lengthScale.p90 + '%' }"></em>
            </span>
            <span class="range-scale">
              <span>{{ $t("m.AI_Hint_Length_Median") }} {{ quality.length.p50 }}</span>
              <span>{{ $t("m.AI_Hint_Length_P90") }} {{ quality.length.p90 }}</span>
              <span>{{ $t("m.AI_Hint_Length_Max") }} {{ quality.length.max }}</span>
            </span>
          </div>
        </el-col>
      </el-row>
    </Panel>

    <Panel :title="$t('m.AI_Hint_Top_Problems')">
      <el-table :data="topProblems" border>
        <el-table-column
          prop="display_id"
          :label="$t('m.AI_Hint_Problem_ID')"
          width="120"
        />
        <el-table-column prop="title" :label="$t('m.AI_Hint_Problem_Title')" />
        <el-table-column prop="turns" :label="$t('m.AI_Hint_Turns')">
          <template slot-scope="scope">
            <div class="cell-bar">
              <span class="cell-bar-track">
                <i :style="{ width: topProblemWidth(scope.row.turns) }"></i>
              </span>
              <b>{{ scope.row.turns }}</b>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="sessions" :label="$t('m.AI_Hint_Sessions')" />
        <el-table-column prop="users" :label="$t('m.AI_Hint_Users')" />
      </el-table>
    </Panel>
  </div>
</template>

<script>
import api from "../../api.js"

const EMPTY = {
  summary: {
    turns: 0,
    sessions: 0,
    users: 0,
    problems: 0,
    hinted_pairs: 0,
    engaged_pairs: 0,
    adoption_rate: 0,
  },
  range: { start: "", end: "", session_gap_minutes: 0, max_range_span_days: 0 },
  monthly: [],
  hourly: [],
  depth: {
    distribution: [],
    avg_turns: 0,
    single_turn_rate: 0,
    limit_reached_rate: 0,
    limit: 0,
  },
  quality: {
    length: { p50: 0, p90: 0, max: 0 },
    label_rate: 0,
  },
  top_problems: [],
}

const DAY_MS = 24 * 60 * 60 * 1000

// 순서형 램프. 진한 쪽이 앞 단계다. 색만으로 구분하지 않도록 막대에 값도 함께 찍는다.
const ORDINAL = ["#1c5cab", "#2a78d6", "#3987e5", "#5598e7", "#86b6ef"]
const MUTED = "#c6dcf7"

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
      // 허용 폭은 서버가 계산해 응답에 실어 보낸다. 포함/배타 규칙을 여기서
      // 다시 세면 서버가 바뀔 때 조용히 어긋난다. 아직 모르면 폭 검사를 쉰다.
      return this.maxRangeSpanDays * DAY_MS
    },
    maxTopProblemTurns() {
      return Math.max(...this.topProblems.map((p) => p.turns), 1)
    },
    limitReachedLabel() {
      return this.depth.limit
        ? this.$t("m.AI_Hint_Limit_Reached_Rate", { limit: this.depth.limit })
        : this.$t("m.AI_Hint_Limit_Reached_Rate_Plain")
    },
    summary() {
      return this.stats.summary
    },
    depth() {
      return this.stats.depth
    },
    quality() {
      return this.stats.quality
    },
    topProblems() {
      return this.stats.top_problems
    },
    summaryCards() {
      const s = this.summary
      return [
        {
          label: this.$t("m.AI_Hint_Card_Turns"),
          value: s.turns,
          note: "",
        },
        {
          label: this.$t("m.AI_Hint_Sessions"),
          value: s.sessions,
          // 아직 응답이 없으면 간격을 모르므로 설명을 비워 둔다.
          note: this.stats.range.session_gap_minutes
            ? this.$t("m.AI_Hint_Card_Sessions_Note", {
                minutes: this.stats.range.session_gap_minutes,
              })
            : "",
        },
        {
          label: this.$t("m.AI_Hint_Card_Users"),
          value: s.users,
          note: "",
        },
        {
          label: this.$t("m.AI_Hint_Card_Problems"),
          value: s.problems,
          note: "",
        },
        {
          label: this.$t("m.AI_Hint_Card_Adoption"),
          value: s.adoption_rate + "%",
          note: `${s.hinted_pairs} / ${s.engaged_pairs}`,
        },
      ]
    },
    monthlyOption() {
      const months = this.stats.monthly.map((m) => m.month)
      return {
        tooltip: { trigger: "axis" },
        legend: {
          data: [
            this.$t("m.AI_Hint_Turns"),
            this.$t("m.AI_Hint_Sessions"),
            this.$t("m.AI_Hint_Users"),
          ],
        },
        grid: { left: 40, right: 16, top: 40, bottom: 28 },
        xAxis: { type: "category", data: months },
        yAxis: { type: "value", minInterval: 1 },
        series: [
          {
            name: this.$t("m.AI_Hint_Turns"),
            type: "line",
            smooth: true,
            data: this.stats.monthly.map((m) => m.turns),
          },
          {
            name: this.$t("m.AI_Hint_Sessions"),
            type: "line",
            smooth: true,
            data: this.stats.monthly.map((m) => m.sessions),
          },
          {
            name: this.$t("m.AI_Hint_Users"),
            type: "line",
            smooth: true,
            data: this.stats.monthly.map((m) => m.users),
          },
        ],
      }
    },
    // 요점이 하나인 막대는 그 하나만 진하게, 나머지는 물러나게 한다.
    hourlyOption() {
      const values = this.stats.hourly.map((h) => h.turns)
      const peak = Math.max(...values, 0)
      return {
        tooltip: { trigger: "axis" },
        grid: { left: 40, right: 16, top: 24, bottom: 28 },
        xAxis: { type: "category", data: this.stats.hourly.map((h) => h.hour) },
        yAxis: { type: "value", minInterval: 1 },
        series: [
          {
            name: this.$t("m.AI_Hint_Turns"),
            type: "bar",
            data: values.map((v) => ({
              value: v,
              itemStyle: { color: v === peak && peak > 0 ? ORDINAL[0] : MUTED },
            })),
          },
        ],
      }
    },
    // "N턴짜리 대화가 몇 건"이 아니라 "몇 건이 N턴까지 이어졌나"를 보여준다.
    // 어디에서 멈추는지가 알고 싶은 것이고, 그건 누적 잔존이라야 보인다.
    retention() {
      const dist = this.depth.distribution
      if (!dist.length) return []
      const maxTurn = Math.max(...dist.map((d) => d.turns))
      const total = dist.reduce((sum, d) => sum + d.sessions, 0)
      const rows = []
      for (let turn = 1; turn <= maxTurn; turn++) {
        const sessions = dist
          .filter((d) => d.turns >= turn)
          .reduce((sum, d) => sum + d.sessions, 0)
        rows.push({
          turn,
          sessions,
          rate: total ? Math.round((1000 * sessions) / total) / 10 : 0,
        })
      }
      return rows
    },
    depthOption() {
      const rows = this.retention
      return {
        tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
        grid: { left: 64, right: 72, top: 16, bottom: 24 },
        xAxis: { type: "value", minInterval: 1 },
        yAxis: {
          type: "category",
          inverse: true,
          data: rows.map((r) => this.$t("m.AI_Hint_Nth_Turn", { n: r.turn })),
          axisTick: { show: false },
        },
        series: [
          {
            name: this.$t("m.AI_Hint_Sessions"),
            type: "bar",
            barWidth: 18,
            data: rows.map((r, i) => ({
              value: r.sessions,
              itemStyle: { color: ORDINAL[i % ORDINAL.length] },
            })),
            label: {
              show: true,
              position: "right",
              formatter: (p) =>
                this.$t("m.AI_Hint_Session_Count", {
                  count: rows[p.dataIndex].sessions,
                }) + ` · ${rows[p.dataIndex].rate}%`,
              color: "#5c6773",
            },
          },
        ],
      }
    },
    // 응답 길이는 분포이므로 눈금 두 개를 얹은 범위 막대로 보여준다.
    lengthScale() {
      const max = Math.max(this.quality.length.max, 1)
      const pct = (v) => Math.min(100, Math.round((1000 * v) / max) / 10)
      return { p50: pct(this.quality.length.p50), p90: pct(this.quality.length.p90) }
    },
  },
  beforeDestroy() {
    clearTimeout(this.fetchTimer)
  },
  methods: {
    topProblemWidth(turns) {
      return Math.round((100 * turns) / this.maxTopProblemTurns) + "%"
    },
    // 달력을 연달아 바꾸면 요청이 겹친다. 응답만 버리면 질의는 그대로 나가므로
    // 마지막 선택만 실제로 보낸다.
    scheduleFetch() {
      clearTimeout(this.fetchTimer)
      this.fetchTimer = setTimeout(this.fetch, 250)
    },
    fetch() {
      // 날짜를 빠르게 바꾸면 느린 응답이 나중에 도착해 최신 결과를 덮어쓸 수 있다.
      // 마지막 요청만 반영한다.
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

.chart {
  width: 100%;
  height: 260px;
}

.chart-title {
  color: #5c6773;
  font-weight: 700;
  font-size: 14px;
  margin-bottom: 8px;
}

.depth-summary {
  padding-top: 24px;

  p {
    margin: 0 0 10px;
    color: #5c6773;
  }
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

.range {
  margin-top: 4px;
}

.range-track {
  position: relative;
  display: block;
  height: 10px;
  border-radius: 5px;
  background: #eef1f5;

  i {
    display: block;
    height: 100%;
    border-radius: 5px;
    background: rgba(64, 158, 255, 0.28);
  }
}

.range-tick {
  position: absolute;
  top: -4px;
  width: 2px;
  height: 18px;
  background: #409eff;
}

.range-scale {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 12px;
  color: #909399;
  font-variant-numeric: tabular-nums;
}

.range-label {
  margin-right: 12px;
  font-size: 12px;
  color: #909399;
  align-self: center;
}

.hint-note {
  color: #999999;
  font-size: 12px;
}

</style>
