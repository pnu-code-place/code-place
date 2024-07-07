<script>

import HorizontalGauge from "./sections/dashboardSection/HorizontalGauge.vue";
import ShineWrapper from "../../../components/ShineWrapper.vue";
import {comma, getTier} from "../../../../../utils/utils";
import {AwardImageSrc, TierImageSrc} from "../../../../../utils/constants";

export default {
  name: 'oj-summary',
  components: {ShineWrapper, HorizontalGauge},
  props: ['ojStatus'],
  computed: {

  },
  methods :{

  }
}
</script>

<template>
  <div class="oj-summary">
    <div class="rank-mark-wrapper">
      <shine-wrapper>
        <img :src="TierImageSrc[ojStatus.tier]" class="rank-mark" alt="rank emblem"/>
      </shine-wrapper>
      <span>{{ getTier(ojStatus.tier) }}</span>
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
          {{ comma(ojStatus.total_score) }} / {{ comma(ojStatus.next_tier_score) }}
        </span>
        <div class="gauge-wrapper">
          <horizontal-gauge :progress="gaugeWidth"></horizontal-gauge>
        </div>
        <span class="progress-next">
          {{$t('m.Until_Promotion_Before')}} <span class="progress-next-number">{{ comma(ojStatus.next_tier_score - ojStatus.total_score) }}{{$t('m.Point')}}</span> {{$t('m.Until_Promotion_After')}}
        </span>
      </div>
    </div>
    <div class="miracle">
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
    width: 75%;
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
    width: 0%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    //background-color: rgba(213, 213, 229, 0.82);
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
