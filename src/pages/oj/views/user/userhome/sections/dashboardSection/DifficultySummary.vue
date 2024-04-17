<script>
import {DIFFICULTY_MAP} from "../../../../../../../utils/constants";

export default {
  name: 'difficulty-summary',
  props: ['difficultyInfo'],
  data() {
    return {
      DIFFICULTY_LABEL: {
        verylow: {label: 'Very Low', color: DIFFICULTY_MAP.VeryLow.textColor},
        low: {label: 'Low', color: DIFFICULTY_MAP.Low.textColor},
        mid: {label: 'Mid', color: DIFFICULTY_MAP.Mid.textColor},
        high: {label: 'High', color: DIFFICULTY_MAP.High.textColor},
        veryhigh: {label: 'Very High', color: DIFFICULTY_MAP.VeryHigh.textColor},
      },
      DIFFICULTY_NAME_TO_CODE: {
        verylow: 'VeryLow',
        low: 'Low',
        mid: 'Mid',
        high: 'High',
        veryhigh: 'VeryHigh',
      }
    }
  },
  methods: {
    getProportion(value) {
      if (this.totalScore === 0) {
        return 0;
      }
      return (value / this.totalScore * 100).toFixed(1);
    },
    chartLabel(params) {
      // 이니셜을 표시해주는 함수
      const initial = params.name.split(' ').map((word) => word[0]).join('')
      return params.percent >= 10 ? initial : ''
    },
    goDifficulty(difficulty) {
      this.$router.push({name: 'user-problems', params: {username: this.$route.params.username}, query: {difficulty: this.DIFFICULTY_NAME_TO_CODE[difficulty]}})
      window.location.reload()
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
          formatter: '<div style="padding:2px 8px">{b}: {c} points ({d}%)</div>'
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
          <th>{{$t('m.Difficulty')}}</th>
          <th>{{$t('m.DifficultySolved')}}</th>
          <th><span class="score">{{$t('m.UserHomeScore')}}</span>
            <span class="ratio">({{$t('m.Ratio')}})</span></th>
        </tr>
        </thead>
        <tbody>
        <tr class="part-row" v-for="(difficulty, key, index) in difficultyInfo" :key="index" @click="goDifficulty(key)">
          <td class="part-name" :style="{color:DIFFICULTY_LABEL[key].color}">{{ DIFFICULTY_LABEL[key].label }}</td>
          <td class="solve-number">{{ difficulty.solve_number }}</td>
          <td class="difficulty-score">{{ difficulty.total_score }}
            <span class="ratio">({{ getProportion(difficulty.total_score) }}%)</span>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
    <div class="dummy">

    </div>
  </div>
</template>

<style scoped lang="less">
.part-row {
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  font-size: 14px;
  border-top: 1px solid #dedede;
  &:hover {
    background-color: #f5f5f5;
  }
}
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

          .ratio {
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

          .ratio {
            font-size: 12px;
          }
        }
      }
    }
  }
}
</style>
