<template>
  <div class="container">
    <side-nav-bar></side-nav-bar>
    <main>
      <user-card :profile="profile"></user-card>
      <keep-alive>
        <component :is="currentSection" :propsData="currentProps"></component>
      </keep-alive>
    </main>
  </div>
</template>
<script>
import {mapActions} from 'vuex'
import time from '@/utils/time'
import api from '@oj/api'
import SideNavBar from "./SideNavBar.vue";
import UserCard from "./UserCard.vue";
import {myPageSections} from "./index";
import CommunitySection from "./sections/CommunitySection.vue";
import InfoSection from "./sections/InfoSection.vue";
import ProblemSection from "./sections/problemSection/ProblemSection.vue";

export default {

  components: {UserCard, SideNavBar, ProblemSection, InfoSection, CommunitySection},
  data() {
    return {
      username: '',
      profile: {},
      problems: [],
    }
  },
  mounted() {
    this.init()
  },
  methods: {
    ...mapActions(['changeDomTitle']),
    init() {
      this.username = this.$route.query.username
      api.getUserInfo(this.username).then(res => {
        this.changeDomTitle({title: res.data.data.user.username})
        this.profile = res.data.data
        this.getSolvedProblems()
        let registerTime = time.utcToLocal(this.profile.user.create_time, 'YYYY-MM-D')
        console.log('The guy registered at ' + registerTime + '.')
      })
    },
    getSolvedProblems() {
      let ACMProblems = this.profile.acm_problems_status.problems || {}
      let OIProblems = this.profile.oi_problems_status.problems || {}
      // todo oi problems
      let ACProblems = []
      for (let problems of [ACMProblems, OIProblems]) {
        Object.keys(problems).forEach(problemID => {
          if (problems[problemID]['status'] === 0) {
            ACProblems.push(problems[problemID]['_id'])
          }
        })
      }
      ACProblems.sort()
      this.problems = ACProblems
    }
  },
  watch: {
    '$route'(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.init()
      }
    }
  },
  computed: {
    current() {
      if (this.$route.name === 'user-home') {
        return 'problems'
      } else {
        return this.$route.name
      }
    },
    currentSection() {
      return myPageSections[this.current].component
    },
    currentProps() {
      return myPageSections[this.current].propsData
    },
    router() {
      return this.$route.params
    }
  }
}
</script>

<style lang="less" scoped>

.container {
  position: relative;
  width: 75%;
  margin: 0 auto;
  text-align: center;
  display: flex;

  main {
    width: 80%;
    gap: 10px;
    display: flex;
    flex-direction: column;
  }

  p {
    margin-top: 8px;
    margin-bottom: 8px;
  }

  .emphasis {
    font-size: 20px;
    font-weight: 600;
  }

  #split {
    margin: 20px auto;
    width: 90%;
  }

  #problems {
    margin-top: 40px;
    padding-left: 30px;
    padding-right: 30px;
    font-size: 18px;

    .btns {
      margin-top: 15px;

      .problem-btn {
        display: inline-block;
        margin: 5px;
      }
    }
  }
}
</style>
