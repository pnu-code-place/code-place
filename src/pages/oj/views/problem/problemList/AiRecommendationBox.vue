<template>
  <div class="aiRecommendationBox">
    <div class="recommendationBoxHeader">
      <span class="aiRecommendationSpan">{{ $t('m.AiRecommendation') }}</span>
      <div>
        <Icon type="ios-information-outline" size="13" color="#7a7a7a"></Icon>
        <span>{{ $t('m.AiRecommendation_Info') }}</span>
      </div>
    </div>
    <div style="text-align: center; margin-top: 10px; padding-left: 10px">
      <ECharts :options="radarGraph" :initOptions="radarInitOpts" style="height: fit-content; width: fit-content"></ECharts>
    </div>
    <div class="aiSolution">
      <span style="font-weight: bold; padding-right: 4px">{{user.username+' 님, '}}</span>
      <FieldCategoryBox :boxType="true" :value="'수학'" :boxColor="'#B5EAB0'"/>
      <span>{{$t('m.AiSolution')}}</span>
    </div>
    <div class="aiRecommendProblem">
            <span style="font-weight: bold; font-size: 15px">
              더 크게 합치기
            </span>
      <a style="text-decoration: underline; color: #7a7a7a">
        {{$t('m.Try_Most_Hard_Problem_In_Last_Week')}}
      </a>
    </div>
    <div class="aiRecommendProblem">
            <span style="font-weight: bold; font-size: 15px">
              주사위 게임 2
            </span>
      <a style="text-decoration: underline; color: #7a7a7a">
        {{$t('m.Try_Most_Hard_Problem_In_Last_Week')}}
      </a>
    </div>
    <div class="aiRecommendProblem">
            <span style="font-weight: bold; font-size: 15px">
              원소들의 곱과 합
            </span>
      <a style="text-decoration: underline; color: #7a7a7a">
        {{$t('m.Try_Most_Hard_Problem_In_Last_Week')}}
      </a>
    </div>
  </div>
</template>

<script>
import {mapActions, mapGetters} from "vuex";
import FieldCategoryBox from "../../../components/FieldCategoryBox.vue";
import {radarGraph} from "../chartData";

export default {
  name: 'AiRecommendationBox',
  components: {FieldCategoryBox},
  data () {
    return {
      radarInitOpts: {
        width: '240',
        height: '250'
      },
      radarGraph: radarGraph,
    }
  },
  methods:{
  },
  computed:{
    ...mapGetters(['user', 'isAuthenticated', 'isAdminRole']),
    ...mapGetters(['profile']),
  }
}
</script>

<style scoped lang="less">
.aiSolution {
  display: flex;
  align-items: center;
  justify-content: center;
}

.aiRecommendProblem {
  border-radius: 7px;
  background-color: #FBFBFB;
  margin-top: 10px;
  margin-bottom: 10px;
  padding: 10px;
  padding-left: 10px;
  padding-right: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.aiRecommendationBox {
  border-radius: 7px;
  border: 1px solid #dedede;
  width: 100%;
  height: fit-content;
  margin-bottom: 20px;
  text-align: center;
  padding-left: 20px;
  padding-right: 20px;
  padding-top: 13px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);

  .aiRecommendationSpan {
    background: linear-gradient(
      to right,
      #7953cd 20%,
      #00affa 30%,
      #0190cd 70%,
      #764ada 80%
    );
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    text-fill-color: transparent;
    background-size: 500% auto;
    animation: textShine 3s ease-in-out infinite alternate;
  }
  @keyframes textShine {
    0% {
      background-position: 0% 50%;
    }
    100% {
      background-position: 100% 50%;
    }
  }
}
.recommendationBoxHeader {

  padding-top: 8px;
  padding-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  //border-bottom: 1px solid #dedede;

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

