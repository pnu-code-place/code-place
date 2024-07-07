<script>
import {TierImageSrc} from "../../../../../utils/constants";
import HorizontalGauge from "./sections/dashboardSection/HorizontalGauge.vue";
import {comma, getTier} from "../../../../../utils/utils";
import ShineWrapper from "../../../components/ShineWrapper.vue";

export default {
  name: "user-card",
  components: {HorizontalGauge, ShineWrapper},
  props: {
    profile: {
      type: Object,
      required: true,
      default: () => {
        return {
          user: {
            username: 'username',
            tier: 'bronze',
            email: 'email'
          },
          avatar: 'avatar',
          school: 'school',
          major: 'major',
          mood: 'mood',
          github: 'github'
        }
      }
    },
    ojStatus: {
      type: Object,
      required: true,
      default: () => {
        return {
          tier: 'bronze',
          total_score: 0,
          current_tier_score: 0,
          next_tier_score: 0,
          total_rank_percentage: 0,
          total_rank: 0,
          submission_number: 0,
          accepted_number: 0
        }
      }
    }
  },
  computed: {
    TierImageSrc() {
      return TierImageSrc
    },
    isMyProfile() {
      return this.$store.getters.user.username === this.profile.user.username;
    },
    gaugeWidth() {
      return (this.ojStatus.total_score - this.ojStatus.current_tier_score) / (this.ojStatus.next_tier_score - this.ojStatus.current_tier_score);
    },
    rankPercent() {
      // 소숫점 1자리까지
      return Math.round(this.ojStatus.total_rank_percentage * 1000) / 10;
    },
    rankingOffset() {
      if (this.ojStatus.total_rank < 10) {
        return 0;
      }
      return (this.ojStatus.total_rank - 4) / 10;
    },
    rankQuery() {
      return {offset: this.rankingOffset}
    }
  },
  methods: {
    getTier,
    comma,
    goSubmission() {
      this.$router.push({name: 'submission-list', query: {username: this.profile.user.username}})
    },
    goSolved() {
      this.$router.push({
        name: 'user-problems',
        params: {username: this.profile.user.username},
        query: {status: "Solved"}
      })
      window.location.reload()
    },
    goRanking() {
      this.$router.push({name: 'user-rank', query:this.rankQuery})
    }
  }
};
</script>

