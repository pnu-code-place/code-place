<template>
  <div id="header">
    <Menu mode="horizontal" @on-select="handleRoute" :active-name="activeMenu" class="oj-menu">
      <div class="logo" @click="handleRoute('/problem')">
        <div>
          <img src="@/assets/pojLogo.png" width="39" style="vertical-align:middle; margin-right: 10px"/>
        </div>
          <p class="pnuName">{{ this.$route.params.problemID + '번' }}</p>
      </div>
      <Tooltip :content="'문제 랜덤 선택'" placement="bottom" style="margin-left: 5px">
        <CustomIconBtn @click="pickOne" iconClass="fas fa-random"/>
      </Tooltip>
      <ProblemTimer/>
      <div style="display: flex; height: 100%; align-items: center">
        <Tooltip :content="'어두운 테마'" placement="bottom"  style="margin-right: 15px">
          <CustomIconBtn iconClass="fas fa-adjust"/>
        </Tooltip>
        <template v-if="isAuthenticated">
          <div class="userAvatarWrapper" @click="handleRoute('/user-home')">
            <img class="avatar" :src="profile.avatar"/>
          </div>
        </template>
      </div>
    </Menu>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import login from '@oj/views/user/Login'
import register from '@oj/views/user/Register'
import ProblemTimer from "./ProblemTimer.vue";
import CustomIconBtn from "./buttons/CustomIconBtn.vue";
import api from '@oj/api'

export default {
  components: {
    CustomIconBtn,
    ProblemTimer,
    login,
    register
  },
  mounted () {
    this.getProfile()
  },
  methods: {
    ...mapActions(['getProfile', 'changeModalStatus']),
    handleRoute (route) {
      if (route && route.indexOf('admin') < 0) {
        this.$router.push(route)
      } else {
        window.open('/admin/')
      }
    },
    handleBtnClick (mode) {
      console.log("setting complete!")
      this.changeModalStatus({
        visible: true,
        mode: mode
      })
    },
    pickOne() {
      api.pickone().then(res => {
        // this.$success('')
        this.$router.push({name: 'problem-details', params: {problemID: res.data.data}})
      })
    },
  },
  computed: {
    ...mapGetters(['website', 'modalStatus', 'user', 'isAuthenticated', 'isAdminRole']),
    ...mapGetters(['profile']),
    activeMenu () {
      return '/' + this.$route.path.split('/')[1]
    },
    modalVisible: {
      get () {
        return this.modalStatus.visible
      },
      set (value) {
        this.changeModalStatus({visible: value})
      }
    }
  }
}
</script>

<style lang="less" scoped>
#header {
  position: fixed;
  top: 0;
  left: 0;
  height: 50px;
  width: 100%;
  z-index: 1000;
  background-color: #fff;

  .oj-menu {
    display: flex;
    padding-left: 30px;
    padding-right: 30px;
    justify-content: space-between;
    align-items: center;
    height: 100%;
  }

  .logo {
    cursor: pointer;
    display: flex;
    align-items: center;
    .pnuName{
      font-size: 14px;
      font-weight: bold;
    }
  }
}

@avatar-radius: 50%;
.avatar {
  cursor: pointer;
  width: 35px;
  max-width: 100%;
  display: block;
  border-radius: @avatar-radius;
  border: 1px solid #7a7a7a;
}
</style>
