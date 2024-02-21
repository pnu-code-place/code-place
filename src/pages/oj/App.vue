<template>
  <div>
    <template v-if="isProblemSolving">
      <NavBar_Problem></NavBar_Problem>
    </template>
    <template v-else>
      <NavBar></NavBar>
    </template>
    <div class="content-app" :class="{'ps': isProblemSolving}">
      <transition name="fadeInUp" mode="out-in">
        <router-view></router-view>
      </transition>
    </div>
    <template v-if="!isProblemSolving">
      <div class="footer">
        <p v-html="website.website_footer"></p>
        <p>Powered by <a href="https://github.com/QingdaoU/OnlineJudge">OnlineJudge</a>
          <span v-if="version">&nbsp; Version: {{ version }}</span>
        </p>
      </div>
    </template>
    <BackTop></BackTop>
  </div>
</template>

<script>
import {mapActions, mapGetters, mapState} from 'vuex'
  import NavBar from './components/NavBar.vue'
  import NavBar_Problem from "./components/NavBar_Problem.vue";

export default {
  name: 'app',
  components: {
    NavBar_Problem,
    NavBar
  },
  data() {
    return {
      version: process.env.VERSION
    }
  },
  created() {
    try {
      document.body.removeChild(document.getElementById('app-loader'))
    } catch (e) {
    }
  },
  mounted() {
    this.getWebsiteConfig()
  },
  methods: {
    ...mapActions(['getWebsiteConfig', 'changeDomTitle'])
  },
  computed: {
    ...mapState(['website']),
    ...mapGetters(['isProblemSolving']),
  },
  watch: {
    'website'() {
      this.changeDomTitle()
    },
    '$route'() {
      this.changeDomTitle()
    }
  }
}
</script>

<style lang="less">

  :root{
    --bg-color: #ffffff;
    --custom-btn-hover-color: #f5f5f5;
    --border-color: #e7e7e7;
    --header-btn-color: rgba(246, 246, 246, 0.45);
    //--markdown--code--color: rgba(27, 31, 35, 0.05);
  }

  :root.dark.problem{
    --bg-color: #1f2430;
    --text-color: #ffffff;
    --difficulty-color: #434e69;
    --custom-btn-hover-color: #434e69;
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

  &:active, &:hover {
    outline-width: 0;
  }
}

  @media screen and (max-width: 1200px) {
  .content-app {
    margin-top: 160px;
    padding: 0 2%;
  }
}

@media screen and (min-width: 1200px) {
  .content-app {
    margin-top: 90px;
    display: flex;
    justify-content: center;
  }
}
  .ps{
    margin-top: 50px;
    background-color: var(--bg-color);
  }
  .footer {
    margin-top: 400px;
    text-align: center;
    font-size: small;
  }

.fadeInUp-enter-active {
  animation: fadeInUp .8s;
}


</style>
