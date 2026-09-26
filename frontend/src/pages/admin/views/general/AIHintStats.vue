<template>
  <div class="view" v-loading="loading">
    <Panel :title="$t('m.AI_Hint_Stats')">
      <div slot="header">
        <el-row type="flex" justify="end" align="middle">
          <el-date-picker
            v-model="range"
            type="daterange"
            value-format="yyyy-MM-dd"
            unlink-panels
            :start-placeholder="$t('m.AI_Hint_Start_Date')"
            :end-placeholder="$t('m.AI_Hint_End_Date')"
            @change="fetch"
          />
        </el-row>
      </div>

      <el-row :gutter="12">
        <el-col :span="4" v-for="card in summaryCards" :key="card.label">
          <div class="stat-card">
            <p class="stat-value">{{ card.value }}</p>
            <p class="stat-label">{{ card.label }}</p>
            <p class="stat-note">{{ card.note }}</p>
          </div>
        </el-col>
      </el-row>
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
              {{ $t("m.AI_Hint_Limit_Reached_Rate") }}
              <b>{{ depth.limit_reached_rate }}%</b>
            </p>
          </div>
        </el-col>
      </el-row>
    </Panel>

    <Panel :title="$t('m.AI_Hint_Effect')">
      <el-table :data="effectRows" border>
        <el-table-column
          prop="group"
          :label="$t('m.AI_Hint_Effect_Group')"
          width="160"
        />
        <el-table-column prop="pairs" :label="$t('m.AI_Hint_Effect_Pairs')" />
        <el-table-column
          prop="accepted"
          :label="$t('m.AI_Hint_Effect_Accepted')"
        />
        <el-table-column prop="rate" :label="$t('m.AI_Hint_Effect_Rate')">
          <template slot-scope="scope">
            <div class="cell-bar">
              <span class="cell-bar-track">
                <i
                  :style="{
                    width: scope.row.rate + '%',
                    background: scope.row.color,
                  }"
                ></i>
              </span>
              <b>{{ scope.row.rate }}%</b>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <p class="warn-note">{{ $t("m.AI_Hint_Effect_Note") }}</p>
    </Panel>

    <Panel :title="$t('m.AI_Hint_Quality')">
      <el-row :gutter="12">
        <el-col :span="12">
          <p>
            {{ $t("m.AI_Hint_Failure_Rate") }}
            <b>{{ quality.failure_rate }}%</b>
            <span class="hint-note">
              ({{ quality.empty }} / {{ quality.turns }})
            </span>
          </p>
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
    failure_rate: 0,
    hinted_pairs: 0,
    engaged_pairs: 0,
    adoption_rate: 0,
  },
  range: { session_gap_minutes: 30 },
  monthly: [],
  hourly: [],
  depth: {
    distribution: [],
    sessions: 0,
    avg_turns: 0,
    single_turn_rate: 0,
    limit_reached_rate: 0,
    limit: 5,
  },
  effect: {
    with_hint: { pairs: 0, accepted: 0, rate: 0 },
    without_hint: { pairs: 0, accepted: 0, rate: 0 },
  },
  quality: {
    turns: 0,
    empty: 0,
    failure_rate: 0,
    length: { p50: 0, p90: 0, max: 0 },
    labeled: 0,
    label_rate: 0,
  },
  top_problems: [],
}

const ACCENT = "#409eff"
// 순서형 램프. 진한 쪽이 앞 단계다. 색만으로 구분하지 않도록 막대에 값도 함께 찍는다.
const ORDINAL = ["#1c5cab", "#2a78d6", "#3987e5", "#5598e7", "#86b6ef"]
// 요점이 하나인 막대는 그 하나만 진하게, 나머지는 물러나게 한다.
const MUTED = "#c6dcf7"

// 막대 하나짜리 단순 차트는 형태가 같아 한 곳에서 만든다.
// colors 를 주면 막대마다 색을 달리한다.
function barOption(categories, values, name, colors) {
  return {
    tooltip: { trigger: "axis" },
    grid: { left: 40, right: 16, top: 24, bottom: 28 },
    xAxis: { type: "category", data: categories },
    yAxis: { type: "value", minInterval: 1 },
    series: [
      {
        name,
        type: "bar",
        data: colors
          ? values.map((v, i) => ({ value: v, itemStyle: { color: colors[i] } }))
          : values,
        itemStyle: { color: ACCENT },
      },
    ],
  }
}

export default {
  name: "AIHintStats",
  data() {
    return {
      loading: false,
      range: [],
      stats: JSON.parse(JSON.stringify(EMPTY)),
    }
  },
  mounted() {
    this.fetch()
  },
  computed: {
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
          label: this.$t("m.AI_Hint_Card_Sessions"),
          value: s.sessions,
          note: this.$t("m.AI_Hint_Card_Sessions_Note", {
            minutes: this.stats.range.session_gap_minutes,
          }),
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
        {
          label: this.$t("m.AI_Hint_Card_Failure"),
          value: s.failure_rate + "%",
          note: "",
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
    hourlyOption() {
      const values = this.stats.hourly.map((h) => h.turns)
      const peak = Math.max(...values, 0)
      return barOption(
        this.stats.hourly.map((h) => h.hour),
        values,
        this.$t("m.AI_Hint_Turns"),
        values.map((v) => (v === peak && peak > 0 ? "#1c5cab" : MUTED)),
      )
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
              formatter: (p) => `${rows[p.dataIndex].sessions}건 · ${rows[p.dataIndex].rate}%`,
              color: "#5c6773",
            },
          },
        ],
      }
    },
    effectRows() {
      const e = this.stats.effect
      // 미사용은 기준선이므로 회색, 관심 대상인 사용 쪽만 강조한다.
      return [
        { group: this.$t("m.AI_Hint_Effect_With"), color: ACCENT, ...e.with_hint },
        { group: this.$t("m.AI_Hint_Effect_Without"), color: "#c0c4cc", ...e.without_hint },
      ]
    },
    // 응답 길이는 분포이므로 눈금 두 개를 얹은 범위 막대로 보여준다.
    lengthScale() {
      const max = Math.max(this.quality.length.max, 1)
      const pct = (v) => Math.min(100, Math.round((1000 * v) / max) / 10)
      return { p50: pct(this.quality.length.p50), p90: pct(this.quality.length.p90) }
    },
  },
  methods: {
    topProblemWidth(turns) {
      const max = Math.max(...this.topProblems.map((p) => p.turns), 1)
      return Math.round((100 * turns) / max) + "%"
    },
    fetch() {
      this.loading = true
      const [start, end] = this.range || []
      api
        .getAIHintStats(start, end)
        .then((res) => {
          this.stats = res.data.data
          this.loading = false
        })
        .catch(() => {
          this.loading = false
        })
    },
  },
}
</script>

<style scoped lang="less">
.stat-card {
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

.hint-note {
  color: #999999;
  font-size: 12px;
}

.warn-note {
  margin-top: 10px;
  color: #e6a23c;
  font-size: 12px;
}
</style>
