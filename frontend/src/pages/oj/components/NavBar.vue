<template>
  <div id="header">
    <Menu mode="horizontal" @on-select="handleRoute" :active-name="activeMenu">
      <LogoButton/>
      <Menu-item class="menuItemText first" name="/">
        {{ $t('m.Home') }}
      </Menu-item>
      <Menu-item class="menuItemText" name="/problem">
        {{ $t('m.NavProblems') }}
      </Menu-item>
      <!--        <Menu-item class="menuItemText" name="/status">-->
      <!--          {{$t('m.Community')}}-->
      <!--        </Menu-item>-->
      <Menu-item class="menuItemText" name="/contest">
        {{ $t('m.Contests') }}
      </Menu-item>
      <Menu-item class="menuItemText" name="/acm-rank">
        {{ $t('m.Rank') }}
      </Menu-item>
      <Menu-item class="menuItemText" name="/status">
        {{ $t('m.NavStatus') }}
      </Menu-item>

      <template v-if="isAuthenticated">
        <Dropdown class="drop-menu" @on-click="handleRoute" placement="bottom" trigger="click">
          <div style="display: flex; align-items: center;">
            <div>
              <img class="avatar" :src="profile.avatar" alt="avatar of the user"/>
            </div>
            <div style="margin-left: 10px">
              <Icon type="arrow-down-b" style="cursor: pointer"></Icon>
            </div>
          </div>
          <Dropdown-menu slot="list">
            <Dropdown-item :name="`/user-home/dashboard/${user.username}`">{{ $t('m.MyHome') }}</Dropdown-item>
            <Dropdown-item name="/status?myself=1">{{ $t('m.MySubmissions') }}</Dropdown-item>
            <Dropdown-item name="/user-setting">{{ $t('m.Settings') }}</Dropdown-item>
            <Dropdown-item v-if="isAdminRole" name="/admin">{{ $t('m.Management') }}</Dropdown-item>
            <Dropdown-item divided name="/logout">{{ $t('m.Logout') }}</Dropdown-item>
          </Dropdown-menu>
        </Dropdown>
      </template>
    </Menu>
    <Modal v-model="modalVisible" :maskClosable="false" :width="400" :styles="{'top': modalStatus.mode === 'login' ? '10%' : '2%'}">
      <div slot="header" class="modal-title" style="text-align: center">
        {{ modalStatus.mode === 'login' ? $t('m.LoginModalHeader') : $t('m.RegisterModalHeader') }}
      </div>
      <component :is="modalStatus.mode" v-if="modalVisible"></component>
      <div slot="footer" style="display: none"></div>
    </Modal>
  </div>
</template>

<script>
import {mapGetters, mapActions} from 'vuex'
import login from '@oj/views/user/Login'
import register from '@oj/views/user/Register'
import LogoButton from "./LogoButton.vue";

export default {
  components: {
    LogoButton,
    login,
    register
  },
  mounted() {
    this.getProfile()
  },
  methods: {
    ...mapActions(['getProfile', 'changeModalStatus']),
    handleRoute(route) {
      if (route && route.indexOf('admin') < 0) {
        this.$router.push(route)
      } else {
        window.open('/admin/')
      }
    },
    handleBtnClick(mode) {
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
    activeMenu() {
      return '/' + this.$route.path.split('/')[1]
    },
    modalVisible: {
      get() {
        return this.modalStatus.visible
      },
      set(value) {
        this.changeModalStatus({visible: value})
      }
    }
  }
}
</script>

<style lang="less" scoped>
#header {
  min-width: var(--global-width);
  position: fixed;
  top: 0;
  left: 0;
  height: var(header-height);
  width: 100%;
  background-color: #fff;
  z-index: 999;
  box-shadow: 0 1px 1.5px 0 rgba(0, 0, 0, 0.1);

  .drop-menu {
    float: right;
    z-index: 1000;
  }
}

.modal {
  &-title {
    font-size: 18px;
    font-weight: 1000;
  }
}

.menuItemText {
  font-size: 18px;
  font-weight: 600;
  line-height: 70px;
  margin-right: 30px;
}

.first {
  margin-left: 100px;
}

.menuItemText:hover {
  color: #32306b;
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
  box-shadow: 0 0 1px 0;
}

.ivu-menu-item-active{
  color: #3c5977!important;
  border-bottom: 2px solid #3c5977!important;

}

.ivu-menu-light.ivu-menu-horizontal .ivu-menu-item:hover {
  color: #3c5977!important;
  border-bottom: 2px solid #3c5977!important;
}

</style>
