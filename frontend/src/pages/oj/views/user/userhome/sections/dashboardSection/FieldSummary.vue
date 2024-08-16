<script>
import {FIELD_MAP} from "../../../../../../../utils/constants";

export default {
  name: "field-summary",
  props: ['fieldInfo'],
  data() {
    return {
      CATEGORY_LABEL: {
        datastructure: {
          label: FIELD_MAP["2"].value,
          color: FIELD_MAP["2"].boxColor,
          bgImg: require('@/assets/fieldBackground/datastructure.svg')
        },
        math: {
          label: FIELD_MAP["1"].value,
          color: FIELD_MAP["1"].boxColor,
          bgImg: require('@/assets/fieldBackground/math.svg')
        },
        sorting: {
          label: FIELD_MAP["4"].value,
          color: FIELD_MAP["4"].boxColor,
          bgImg: require('@/assets/fieldBackground/sort.svg')
        },
        implementation: {
          label: FIELD_MAP["0"].value,
          color: FIELD_MAP["0"].boxColor,
          bgImg: require('@/assets/fieldBackground/implement.svg')
        },
        search: {
          label: FIELD_MAP["3"].value,
          color: FIELD_MAP["3"].boxColor,
          bgImg: require('@/assets/fieldBackground/search.svg')
        },
      },
      CATEGORY_NAME_TO_CODE: {
        datastructure: 2,
        math: 1,
        sorting: 4,
        implementation: 0,
        search: 3,
      }
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
    goField(category) {
      this.$router.push({
        name: 'user-problems',
        params: {username: this.$route.params.username},
        query: {field: this.CATEGORY_NAME_TO_CODE[category]}
      })
      window.location.reload()
    }
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
        {text: FIELD_MAP["1"].value, max: 1, color: '#000000',},
        {text: FIELD_MAP["4"].value, max: 1, color: '#000000',},
        {text: FIELD_MAP["0"].value, max: 1, color: '#000000',},
        {text: FIELD_MAP["3"].value, max: 1, color: '#000000',},
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
            <span class="ratio">({{ $t('m.Percent') }})</span>
          </th>
          <th>
            <span class="score">{{ $t('m.UserHomeScore') }}</span>
            <span class="ratio">({{ $t('m.Ratio') }})</span>
          </th>
        </tr>
        </thead>
        <tbody>
        <tr class="part-row" v-for="(category, category_name) in fieldInfo" @click="goField(category_name)">
          <td class="part-name-wrapper">
            <img :src="CATEGORY_LABEL[category_name].bgImg" alt="">
            <span class="part-name">
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

  .part-row {
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    font-size: 14px;
    border-top: 1px solid #dedede;

    &:hover {
      background-color: #f5f5f5;
    }
  }

  .graph-column {
    width: 30%;
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

        .ratio {
          font-size: 12px;
        }
      }
    }
  }
}

.part-row {
  .part-name-wrapper {
    font-size: 14px;
    padding: 7px 0;
    font-weight: 700;
    text-align: left;
    color: var(--ps-content-text-color);
    position: relative;
    overflow: hidden;

    .part-name {
      z-index: 10;
      position: relative;
    }

    img {
      position: absolute;
      left: 0;
      top: -10px;
      width: 200px;
      z-index: 0;
      transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
  }

  &:hover {
    .part-name-wrapper {
      img {
        transform: translateY(-40%);
      }
    }
  }
}
</style>
