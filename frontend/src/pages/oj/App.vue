<template>
  <div id="wrapper">
    <PopUp v-for="(popup, index) in this.filteredPopup" :key="popup.id" :id="popup.id" :link="popup.link"
           :width="popup.width === null || popup.width <=50 ? 0 : popup.width"
           :p_position="{x: 100 + index * 50, y: 100 + index * 50}">
      <img :src="popup.image" :alt="popup.alt" draggable="false"
           :style="{width:'100%', objectFit:'contain'}"/>
    </PopUp>
    <template v-if="isProblemSolving">
      <NavBar_Problem></NavBar_Problem>
    </template>
    <template v-else>
      <NavBar></NavBar>
    </template>
    <div class="content-app" :class="{ ps: isProblemSolving }">
      <transition name="fadeInUp" mode="out-in">
        <router-view></router-view>
      </transition>
    </div>
    <template v-if="!isProblemSolving">
      <div class="footer-dummy"></div>
      <CSEPFooter></CSEPFooter>
    </template>
    <BackTop></BackTop>
  </div>
</template>

<script>
import {mapActions, mapGetters, mapState} from "vuex";
import NavBar from "./components/NavBar.vue";
import NavBar_Problem from "./views/problem/problemSolving/problemSolvingNavbar/NavBar_Problem.vue";
import CSEPFooter from "./views/general/CSEPFooter.vue";
import PopUp from "./components/modal/PopUp.vue";
import api from "./api";

export default {
  data() {
    return {
      popupData: []
    }
  },
  name: "app",
  components: {
    PopUp,
    CSEPFooter,
    NavBar_Problem,
    NavBar,
  },
  created() {
    try {
      document.body.removeChild(document.getElementById("app-loader"));
    } catch (e) {
    }
  },
  mounted() {
    this.getWebsiteConfig();
    this.init()
  },
  methods: {
    init() {
      api.getPopup().then((res) => {
        this.$store.commit('refreshPopup')
        this.popupData = res.data.data
      })
    },
    ...mapActions(["getWebsiteConfig", "changeDomTitle"]),
  },
  computed: {
    ...mapState(["website"]),
    ...mapGetters(["isProblemSolving", "removedPopupId"]),
    filteredPopup() {
      return this.popupData.filter(popup => !this.removedPopupId.includes(popup.id))
    }
  },
  watch: {
    website() {
      this.changeDomTitle();
    },
    $route() {
      this.changeDomTitle();
    },
  },
};
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
  --title-font-color: var(--container-font-color);
  --title_font-size: 24px;
  --title_font-weight: 700;


  --point-color: #32306b;
  --pale-point-color: #F8F9FF;
  // hex #024D97; to rgb 2, 77, 151
  --pnu-green: rgb(6, 186, 110);
  --pnu-blue: rgb(2, 77, 151);

  --pale-pnu-green: rgba(6, 186, 110, 0.05);
  --pale-pnu-blue: rgba(2, 77, 151, 0.05);

  --pale-gold-color: #FAF882;
  --pale-silver-color: #F4F4F4;
  --pale-bronze-color: #D6C68B;

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

  /* Contest Page */
  --container-border-color: #dedede;
  --rule-type-border-color: #6b6b6b;
  --container-font-color: #495060;
  --container-border-radius: 10px;
  --container-comment-color: #7e7e7e;

  /* header */
  --header-height: 60px;
  --header-margin: 20px;
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

  --bg-color: #1f2430;
  --text-color: #ffffff;
  --difficulty-color: #434e69;
  --custom-btn-hover-color: #465477;
  --border-color: rgba(140, 140, 140, 0.29);
  --header-btn-color: rgba(170, 179, 203, 0.37);
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
  min-width: var(--global-width);
  background-color: var(--site-background-color);
}

.ps {
  margin-top: 50px;
  background-color: var(--bg-color);
}

.fadeInUp-enter-active {
  animation: fadeInUp 0.8s;
}
</style>
