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
          <p class="pnuName contest-heading">
            <span>대회</span>
            <span v-if="contestLoaded && contestTitle" class="contest-heading-separator">-</span>
            <span
              v-if="contestLoaded && contestTitle"
              class="contest-heading-title"
              :title="contestTitle"
            >
              {{ contestTitle }}
            </span>
          </p>
        </template>
      </div>
      <div
        v-if="isContestProblemHeader && contestLoaded && countdown"
        class="contest-context"
      >
        <div
          class="contest-timer"
          :class="
            'contest-timer--' +
            (countdownParts ? countdownParts.status : 'ended')
          "
        >
          <template v-if="countdownParts && countdownParts.status !== 'ended'">
            <span class="contest-timer__label">{{
              countdownParts.status === "running" ? "남은 시간" : "시작까지"
            }}</span>
            <span class="contest-timer__text">{{ formattedTime }}</span>
          </template>
          <template v-else>
            <span class="contest-timer__label">대회 종료</span>
          </template>
        </div>
      </div>
      <div class="header-actions">
        <button
          type="button"
          class="header-action-button"
          :aria-label="themeTooltipContent"
          :title="themeTooltipContent"
          @click="toggleProblemTheme"
        >
          <i class="fas fa-adjust"></i>
        </button>
        <button
          v-if="isProblemSolvingHeader"
          type="button"
          class="header-action-button"
          aria-label="설정"
          title="설정"
          @click.stop="openProblemSettings"
        >
          <i class="fas fa-cog"></i>
        </button>
        <div
          v-if="isAuthenticated || !profileResolved"
          class="userAvatarWrapper"
          :class="{ 'userAvatarWrapper--loading': !isAuthenticated }"
          @click="goUserHome"
        >
          <img
            v-if="isAuthenticated && profile.avatar"
            class="avatar"
            :src="profile.avatar"
          />
        </div>
      </div>
    </Menu>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex"
export default {
  mounted() {
    const profileRequest = this.getProfile()
    if (profileRequest && typeof profileRequest.then === "function") {
      profileRequest.then(
        () => {
          this.profileResolved = true
        },
        () => {
          this.profileResolved = true
        },
      )
    } else {
      this.profileResolved = true
    }
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
      profileResolved: false,
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
    openProblemSettings(event) {
      const rect = event.currentTarget.getBoundingClientRect()
      window.dispatchEvent(
        new CustomEvent("open-problem-settings", {
          detail: {
            anchorRect: {
              top: rect.top,
              right: rect.right,
              bottom: rect.bottom,
              left: rect.left,
              width: rect.width,
              height: rect.height,
            },
          },
        }),
      )
    },
  },
  computed: {
    ...mapGetters([
      "website",
      "modalStatus",
      "isAdminRole",
      "isAuthenticated",
      "user",
      "contestLoaded",
      "countdown",
      "countdownParts",
    ]),
    ...mapGetters(["profile"]),
    activeMenu() {
      return "/" + this.$route.path.split("/")[1]
    },
    isContestProblemHeader() {
      return this.$route.name === "contest-problem-details"
    },
    isProblemSolvingHeader() {
      return (
        this.$route.name === "problem-details" ||
        this.$route.name === "contest-problem-details"
      )
    },
    contestTitle() {
      return (this.$store.state.contest.contest || {}).title || ""
    },
    formattedTime() {
      if (!this.countdownParts || this.countdownParts.status === "ended") {
        return ""
      }
      const pad = (num) => String(num).padStart(2, "0")
      const { days, hours, minutes, seconds } = this.countdownParts

      let timeStr = `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`
      if (days > 0) {
        timeStr = `${days}일 ${timeStr}`
      }
      return timeStr
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
  height: 50px;
  z-index: 1000;

  .oj-problem-menu {
    box-sizing: border-box;
    transition: 0.3s;
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
    padding-left: 20px;
    padding-right: 20px;
    height: 50px;
    min-height: 50px;
    max-height: 50px;
    align-items: center;
    column-gap: 16px;
    overflow: hidden;
    border-bottom: 1px solid var(--border-color);
    background-color: var(--bg-color);
    color: var(--text-color);
    line-height: normal;
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
    grid-column: 1;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-self: start;
    min-width: 0;
    max-width: 100%;
    height: 50px;
    .pnuName {
      margin: 0 0 0 10px;
      font-size: 18px;
      font-weight: 600;
      line-height: 20px;
      white-space: nowrap;
    }
  }

  .contest-heading {
    min-width: 0;
    max-width: 42vw;
    display: flex;
    align-items: center;
    gap: 7px;
    line-height: 20px;
  }

  .contest-heading-separator {
    flex: 0 0 auto;
    color: #94a3b8;
    font-weight: 500;
  }

  .contest-heading-title {
    min-width: 0;
    overflow: hidden;
    color: #334155;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 15px;
    font-weight: 600;
  }

  .contest-context {
    grid-column: 2;
    min-width: 0;
    display: flex;
    align-items: center;
    justify-self: center;
    justify-content: center;
    height: 50px;
    padding: 0 8px;
  }

  .header-actions {
    grid-column: 3;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    justify-self: end;
    gap: 12px;
    min-width: 0;
    height: 50px;
  }

  .header-action-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 34px;
    height: 34px;
    border: 0;
    border-radius: 8px;
    background: transparent;
    color: var(--text-color);
    cursor: pointer;
    font-size: 14px;
    line-height: 1;
    transition:
      background-color 0.12s ease,
      color 0.12s ease;
  }

  .header-action-button:hover {
    background-color: rgba(100, 116, 139, 0.1);
  }

  .header-action-button:active {
    background-color: rgba(100, 116, 139, 0.16);
  }

  .userAvatarWrapper {
    box-sizing: border-box;
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

  .userAvatarWrapper--loading {
    cursor: default;
    pointer-events: none;
  }

}

:root.dark.problem #header {
  .header-action-button:hover {
    background-color: rgba(203, 213, 225, 0.1);
  }

  .header-action-button:active {
    background-color: rgba(203, 213, 225, 0.16);
  }

  .contest-heading-separator {
    color: #64748b;
  }

  .contest-heading-title {
    color: #cbd5e1;
  }

  .userAvatarWrapper {
    background-color: rgba(170, 179, 203, 0.14);
  }

  .userAvatarWrapper:hover {
    border-color: rgba(170, 179, 203, 0.34);
    background-color: rgba(170, 179, 203, 0.22);
  }
}

/* ── Contest Timer ── */
.contest-timer {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--text-color);
}

.contest-timer__label {
  font-weight: 500;
  color: #64748b;
}

.contest-timer__text {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--text-color);
}

:root.dark.problem .contest-timer__label {
  color: #94a3b8;
}

@media (max-width: 720px) {
  #header {
    .oj-problem-menu {
      grid-template-columns: minmax(0, auto) minmax(0, 1fr) auto;
      padding-left: 12px;
      padding-right: 12px;
      column-gap: 8px;
    }

    .contest-context {
      padding: 0 4px;
    }

    .contest-timer__text {
      font-size: 12px;
    }

    .contest-heading {
      max-width: 30vw;
      gap: 5px;
    }

    .contest-heading-title {
      font-size: 13px;
    }
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
