<template>
  <div id="wrapper">
    <template v-if="isProblemSolving">
      <NavBar_Problem></NavBar_Problem>
    </template>
    <template v-else>
      <NavBar></NavBar>
    </template>
    <div
      class="content-app"
      :class="{ ps: isProblemSolving, 'submission-list-app': isSubmissionList }"
    >
      <transition name="fadeInUp" mode="out-in">
        <router-view></router-view>
      </transition>
    </div>
    <template v-if="!isProblemSolving">
      <div
        class="footer-dummy"
        :class="{ 'submission-list-footer-dummy': isSubmissionList }"
      ></div>
      <CSEPFooter></CSEPFooter>
    </template>
    <BackTop></BackTop>
  </div>
</template>

<script>
import { mapActions, mapGetters, mapState } from "vuex"
import NavBar from "./components/NavBar.vue"
import NavBar_Problem from "./views/problem/problemSolving/problemSolvingNavbar/NavBar_Problem.vue"
import CSEPFooter from "./views/general/CSEPFooter.vue"

export default {
  name: "app",
  components: {
    CSEPFooter,
    NavBar_Problem,
    NavBar,
  },
  created() {
    try {
      document.body.removeChild(document.getElementById("app-loader"))
    } catch (e) {
      // ignore when loader is already removed
    }
  },
  mounted() {
    this.getWebsiteConfig()
    this.syncSubmissionListChrome()
  },
  updated() {
    this.syncSubmissionListChrome()
  },
  beforeDestroy() {
    this.syncSubmissionListChrome(false)
  },
  methods: {
    ...mapActions(["getWebsiteConfig", "changeDomTitle"]),
    syncSubmissionListChrome(force) {
      const enabled =
        typeof force === "boolean" ? force : this.isSubmissionList
      document.documentElement.classList.toggle(
        "submission-list-page",
        enabled,
      )
      document.body.classList.toggle("submission-list-page", enabled)
    },
  },
  computed: {
    ...mapState(["website"]),
    ...mapGetters(["isProblemSolving", "removedPopupId"]),
    isSubmissionList() {
      return (
        this.$route.name === "submission-list" || this.$route.path === "/status"
      )
    },
  },
  watch: {
    website() {
      this.changeDomTitle()
    },
    $route: {
      immediate: true,
      handler() {
        this.changeDomTitle()
        this.$nextTick(() => {
          this.syncSubmissionListChrome()
        })
      },
    },
  },
}
</script>

<style lang="less">
#wrapper {
  min-height: calc(100vh - var(--header-height) - var(--header-margin));
  position: relative;
}

h1.main-title {
  font-size: var(--title_font-size);
  font-weight: var(--title_font-weight);
  color: var(--title-font-color);
}

