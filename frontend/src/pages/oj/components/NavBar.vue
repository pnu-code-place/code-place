<template>
  <div id="header">
    <Menu
      class="header-menu"
      mode="horizontal"
      @on-select="handleRoute"
      :active-name="activeMenu"
    >
      <LogoButton />
      <Menu-item class="menuItemText first" name="/">
        {{ $t("m.Home") }}
      </Menu-item>
      <Menu-item class="menuItemText" name="/problem">
        {{ $t("m.NavProblems") }}
      </Menu-item>
      <Dropdown
        class="ivu-menu-item menuItemText"
        trigger="custom"
        :visible="communityDropdownVisible"
        placement="bottom"
        @on-click="handleRoute"
        @mouseenter.native="showCommunityDropdown"
        @mouseleave.native="hideCommunityDropdown"
      >
        <span class="menuItemText_community" @click="handleRoute('/community')">
          {{ $t("m.Community") }}
        </span>
        <Dropdown-menu class="community-dropdown-menu" slot="list">
          <Dropdown-item name="/community/free">{{
            $t("m.Community_Free")
          }}</Dropdown-item>
          <Dropdown-item name="/community/question">{{
            $t("m.Community_Question")
          }}</Dropdown-item>
        </Dropdown-menu>
      </Dropdown>
      <Menu-item class="menuItemText" name="/contest">
        {{ $t("m.Contests") }}
      </Menu-item>
      <Menu-item class="menuItemText" name="/acm-rank">
        {{ $t("m.Rank") }}
      </Menu-item>
      <Menu-item class="menuItemText" name="/status">
        {{ $t("m.NavStatus") }}
      </Menu-item>

      <template v-if="isAuthenticated">
        <Dropdown
          class="drop-menu"
          @on-click="handleRoute"
          placement="bottom"
          trigger="click"
        >
          <div class="user-menu-trigger">
            <img class="avatar" :src="profile.avatar" alt="avatar of the user" />
            <Icon class="user-menu-arrow" type="arrow-down-b"></Icon>
          </div>
          <Dropdown-menu class="user-dropdown-menu" slot="list">
            <Dropdown-item :name="`/user-home/dashboard/${user.username}`">{{
              $t("m.MyHome")
            }}</Dropdown-item>
            <Dropdown-item name="/status?myself=1">{{
              $t("m.MySubmissions")
            }}</Dropdown-item>
            <Dropdown-item name="/user-setting">{{
              $t("m.Settings")
            }}</Dropdown-item>
            <Dropdown-item v-if="isAdminRole" name="/admin">{{
              $t("m.Management")
            }}</Dropdown-item>
            <Dropdown-item divided name="/logout">{{
              $t("m.Logout")
            }}</Dropdown-item>
          </Dropdown-menu>
        </Dropdown>
      </template>
    </Menu>
    <Modal
      v-model="modalVisible"
      :maskClosable="false"
      :width="400"
      :styles="{ top: modalStatus.mode === 'login' ? '10%' : '2%' }"
    >
      <div slot="header" class="modal-title" style="text-align: center">
        {{
          modalStatus.mode === "login"
            ? $t("m.LoginModalHeader")
            : $t("m.RegisterModalHeader")
        }}
      </div>
      <component :is="modalStatus.mode" v-if="modalVisible"></component>
      <div slot="footer" style="display: none"></div>
    </Modal>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex"
import login from "@oj/views/user/Login"
import register from "@oj/views/user/Register"
import LogoButton from "./LogoButton.vue"

export default {
  components: {
    LogoButton,
    login,
    register,
  },
  mounted() {
    this.getProfile()
  },
  beforeDestroy() {
    if (this.communityDropdownTimer) {
      clearTimeout(this.communityDropdownTimer)
      this.communityDropdownTimer = null
    }
  },
  data() {
    return {
      communityDropdownVisible: false,
      communityDropdownTimer: null,
    }
  },
  methods: {
    ...mapActions(["getProfile", "changeModalStatus"]),
    showCommunityDropdown() {
      if (this.communityDropdownTimer) {
        clearTimeout(this.communityDropdownTimer)
        this.communityDropdownTimer = null
      }
      this.communityDropdownVisible = true
    },
    hideCommunityDropdown() {
      if (this.communityDropdownTimer) clearTimeout(this.communityDropdownTimer)
      this.communityDropdownTimer = setTimeout(() => {
        this.communityDropdownVisible = false
      }, 80)
    },
    handleRoute(route) {
      this.communityDropdownVisible = false
      if (route && route.indexOf("admin") < 0) {
        this.$router.push(route)
      } else {
        window.open("/admin/")
      }
    },
    handleBtnClick(mode) {
      console.log("setting complete!")
      this.changeModalStatus({
        visible: true,
        mode: mode,
      })
    },
  },
  computed: {
    ...mapGetters([
      "website",
      "modalStatus",
      "user",
      "isAuthenticated",
      "isAdminRole",
    ]),
    ...mapGetters(["profile"]),
    // 跟随路由变化
    activeMenu() {
      return "/" + this.$route.path.split("/")[1]
    },
    modalVisible: {
      get() {
        return this.modalStatus.visible
      },
      set(value) {
        this.changeModalStatus({ visible: value })
      },
    },
  },
}
</script>

