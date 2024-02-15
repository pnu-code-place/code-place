<script>
export default {
  name: 'difficulty-summary',
  props: ['difficultyInfo'],
  data() {
    return {
      DIFFICULTY_LABEL: {
        very_easy: {label: 'Very Low', color: '#95ef4c'},
        easy: {label: 'Low', color: '#B5EAB0'},
        medium: {label: 'Mid', color: '#7c7878'},
        hard: {label: 'High', color: '#ff8828'},
        very_hard: {label: 'Very High', color: '#c02b2b'},
      }
    }
  },
  methods: {
    getProportion(value) {
      return (value / this.totalScore * 100).toFixed(1);
    },
    chartLabel(params) {
      // 이니셜을 표시해주는 함수
      const initial = params.name.split(' ').map((word) => word[0]).join('')
      return params.percent >= 10 ? initial : ''
    }
  },
  computed: {
    labelColors() {
      return Object.keys(this.difficultyInfo).map((key) => this.DIFFICULTY_LABEL[key].color)
    },
    totalScore() {
      return Object.keys(this.difficultyInfo).reduce((acc, key) => {
        return acc + this.difficultyInfo[key].total_score;
      }, 0)
    },
    pieChartData() {
      return Object.keys(this.difficultyInfo).map((key) => {
        return {
          value: this.difficultyInfo[key].total_score,
          name: this.DIFFICULTY_LABEL[key].label
        }
      })
    },
    pieChartOption() {
      return {
        tooltip: {
          trigger: 'item',
          formatter: '<div style="padding:2px 8px">{b}: {c}점 ({d}%)</div>'
        },
        series: [
          {
            name: '문제 난이도',
            type: 'pie',
            radius: ['15%', '90%'],
            data: this.pieChartData,
            itemStyle: {
              normal: {
                label: {
                  position: 'inside',
                  formatter: (params) => {
                    return this.chartLabel(params)
                  },
                  textStyle: {
                    color: '#ffffff',
                    fontSize: 14,
                    fontWeight: 'bold'
                  }
                },
                labelLine: {
                  show: false
                }
              }
            },
            animationType: 'scale',
            animationEasing: 'cubicOut',
            animationDelay: function (idx) {
              return Math.random() * 200;
            }
          }
        ],
        color: this.labelColors
      }
    }
  }
}
</script>

<template>
  <div class="difficulty-summary">
    <div class="graph-wrapper">
      <ECharts :options="pieChartOption" style="width: 100%; height: 100%"/>
    </div>
    <div class="table-wrapper">
      <table>
        <thead>
        <tr>
          <th>난이도</th>
          <th>푼 문제</th>
          <th><span class="score">점수</span><span class="score-ratio">(비율)</span></th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(difficulty, key, index) in difficultyInfo" :key="index">
          <td class="part-name" :style="{color:DIFFICULTY_LABEL[key].color}">{{ DIFFICULTY_LABEL[key].label }}</td>
          <td class="solve-number">{{ difficulty.solve_number }}</td>
          <td class="difficulty-score">{{ difficulty.total_score }} <span
              class="score-ratio">({{ getProportion(difficulty.total_score) }}%)</span></td>
        </tr>
        </tbody>
      </table>
    </div>
    <div class="dummy">

    </div>
  </div>
</template>

<style scoped lang="less">
.difficulty-summary {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  padding: 0 10px;
  gap: 20px;

  .graph-wrapper {
    width: 30%;

  }

  .table-wrapper {
    width: 75%;

    table {
      border-collapse: collapse;

      thead {
        tr {
          border-top: none;
        }
      }

      tr {
        border-top: 1px solid #dedede;

        th {
          text-align: center;
          font-size: 16px;
        }

        th:first-child {
          width: 50%;
          text-align: left
        }

        th:nth-child(2) {
          width: 20%;
        }

        th:nth-child(3) {
          .score {
            font-weight: 700;
          }

          .score-ratio {
            font-size: 13px;
          }
        }

        td {
          font-size: 14px;
          border-top: 1px solid #dedede;
          padding: 7px 0;
        }

        .part-name {
          font-weight: 600;
          text-align: left
        }

        .difficulty-score {
          font-size: 14px;

          .score-ratio {
            font-size: 12px;
          }
        }
      }
    }
  }
}
</style>