:root {
  /* Site Global Variable */
  --box-background-color: #ffffff;
  --site-background-color: #f9fafb;
  --bg-color: #ffffff;
  --custom-btn-hover-color: #ffffff;
  --border-color: #e7e7e7;
  --header-btn-color: rgba(237, 237, 237, 0.45);
  --difficulty-color: #e7e7e7;
  --title-font-color: var(--container-font-color);
  --title_font-size: 24px;
  --title_font-weight: 700;

  --point-color: #5b64ed;
  --pale-point-color: #f8f9ff;
  // hex #024D97; to rgb 2, 77, 151
  --pnu-green: rgb(6, 186, 110);
  --pnu-blue: rgb(2, 77, 151);

  --pale-pnu-green: rgba(6, 186, 110, 0.05);
  --pale-pnu-blue: rgba(2, 77, 151, 0.05);

  --pale-gold-color: #faf882;
  --pale-silver-color: #f4f4f4;
  --pale-bronze-color: #d6c68b;

  /* Problem Solving Page */
  --ps-background-color: #f9fafb;
  /* Problem Solving Page - Inner Content */
  --ps-content-color: #ffffff;
  --ps-content-text-color: #454545;
  --ps-content-title-color: #000000;
  --ps-content-pre-background-color: #f6f6f6;
  --ps-content-pre-border-color: #e7e7e7;
  --ps-content-code-background-color: #f3f4f4;
  --ps-content-code-text-color: #1a1f29;
  /* Code Submission */
  --submit-btn-color: rgba(238, 247, 251, 0.84);
  --submit-btn-hover-color: rgba(221, 240, 250, 0.84);
  --submission-result-btn-color: #f8f8f8;
  --submission-result-btn-text-color: #d1d1d1;
  --submission-primary-btn-bg: #4398ff;
  --submission-primary-btn-text-color: #ffffff;
  --submission-primary-btn-hover-bg: #2b84f0;
  --submission-primary-btn-hover-text-color: #ffffff;
  --ai-assistant-btn-bg: #f0f1ff;
  --ai-assistant-btn-text-color: #000478;
  --ai-assistant-btn-hover-bg: #000478;
  --ai-assistant-btn-hover-text-color: #f0f1ff;
  --ai-assistant-btn-icon-color: #000478;
  --ai-assistant-btn-hover-icon-color: #f0f1ff;
  --ai-assistant-panel-bg: #f8f9ff;
  --ai-assistant-header-bg: #ffffff;
  --ai-assistant-border-color: #e0e0e0;
  --ai-assistant-header-border-color: #e8e8e8;
  --ai-assistant-tab-text-color: #999999;
  --ai-assistant-tab-active-color: #3a3fc4;
  --ai-assistant-muted-text-color: #666666;
  --ai-assistant-subtle-text-color: #555555;
  --ai-assistant-subtle-bg: #eef0ff;
  --ai-assistant-subtle-hover-bg: #dde0ff;
  --ai-assistant-avatar-bg: #dde0ff;
  --ai-assistant-avatar-icon-filter: invert(18%) sepia(79%) saturate(3438%)
    hue-rotate(234deg) brightness(68%) contrast(117%);
  --ai-assistant-bubble-bg: #eef0ff;
  --ai-assistant-bubble-text-color: #222222;
  --ai-assistant-thinking-bg: #f0f0f0;
  --ai-assistant-thinking-text-color: #888888;
  --ai-assistant-close-text-color: #aaaaaa;
  --ai-assistant-close-hover-bg: #eeeeee;
  --ai-assistant-close-hover-text-color: #555555;
  --ai-assistant-error-text-color: #c0392b;

  /* Contest Page */
  --container-border-color: #dedede;
  --rule-type-border-color: #6b6b6b;
  --container-font-color: #495060;
  --container-border-radius: 10px;
  --container-comment-color: #7e7e7e;

  /* header */
  --header-height: 64px;
  --header-margin: 20px;
  --header-glass-bg: rgba(255, 255, 255, 0.78);
  --header-glass-border-color: rgba(15, 23, 42, 0.08);
  --header-glass-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
  /* footer */
  --footer-height: 200px;
  --footer-margin: 80px;

  --global-width: 1200px;
}