<style lang="less" scoped>
#header {
  min-width: var(--global-width);
  position: fixed;
  top: 0;
  left: 0;
  height: var(--header-height);
  width: 100%;
  background-color: #fff;
  z-index: 999;
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.045);

  .header-menu {
    width: var(--global-width);
    margin: 0 auto;
  }

  .header-menu.ivu-menu-horizontal.ivu-menu-light::after {
    height: 0;
    background: transparent;
  }

  /deep/ .header-menu.ivu-menu-horizontal > .ivu-menu-item,
  /deep/ .header-menu.ivu-menu-horizontal > .ivu-dropdown {
    padding-right: 14px;
    padding-left: 14px;
  }

  /deep/ .header-menu.ivu-menu-light.ivu-menu-horizontal .ivu-menu-item,
  /deep/ .header-menu.ivu-menu-light.ivu-menu-horizontal .ivu-dropdown,
  /deep/ .header-menu.ivu-menu-light.ivu-menu-horizontal .menuItemText_community {
    color: rgb(15, 19, 23);
  }

  .drop-menu {
    float: right;
    margin-right: 0;
    z-index: 1000;
    height: var(--header-height);
    display: flex;
    align-items: center;
  }

  .user-menu-trigger {
    display: flex;
    align-items: center;
    gap: 8px;
    height: 36px;
    padding: 0 10px 0 6px;
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 999px;
    background-color: #fff;
    cursor: pointer;
    transition:
      border-color 0.2s ease,
      background-color 0.2s ease;
  }

  .user-menu-trigger:hover {
    border-color: rgba(50, 48, 107, 0.28);
    background-color: rgba(50, 48, 107, 0.04);
  }

  .user-menu-arrow {
    color: rgb(15, 19, 23);
    font-size: 12px;
    line-height: 1;
    opacity: 0.72;
  }

  .menuItemText_community {
    cursor: pointer;
  }

  /deep/ .community-dropdown-menu .ivu-dropdown-item {
    min-width: 132px;
    padding: 8px 16px;
    text-align: left;
    font-family:
      "Noto Sans KR", "Apple SD Gothic Neo", "Helvetica Neue", Helvetica, Arial,
      sans-serif;
    font-size: 14px !important;
    font-weight: 400 !important;
    color: rgb(15, 19, 23) !important;
  }

  /deep/ .header-menu > .ivu-dropdown.menuItemText > .ivu-select-dropdown {
    padding: 4px 0;
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
  }

  /deep/ .drop-menu > .ivu-select-dropdown {
    min-width: 156px;
    padding: 6px;
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 8px;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.09);
  }

  /deep/ .user-dropdown-menu .ivu-dropdown-item {
    padding: 9px 12px;
    border-radius: 6px;
    font-family:
      "Noto Sans KR", "Apple SD Gothic Neo", "Helvetica Neue", Helvetica, Arial,
      sans-serif;
    font-size: 14px !important;
    font-weight: 400 !important;
    line-height: 20px;
    color: rgb(15, 19, 23) !important;
  }

  /deep/ .user-dropdown-menu .ivu-dropdown-item:hover {
    color: #32306b !important;
    background-color: rgba(15, 19, 23, 0.04) !important;
  }

  /deep/ .user-dropdown-menu .ivu-dropdown-item-divided {
    margin-top: 6px;
    border-top: 1px solid rgba(15, 23, 42, 0.08);
  }

  /deep/ .user-dropdown-menu .ivu-dropdown-item-divided::before {
    height: 6px;
    margin: 0 -12px;
    background-color: #fff;
    top: -9px;
  }

  /deep/ .community-dropdown-menu .ivu-dropdown-item:first-child {
    border-radius: 5px 5px 0 0;
  }

  /deep/ .community-dropdown-menu .ivu-dropdown-item:last-child {
    border-radius: 0 0 5px 5px;
  }

  /deep/ .community-dropdown-menu .ivu-dropdown-item:hover {
    color: #32306b !important;
    background-color: rgba(15, 19, 23, 0.04) !important;
  }

  /deep/ .community-dropdown-menu .ivu-dropdown-item:first-child:hover {
    margin-top: -4px;
    padding-top: 12px;
  }

  /deep/ .community-dropdown-menu .ivu-dropdown-item:last-child:hover {
    margin-bottom: -4px;
    padding-bottom: 12px;
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
  margin-right: 12px;
  color: rgb(15, 19, 23);
}

.first {
  margin-left: 48px;
}

.menuItemText:hover {
  color: #32306b;
}

@avatar-radius: 50%;

.avatar {
  width: 27px;
  height: 27px;
  display: block;
  border-radius: @avatar-radius;
  border: none;
  object-fit: cover;
}

.ivu-menu-item-active {
  color: #32306b !important;
  border-bottom: 3px solid #32306b !important;
}

.ivu-menu-light.ivu-menu-horizontal .ivu-menu-item:hover {
  color: #32306b !important;
  border-bottom: 3px solid #32306b !important;
}
</style>
