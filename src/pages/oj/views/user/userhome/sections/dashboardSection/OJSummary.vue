<script>

import HorizontalGauge from "./HorizontalGauge.vue";
import ShineWrapper from "../../../../../components/ShineWrapper.vue";
import {comma, getTier} from "../../../../../../../utils/utils";
import {AwardImageSrc, TierImageSrc} from "../../../../../../../utils/constants";

export default {
  name: 'oj-summary',
  components: {ShineWrapper, HorizontalGauge},
  props: ['ojStatus'],
  computed: {
    TierImageSrc() {
      return TierImageSrc
    },
    gaugeWidth() {
      return (this.ojStatus.total_score - this.ojStatus.rank_current) / (this.ojStatus.rank_next - this.ojStatus.rank_current);
    },
    rankPercent() {
      // 소숫점 1자리까지
      return Math.round(this.ojStatus.rank_percent * 1000) / 10;
    }
  },
  methods :{
    getTier,
    comma,
  }
}
</script>

<template>
  <div class="oj-summary">
    <div class="rank-mark-wrapper">
      <shine-wrapper>
        <img :src="TierImageSrc[ojStatus.rank_tier]" class="rank-mark" alt="rank emblem"/>
      </shine-wrapper>
      <span>{{ getTier(ojStatus.rank_tier) }}</span>
    </div>
    <div class="rank-info">
      <div class="rank-info-top">
        <div class="rank-info-elem">
          <span class="header">{{$t('m.UserHomeScore')}}</span>
          <span class="value">{{ comma(ojStatus.total_score) }}</span>
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
          {{ comma(ojStatus.total_score) }} / {{ comma(ojStatus.rank_next) }}
        </span>
        <div class="gauge-wrapper">
          <horizontal-gauge :progress="gaugeWidth"></horizontal-gauge>
        </div>
        <span class="progress-next">
          {{$t('m.Until_Promotion_Before')}} <span class="progress-next-number">{{ comma(ojStatus.rank_next - ojStatus.total_score) }}{{$t('m.Point')}}</span> {{$t('m.Until_Promotion_After')}}
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
    padding : 0 20px 15px;
    gap: 10px;

    .rank-mark {
      width: 120px;
      height: auto;
    }

    span {
      width: 100%;
      font-size: 18px;
      font-weight: 700;
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
    background-color: rgba(213, 213, 229, 0.82);
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
