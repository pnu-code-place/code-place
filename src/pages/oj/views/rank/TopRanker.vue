<template>
  <div class="top-ranker-banner">
    <div class="user-info">
      <div class="avatar-wrapper">
        <img class="avatar" :src="user.avatar" alt="avatar"/>
        <img class="trophy" :src="user.avatar"/>
      </div>
      <router-link :to="{name : 'user-dashboard', params : {username:user.username}}" class="user-name">
        {{ user.username }}
      </router-link>
      <span class="user-major">{{ user.major }}</span>
    </div>
    <div class="user-score">{{ $t('m.Points') }} {{ this.commaScore }}</div>
  </div>
</template>
<script>
import api from "../../api";

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
  props: {
    rank: {
      type: Number,
      default: 1
    }
  },
  methods: {
    init() {
      this.isLoading = true
      api.getUserRank(this.rank, 0).then(res => {
        this.isLoading = false
        this.user = res.data.data.results[0]
      })
    }
  },
  mounted() {
    this.init()
  },
  computed: {
    commaScore() {
      return this.user.score.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
    }
  }
}
</script>


<style scoped lang="less">

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
    height: 40%;
    position: absolute;
    bottom: 0;
    right: 0;
  }
}

.user-info {
  display: flex;
  align-items: center;
  flex-direction: column;

  .user-name {
    font-size: 20px;
    font-weight: 700;
  }
}

.user-score {
  font-size: 14px;
  text-align: center;
}
</style>
