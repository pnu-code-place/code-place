<template>
  <div id="header">
    <Menu
      ref="menuRef"
      class="header-menu"
      mode="horizontal"
      @on-select="handleRoute"
      :active-name="activeMenu"
    >
      <LogoButton />
      <Menu-item class="menuItemText first" :class="{ 'nav-active': activeMenu === '/' }" name="/" data-menu-key="/">
        {{ $t("m.Home") }}
      </Menu-item>
      <Menu-item class="menuItemText" :class="{ 'nav-active': activeMenu === '/problem' }" name="/problem" data-menu-key="/problem">
        {{ $t("m.NavProblems") }}
      </Menu-item>
      <Dropdown
        class="ivu-menu-item menuItemText"
        :class="{ 'nav-active': activeMenu === '/community' }"
        data-menu-key="/community"
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
      <Menu-item class="menuItemText" :class="{ 'nav-active': activeMenu === '/contest' }" name="/contest" data-menu-key="/contest">
        {{ $t("m.Contests") }}
      </Menu-item>
      <Menu-item
        class="menuItemText"
        :class="{ 'nav-active': activeMenu === '/acm-rank' }"
        name="/acm-rank"
        data-menu-key="/acm-rank"
      >
        {{ $t("m.Rank") }}
      </Menu-item>
      <Menu-item class="menuItemText" :class="{ 'nav-active': activeMenu === '/status' }" name="/status" data-menu-key="/status">
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
            <img
              class="avatar"
              :src="profile.avatar"
              alt="avatar of the user"
            />
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
      <template v-else>
        <div class="auth-buttons">
          <button class="btn-login" @click="handleBtnClick('login')">
            {{ $t("m.Login") }}
          </button>
          <button class="btn-register" @click="handleBtnClick('register')">
            {{ $t("m.Register") }}
          </button>
        </div>
      </template>
    </Menu>
    <span
      class="menu-hover-indicator"
      :class="{
        'is-visible': indicator.visible,
        'is-ready': indicatorReady,
      }"
      :style="indicatorStyle"
    ></span>
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
    this.$nextTick(this.initIndicator)
  },
  beforeDestroy() {
    if (this.communityDropdownTimer) {
      clearTimeout(this.communityDropdownTimer)
      this.communityDropdownTimer = null
    }
    this.teardownIndicator()
  },
  data() {
    return {
      communityDropdownVisible: false,
      communityDropdownTimer: null,
      indicator: {
        left: 0,
        width: 0,
        visible: false,
      },
      indicatorReady: false,
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
        if (this.$route.fullPath === route) return
        this.$router.push(route).catch((err) => {
          if (err && err.name !== "NavigationDuplicated") throw err
        })
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
    initIndicator() {
      const menuEl = this.$refs.menuRef && this.$refs.menuRef.$el
      if (!menuEl) return
      this._menuEl = menuEl
      this._onMenuOver = this.handleMenuMouseOver.bind(this)
      this._onMenuLeave = this.handleMenuMouseLeave.bind(this)
      this._onWindowResize = () => this.scheduleIndicatorUpdate()
      this._onWindowLoad = () => this.scheduleIndicatorUpdate()
      menuEl.addEventListener("mouseover", this._onMenuOver)
      menuEl.addEventListener("mouseleave", this._onMenuLeave)
      window.addEventListener("resize", this._onWindowResize)
      window.addEventListener("load", this._onWindowLoad)
      this.observeIndicatorLayout(menuEl)
      this.scheduleIndicatorUpdate()
      this.showIndicatorWhenLayoutReady()
    },
    observeIndicatorLayout(menuEl) {
      if (window.ResizeObserver) {
        this._indicatorResizeObserver = new ResizeObserver(() => {
          this.scheduleIndicatorUpdate()
        })
        this._indicatorResizeObserver.observe(menuEl)
        this._indicatorResizeObserver.observe(this.$el)
      }

      this._indicatorImages = Array.prototype.slice.call(
        menuEl.querySelectorAll("img"),
      )
      this._onIndicatorAssetLoad = () => this.scheduleIndicatorUpdate()
      this._indicatorImages.forEach((img) => {
        if (img.complete) return
        img.addEventListener("load", this._onIndicatorAssetLoad)
        img.addEventListener("error", this._onIndicatorAssetLoad)
      })
    },
    showIndicatorWhenLayoutReady() {
      const showIndicator = () => {
        this.scheduleIndicatorUpdate()
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            if (this._menuEl) this.indicatorReady = true
          })
        })
      }

      if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(showIndicator)
      } else {
        showIndicator()
      }
    },
    scheduleIndicatorUpdate() {
      if (this._indicatorFrame) {
        cancelAnimationFrame(this._indicatorFrame)
      }
      this._indicatorFrame = requestAnimationFrame(() => {
        this._indicatorFrame = null
        this.moveIndicatorToActive()
      })
    },
    teardownIndicator() {
      if (this._menuEl) {
        this._menuEl.removeEventListener("mouseover", this._onMenuOver)
        this._menuEl.removeEventListener("mouseleave", this._onMenuLeave)
      }
      if (this._onWindowResize) {
        window.removeEventListener("resize", this._onWindowResize)
      }
      if (this._onWindowLoad) {
        window.removeEventListener("load", this._onWindowLoad)
      }
      if (this._indicatorResizeObserver) {
        this._indicatorResizeObserver.disconnect()
      }
      if (this._indicatorImages && this._onIndicatorAssetLoad) {
        this._indicatorImages.forEach((img) => {
          img.removeEventListener("load", this._onIndicatorAssetLoad)
          img.removeEventListener("error", this._onIndicatorAssetLoad)
        })
      }
      if (this._indicatorFrame) {
        cancelAnimationFrame(this._indicatorFrame)
      }
      this._menuEl = null
      this._onMenuOver = null
      this._onMenuLeave = null
      this._onWindowResize = null
      this._onWindowLoad = null
      this._indicatorResizeObserver = null
      this._indicatorImages = null
      this._onIndicatorAssetLoad = null
      this._indicatorFrame = null
    },
    handleMenuMouseOver(e) {
      if (!this._menuEl) return
      const target = e.target.closest("[data-menu-key]")
      if (!target || !this._menuEl.contains(target)) return
      this.updateIndicator(target, true)
    },
    handleMenuMouseLeave() {
      this.moveIndicatorToActive()
    },
    updateIndicator(el, visible) {
      if (!el || !this.$el) return
      const headerRect = this.$el.getBoundingClientRect()
      const rect = el.getBoundingClientRect()
      this.indicator = {
        left: rect.left - headerRect.left,
        width: rect.width,
        visible,
      }
    },
    moveIndicatorToActive() {
      if (!this._menuEl) return
      const active = this._menuEl.querySelector(
        `[data-menu-key="${this.activeMenu}"]`,
      )
      if (active) {
        this.updateIndicator(active, true)
      } else {
        this.indicator = { ...this.indicator, visible: false }
      }
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
    indicatorStyle() {
      return {
        left: this.indicator.left + "px",
        width: this.indicator.width + "px",
      }
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
  watch: {
    activeMenu() {
      this.$nextTick(() => this.scheduleIndicatorUpdate())
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
  background-color: var(--header-glass-bg);
  -webkit-backdrop-filter: saturate(160%) blur(14px);
  backdrop-filter: saturate(160%) blur(14px);
  z-index: 999;
  border-bottom: 1px solid var(--header-glass-border-color);
  box-shadow: var(--header-glass-shadow);

  .header-menu {
    width: var(--global-width);
    margin: 0 auto;
    background: transparent;
  }

  /deep/ .header-menu.ivu-menu-horizontal,
  /deep/ .header-menu.ivu-menu-horizontal > .ivu-menu-item,
  /deep/ .header-menu.ivu-menu-horizontal > .ivu-dropdown {
    height: var(--header-height);
    line-height: var(--header-height);
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

  /* iView 기본 active/hover border-bottom 을 숨기고 슬라이딩 indicator 로 대체 */
  /deep/ .header-menu.ivu-menu-horizontal > .ivu-menu-item,
  /deep/ .header-menu.ivu-menu-horizontal > .ivu-menu-item-active,
  /deep/ .header-menu.ivu-menu-horizontal > .ivu-menu-item-selected,
  /deep/ .header-menu.ivu-menu-horizontal > .ivu-menu-item:hover,
  /deep/ .header-menu.ivu-menu-horizontal > .ivu-dropdown:hover {
    border-bottom-color: transparent !important;
  }

  .menu-hover-indicator {
    position: absolute;
    bottom: -1px;
    left: 0;
    width: 0;
    height: 3px;
    background-color: #5b64ed;
    opacity: 0;
    pointer-events: none;
    z-index: 1001;
    transform: translateZ(0);
    transition: none;
    will-change: left, width;
  }
  .menu-hover-indicator.is-ready {
    transition:
      left 0.28s cubic-bezier(0.22, 0.61, 0.36, 1),
      width 0.28s cubic-bezier(0.22, 0.61, 0.36, 1),
      opacity 0.18s ease;
  }
  .menu-hover-indicator.is-visible {
    opacity: 1;
  }

  /deep/ .header-menu.ivu-menu-light.ivu-menu-horizontal .ivu-menu-item,
  /deep/ .header-menu.ivu-menu-light.ivu-menu-horizontal .ivu-dropdown,
  /deep/
    .header-menu.ivu-menu-light.ivu-menu-horizontal
    .menuItemText_community {
    color: rgb(15, 19, 23);
  }

  /deep/ .header-menu.ivu-menu-light.ivu-menu-horizontal .ivu-menu-item.ivu-menu-item-active,
  /deep/ .header-menu.ivu-menu-light.ivu-menu-horizontal .ivu-menu-item.ivu-menu-item-selected {
    color: rgb(15, 19, 23);
  }

  /deep/ .header-menu.ivu-menu-light.ivu-menu-horizontal .ivu-menu-item:hover,
  /deep/ .header-menu.ivu-menu-light.ivu-menu-horizontal .ivu-menu-item.nav-active {
    color: #5b64ed;
  }

  /deep/ .header-menu.ivu-menu-light.ivu-menu-horizontal .ivu-dropdown:hover .menuItemText_community,
  /deep/ .header-menu.ivu-menu-light.ivu-menu-horizontal .ivu-dropdown.nav-active .menuItemText_community {
    color: #5b64ed;
  }

  .drop-menu {
    float: right;
    margin-right: 0;
    z-index: 1000;
    height: var(--header-height);
    display: flex;
    align-items: center;
  }

  .auth-buttons {
    float: right;
    display: flex;
    align-items: center;
    gap: 8px;
    height: var(--header-height);
  }

  .btn-login {
    height: 34px;
    line-height: 34px;
    padding: 0 18px;
    border-radius: 999px;
    border: 1px solid rgba(91, 100, 237, 0.4);
    background-color: transparent;
    color: #59596b;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition:
      border-color 0.2s,
      color 0.2s;

    &:hover {
      border-color: #5b64ed;
      color: #5b64ed;
    }
  }

  .btn-register {
    height: 34px;
    line-height: 34px;
    padding: 0 18px;
    border-radius: 999px;
    border: none;
    background-color: #5b64ed;
    color: #ffffff;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;

    &:hover {
      background-color: #4a53d4;
    }
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
    color: #5b64ed !important;
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
    color: #5b64ed !important;
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

.menuItemText:hover,
.menuItemText.nav-active {
  color: #5b64ed;
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
</style>
