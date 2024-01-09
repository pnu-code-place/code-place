<script>
import ShineWrapper from "@oj/components/ShineWrapper.vue";

export default {
  components: {ShineWrapper},
  props: {profile: Object},
  methods: {
  }
};
</script>

<template>
  <div class="user-card" :padding="0">
    <div>
      <div class="avatar-container">
        <img class="avatar" :src="profile.avatar"/>
      </div>
      <div class="user-info">
        <div class="user-info__top">
          <div class="username">{{ profile.user.username }}</div>
          <div class="user-description">{{ profile.school || "단과대" }}</div>
          <div class="user-description">{{ profile.major || "전공 없음" }}</div>
        </div>
        <!--      <button @click="logProfile">logging</button>-->
      </div>
      <div class="user-rank">
        <shine-wrapper>
          <img src="https://cdn-icons-png.flaticon.com/512/473/473406.png" class="rank-mark"/>
        </shine-wrapper>
      </div>
    </div>
    <div class="flex-container">
      <div class="left">
        <p>{{ $t('m.UserHomeSolved') }}</p>
        <p class="emphasis">{{ profile.accepted_number }}</p>
      </div>
      <div class="middle">
        <p>{{ $t('m.UserHomeserSubmissions') }}</p>
        <p class="emphasis">{{ profile.submission_number }}</p>
      </div>
      <div class="right">
        <p>{{ $t('m.UserHomeScore') }}</p>
        <p class="emphasis">{{ profile.total_score }}</p>
      </div>
    </div>
    <div id="icons">
      <a :href="profile.github">
        <Icon type="social-github-outline" size="30"></Icon>
      </a>
      <a :href="'mailto:'+ profile.user.email">
        <Icon class="icon" type="ios-email-outline" size="30"></Icon>
      </a>
      <a :href="profile.blog">
        <Icon class="icon" type="ios-world-outline" size="30"></Icon>
      </a>
    </div>
  </div>
</template>

<style scoped lang="less">
.user-card {
  width: 100%;
  padding: 10px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border: 1px solid #eee;
  border-radius: 5px;

  div {
    display: flex;
    justify-content: center;
    align-items: center;


    .avatar-container {
      z-index: 1;

      .avatar {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        box-shadow: 0 1px 1px 0;
      }
    }

    .user-rank {
      height: 140px;
      position: relative;
    }

    .user-info {
      flex: 1 1;
      margin-left: 20px;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      z-index: 1;

      .user-info__top {
        flex: 1 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: flex-start;

        .username {
          font-size: 26px;
          font-weight: 700;
        }

        .user-description {
          font-size: 16px;
          font-weight: 500;
        }
      }
    }

    .rank-mark {
      height: 100%;
      z-index: 0;
    }
  }
  .flex-container {
    padding: 20px;
    text-align: center;

    p {
      margin-top: 8px;
      margin-bottom: 8px;
    }
    .emphasis {
      font-size: 20px;
      font-weight: 600;
    }
    .left {
      flex: 1 1;
      gap: 10px;
    }
    .middle {
      flex: 1 1;
      border-left: 1px solid #999;
      border-right: 1px solid #999;
      gap: 10px;
    }
    .right {
      flex: 1 1;
      gap: 10px;
    }
  }
  #icons {
    display: flex;
    bottom: 20px;
    left: 50%;

    .icon {
      padding-left: 20px;
    }
  }
}


</style>
