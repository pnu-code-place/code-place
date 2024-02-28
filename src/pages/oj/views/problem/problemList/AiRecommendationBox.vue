<template>
  <main>
    <header>
      <span class="aiRecommendationSpan">{{ $t('m.AiRecommendation') }}</span>
      <div>
        <Icon type="ios-information-outline" size="13" color="#7a7a7a"></Icon>
        <span>{{ $t('m.AiRecommendation_Info') }}</span>
      </div>
    </header>
      <template v-if="!this.isAuthenticated">
        <div style="height: 350px; display: flex; align-items: center; justify-content: center">
          <span>{{$t('m.AiRecommendation_No_Auth')}}</span>
        </div>
      </template>
      <template v-else>
        <div style="text-align: center; margin-top: 10px; padding-left: 10px">
          <ECharts ref="chart" :options="option" :initOptions="radarInitOpts" style="height: fit-content; width: fit-content"></ECharts>
        </div>
        <div class="aiSolution">
          <span style="font-weight: bold; padding-right: 4px">{{user.username+' 님, '}}</span>
          <FieldCategoryBox :boxType="true" :value="FIELD_MAP[this.recommend_field].value" :boxColor="FIELD_MAP[this.recommend_field].boxColor"/>
          <span>{{$t('m.AiSolution')}}</span>
        </div>
        <template v-for="(recommend_problem, index) of this.recommend_problems">
          <div class="aiRecommendProblem">
                <span style="font-weight: bold; font-size: 15px">
                  {{ recommend_problem.title }}
                </span>
            <a @click="enterProblemDetail(recommend_problem.id)" style="text-decoration: underline; color: #7a7a7a">
              {{$t('m.Try_Most_Hard_Problem_In_Last_Week')}}
            </a>
          </div>
        </template>
        <div class="aiRecommendProblem">
                <span style="font-weight: bold; font-size: 15px">
                  {{ "벡터 매칭" }}
                </span>
          <a @click="enterProblemDetail('')" style="text-decoration: underline; color: #7a7a7a">
            {{$t('m.Try_Most_Hard_Problem_In_Last_Week')}}
          </a>
        </div>
        <div class="aiRecommendProblem">
                <span style="font-weight: bold; font-size: 15px">
                  {{ "두 수 더하기"}}
                </span>
          <a @click="enterProblemDetail('')" style="text-decoration: underline; color: #7a7a7a">
            {{$t('m.Try_Most_Hard_Problem_In_Last_Week')}}
          </a>
        </div>

      </template>
  </main>
</template>

<script>
import {mapActions, mapGetters} from "vuex";
import FieldCategoryBox from "../../../components/FieldCategoryBox.vue";
import api from "../../../api";
import {FIELD_MAP} from "../../../../../utils/constants";

export default {
  name: 'AiRecommendationBox',
  components: {FieldCategoryBox},
  data () {
    return {
      radarInitOpts: {
        width: '240',
        height: '250'
      },
      option: {
        color: ['#efad4b'],
        legend: {},
        tooltip: {
          trigger: 'axis'
        },
        radar: {
          indicator: [
            { text: '자료구조', max: 25600, color: '#000000', },
            { text: '구현', max: 25600, color: '#000000', },
            { text: '수학', max: 25600, color: '#000000', },
            { text: '탐색', max: 25600, color: '#000000', },
            { text: '정렬', max: 25600, color: '#000000', },
          ],
          center: ['50%', '50%'],
          axisName:{
            fontWeight: 'bold'
          },
          splitArea: {
            areaStyle: {
              color: ['rgba(255,255,255,0)', 'rgba(255,255,255,0)', 'rgba(255,255,255,0)', 'rgba(255,255,255,0)'],
            }
          },
          splitNumber: 4,
        },
        series: [
          {
            name: 'ACM Score',
            type: 'radar',
            emphasis:{
              areaStyle:{
                color: '#756e6c',
                shadowColor: '#FF917C'
              },
            },
            data: [
              {
                value: [13200,1320,23400,5600,12300,20000],
                tooltip: {
                  trigger: 'item',
                  backgroundColor: 'rgba(255,145,124,0.22)',
                  textStyle: {
                    color: '#1C1C1C',
                    fontWeight: 'bold'
                  }
                },
              },
            ],
          }
        ]
      },
      recommend_problems: [],
      recommend_field: 0
    }
  },
  mounted() {
    // this.init()
  },
  methods:{
    ...mapActions(['changeProblemSolvingState']),
    init(){
      api.getAiRecommendProblem()
        .then((res)=> {
          console.log("res: ", res)
          let field_scores = res.data.data.field_score
          this.recommend_problems = res.data.data.recommend_problems
          this.recommend_field = field_scores.indexOf(Math.min([...field_scores]))
        })
    },
    setRadarGraph(){
      this.$refs.chart.setOption(

      )
    },
    enterProblemDetail(problemId) {
      this.changeProblemSolvingState(true)
      this.$router.push({name: 'problem-details', params: {problemID: problemId}})
    },
  },
  computed:{
    FIELD_MAP() {
      return FIELD_MAP
    },
    ...mapGetters(['user', 'isAuthenticated', 'isAdminRole']),
  }
}
</script>

<style scoped lang="less">
header {
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

main {
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

</style>

