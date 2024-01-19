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
      <template v-if="!isProblemSolving">
        <div class="footer">
          <p v-html="website.website_footer"></p>
          <p>Powered by <a href="https://github.com/QingdaoU/OnlineJudge">OnlineJudge</a>
            <span v-if="version">&nbsp; Version: {{ version }}</span>
          </p>
        </div>
      </template>
    </div>
    <BackTop></BackTop>
  </div>
</template>

<script>
import {mapActions, mapGetters, mapState} from 'vuex'
  import NavBar from '@oj/components/NavBar.vue'
  import NavBar_Problem from "./components/NavBar_Problem.vue";

  export default {
    name: 'app',
    components: {
      NavBar_Problem,
      NavBar
    },
    data () {
      return {
        version: process.env.VERSION
      }
    },
    created () {
      try {
        document.body.removeChild(document.getElementById('app-loader'))
      } catch (e) {
      }
    },
    mounted () {
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
      'website' () {
        this.changeDomTitle()
      },
      '$route' () {
        this.changeDomTitle()
      }
    }
  }
</script>

<style lang="less">

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
    padding: 0 11%;
  }
}
  .ps{
    margin-top: 50px;
    padding: 0 1%;
    background-color: #F8F8F8;
  }
  .footer {
    //margin-top: 400px;
    //margin-bottom: 10px;
    text-align: center;
    font-size: small;
  }

  .fadeInUp-enter-active {
    animation: fadeInUp .8s;
  }


</style>
