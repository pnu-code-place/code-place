<script>
import ShineWrapper from "../../../components/ShineWrapper.vue";
import {comma, getTier} from "../../../../../utils/utils";
import {TierImageSrc} from "../../../../../utils/constants";

export default {
  name: "MajorRankPeople",
  computed: {
    TierImageSrc() {
      return TierImageSrc
    },
    shift() {
      return `shift-${this.ranking}`
    }
  },
  methods: {
    comma,
    goUserInfo() {
      this.$router.push({name: 'user-home', params: {username: this.user.username}})
    },
    extend() {
      this.is_extended = true
    },
    shrink() {
      this.is_extended = false
    }
  },
  components: {ShineWrapper},
  data() {
    return {
      is_extended: false,
    }
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
  <div class="major-rank-people " @click="goUserInfo" @mouseover="extend" @mouseout="shrink"
       :class="is_extended? `extended ${this.shift}`: `shrink ${this.shift}`">
    <div class="user-avatar">
      <img :src="user.avatar_url" alt="avatar">
    </div>
    <div class="extend-user-badge">
      <div class="left">
        <div class="top">
          <div class="username">{{ this.user.username }}</div>
        </div>
        <div class="score">{{ comma(this.user.score) }}{{ $t('m.Point') }}</div>
        <!--        <div :class="this.user.mood? 'mood exist' : 'mood'">{{ this.user.mood }}</div>-->
      </div>
      <div class="tier">
        <shine-wrapper class="tier-mark-wrapper">
          <img class="tier-mark" :src="TierImageSrc[user.tier]" alt='tier-mark'>
        </shine-wrapper>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">

.shrink {
  width: var(--user-avatar-size);
}

.extended {
  overflow: hidden;
  width: auto;
}

.shift-1 {
  transform: translateX(calc(-7px));
}

.shift-2 {
  transform: translateX(calc(-14px));
}

.shift-3 {
  transform: translateX(calc(-21px));
}

.shift-4 {
  transform: translateX(calc(-28px));
}

.shift-5 {
  transform: translateX(calc(-35px));
}

.major-rank-people {
  --user-avatar-size: 45px;
  box-shadow: 0 3px 3px rgba(0, 0, 0, 0.10);
  height: var(--user-avatar-size);
  display: flex;
  justify-content: flex-start;
  align-items: center;
  color: #666;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border-radius: calc(var(--user-avatar-size) / 2);
  overflow: hidden;

  .user-avatar {
    width: var(--user-avatar-size);
    height: var(--user-avatar-size);
    border-radius: 50%;
    text-align: center;

    img {
      width: var(--user-avatar-size);
      height: var(--user-avatar-size);
      border-radius: 50%;
    }
  }

  .extend-user-badge {
    display: flex;
    gap: 5px;
    padding-right: 10px;

    .left {
      display: flex;
      flex-direction: column;
      padding-left: 10px;

      .top {
        display: flex;
        gap: 10px;

        .username {
          text-align: left;
        }

        .score {
          text-align: right;
        }
      }
      .mood {
        background-color:var(--site-background-color);
        max-width: 200px;
        padding: 0 7px;
        border-radius: 5px;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    .ranking {
      width: 5%;
      text-align: center;
    }

    .tier {
      text-align: center;
      display: flex;
      justify-content: center;
      align-items: center;
      flex-direction: column;

      & > .tier-mark-wrapper {
        width: var(--user-avatar-size);
        height: var(--user-avatar-size);

        & > .tier-mark {
          width: 80%;
          height: 80%;
        }
      }
    }
  }
}
</style>
