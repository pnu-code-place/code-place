<script>
export default {
  name: 'difficulty-summary',
  props: ['difficulty_info'],
  data() {
    return {
      difficulty_label: {
        very_easy: {label: 'Very Easy', color: '#82CDC8'},
        easy: {label: 'Easy', color: '#1AA9ff'},
        medium: {label: 'Medium', color: '#1AA931'},
        hard: {label: 'Hard', color: '#FFA800'},
        very_hard: {label: 'Very Hard', color: '#FF4D4D'},

      }
    }
  }
}
</script>

<template>
  <div class="difficulty-summary">
    <div class="graph-wrapper">

    </div>
    <div class="table-wrapper">
      <table>
        <thead>
        <tr>
          <th>난이도</th>
          <th>푼 문제</th>
          <th><span class="ranking">랭킹</span><span class="ranking-percent">(백분율)</span></th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(difficulty, key, index) in difficulty_info" :key="index">
          <td class="part-name" :style="{color:difficulty_label[key].color}">{{ difficulty_label[key].label }}</td>
          <td class="solve-number">{{ difficulty.solve_number }}</td>
          <td class="solve-ranking">
            <span class="ranking">{{ difficulty.ranking }}</span>
            <span class="ranking-percent">({{ (difficulty.ranking_percent * 100).toFixed(1) }}%)</span>
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
.difficulty-summary {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  padding: 0 10px;
  gap: 20px;

  .graph-wrapper {
    width: 25%;

  }

  .table-wrapper {
    width: 75%;

    table {

      tr {

        th {
          text-align: center;
          font-size: 20px;
          border-bottom: 2px solid #dedede;
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
            font-size: 16px;
          }
        }

        td {
          font-size: 18px;
          border-bottom: 1px solid #dedede;
          padding: 7px 0;
        }

        .part-name {
          font-weight: 500;
          text-align: left
        }

        .solve-ranking {

          .ranking {
          }

          .ranking-percent {
            font-size: 16px;
          }
        }
      }
    }
  }
}
</style>
