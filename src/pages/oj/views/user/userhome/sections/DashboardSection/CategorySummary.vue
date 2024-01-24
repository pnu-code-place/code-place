<script>

// const category_info = {
//   data_structure: {
//     solve_number: 33,
//     ranking: 60,
//     ranking_percent: 0.3,
//   },
//   mathematics: {
//     solve_number: 20,
//     ranking: 101,
//     ranking_percent: 0.505,
//   },
//   sorting: {
//     solve_number: 45,
//     ranking: 34,
//     ranking_percent: 0.17,
//   },
//   implementation: {
//     solve_number: 61,
//     ranking: 20,
//     ranking_percent: 0.1012,
//   },
//   searching: {
//     solve_number: 3,
//     ranking: 190,
//     ranking_percent: 0.95,
//   }
// }
export default {
  name: "category-summary",
  props: ['categoryInfo'],
  data() {
    return {
      category_label: {
        data_structure: '자료구조',
        mathematics: '수학',
        sorting: '정렬',
        implementation: '구현',
        searching: '탐색'
      },
    }
  },
  methods: {
    percentageToScoreElement(label, percentage) {
      return `<div style="display:flex; width:100%; justify-content: space-between"><span>${label}</span><span>${((1 - percentage) * 100).toFixed(1)}</span></div>`
    }
  },
  computed: {
    graphRankData() {
      return Object.keys(this.categoryInfo).map((key) => ((1 - this.categoryInfo[key].ranking_percent) * 100).toFixed(1))
    },
    tooltipFormatter() {
      return `<div style="display:flex; flex-direction: column; padding:4px 15px">영역별 상대점수<br>
              ${this.percentageToScoreElement('자료구조', this.categoryInfo.data_structure.ranking_percent)}
              ${this.percentageToScoreElement('구현', this.categoryInfo.implementation.ranking_percent)}
              ${this.percentageToScoreElement('수학', this.categoryInfo.mathematics.ranking_percent)}
              ${this.percentageToScoreElement('탐색', this.categoryInfo.searching.ranking_percent)}
              ${this.percentageToScoreElement('정렬', this.categoryInfo.sorting.ranking_percent)} </div>`
    },
    tooltip() {
      return {
        trigger: 'item',
        formatter: this.tooltipFormatter,
        backgroundColor: 'rgba(0,0,0,0.7)',
        textStyle: {
          color: '#ffffff',
          fontWeight: 'bold'
        }
      }
    },
    chartOption() {
      return {
        color: ['#FF917C'],
        legend: {},
        tooltip: {
          trigger: 'axis'
        },
        radar: {
          indicator: [
            {text: '자료구조', max: 100, color: '#000000',},
            {text: '구현', max: 100, color: '#000000',},
            {text: '수학', max: 100, color: '#000000',},
            {text: '탐색', max: 100, color: '#000000',},
            {text: '정렬', max: 100, color: '#000000',},
          ],
          axisName: {
            fontWeight: 'bold'
          },
          splitArea: {
            areaStyle: {
              color: ['rgba(255,255,255,0)', 'rgba(255,255,255,0)', 'rgba(255,255,255,0)', 'rgba(255,255,255,0)'],
            }
          },
          splitNumber: 4,
          center: ['50%', '55%'],
        },
        series: [
          {
            name: 'ACM Score',
            type: 'radar',
            emphasis: {
              areaStyle: {
                color: '#FF917C',
                shadowColor: '#FF917C'
              },
            },
            data: [
              {
                value: this.graphRankData,
                tooltip: this.tooltip,
              },
            ],
          }
        ]
      }
    }
  }
}
</script>

<template>
  <div class="category-summary">
    <div class="graph-column">
      <ECharts :options="chartOption" style="width: 100%; height: 100%"/>
    </div>
    <div class="table-wrapper">
      <table>
        <thead>
        <tr>
          <th>영역</th>
          <th>점수</th>
          <th><span class="ranking">랭킹</span><span class="ranking-percent">(백분율)</span></th>
        </tr>
        </thead>
        <tbody>
        <tr class="part-row" v-for="(category, category_name, index) in categoryInfo">
          <td class="part-name">{{ category_label[category_name] }}</td>
          <td class="solve-number">{{ category.solve_number }}</td>
          <td class="solve-ranking">
            <span class="ranking">{{ category.ranking }}</span>
            <span class="ranking-percent">({{ (category.ranking_percent * 100).toFixed(1) }}%)</span>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
    <div>

    </div>
  </div>
</template>

<style scoped lang="less">
.category-summary {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  padding: 0 10px;
  gap: 20px;

  .graph-column {
    width: 30%;
    height: 100%;
  }

  .table-wrapper {
    width: 75%;
    height: 100%;

    table {
      border-collapse: collapse;

      thead tr {
        border-top: none;
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
          .ranking {
            font-weight: 700;
          }

          .ranking-percent {
            font-size: 13px;
          }
        }

        td {
          font-size: 15px;
          padding: 7px 0;
        }

        .part-name {
          font-weight: 400;
          text-align: left
        }

        .solve-ranking {

          .ranking {
          }

          .ranking-percent {
            font-size: 13px;
          }
        }
      }
    }
  }
}
</style>
