<template>
  <div id="header">
    <Menu theme="default" mode="horizontal" @on-select="handleRoute" :active-name="activeMenu" class="oj-menu">
      <div class="logo" @click="handleRoute('/')">
        <img src="@/assets/pnu.png" width="70" height="70"/>
        <div class="headerIcon">
          <p class="pnuName">부산대학교</p>
          <p class="systemTitle">온라인 저지 시스템</p>
        </div>
      </div>

      <Menu-item class="menuItemText first" name="/">
        {{$t('m.Home')}}
      </Menu-item>
<!--      <Menu-item class="menuItemText" name="/notice">-->
<!--        {{$t('m.Notice')}}-->
<!--      </Menu-item>-->
      <Menu-item class="menuItemText" name="/problem">
        {{$t('m.NavProblems')}}
      </Menu-item>
      <Menu-item class="menuItemText" name="/status">
        {{$t('m.Community')}}
      </Menu-item>
      <Menu-item class="menuItemText" name="/contest">
        {{$t('m.Contests')}}
      </Menu-item>
<!--      <Menu-item class="menuItemText" name="/status"> //TODO 채점현황-->
<!--        {{$t('m.NavStatus')}}-->
<!--      </Menu-item>-->
      <Menu-item class="menuItemText" name="/status">
        {{$t('m.Rank')}}
      </Menu-item>
<!--        <Menu-item class="menuItemText" name="/status">-->
<!--            {{$t('m.About')}}-->
<!--        </Menu-item>-->
<!--      <Menu-item class="menuItemText" name="/status">-->
<!--        {{$t('m.NavStatus')}}-->
<!--      </Menu-item>-->
<!--      <Submenu name="rank">-->
<!--        <template slot="title">-->
<!--          {{$t('m.Rank')}}-->
<!--        </template>-->
<!--        <Menu-item name="/acm-rank">-->
<!--          {{$t('m.ACM_Rank')}}-->
<!--        </Menu-item>-->
<!--        <Menu-item name="/oi-rank">-->
<!--          {{$t('m.OI_Rank')}}-->
<!--        </Menu-item>-->
<!--      </Submenu>-->
<!--      <Submenu name="about">-->
<!--        <template  slot="title">-->
<!--            {{$t('m.About')}}-->
<!--        </template>-->
<!--        <Menu-item name="/about">-->
<!--          {{$t('m.Judger')}}-->
<!--        </Menu-item>-->
<!--        <Menu-item name="/FAQ">-->
<!--          {{$t('m.FAQ')}}-->
<!--        </Menu-item>-->
<!--      </Submenu>-->

      <template v-if="isAuthenticated">
        <Dropdown class="drop-menu" @on-click="handleRoute" placement="bottom" trigger="click">
          <Button type="text" class="drop-menu-title">{{ user.username+' 님' }}
            <Icon type="arrow-down-b"></Icon>
          </Button>
          <Dropdown-menu slot="list">
            <Dropdown-item name="/user-home">{{$t('m.MyHome')}}</Dropdown-item>
            <Dropdown-item name="/status?myself=1">{{$t('m.MySubmissions')}}</Dropdown-item>
            <Dropdown-item name="/setting/profile">{{$t('m.Settings')}}</Dropdown-item>
            <Dropdown-item v-if="isAdminRole" name="/admin">{{$t('m.Management')}}</Dropdown-item>
            <Dropdown-item divided name="/logout">{{$t('m.Logout')}}</Dropdown-item>
          </Dropdown-menu>
        </Dropdown>
      </template>
    </Menu>
    <Modal v-model="modalVisible" :width="400" :styles="{'top': modalStatus.mode == 'login' ? '10%' : '10%'}">
      <div slot="header" class="modal-title" style="text-align: center">{{modalStatus.mode == 'login' ? $t('m.LoginModalHeader') : $t('m.RegisterModalHeader') }}</div>
      <component :is="modalStatus.mode" v-if="modalVisible"></component>
      <div slot="footer" style="display: none"></div>
    </Modal>
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
    padding-left: 10%;
    padding-right: 10%;
    top: 0;
    left: 0;
    height: 8%;
    width: 100%;
    z-index: 1000;
    background-color: #fff;
    box-shadow: 0 1px 1.5px 0 rgba(0, 0, 0, 0.1);

    .oj-menu {
      background: #fdfdfd;
      height: auto;
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
        font-size: 18px;
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
</style>
