<template>
  <div id="header">
    <Menu theme="default" mode="horizontal" @on-select="handleRoute" :active-name="activeMenu" class="oj-menu">
      <div class="logo" @click="handleRoute('/')">
<!--        <img src="@/assets/pnu.png" width="70" height="70"/>-->
        <div class="headerIcon">
          <p class="pnuName">문제 풀이</p>
          <p class="systemTitle">온라인 저지 시스템</p>
        </div>
      </div>

      <template v-if="isAuthenticated">
        <div class="userAvatarWrapper" @click="handleRoute('/user-home')">
          <img class="avatar" :src="profile.avatar"/>
        </div>
<!--        <Dropdown class="drop-menu" @on-click="handleRoute" placement="bottom" trigger="click">-->
<!--          <Button type="text" class="drop-menu-title">{{ user.username+' 님' }}-->
<!--            <Icon type="arrow-down-b"></Icon>-->
<!--          </Button>-->
<!--        </Dropdown>-->
      </template>
    </Menu>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import login from '@oj/views/user/Login'
import register from '@oj/views/user/Register'

export default {
  components: {
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
    }
  },
  computed: {
    ...mapGetters(['website', 'modalStatus', 'user', 'isAuthenticated', 'isAdminRole']),
    ...mapGetters(['profile']),
    // 跟随路由变化
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
  min-width: 300px;
  position: fixed;
  top: 0;
  left: 0;
  height: 50px;
  width: 100%;
  z-index: 1000;
  padding-left: 30px;
  padding-right: 30px;
  background-color: #fff;
  box-shadow: 0 1px 1.5px 0 rgba(0, 0, 0, 0.1);

  .oj-menu {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #fdfdfd;
    height: auto;
    overflow-x: hidden;
  }

  .logo {
    cursor: pointer;
    text-align: left;
    float: left;
    height: auto;
    display: flex;
    line-height: normal;
    .pnuName{
      font-size: 14px;
      font-weight: normal;
    }
    .systemTitle{
      font-size: 18px;
      font-weight: bold;
      color: #255AA4;
    }
  }

  .headerIcon{
    width: auto;
    margin-top: 6%;
  }

  .drop-menu {
    float: right;
    right: 0px;
    &-title {
      font-size: 13px;
    }
  }

}
.btn-menu {
  font-size: 30px;
  height: auto;
  float: right;
}

.modal {
  &-title {
    font-size: 18px;
    font-weight: 1000;
  }
}

.menuItemText{
  font-size: 18px;
  font-weight: 600;
  line-height: 70px;
  margin-right: 30px;
}

.first{
  margin-left: 100px;
}

.menuItemText:hover{
  color: #4A86C0;
}

@avatar-radius: 50%;
.avatar {
  cursor: pointer;
  width: 35px;
  height: auto;
  max-width: 100%;
  display: block;
  border-radius: @avatar-radius;
  border: 1px solid #7a7a7a;
  box-shadow: 0px 0px 1px 0px;
}
</style>