:root.dark.problem {
  /* Problem Solving Page */
  --ps-background-color: #181c25;
  /* Problem Solving Page - Inner Content */
  --ps-content-color: #1f2430;
  --ps-content-text-color: #b2c0cc;
  --ps-content-title-color: #ffffff;
  --ps-content-pre-background-color: #1a1f29;
  --ps-content-pre-border-color: rgba(140, 140, 140, 0.29);
  --ps-content-code-background-color: #1b212c;
  --ps-content-code-text-color: #ffffff;
  /* Code Submission */
  --submit-btn-color: #343f5a;
  --submit-btn-hover-color: #364361;
  --submission-result-btn-color: #1b212c;
  --submission-result-btn-text-color: #333842;
  --submission-primary-btn-bg: #4d8ff5;
  --submission-primary-btn-text-color: #ffffff;
  --submission-primary-btn-hover-bg: #679ffc;
  --submission-primary-btn-hover-text-color: #ffffff;
  --ai-assistant-btn-bg: #343f5a;
  --ai-assistant-btn-text-color: #ffffff;
  --ai-assistant-btn-hover-bg: #465477;
  --ai-assistant-btn-hover-text-color: #ffffff;
  --ai-assistant-btn-icon-color: #ffffff;
  --ai-assistant-btn-hover-icon-color: #ffffff;
  --ai-assistant-panel-bg: #1f2430;
  --ai-assistant-header-bg: #1b212c;
  --ai-assistant-border-color: rgba(140, 140, 140, 0.29);
  --ai-assistant-header-border-color: rgba(140, 140, 140, 0.29);
  --ai-assistant-tab-text-color: #b2c0cc;
  --ai-assistant-tab-active-color: #ffffff;
  --ai-assistant-muted-text-color: #b2c0cc;
  --ai-assistant-subtle-text-color: #d0d8e2;
  --ai-assistant-subtle-bg: #343f5a;
  --ai-assistant-subtle-hover-bg: #465477;
  --ai-assistant-avatar-bg: #364361;
  --ai-assistant-avatar-icon-filter: brightness(0) saturate(100%) invert(99%)
    sepia(19%) saturate(331%) hue-rotate(176deg) brightness(116%) contrast(87%);
  --ai-assistant-bubble-bg: #343f5a;
  --ai-assistant-bubble-text-color: #ffffff;
  --ai-assistant-thinking-bg: #2a3142;
  --ai-assistant-thinking-text-color: #c6d1dc;
  --ai-assistant-close-text-color: #c6d1dc;
  --ai-assistant-close-hover-bg: #343f5a;
  --ai-assistant-close-hover-text-color: #ffffff;
  --ai-assistant-error-text-color: #ff9e9e;

  --bg-color: #1f2430;
  --text-color: #ffffff;
  --difficulty-color: #5a6885;
  --custom-btn-hover-color: #465477;
  --border-color: rgba(140, 140, 140, 0.29);
  --header-btn-color: rgba(170, 179, 203, 0.37);
  --header-glass-bg: rgba(27, 33, 44, 0.86);
  --header-glass-border-color: rgba(140, 140, 140, 0.22);
  --header-glass-shadow: 0 8px 24px rgba(0, 0, 0, 0.24);
  --markdown--code--color: rgb(6, 6, 196);
}

* {
  -webkit-box-sizing: border-box;
  -moz-box-sizing: border-box;
  box-sizing: border-box;
}

a {
  text-decoration: none;
  background-color: transparent;

  &:active,
  &:hover {
    outline-width: 0;
  }
}

.footer-dummy {
  height: calc(var(--footer-height) + var(--footer-margin));
}

.content-app {
  margin-top: calc(var(--header-height) + var(--header-margin));
  display: flex;
  justify-content: center;
  width: 100%;
  background-color: var(--site-background-color);
}

.submission-list-app,
.submission-list-footer-dummy {
  background-color: #ffffff;
}

.submission-list-app {
  margin-top: calc(var(--header-height) + 28px);
}

.submission-list-page .submission-list-app > .flex-container {
  transform: none !important;
}

html.submission-list-page,
body.submission-list-page,
html.submission-list-page #app,
html.submission-list-page #wrapper {
  background-color: #ffffff;
}

html:has(.content-app.submission-list-app),
body:has(.content-app.submission-list-app) {
  background-color: #ffffff;
}

html.submission-list-page {
  --header-glass-bg: #ffffff;
  --header-glass-border-color: #eef1f5;
  --header-glass-shadow: none;
}

html.submission-list-page #header .header-menu {
  padding-right: 32px;
  padding-left: 32px;
}

html.submission-list-page #header .logo {
  margin-left: 0;
}

html.submission-list-page #header .header-menu > .drop-menu {
  padding-right: 0 !important;
}

.ps {
  margin-top: 50px;
  background-color: var(--bg-color);
}

.fadeInUp-enter-active {
  animation: fadeInUp 0.8s;
}
</style>
