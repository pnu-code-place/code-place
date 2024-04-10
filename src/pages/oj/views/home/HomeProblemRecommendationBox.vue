<template>
  <div class="problemRecommendationBox">
    <header class="problemRecommendationBoxHeader">
      <span @click="handleRoute('problem')">이번 주 보너스 문제</span>
      <div class="plusDiv">
        <Icon type="ios-information" size="13" color="#7a7a7a"></Icon>
        <span class="plusSpan">주마다 보너스 점수(x2)가 있는 문제를 추천해드려요!</span>
      </div>
    </header>
    <div class="problemRecommendationBoxBody">
      <template v-for="(problem, index) in problems" v-if="index <= 2">
<!--        <ShineWrapper>-->
          <div @click="enterProblemDetail(problem.id)" class="bonusProblem" :style="{ 'background-image': 'url(' + FIELD_MAP[problem.field].backgroundImage + ')' }">
            <span>{{problem.title}}</span>
            <FieldCategoryBox :boxType="true" :value="FIELD_MAP[problem.field].value"
                              :boxColor="FIELD_MAP[problem.field].boxColor"/>
            <template v-for="(category, idx) in [problem.tags[0]]">
              <FieldCategoryBox :boxType="false" :value="'#' + category" :boxColor="'#ffffff'"/>
            </template>
          </div>
<!--        </ShineWrapper>-->
      </template>
    </div>
  </div>
</template>

<script>
import api from '@oj/api'
import {FIELD_MAP} from "../../../../utils/constants";
import FieldCategoryBox from "../../components/FieldCategoryBox.vue";
import {mapActions} from "vuex";
import ShineWrapper from "../../components/ShineWrapper.vue";

export default {
  name: 'HomeProblemRecommendationBox',
  components: {ShineWrapper, FieldCategoryBox},
  computed: {
    FIELD_MAP() {
      return FIELD_MAP
    }
  },
  data () {
    return {
      value1: 0,
      problems: []
    }
  },
  mounted() {
    this.init()
  },
  methods:{
    ...mapActions(['changeProblemSolvingState']),
    handleRoute(route) {
      this.$router.push({name: route});
    },
    init(){
      api.getHomeBonusProblem()
        .then((res) =>{
          this.problems = res.data.data
        })
    },
    enterProblemDetail(problemId) {
      this.changeProblemSolvingState(true)
      this.$router.push({name: 'problem-details', params: {problemID: problemId}})
    },
  }
}
</script>

<style scoped lang="less">

.problemRecommendationBox{
  background-color: #ffffff;
  border-radius: 7px;
  border: 1px solid #dedede;
  width: 100%;
  height: 220px;
  padding-left: 30px;
  padding-right: 30px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  .problemRecommendationBoxHeader{
    padding-top: 15px;
    padding-bottom: 15px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #dedede;

    span:first-child {
      font-weight: 650;
      font-size: 15px;
    }

    .plusDiv{
      cursor: pointer;
      .plusSpan {
        color: #7a7a7a;
        font-size: 12px;
      }
    }
  }
  .problemRecommendationBoxBody{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 0;
    span{
      font-size: medium;
      font-weight: bold;
    }
    .bonusProblem{
      cursor: pointer;
      align-items: center;
      padding: 30px;
      width: 220px;
      border-radius: 7px;
      background-color: #e9ece9;
      transition: all .2s ease-in-out;
    }
    .bonusProblem:hover { transform: scale(1.11); }
  }
}
.problemRecommendationBox:hover{
  border: 1px solid #cccccc;
}
</style>
