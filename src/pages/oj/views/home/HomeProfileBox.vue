<template>
  <div class="profileBox">
    <template v-if="!isAuthenticated">
            <span style="font-weight: 600">
              안전한 서비스 이용을 위해 로그인을 해주세요
            </span>
      <div class="loginBtn" @click="handleLoginBtnClick('login')">
        <Icon type="android-lock" size="20"></Icon>
        <span>로그인</span>
      </div>
      <div class="profileBoxFooter">
        <span @click.stop="handleLoginBtnClick('register')">회원가입</span>
        <span @click.stop="goResetPassword">비밀번호 찾기</span>
      </div>
    </template>
    <template v-else>
      <div class="authenticatedBox">
        <div class="authenticatedBody">
          <div class="userAvatarWrapper">
            <img class="avatar" :src="profile.avatar"/>
          </div>
          <div class="userInfoWrapper">
                  <span>
                    {{ user.username + '님' }}
                    <img :src="getTierImageSrc(user.tier)" width="13px"/>
                  </span>
            <br>
<!--            <span>{{ user.email }}</span>-->
            <span>정보컴퓨터공학부</span>
            <br>
            <span>PLATINUM III</span>
          </div>
          <div class="logoutBtn">
                  <span @click="goRouter('logout')">
                    로그아웃
                  </span>
          </div>
        </div>
        <div class="authenticatedFooter">
          <span @click="goRouter('user-home')"><router-link
              :to="{name:'user-home', params:{username:user.username}}">{{ $t('m.MyHome') }}</router-link></span>
          <span>정보수정</span>
          <span @click="goRouter('profile-setting')"><router-link
              :to="{name:'default-setting'}">{{ $t('m.Settings') }}</router-link></span>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import api from '@oj/api'
import {mapActions, mapGetters} from "vuex";
import {getTierImageSrc} from "../../../../utils/constants";

export default {
  name: 'HomeProfileBox',
  data() {
    return {}
  },
  methods: {
    getTierImageSrc,
    ...mapActions(['getProfile', 'changeModalStatus']),
    handleLoginBtnClick(mode) {
      console.log("setting complete!")
      this.changeModalStatus({
        visible: true,
        mode: mode
      })
    },
    handleRoute(route) {
      this.$router.push({name: route});
    },
    goResetPassword() {
      this.changeModalStatus({visible: false});
      this.$router.push({name: "apply-reset-password"});
    },
    goRouter(routeName) {
      this.$router.push({name: routeName})
    }
  },
  computed: {
    ...mapGetters(['website', 'modalStatus', 'user', 'isAuthenticated', 'isAdminRole']),
    ...mapGetters(['profile']),
  }
}
</script>

<style scoped lang="less">
.profileBox {
  background-color: #ffffff;
  border-radius: 7px;
  border: 1px solid #dedede;
  width: 100%;
  height: 200px;
  margin-bottom: 20px;
  text-align: center;
  padding-left: 20px;
  padding-right: 20px;
  padding-top: 25px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);

  .loginBtn {
    cursor: pointer;
    color: white;
    border-radius: 5px;
    height: 60px;
    line-height: 60px;
    background-color: #32306b;
    margin-top: 30px;
    margin-bottom: 30px;

    span {
      margin-left: 10px;
      font-weight: 650;
      font-size: 15px;
    }
  }

  .profileBoxFooter {
    display: flex;
    justify-content: right;

    span {
      cursor: pointer;
    }

    span:nth-child(1) {
      margin-right: 10px;
    }
  }
}

.authenticatedBox {

  @avatar-radius: 50%;

  .avatar {
    width: 100%;
    height: auto;
    max-width: 100%;
    display: block;
    border-radius: @avatar-radius;
    box-shadow: 0px 0px 1px 0px;
  }

  .authenticatedBody {
    display: flex;
    justify-content: space-around;
    align-items: center;
    margin-bottom: 30px;

    .userAvatarWrapper {
      width: 27%;
      height: 100%;
    }

    .userInfoWrapper {
      text-align: left;

      span:first-child {
        font-size: 13px;
        font-weight: 600;
      }
    }

    .logoutBtn {
      cursor: pointer;
      width: 70px;
      padding: 3px 0;
      border-radius: 7px;
      color: white;
      background-color: rgba(34, 33, 72, 0.82);
    }
  }

  .authenticatedFooter {
    display: flex;
    background-color: #FBFBFB;
    justify-content: space-around;
    align-items: center;
    height: 35px;

    span {
      cursor: pointer;

      a {
        color: inherit;
      }
    }
  }
}
</style>
