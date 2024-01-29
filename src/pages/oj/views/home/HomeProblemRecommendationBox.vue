<template>
  <div class="problemRecommendationBox">
    <div class="problemRecommendationBoxHeader">
      <span @click="handleRoute('problem')">이번 주 보너스 문제</span>
      <div class="plusDiv">
        <Icon type="ios-information" size="13" color="#7a7a7a"></Icon>
        <span class="plusSpan">주마다 보너스 점수가 있는 문제를 추천해드려요!</span>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@oj/api'

export default {
  name: 'HomeProblemRecommendationBox',
  data () {
    return {
      value1: 0
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

.problemRecommendationBox{
  background-color: #ffffff;
  border-radius: 7px;
  border: 1px solid #dedede;
  width: 100%;
  height: 300px;
  padding-left: 30px;
  padding-right: 30px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  .problemRecommendationBoxHeader{
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

    .plusDiv{
      cursor: pointer;

      .plusSpan {
        color: #7a7a7a;
        font-size: 12px;
      }
    }

  }
}
</style>
