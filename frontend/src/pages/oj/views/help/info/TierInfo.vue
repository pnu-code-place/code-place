<script>
import TierTable from "./TierTable.vue";
import DifficultySummary from "../../user/userhome/sections/dashboardSection/DifficultySummary.vue";
import DifficultyTable from "./DifficultyTable.vue";

export default {
  name: 'tier-info',
  components: {DifficultyTable, DifficultySummary, TierTable}
}
</script>

<template>
  <div class="tier-info">
    <h1 class="section-title">레벨에 관하여</h1>
    <div class="tier-info__contents">
      <h2 class="">레벨</h2>
      <p>
        사용자들의 알고리즘 문제풀이 동기부여를 위해서 레벨 시스템이 도입되었습니다.<br/>
        일점 점수 이상을 달성하게 될 경우, 티어가 상승하게 됩니다. 점수별 티어표는 아래와 같습니다.
      </p>
      <div class="tier-info__description">
        <div class="tier-table">
          <h2 class="align-center">점수별 티어표</h2>
          <div class="tier-table-wrapper">
            <tier-table/>
          </div>
        </div>

        <div class="score-table">
          <h2 class="align-center">난이도별 획득량</h2>
          <difficulty-table></difficulty-table>
        </div>
      </div>
      <h2>
        점수를 얻는 방법
      </h2>
      <p>
        일반적으로 문제의 정답을 맞추게 될 경우 난이도에 따라 점수가 상승합니다.<br/>
        메인화면의 이주의 추천문제를 풀이하게 되면, 2배의 점수를 획득할 수 있습니다.<br/>
        만약 레벨시스템에 관해서 더 좋은 아이디어가 있다면, 문의하기 페이지를 통해서 알려주시면 감사하겠습니다.<br/>
        난이도에 따른 점수 획득량은 아래와 같습니다.
      </p>
    </div>
  </div>
</template>

<style scoped lang="less">
h1 {
  font-weight: bold;
}

h2 {
  font-size: 24px;
  padding: 10px 0;
}

p {
  font-size: 18px;
}

.tier-info {
  width: var(--global-width);

  .tier-info__contents {
    background-color: var(--box-background-color);
    border: 1px solid #dedede;
    border-radius: 7px;
    padding: 10px 20px 40px;

    display: flex;
    flex-direction: column;

    .tier-info__description {
      display: flex;
      gap: 20px;
      padding: 10px;

      .tier-table {
        width: 100%;

        .tier-table-wrapper {
          width: 100%;
          display: flex;
          flex-direction: column;
          align-items: center;
        }
      }

      .score-table {
        width: 100%;
      }
    }
  }


}

.align-center {
  text-align: center;
}
</style>
