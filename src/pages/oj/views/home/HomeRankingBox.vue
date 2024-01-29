<template>
  <div class="rankingBox">
    <div class="rankingBoxHeader">
      <span>실시간 랭킹</span>
      <div>
        <Icon type="ios-information-outline" size="13" color="#7a7a7a"></Icon>
        <span>순위는 매일 밤 12시 갱신됩니다</span>
      </div>
    </div>
    <ul class="ranking-container" key="list">
      <li
        v-for="(rankingInfo, idx) in rankingItems.testRealTimeRankingDTO"
        v-if="idx <= 9"
      >
        <div class="flex-container">
          <!-- 랭킹 10위까지 데이터 바인딩 필요 -->
          <!--                <div class="title">-->
          <!--                  <a class="entry">-->
          <!--                    {{ rankingInfo.ranking + '위' }}-->
          <!--                  </a>-->
          <!--                  <a class="entry">-->
          <!--                    {{ rankingInfo.userName }}-->
          <!--                  </a>-->
          <!--                  <img src="@/assets/badgeExample.png" width="13px"/>-->
          <!--                </div>-->
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
import testRealTimeRankingDTO from "../general/testRealTimeRankingDTO";

export default {
  name: 'HomeRankingBox',
  data () {
    return {
      rankingItems: testRealTimeRankingDTO,
    }
  },
  methods:{
    handleRoute(route) {
      this.$router.push({name: route});
    },
  }
}
</script>

<style scoped lang="less">

.rankingBox {
  background-color: #ffffff;
  border-radius: 7px;
  border: 1px solid #dedede;
  width: 100%;
  height: 450px;
  padding-left: 30px;
  padding-right: 30px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);

  .rankingBoxHeader {

    padding-top: 15px;
    padding-bottom: 15px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #dedede;

    span:first-child {
      font-weight: 650;
      font-size: 15px;
    }

    span:nth-child(2) {
      color: #7a7a7a;
      font-size: 12px;
    }
  }
}


.ranking-container {
  margin-top: -5px;
  margin-bottom: 5px;

  li {
    padding-top: 5px;
    list-style: none;
    padding-bottom: 5px;
    margin-top: 9px;
    border-radius: 15px;
    margin-left: 20px;
    margin-right: 20px;
    font-size: 12px;
    font-weight: bold;

    &:last-child {
      border-bottom: none;
    }

    .flex-container {
      img {
        margin-right: 1px;
      }

      .title {
        flex: 1 1;
        text-align: left;
        a.entry:first-child {
          margin-left: 12px;
          margin-right: 80px;
          color: #495060;
        }
      }
    }
  }
}

</style>
