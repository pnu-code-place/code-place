<template>
  <section id="problem-section">
<!--    <button @click="logProps">prop 확인하기</button>-->
    <h1>내 문제 통계</h1>
    <div v-if="problems.length">{{ $t('m.List_Solved_Problems') }}
      <Poptip v-if="refreshVisible" trigger="hover" placement="right-start">
        <Icon type="ios-help-outline"></Icon>
        <div slot="content">
          <p>If you find the following problem id does not exist,<br> try to click the button.</p>
          <Button type="info" @click="freshProblemDisplayID">regenerate</Button>
        </div>
      </Poptip>
    </div>
    <p v-else>{{ $t('m.UserHomeIntro') }}</p>
    <div class="btns">
      <div class="problem-btn" v-for="problemID of problems" :key="problemID">
        <Button type="ghost" @click="goProblem(problemID)">{{ problemID }}</Button>
      </div>
    </div>
  </section>
</template>

<script>
import api from '@oj/api'
import {failedProblems, solvedProblems} from "../dummies";
export default {
  name: 'ProblemSection',
  data() {
    return {
    }
  },
  props :{
    userProblemData: {
      type: Object,
      required: true
    },
    statistics: {

    }
  },
  methods: {
    goProblem(problemID) {
      this.$router.push({name: 'problem-details', params: {problemID: problemID}})
    },
    freshProblemDisplayID() {
      api.freshDisplayID().then(res => {
        this.$success('Update successfully')
        this.init()
      })
    },
    // logProps() {
    //   console.log(this.$props)
    // }
  },
  computed: {
    refreshVisible() {
      if (!this.username) return true
      if (this.username && this.username === this.$store.getters.user.username) return true
      return false
    }
  },
}
</script>

<style scoped lang="less">
section {
  border : 1px solid #dedede;
  border-radius: 7px;
  transition : all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  padding : 10px;
  h1 {
    text-align : left;
    margin-bottom: 10px;
  }
}
</style>
