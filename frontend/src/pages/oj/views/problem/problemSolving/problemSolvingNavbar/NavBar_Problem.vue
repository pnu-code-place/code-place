<template>
  <div id="header">
    <Menu
      mode="horizontal"
      theme="primary"
      @on-select="handleRoute"
      :active-name="activeMenu"
      class="oj-problem-menu"
    >
      <div class="logo" @click="goHeadPage()">
        <img class="solvingLogo" src="@/assets/code-place-logo.svg" />
        <template v-if="this.$route.name === 'problem-details'">
          <p class="pnuName">{{ "문제 풀이" }}</p>
        </template>
        <template v-else>
          <p class="pnuName">{{ "대회" }}</p>
        </template>
      </div>
      <div
        class="header-actions"
      >
        <Tooltip
          :content="this.themeTooltipContent"
          placement="bottom"
          class="theme-toggle"
        >
          <CustomIconBtn
            @click="toggleProblemTheme"
            iconClass="fas fa-adjust"
          />
        </Tooltip>
        <template v-if="isAuthenticated">
          <div class="userAvatarWrapper" @click="goUserHome">
            <img class="avatar" :src="profile.avatar" />
          </div>
        </template>
      </div>
    </Menu>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex"
import login from "@oj/views/user/Login"
import register from "@oj/views/user/Register"
import CustomIconBtn from "../../../../components/buttons/CustomIconBtn.vue"
export default {
  components: {
    CustomIconBtn,
    login,
    register,
  },
  mounted() {
    this.getProfile()
    const el = document.querySelector(":root")
    el.classList.add("problem")
  },
  destroyed() {
    const el = document.querySelector(":root")
    el.classList.remove("problem")
  },
  data() {
    return {
      themeTooltipContent: "다크 테마",
    }
  },
  methods: {
    ...mapActions([
      "getProfile",
      "changeModalStatus",
      "changeProblemSolvingTheme",
    ]),
    handleRoute(route) {
      if (route && route.indexOf("admin") < 0) {
        if (this.$route.fullPath === route) return
        this.$router.push(route).catch((err) => {
          if (err && err.name !== "NavigationDuplicated") throw err
        })
      } else {
        window.open("/admin/")
      }
    },
    toggleProblemTheme() {
      const el = document.querySelector(":root")
      const isLightMode = !el.classList.contains("dark")
      if (isLightMode) {
        el.classList.add("dark")
        this.changeProblemSolvingTheme(true)
        this.themeTooltipContent = "라이트 테마"
      } else {
        el.classList.remove("dark")
        this.changeProblemSolvingTheme(false)
        this.themeTooltipContent = "다크 테마"
      }
    },
    goUserHome() {
      if (!this.user.username) return
      this.$router.push({
        name: "user-dashboard",
        params: { username: this.user.username },
      })
    },
    goHeadPage() {
      if (this.$route.name === "problem-details") this.handleRoute("/problem")
      else this.handleRoute(`/contest/${this.$route.params.contestID}/problems`)
    },
  },
  computed: {
    ...mapGetters([
      "website",
      "modalStatus",
      "isAdminRole",
      "isAuthenticated",
      "user",
    ]),
    ...mapGetters(["profile"]),
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

<style scoped lang="less">
#header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;

  .oj-problem-menu {
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

  /deep/ .oj-problem-menu.ivu-menu-primary {
    background-color: var(--bg-color);
    color: var(--text-color);
  }

  /deep/ .oj-problem-menu.ivu-menu-horizontal::after {
    height: 0;
    background: transparent;
  }

  .logo {
    cursor: pointer;
    display: flex;
    align-items: center;
    .pnuName {
      margin-left: 10px;
      font-size: 16px;
      font-weight: bold;
    }
  }

  .header-actions {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 12px;
    width: 200px;
  }

  .theme-toggle {
    display: flex;
  }

  .userAvatarWrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    padding: 3px;
    border: 1px solid var(--header-glass-border-color);
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.72);
    cursor: pointer;
    transition:
      border-color 0.2s ease,
      background-color 0.2s ease;
  }

  .userAvatarWrapper:hover {
    border-color: rgba(50, 48, 107, 0.28);
    background-color: rgba(255, 255, 255, 0.9);
  }

}

:root.dark.problem #header {
  .userAvatarWrapper {
    background-color: rgba(170, 179, 203, 0.14);
  }

  .userAvatarWrapper:hover {
    border-color: rgba(170, 179, 203, 0.34);
    background-color: rgba(170, 179, 203, 0.22);
  }

}

.solvingLogo {
  display: block;
  width: 25px;
}

@avatar-radius: 50%;
.avatar {
  cursor: pointer;
  width: 100%;
  height: 100%;
  max-width: 100%;
  display: block;
  border-radius: @avatar-radius;
  border: 0;
  object-fit: cover;
}
</style>
