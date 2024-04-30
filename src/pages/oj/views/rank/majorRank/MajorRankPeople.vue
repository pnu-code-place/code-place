<script>
import ShineWrapper from "../../../components/ShineWrapper.vue";
import {getTier} from "../../../../../utils/utils";
import {TierImageSrc} from "../../../../../utils/constants";

export default {
  name: "MajorRankPeople",
  computed: {
    TierImageSrc() {
      return TierImageSrc
    }
  },
  methods: {getTier,
    goUserInfo() {
      this.$router.push({name: 'user-home', params: {username: this.user.username}})
    }
  },
  components: {ShineWrapper},
  data() {
    return {}
  },
  props: {
    user: {
      type: Object,
      default: () => {
        return {
          mood: '',
          username: '',
          score: 0,
          tier: 'sprout',
          avatar_url: ''
        }
      }
    },
    ranking: {
      type: Number,
      default: 0
    }
  }
}
</script>

<template>
  <div class="major-rank-people" @click="goUserInfo">
    <div class="ranking">{{ this.ranking }}</div>
    <div class="user-avatar">
      <img :src="user.avatar_url" alt="avatar">
    </div>
    <div class="username">{{ this.user.username }}</div>
    <div :class="this.user.mood? 'mood exist' : 'mood'">{{ this.user.mood }}</div>
    <div class="tier">
      <shine-wrapper class="tier-mark-wrapper">
        <img class="tier-mark" :src="TierImageSrc[user.tier]" alt='tier-mark'>
      </shine-wrapper>
<!--      <span class="tier">{{ getTier(user.tier) }}</span>-->
    </div>
    <div class="score">{{ this.user.score }} {{$t('m.Point')}}</div>
  </div>
</template>

<style scoped lang="less">
.major-rank-people {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding: 10px 0 10px 120px;
  color: #666;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;

  &:hover {
    background-color: #f5f5f5;
  }

  & > .ranking {
    width: 5%;
    text-align: center;
  }

  & > .username {
    width: 15%;
    text-align: left;
    padding-left : 10px;
  }

  & > .score {
    width: 12%;
    text-align: right;
  }

  & > .user-avatar {
    width: 35px;
    height: 35px;
    border-radius: 50%;
    text-align: center;
    background-color: #f0f0f0;

    & > img {
      width: 35px;
      height: 35px;
      border-radius: 50%;
    }
  }

  & > .mood {
    width: 30%;
    text-align: left;
    font-weight: 400;
    padding: 10px;
    margin-right: 20px;
    border-radius: 10px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;

    &.exist {
      background-color : rgba(208, 223, 248, 0.18);
    }
  }

  & > .tier {
    text-align: center;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;

    & > .tier-mark-wrapper {
      width: 35px;
      height: 35px;

      & > .tier-mark {
        width: 100%;
        height: 100%;
      }
    }
  }
}
</style>
