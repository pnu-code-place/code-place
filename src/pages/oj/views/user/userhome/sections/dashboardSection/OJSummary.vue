<script>

// const ojStatus = {
//   rank: 1, // 랭킹
//   rank_percent: 0.1, // 랭킹 퍼센트 ( 상위 10% )
//   score: 100,
//   submission_number: 100,
//   accepted_number: 100,
//   total_score: 56000, // 현재 점수
//   rank_next: 60000, // 다음 랭킹의 허들
//   rank_current: 50000, // 현재 랭킹의 허들
//   miracle_current: 10, // 현재 연속 코딩일수
//   miracle_record: 20 // 최고 연속 코딩일수
// }

import HorizontalGauge from "./HorizontalGauge.vue";
import ShineWrapper from "../../../../../components/ShineWrapper.vue";

export default {
  name: 'oj-summary',
  components: {ShineWrapper, HorizontalGauge},
  props: ['ojStatus'],
  computed: {
    gaugeWidth() {
      return (this.ojStatus.total_score - this.ojStatus.rank_current) / (this.ojStatus.rank_next - this.ojStatus.rank_current);
    },
    rankPercent() {
      // 소숫점 1자리까지
      return Math.round(this.ojStatus.rank_percent * 1000) / 10;
    }
  }
}
</script>

<template>
  <div class="oj-summary">
    <div class="rank-mark-wrapper">
      <shine-wrapper>
        <img :src="ojStatus.rank_image" class="rank-mark" alt="rank emblem"/>
      </shine-wrapper>
      <span>{{ojStatus.rank_tier}}</span>
    </div>
    <div class="rank-info">
      <div class="rank-info-top">
        <div class="rank-info-elem">
          <span class="header">{{$t('m.UserHomeScore')}}</span>
          <span class="value">{{ ojStatus.score }}</span>
        </div>
        <div class="rank-info-elem">
          <span class="header">{{$t('m.Ranking')}}</span>
          <span class="value">{{ ojStatus.rank }} ({{$t('m.TOP')}} {{ rankPercent }}%)</span>
        </div>
        <div class="rank-info-elem">
          <span class="header">{{$t('m.Submit')}}</span>
          <span class="value">{{ ojStatus.submission_number }}</span>
        </div>
        <div class="rank-info-elem">
          <span class="header">{{$t('m.UserHomeSolved')}}</span>
          <span class="value">{{ ojStatus.accepted_number }}</span>
        </div>
      </div>
      <div class="progress">
        <span class="progress-info">
          {{ ojStatus.total_score }} / {{ ojStatus.rank_next }}
        </span>
        <div class="gauge-wrapper">
          <horizontal-gauge :progress="gaugeWidth"></horizontal-gauge>
        </div>
        <span class="progress-next">
          {{$t('m.Until_Promotion_Before')}} <span class="progress-next-number">{{ ojStatus.rank_next - ojStatus.total_score }}{{$t('m.Point')}}</span> {{$t('m.Until_Promotion_After')}}
        </span>
      </div>
    </div>
    <div class="miracle">
      <span class="miracle-title">{{$t('m.Miracle_Coding')}}</span>
      <span class="miracle-current">{{ ojStatus.miracle_current }}{{$t('m.MiracleCodingDays')}}</span>
      <span class="miracle-record">{{$t('m.Best_Record')}} {{ ojStatus.miracle_record }}{{$t('m.MiracleCodingDays')}}</span>
    </div>
  </div>
</template>

<style scoped lang="less">

.oj-summary {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  padding: 0 10px;
  gap: 20px;

  .rank-mark-wrapper {
    width: 30%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

    padding : 0 20px 10px;
    gap: 30px;

    .rank-mark {
      width: 180px;
      height: auto;
    }

    span {
      width: 100%;
      font-size: 15px;
      font-weight: 700;
      border-radius: 5px;
      border : 1px solid #B6B6B6;
      padding: 5px 10px;
      background-color: #F2F8F3;
    }
  }

  .rank-info {
    width: 50%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;

    .rank-info-top {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      align-items: flex-start;
      font-size: 15px;


      .rank-info-elem {
        width: 100%;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;

        .header {
          font-weight: 700;
        }
      }
    }

    .progress {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      font-size: 14px;
      gap: 5px;

      .progress-info {
        font-weight: 700;
      }

      .progress-next {

        .progress-next-number {
          font-weight: 700;
        }
      }

      .gauge-wrapper {
        width: 100%;
        height: 8px;
      }
    }
  }

  .miracle {
    width: 25%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    background-color: #F2F8F3;
    border-radius: 10px;

    .miracle-title {
      font-size: 15px;
      font-weight: 700;
    }

    .miracle-current {
      font-size: 18px;
      font-weight: 900;
    }

    .miracle-record {
      font-size: 12px;
    }
  }
}
</style>
