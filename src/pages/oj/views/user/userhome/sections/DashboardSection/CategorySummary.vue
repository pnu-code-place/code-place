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
  props: ['category_info'],
  data() {
    return {
      category_label: {
        data_structure: '자료구조',
        mathematics: '수학',
        sorting: '정렬',
        implementation: '구현',
        searching: '탐색'
      }
    }
  },
  methods: {}
}
</script>

<template>
  <div class="category-summary">
    <div class="graph-column">ㅇ</div>
    <div class="table-wrapper">
      <table>
        <thead>
        <tr>
          <th>영역</th>
          <th>푼 문제</th>
          <th><span class="ranking">랭킹</span><span class="ranking-percent">(백분율)</span></th>
        </tr>
        </thead>
        <tbody>
        <tr class="part-row" v-for="(category, category_name, index) in category_info">
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
    width: 25%;
    height: 100%;
  }

  .table-wrapper {
    width: 75%;
    height: 100%;

    table {

      tr {

        th {
          text-align: center;
          font-size: 20px;
          border-bottom: 1px solid #dedede;
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
          font-weight: 400;
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