<template>
  <div class="user-card">
    <div class="user-info">
      <div class="avatar-wrapper">
        <img class="avatar" :src="profile.avatar"/>
      </div>
      <div class="info-column">
        <div class="info-column__top">
          <div class="user-name">
            {{ profile.user.username }}
          </div>
          <div class="user-description">
            {{ profile.school || "대학" }} {{ profile.major || "전공" }}
          </div>
          <div v-if="profile.mood" class="user-mood">
            {{ profile.mood || "" }}
          </div>
        </div>
        <div class="info-column__bottom">
          <div class="modify-button-wrapper">
            <router-link class="modify-button" v-if="isMyProfile" :to="{name : 'default-setting'}">
              {{ $t('m.User_Setting') }}
            </router-link>
          </div>
          <div class="icons">
            <a :href="'mailto:'+ profile.user.email">
              <Icon class="icon" type="ios-email-outline" size="30"></Icon>
            </a>
            <a :href="profile.github">
              <Icon type="social-github-outline" size="30"></Icon>
            </a>
          </div>
        </div>
      </div>
    </div>
    <div class="tier-info">
      <div class="tier-info__top">
        <div class="tier-mark-wrapper">
          <shine-wrapper>
            <img :src="TierImageSrc[ojStatus.tier]" class="rank-mark" alt="rank emblem"/>
          </shine-wrapper>
        </div>
        <div class="tier-progress">
          <div class="tier-name">{{ getTier(ojStatus.tier) }}</div>
          <div class="progress-container">
            <span class="progress-info">
              {{ comma(ojStatus.total_score) }} / {{ comma(ojStatus.next_tier_score) }}
            </span>
            <div class="gauge-wrapper">
              <horizontal-gauge :progress="gaugeWidth"></horizontal-gauge>
            </div>
            <span class="progress-next">
              {{ $t('m.Until_Promotion_Before') }}
            <span class="progress-next-number">
              {{ comma(ojStatus.next_tier_score - ojStatus.total_score) }}{{ $t('m.Point') }}
            </span>
              {{ $t('m.Until_Promotion_After') }}
            </span>
          </div>
        </div>
      </div>
      <div class="tier-info__bottom">
        <div class="content score">
          <span class="header">{{ $t('m.UserHomeScore') }}</span>
          <span class="value">{{ comma(ojStatus.total_score) }}</span>
        </div>
        <div class="content ranking clickable" @click="goRanking">
          <span class="header">{{ $t('m.Ranking') }}</span>
          <span class="value">{{ ojStatus.total_rank }} ({{ $t('m.TOP') }} {{ rankPercent }}%)</span>
        </div>
        <div class="content submission clickable" @click="goSubmission">
          <span class="header">{{ $t('m.Submit') }}</span>
          <span class="value">{{ ojStatus.submission_number }}</span>
        </div>
        <div class="content solve clickable" @click="goSolved">
          <span class="header">{{ $t('m.UserHomeSolved') }}</span>
          <span class="value">{{ ojStatus.accepted_number }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
.user-card {
  --usercard-avatar-size: 160px;
  --tier-mark-size: 70px;

  width: 100%;
  display: flex;
  background-color: var(--box-background-color);
  border: 1px var(--container-border-color) solid;
  border-radius: 7px;
  padding: 15px 30px 15px;

  .user-info {
    width: 50%;
    display: flex;

    .avatar-wrapper {
      width: var(--usercard-avatar-size);
      height: var(--usercard-avatar-size);
      overflow: hidden;
      border-radius: calc(var(--usercard-avatar-size) / 2);
      border: 1px solid var(--container-border-color);
      box-shadow: 0 0 10px 0 rgba(0, 0, 0, 0.1);
      flex-shrink: 0;

      img {
        width: 100%;
      }
    }

    .info-column {
      width: calc(100% - var(--usercard-avatar-size));
      height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      text-align: left;
      padding: 0 30px;

      .info-column__top {
        .user-name {
          font-size: 20px;
          font-weight: 600;
        }

        .user-description {
          font-size: 14px;
          font-weight: 600;
          color: var(--ps-content-text-color);
        }

        .user-mood {
          background-color: var(--pale-point-color);
          padding: 4px;
          border-radius: 4px;
          // 3줄을 넘어갈 경우 ...으로 축약
          overflow: hidden;
          text-overflow: ellipsis;
          display: -webkit-box;
          -webkit-line-clamp: 3;
          -webkit-box-orient: vertical;
        }
      }

      .info-column__bottom {
        display: flex;
        justify-content: space-between;
        gap: 10px;

        .modify-button-wrapper {
          width: 30%;
          display: flex;

          .modify-button {
            width: 100%;
            height: 100%;
            padding: 5px 10px;
            font-size: 14px;
            font-weight: 600;
            color: var(--box-background-color);
            background-color: var(--point-color);
            border-radius: 7px;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            cursor: pointer;

            &:hover {
              text-shadow: 0 0 10px rgba(255, 255, 255, 1);
            }
          }
        }

        .icons {
          width: 70%;
          display: flex;
          justify-content: end;
          gap: 15px;
        }
      }

      div {
        width: 100%;
      }
    }
  }

  .tier-info {
    width: 50%;
    gap: 10px;
    display: flex;
    flex-direction: column;

    .tier-info__top {
      display: flex;
      height: 100%;
      gap: 30px;

      .tier-mark-wrapper {
        width: var(--tier-mark-size);
        flex-shrink: 0;
      }

      .tier-progress {
        font-size: 14px;
        width: calc(100% - var(--tier-mark-size));
        flex-direction: column;
        display: flex;
        justify-content: space-between;

        .tier-name {
          font-size: 20px;
          font-weight: 600;
        }

        .progress-container {
          display: flex;
          flex-direction: column;

          .progress-info {
            font-size: 14px;
            font-weight: 600;
          }

          .gauge-wrapper {
            height: 7px;
          }

          .progress-next-number {
            font-weight: 600;
          }
        }
      }
    }

    .tier-info__bottom {
      height: 100%;
      display: flex;
      justify-content: space-between;
      gap: 10px;

      .content {
        display: flex;
        flex-direction: column;
        width: 100%;
        border: 1px solid var(--container-border-color);
        box-shadow: 0 0 10px 0 rgba(0, 0, 0, 0.1);
        border-radius: 7px;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        overflow: hidden;
        cursor: default;

        .header {
          font-size: 14px;
          font-weight: 600;
          padding: 5px;
          color: var(--box-background-color);
          background-color: var(--point-color)
        }

        .value {
          padding: 7px;
          font-size: 14px;
          font-weight: 600;
        }

        &:hover {
          box-shadow: 0 0 10px 0 rgba(0, 0, 0, 0.3);
          border-color: rgba(0, 0, 0, 0.3);
          transform: scale(1.03);

          .value {
            //background-color: var(--pale-point-color)
          }
        }

        &.clickable {
          cursor: pointer;
        }
      }
    }
  }
}
</style>
