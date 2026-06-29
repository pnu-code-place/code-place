<template>
  <div id="header" :style="headerStyle">
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
    <!-- 모바일 햄버거 버튼 -->
    <button class="hamburger-btn" @click="mobileMenuOpen = true" aria-label="메뉴 열기">
      <span class="hamburger-line" />
      <span class="hamburger-line" />
      <span class="hamburger-line" />
    </button>

    <!-- 모바일 드로어 오버레이 -->
    <transition name="fade">
      <div v-if="mobileMenuOpen" class="mobile-overlay" @click="mobileMenuOpen = false" />
    </transition>
    <transition name="slide-in">
      <div v-if="mobileMenuOpen" class="mobile-drawer">
        <div class="mobile-drawer-header">
          <LogoButton @click.native="mobileMenuOpen = false" />
          <button class="drawer-close-btn" @click="mobileMenuOpen = false" aria-label="메뉴 닫기">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <nav class="mobile-nav">
          <a class="mobile-nav-item" :class="{ active: activeMenu === '/' }" @click="mobileNavigate('/')">홈</a>
          <a class="mobile-nav-item" :class="{ active: activeMenu === '/problem' }" @click="mobileNavigate('/problem')">문제</a>
          <a class="mobile-nav-item" :class="{ active: activeMenu === '/community' }" @click="mobileNavigate('/community')">커뮤니티</a>
          <div class="mobile-nav-sub">
            <a class="mobile-nav-subitem" @click="mobileNavigate('/community/free')">자유게시판</a>
            <a class="mobile-nav-subitem" @click="mobileNavigate('/community/question')">질문게시판</a>
          </div>
          <a class="mobile-nav-item" :class="{ active: activeMenu === '/contest' }" @click="mobileNavigate('/contest')">대회</a>
          <a class="mobile-nav-item" :class="{ active: activeMenu === '/acm-rank' }" @click="mobileNavigate('/acm-rank')">랭킹</a>
          <a class="mobile-nav-item" :class="{ active: activeMenu === '/status' }" @click="mobileNavigate('/status')">제출 현황</a>
        </nav>
        <div class="mobile-drawer-footer">
          <template v-if="isAuthenticated">
            <a class="mobile-nav-item" @click="mobileNavigate(`/user-home/dashboard/${user.username}`)">마이페이지</a>
            <a class="mobile-nav-item" @click="mobileNavigate('/user-setting')">설정</a>
            <a v-if="isAdminRole" class="mobile-nav-item" @click="mobileNavigate('/admin')">관리자</a>
            <a class="mobile-nav-item danger" @click="mobileNavigate('/logout')">로그아웃</a>
          </template>
          <template v-else>
            <div class="mobile-auth-buttons">
              <button class="btn-login" @click="mobileBtnClick('login')">로그인</button>
              <button class="btn-register" @click="mobileBtnClick('register')">회원가입</button>
            </div>
          </template>
        </div>
      </div>
    </transition>

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
      <div slot="header" class="modal-title">
        <div class="modal-heading">
          {{
            modalStatus.mode === "login"
              ? $t("m.LoginModalHeader")
              : $t("m.RegisterModalHeader")
          }}
        </div>
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
    this.syncHeaderScroll()
    window.addEventListener("scroll", this.handleWindowScroll, { passive: true })
  },
  beforeDestroy() {
    if (this.communityDropdownTimer) {
      clearTimeout(this.communityDropdownTimer)
      this.communityDropdownTimer = null
    }
    window.removeEventListener("scroll", this.handleWindowScroll)
    if (this._headerScrollFrame) {
      cancelAnimationFrame(this._headerScrollFrame)
    }
    this.teardownIndicator()
  },
  data() {
    return {
      mobileMenuOpen: false,
      communityDropdownVisible: false,
      communityDropdownTimer: null,
      indicator: {
        left: 0,
        width: 0,
        visible: false,
      },
      indicatorReady: false,
      headerOffsetX: 0,
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
    mobileNavigate(route) {
      this.mobileMenuOpen = false
      if (route === '/admin') {
        window.open('/admin/')
        return
      }
      if (this.$route.fullPath === route) return
      this.$router.push(route).catch((err) => {
        if (err && err.name !== 'NavigationDuplicated') throw err
      })
    },
    mobileBtnClick(mode) {
      this.mobileMenuOpen = false
      this.changeModalStatus({ visible: true, mode })
    },
    handleBtnClick(mode) {
      this.changeModalStatus({ visible: true, mode })
    handleWindowScroll() {
      if (this._headerScrollFrame) return
      this._headerScrollFrame = requestAnimationFrame(() => {
        this._headerScrollFrame = null
        this.syncHeaderScroll()
      })
    },
    syncHeaderScroll() {
      this.headerOffsetX = window.pageXOffset || window.scrollX || 0
      this.scheduleIndicatorUpdate()
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
    headerStyle() {
      return {
        transform: `translateX(${-this.headerOffsetX}px)`,
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
  min-width: unset;
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
    width: 100%;
    max-width: var(--global-width);
    margin: 0 auto;
    background: transparent;
    padding: 0 30px;

    @media (max-width: 1024px) {
      padding: 0 20px;
    }
    @media (max-width: 768px) {
      padding: 0 14px;
    }
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
    text-align: center;
  }

  &-heading {
    color: #17193d;
    font-size: inherit;
    font-weight: inherit;
    line-height: inherit;
  }

  &-subtitle {
    margin-top: 6px;
    color: #7b8191;
    font-size: 12px;
    font-weight: 500;
    line-height: 1.4;
  }
}

.menuItemText {
  font-size: 18px;
  font-weight: 600;
  line-height: 70px;
  margin-right: 12px;
  color: rgb(15, 19, 23);

  @media (max-width: 1024px) {
    font-size: 15px;
    margin-right: 4px;
  }
  @media (max-width: 768px) {
    display: none !important;
  }
}

/* 모바일에서 auth/user 드롭다운 숨김 */
/deep/ .header-menu > .ivu-dropdown.drop-menu {
  @media (max-width: 768px) {
    display: none !important;
  }
}

.auth-buttons {
  @media (max-width: 768px) {
    display: none !important;
  }
}

.first {
  margin-left: 48px;

  @media (max-width: 768px) {
    margin-left: 0;
  }
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

/* 햄버거 버튼 (모바일 전용) */
.hamburger-btn {
  display: none;
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  width: 38px;
  height: 38px;
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0;
  z-index: 1000;

  @media (max-width: 768px) {
    display: flex;
  }
}

.hamburger-line {
  display: block;
  width: 22px;
  height: 2px;
  border-radius: 2px;
  background-color: #14141f;
}

/* 모바일 오버레이 */
.mobile-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1100;
}

/* 모바일 드로어 */
.mobile-drawer {
  position: fixed;
  top: 0;
  right: 0;
  width: 280px;
  max-width: 90vw;
  height: 100dvh;
  background: #fff;
  z-index: 1200;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.12);
  overflow-y: auto;
}

.mobile-drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  height: var(--header-height);
  border-bottom: 1px solid #f0f0f6;
  flex-shrink: 0;
}

.drawer-close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: #f4f4f8;
  border-radius: 10px;
  color: #555;
  cursor: pointer;
  flex-shrink: 0;

  &:hover {
    background: #ebebf4;
    color: #14141f;
  }
}

.mobile-nav {
  flex: 1;
  padding: 12px 12px 0;
  display: flex;
  flex-direction: column;
}

.mobile-nav-item {
  display: block;
  padding: 13px 14px;
  font-size: 15px;
  font-weight: 600;
  color: #14141f;
  border-radius: 10px;
  cursor: pointer;
  transition: background-color 0.15s;
  text-decoration: none;

  &:hover {
    background-color: #f4f4f8;
  }

  &.active {
    color: #5b64ed;
    background-color: #eeeffe;
  }

  &.danger {
    color: #e24b4a;

    &:hover {
      background-color: #fff0f0;
    }
  }
}

.mobile-nav-sub {
  padding-left: 14px;
  margin-bottom: 4px;
}

.mobile-nav-subitem {
  display: block;
  padding: 9px 14px;
  font-size: 14px;
  font-weight: 500;
  color: #59596b;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.15s;

  &:hover {
    background-color: #f4f4f8;
    color: #5b64ed;
  }
}

.mobile-drawer-footer {
  padding: 12px 12px 24px;
  border-top: 1px solid #f0f0f6;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.mobile-auth-buttons {
  display: flex;
  gap: 8px;
  padding: 4px 2px;

  .btn-login,
  .btn-register {
    flex: 1;
    height: 42px;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
  }

  .btn-login {
    border: 1.5px solid rgba(91, 100, 237, 0.4);
    background: transparent;
    color: #5b64ed;

    &:hover {
      border-color: #5b64ed;
      background: #eeeffe;
    }
  }

  .btn-register {
    border: none;
    background: #5b64ed;
    color: #fff;

    &:hover {
      background: #4a53d4;
    }
  }
}

/* 트랜지션 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.22s ease;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
}

.slide-in-enter-active,
.slide-in-leave-active {
  transition: transform 0.28s cubic-bezier(0.22, 0.61, 0.36, 1);
}
.slide-in-enter,
.slide-in-leave-to {
  transform: translateX(100%);
}
</style>
