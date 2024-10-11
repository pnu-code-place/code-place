<script>
export default {
  name: "DifficultyTable",
  data() {
    return {
      difficultyInfo: [
        {
          name: "매우 쉬움",
          score: 10
        },
        {
          name: "쉬움",
          score: 40
        },
        {
          name: "보통",
          score: 160
        },
        {
          name: "어려움",
          score: 640
        },
        {
          name: "매우 어려움",
          score: 2560
        }
      ]
    }
  }
}
</script>

<template>
  <table class="difficulty-table">
    <thead>
    <tr>
      <th>난이도</th>
      <th>획득량</th>
    </tr>
    </thead>
    <tbody>
    <tr v-for="difficulty in difficultyInfo" :key="difficulty.name">
      <td>{{ difficulty.name }}</td>
      <td>{{ difficulty.score }}</td>
    </tr>
    </tbody>
  </table>
</template>

<style scoped lang="less">
table {
  width: 100%;
  border-collapse: collapse;



  th, td {
    border: 1px solid #dedede;
    padding: 10px;
    text-align: center;
    font-size: 16px;
  }

  th {
    background-color: var(--pale-point-color);
    font-size: 16px;
    font-weight: bold;
  }
}
</style>
