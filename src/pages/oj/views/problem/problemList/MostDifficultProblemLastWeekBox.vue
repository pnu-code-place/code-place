<template>
  <div class="recommendationBox">
    <div class="recommendationBoxHeader">
            <span class="animation">{{$t('m.Most_Hard_Problem_In_Last_Week')}}
              <img src="@/assets/fireIcon.png" width="15" style="padding-top: 1px"/>
            </span>
    </div>
    <div class="hardProblemRecommendationBoxBody">
      <template v-if="problem">
        <div class="hardProblemFieldCategory">
          <FieldCategoryBox :boxType="true" :value="FIELD_MAP[problem.field].value"
                            :boxColor="FIELD_MAP[problem.field].boxColor"/>
          <template v-for="(category, idx) in problem.tags">
            <FieldCategoryBox :boxType="false" :value="'#' + category" :boxColor="'#ffffff'"/>
          </template>
        </div>
        <div class="hardProblemFieldCategory" style="justify-content: space-between; margin-top: 2px">
          <span style="font-weight: bold;font-size: medium"> {{ problem.title }} </span>
          <a style="color: #7a7a7a; text-decoration: underline" @click="enterProblemDetail(problem._id)">{{ $t('m.Try_AiRecommendation_Problem') }}</a>
        </div>
        <div class="hardProblemInfo" style="margin-top: 15px">
          <div style="display: flex; justify-content: space-between; width: 50%; float: right">
            <span>정답률</span>
            <span>{{ problem.submission_number == 0 ? "없음" : (problem.accepted_number / problem.submission_number ) * 100 + '%' }}</span>
          </div>
        </div>
        <br>
        <div class="hardProblemInfo" style="margin-top: 5px">
          <div style="display: flex; justify-content: space-between; width: 50%; float: right">
            <span>완료한 사람</span>
            <span>{{problem.accepted_number}}명</span>
          </div>
        </div>
        <br>
        <div class="hardProblemInfo" style="margin-top: 5px; margin-bottom: 20px">
          <div style="display: flex; justify-content: space-between; width: 50%; float: right">
            <span>난이도</span>
            <span style="color: #c02b2b; font-weight: bolder">{{ DIFFICULTY_MAP[problem.difficulty].value }}</span>
          </div>
        </div>
      </template>
      <template v-else>
        <div style="height:100%; display: flex; align-items: center; justify-content: center">
          표시할 데이터가 충분하지 않습니다.
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import api from '@oj/api'
import {mapActions, mapGetters} from "vuex";
import FieldCategoryBox from "../../../components/FieldCategoryBox.vue";
import {DIFFICULTY_MAP, FIELD_MAP} from "../../../../../utils/constants";

export default {
  name: 'MostDifficultProblemLastWeekBox',
  components: {FieldCategoryBox},
  props:{
    problem:{
      type: Object
    }
  },
  data () {
    return {

    }
  },
  methods:{
    ...mapActions(['getProfile', 'changeModalStatus','changeProblemSolvingState']),
    enterProblemDetail(problemId) {
      this.changeProblemSolvingState(true)
      this.$router.push({name: 'problem-details', params: {problemID: problemId}})
    },
  },
  computed:{
    FIELD_MAP() {
      return FIELD_MAP
    },
    DIFFICULTY_MAP() {
      return DIFFICULTY_MAP
    },
    ...mapGetters(['website', 'modalStatus', 'user', 'isAuthenticated', 'isAdminRole']),
    ...mapGetters(['profile']),
  }
}
</script>

<style scoped lang="less">

.recommendationBox {
  border-radius: 7px;
  border: 1px solid #dedede;
  width: 100%;
  height: 240px;
  margin-bottom: 20px;
  text-align: center;
  padding-left: 20px;
  padding-right: 20px;
  padding-top: 13px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);

  .hardProblemRecommendationBoxBody {
    border-radius: 7px;
    background-color: #FBFBFB;
    padding: 20px;
    height: 160px;

    .hardProblemFieldCategory {
      display: flex;
      align-items: center;
      justify-content: left;
    }
  }
}

.recommendationBox:hover{
  border: 1px solid #cccccc;
}

.recommendationBoxHeader {
  padding-top: 8px;
  padding-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: space-between;

  span:first-child {
    font-weight: 650;
    font-size: 15px;
  }

  span:nth-child(2) {
    color: #7a7a7a;
    font-size: 12px;
  }

  .animation {
    display: inline-block;
    transform-origin: center;
    padding: 0 0.5rem;
    animation: animate 2s infinite;
  }

  @keyframes animate {
    0% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.05);
    }
    100% {
      transform: scale(1);
    }
  }
}
</style>
