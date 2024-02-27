<template>
  <div v-if="isLoading" class="skeleton-wrapper">
    <div class="avatar-skeleton skeleton"></div>
    <div class="bar-skeleton skeleton"></div>
    <div class="bar-skeleton skeleton"></div>
  </div>
  <div class="top-ranker-banner" @click="goUserDashboard" v-else>
    <div class="user-info">
      <div class="avatar-wrapper">
        <img class="avatar" :src="user.avatar" alt="avatar"/>
        <img class="trophy" :src="AwardImageSrc[rank.toString()]" alt="medal"/>
        <img class="tier-mark" :src="TierImageSrc[user.tier]" alt="tier mark"/>
      </div>
      <span class="user-name">{{ user.username }}</span>
      <span class="user-major">{{ user.major }}</span>
    </div>
    <div class="user-score">{{ comma(user.score) }}{{ $t('m.Point') }}</div>
  </div>
</template>
<script>
import api from "../../api";
import {comma} from "../../../../utils/utils";
import {AwardImageSrc, TierImageSrc} from "../../../../utils/constants";

export default {
  data() {
    return {
      user: {
        username: 'username',
        avatar: '',
        score: 0,
        solved: 0,
        accuracy: 0.0
      },
      isLoading: false,
    }
  },
  computed: {
    TierImageSrc() {
      return TierImageSrc
    },
    AwardImageSrc() {
      return AwardImageSrc
    }
  },
  props: {
    rank: {
      type: Number,
      default: 1
    }
  },
  methods: {
    comma,
    init() {
      this.isLoading = true
      api.getUserRank(this.rank, 0).then(res => {
        this.isLoading = false
        this.user = res.data.data.results[0]
      })
    },
    goUserDashboard() {
      this.$router.push({name: 'user-dashboard', params: {username: this.user.username}})
    }
  },
  mounted() {
    this.init()
  },
}
</script>


<style scoped lang="less">

.top-ranker-banner {
  cursor: pointer;

  .user-info {
    display: flex;
    align-items: center;
    flex-direction: column;

    .avatar-wrapper {
      position: relative;

      .avatar {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: linear-gradient(90deg, #f0f0f0 25%, #f5f5f5 50%, #f0f0f0 75%);
      }

      .trophy {
        width: 40%;
        height: auto;
        position: absolute;
        bottom: 0;
        right: 0;
      }
    }

    .user-name {
      font-size: 20px;
      font-weight: 700;
    }

    a {
      display: flex;
      align-items: center;
    }
  }
}
.user-score {
  font-size: 14px;
  text-align: center;
  font-weight: 500;
}

.tier-mark {
  width: 40px;
  height: auto;
  margin-top: 10px;
  position: absolute;
  bottom: 0;
  left: 0;
}

.skeleton {
  width: 100px;
  height: 174px;
  border-radius: 10px;
  margin: 10px 0;
  animation: loading 1s infinite;
}

.avatar-skeleton {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  margin: 10px 0;
}

.bar-skeleton {
  width: 100%;
  height: 20px;
  border-radius: 5px;
  margin: 5px 0;
}

@keyframes loading {
  0% {
    background-color: #e3e3e3;
  }
  50% {
    background-color: #f5f5f5;
  }
  100% {
    background-color: #e3e3e3;
  }
}

</style>
