<template>
  <div id="header">
    <Menu mode="horizontal" theme="primary" @on-select="handleRoute" :active-name="activeMenu" class="oj-menu">
      <div class="logo" @click="goHeadPage()">
        <img class="solvingLogo" src="@/assets/pojLogo.png"/>
        <template v-if="this.$route.name === 'problem-details'">
          <p class="pnuName">{{ '문제 풀이' }}</p>
        </template>
        <template v-else>
          <p class="pnuName">{{ '대회' }}</p>
        </template>
      </div>
      <div style="display: flex; align-items: center; width: 200px;justify-content: right">
        <Tooltip :content="this.themeTooltipContent" placement="bottom"  style="margin-right: 15px">
          <CustomIconBtn @click="toggleProblemTheme" iconClass="fas fa-adjust"/>
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
import CustomIconBtn from "../../../../components/buttons/CustomIconBtn.vue";
export default {
  components: {
    CustomIconBtn,
    login,
    register
  },
  mounted () {
    this.getProfile()
    const el = document.querySelector(':root');
    el.classList.add('problem')
  },
  destroyed() {
    const el = document.querySelector(':root');
    el.classList.remove('problem')
  },
  data(){
    return{
      themeTooltipContent: '다크 테마',
    }
  },
  methods: {
    ...mapActions(['getProfile', 'changeModalStatus', 'changeProblemSolvingTheme']),
    handleRoute(route) {
      if (route && route.indexOf('admin') < 0) {
        this.$router.push(route)
      } else {
        window.open('/admin/')
      }
    },
    toggleProblemTheme() {
      const el = document.querySelector(':root');
      const isLightMode = !el.classList.contains('dark');
      if (isLightMode) {
        el.classList.add('dark')
        this.changeProblemSolvingTheme(true)
        this.themeTooltipContent = '라이트 테마'
      } else {
        el.classList.remove('dark');
        this.changeProblemSolvingTheme(false)
        this.themeTooltipContent = '다크 테마'
      }
    },
    goHeadPage() {
      if(this.$route.name === 'problem-details')
        this.handleRoute('/problem');
      else 
        this.handleRoute(`/contest/${this.$route.params.contestID}/problems`);
    }
  },
  computed: {
    ...mapGetters(['website', 'modalStatus', 'isAdminRole','isAuthenticated']),
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
  },
}
</script>

<style scoped lang="less">
#header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;

  .oj-menu{
    transition: 0.3s;
    display: flex;
    padding-left: 20px;
    padding-right: 20px;
    justify-content: space-between;
    height: 50px;
    align-items: center;
    border-bottom: 1px solid var(--border-color);
    background-color: var(--bg-color);
    color: var(--text-color);
  }

  .logo {
    cursor: pointer;
    display: flex;
    align-items: center;
    .pnuName{
      margin-left: 10px;
      font-size: 16px;
      font-weight: bold;
    }
  }
}

.solvingLogo{
  display: block;
  width: 35px;
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
