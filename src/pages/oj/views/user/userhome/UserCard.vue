<script>
import ShineWrapper from "@oj/components/ShineWrapper.vue";

// const profile = {
//   avatar: "https://avatars.githubusercontent.com/u/48755175?v=4",
//   user: {
//     username: "minmunui",
//     email: "ehdwls1638@pusan.ac.kr",
//     school: "공과대학",
//     major: "전기컴퓨터공학부 정보컴퓨터공학전공",
//     create_time: "2021-09-01T15:00:00.000Z",
//     admin_type: 0,
//     _id: "6130b4b0e7c9d9b4e8b3f7b5",
//   },
//   github: "",
//   blog: "",
// }

export default {
  components: {ShineWrapper},
  props: {profile: Object},
};
</script>

<template>
  <div class="user-card">
    <div class="avatar-container">
      <img class="avatar" :src="profile.avatar"/>
    </div>
    <div class="user-info">
      <div class="username">{{ profile.user.username }}
        <div class="user-rank">
          <shine-wrapper>
            <img src="https://cdn-icons-png.flaticon.com/512/473/473406.png" class="rank-mark"/>
          </shine-wrapper>
        </div>
      </div>
      <div class="user-description">{{ profile.user.email }}</div>
      <div class="user-description">{{ profile.user.school || "공과대학" }}</div>
      <div class="user-description">{{ profile.user.major || "전기컴퓨터공학부 정보컴퓨터공학전공" }}</div>
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
  padding: 20px;
  gap: 20px;
  display: flex;
  justify-content: space-between;
  border: 1px solid #dedede;
  border-radius: 7px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);

  .avatar-container {
    z-index: 1;
    width: 25%;
    padding: 0 40px;

    .avatar {
      width: 100%;
      height: auto;
      object-fit: contain;
      border-radius: 50%;
      box-shadow: 0 1px 1px 0;
    }
  }

  .user-info {
    width: 50%;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    z-index: 1;

    .username {
      font-size: 20px;
      font-weight: 700;
      display: flex;

      .user-rank {
        width: 30px;
        height: 30px;
        position: relative;
      }

      .rank-mark {
        width: 100%;
        height: auto;
        position: absolute;
        top: 0;
        left: 0;
      }
    }

    .user-description {
      font-size: 14px;
      font-weight: 500;
    }
  }
}

#icons {
  width: 25%;
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: end;
  gap: 20px;
  padding: 10px;
}


</style>
