<script>
import ShineWrapper from "../../../components/ShineWrapper.vue";
import {comma} from "../../../../../utils/utils";
import {TierImageSrc} from "../../../../../utils/constants";

export default {
  name: 'TestItem',
  data() {
    return {
      faceImage: require('@/assets/github.png')
    }
  },
  computed: {
    tierImageSrc() {
      return TierImageSrc
    },
    shift() {
      return `shift-${this.userNum - this.ranking}`
    }
  },
  methods: {
    comma,
    goUserInfo() {
      this.$router.push({name: 'user-home', params: {username: this.user.username}})
    },
  },
  components: {ShineWrapper},
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
      default: 0,
    },
    userNum: {
      type: Number,
      default: 1,
    }
  }
}
</script>

<template>
  <div :class="'extend-badge ' + `shrink ${this.shift}`" @click="goUserInfo">
    <img class="user-avatar" :src="this.user.avatar_url"/>
    <div class="detail">
      <div class="user-name">{{ this.user.username }}</div>
      <div class="user-score">{{ comma(this.user.score) }}{{ $t('m.Point') }}</div>
    </div>
    <!--      <img :src="this.tierImageSrc"/>-->
    <div class="tier-wrapper">
      <shine-wrapper class="tier-mark-wrapper">
        <!--      <img src="@/assets/github.png"/>-->
        <img class="tier" :src="tierImageSrc[user.tier]" alt='tier-mark'>
      </shine-wrapper>
    </div>
  </div>
</template>

<style scoped lang="less">

.extend-badge {
  --user-avatar-size: 45px;

  display: flex;
  overflow: hidden;
  max-width: var(--user-avatar-size);
  height: var(--user-avatar-size);
  border-radius: calc(var(--user-avatar-size) / 2);
  gap: 10px;
  transition: all 0.5s ease-in-out;
  box-shadow: 0 3px 3px rgba(0, 0, 0, 0.50);
  padding-right: 10px;
  cursor: pointer;

  &:hover {
    max-width: 400px;
  }
}

.detail {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: start;
  min-width: 70px;

  .user-name {
    font-weight: 600;
    text-overflow: clip;
    height: 100%;
  }

  .user-score {
    font-size: 13px;
    text-overflow: clip;
    height: 100%;
  }

}

.contents {
  display: flex;
}

.user-avatar {
  display: flex;
  justify-content: center;
  align-items: center;
  width: var(--user-avatar-size);
  height: var(--user-avatar-size);
  border-radius: calc(var(--user-avatar-size) / 2);
  background-color: #f5f5f5;
}

.tier {
  width: 40px;
  height: 40px;
}

.shift-0 {
  transform: translateX(0);
}

.shift-1 {
  transform: translateX(calc(5px));
}

.shift-2 {
  transform: translateX(calc(10px));
}

.shift-3 {
  transform: translateX(calc(15px));
}

.shift-4 {
  transform: translateX(calc(20px));
}
</style>
