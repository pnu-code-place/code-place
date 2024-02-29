<script>
import {FIELD_MAP} from "../../../../../../../utils/constants";

export default {
  name: "field-summary",
  props: ['fieldInfo'],
  data() {
    return {
      CATEGORY_LABEL: {
        data_structure: {label: FIELD_MAP["2"].value, color: FIELD_MAP["2"].boxColor},
        mathematics: {label: FIELD_MAP["1"].value, color: FIELD_MAP["1"].boxColor},
        sorting: {label: FIELD_MAP["4"].value, color: FIELD_MAP["4"].boxColor},
        implementation: {label: FIELD_MAP["0"].value, color: FIELD_MAP["0"].boxColor},
        searching: {label: FIELD_MAP["3"].value, color: FIELD_MAP["3"].boxColor},
      },
    }
  },
  methods: {
    percentageToScoreElement(label, percentage) {
      return `<div style="display:flex; width:100%; justify-content: space-between"><span>${label}</span><span>${((1 - percentage) * 100).toFixed(1)}</span></div>`
    },
  },
  computed: {
    graphRankData() {
      return Object.keys(this.fieldInfo).map((key) => ((1 - this.fieldInfo[key].ranking_percent) * 100).toFixed(1))
    },
    tooltipFormatter() {
      return `<div style="display:flex; flex-direction: column; padding:4px 15px">영역별 상대점수<br>
              ${this.percentageToScoreElement('자료구조', this.fieldInfo.data_structure.ranking_percent)}
              ${this.percentageToScoreElement('구현', this.fieldInfo.implementation.ranking_percent)}
              ${this.percentageToScoreElement('수학', this.fieldInfo.mathematics.ranking_percent)}
              ${this.percentageToScoreElement('탐색', this.fieldInfo.searching.ranking_percent)}
              ${this.percentageToScoreElement('정렬', this.fieldInfo.sorting.ranking_percent)} </div>`
    },
    radarIndicator() {
      return [
        {text: FIELD_MAP["2"].value, max: this.fieldInfo.data_structure.max, color: '#000000',},
        {text: FIELD_MAP["0"].value, max: this.fieldInfo.implementation.max, color: '#000000',},
        {text: FIELD_MAP["1"].value, max: this.fieldInfo.mathematics.max, color: '#000000',},
        {text: FIELD_MAP["3"].value, max: this.fieldInfo.searching.max, color: '#000000',},
        {text: FIELD_MAP["4"].value, max: this.fieldInfo.sorting.max, color: '#000000',},
      ]
    },
    tooltip() {
      return {
        trigger: 'item',
        formatter: this.tooltipFormatter,
        backgroundColor: 'rgba(0,0,0,0.7)',
        textStyle: {
          color: '#ffffff',
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
          indicator: this.radarIndicator,
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
          <th>{{ $t('m.Field') }}</th>
          <th>{{ $t('m.UserHomeScore') }}</th>
          <th><span class="score">{{ $t('m.Ranking') }}</span><span class="score-ratio">({{ $t('m.Percent') }})</span>
          </th>
        </tr>
        </thead>
        <tbody>
        <tr class="part-row" v-for="(category, category_name) in fieldInfo">
          <td class="part-name"><span :style="{backgroundColor:CATEGORY_LABEL[category_name].color}">{{
              CATEGORY_LABEL[category_name].label
            }}</span></td>
          <td class="solve-number">{{ category.score }}</td>
          <td class="difficulty-score">
            <span class="score">{{ category.ranking }}</span>
            <span class="score-ratio">({{ (category.ranking_percent * 100).toFixed(1) }}%)</span>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
    <div></div>
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
          .score {
            font-weight: 700;
          }

          .score-ratio {
            font-size: 13px;
          }
        }

        td {
          font-size: 14px;
          padding: 7px 0;
        }

        .part-name {
          font-weight: 700;
          text-align: left;
          color: #fff;

          span {
            padding: 2px 5px;
            border-radius: 5px;
          }
        }

        .difficulty-score {

          .score-ratio {
            font-size: 12px;
          }
        }
      }
    }
  }
}
</style>
