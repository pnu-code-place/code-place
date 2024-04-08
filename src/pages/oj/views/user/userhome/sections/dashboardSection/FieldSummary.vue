<script>
import {FIELD_MAP} from "../../../../../../../utils/constants";

export default {
  name: "field-summary",
  props: ['fieldInfo'],
  data() {
    return {
      CATEGORY_LABEL: {
        datastructure: {label: FIELD_MAP["2"].value, color: FIELD_MAP["2"].boxColor},
        math: {label: FIELD_MAP["1"].value, color: FIELD_MAP["1"].boxColor},
        sorting: {label: FIELD_MAP["4"].value, color: FIELD_MAP["4"].boxColor},
        implementation: {label: FIELD_MAP["0"].value, color: FIELD_MAP["0"].boxColor},
        search: {label: FIELD_MAP["3"].value, color: FIELD_MAP["3"].boxColor},
      },
    }
  },
  methods: {
    getTooltipRow(label, score) {
      return `<div style="display:flex; width:100%; justify-content: space-between"><span>${label}</span><span>${score}</span></div>`
    },
    getProportion(value) {
      if (this.totalScore === 0) {
        return 0;
      }
      return (value / this.totalScore * 100).toFixed(1);
    },
  },
  computed: {
    totalScore() {
      return Object.keys(this.fieldInfo).reduce((acc, key) => {
        return acc + this.fieldInfo[key].score;
      }, 0)
    },
    maxScore() {
      return Math.max(...Object.keys(this.fieldInfo).map((key) => (this.fieldInfo[key].score)))
    },
    graphData() {
      // 각 영역별로 점수를 배열로 만들어서 반환
      return Object.keys(this.fieldInfo).map((key) => (this.fieldInfo[key].score) / this.maxScore)
    },
    tooltipFormatter() {
      return `<div style="display:flex; flex-direction: column; padding:4px 15px; min-width: 150px">영역별 점수<br>
              ${this.getTooltipRow('자료구조', this.fieldInfo.datastructure.score)}
              ${this.getTooltipRow('구현', this.fieldInfo.implementation.score)}
              ${this.getTooltipRow('수학', this.fieldInfo.math.score)}
              ${this.getTooltipRow('탐색', this.fieldInfo.search.score)}
              ${this.getTooltipRow('정렬', this.fieldInfo.sorting.score)} </div>`
    },
    radarIndicator() {
      return [
        {text: FIELD_MAP["2"].value, max: 1, color: '#000000',},
        {text: FIELD_MAP["0"].value, max: 1, color: '#000000',},
        {text: FIELD_MAP["1"].value, max: 1, color: '#000000',},
        {text: FIELD_MAP["3"].value, max: 1, color: '#000000',},
        {text: FIELD_MAP["4"].value, max: 1, color: '#000000',},
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
                value: this.graphData,
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
          <th>
            <span class="score">{{ $t('m.Ranking') }}</span>
            <span class="ratio">({{$t('m.Percent') }})</span>
          </th>
          <th>
            <span class="score">{{ $t('m.UserHomeScore') }}</span>
            <span class="ratio">({{ $t('m.Ratio') }})</span>
          </th>
        </tr>
        </thead>
        <tbody>
        <tr class="part-row" v-for="(category, category_name) in fieldInfo">
          <td class="part-name">
            <span :style="{backgroundColor:CATEGORY_LABEL[category_name].color}">
              {{ CATEGORY_LABEL[category_name].label }}
            </span>
          </td>
          <td class="field-score">
            <span class="score">{{ category.ranking }}</span>
            <span class="ratio">({{ (category.ranking_percent * 100).toFixed(1) }}%)</span>
          </td>
          <td class="solve-number">
            <span class="score">{{ category.score }}</span>
            <span class="ratio">({{ getProportion(category.score) }}%)</span>
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
    //height: 100%;
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

          .ratio {
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

        .ratio {
          font-size: 12px;
        }
      }
    }
  }
}
</style>
