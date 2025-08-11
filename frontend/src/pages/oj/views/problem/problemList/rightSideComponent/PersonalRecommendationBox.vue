<template>
  <main>
    <header>
      <span class="personal-recommendation-span-title">{{
        $t("m.PersonalRecommendation")
      }}</span>
    </header>
    <div v-if="!this.isAuthenticated" class="no-auth">
      <span style="font-size: medium; font-weight: bold">{{
        $t("m.PersonalRecommendation_No_Auth")
      }}</span>
    </div>
    <template v-else>
      <template v-if="!recommendation">
        <InSufficientData :type="false" />
      </template>
      <template v-else>
        <template v-if="!isScoreDataInSufficient">
          <div style="height: 200px; text-align: center">
            <ECharts :options="chartOption" style="width: 100%; height: 100%" />
          </div>
          <div style="justify-content: center; padding: 10px">
            <span style="font-weight: 500"
              ><span style="font-weight: bold">{{ user.username }}</span> 님을
              위해 선별된 문제들이에요!</span
            >
          </div>
        </template>
        <template v-else>
          <InSufficientData :type="true" />
        </template>
      </template>
      <template
        v-for="(recommend_problem, index) of this.recommendation
          .recommend_problems"
      >
        <RecommendProblem :recommend_problem="recommend_problem" />
      </template>
    </template>
  </main>
</template>

<script>
import { mapActions, mapGetters } from "vuex"
import FieldCategoryBox from "../../../../components/FieldCategoryBox.vue"
import api from "../../../../api"
import { FIELD_MAP } from "../../../../../../utils/constants"
import RecommendProblem from "./RecommendProblem.vue"
import InSufficientData from "./InSufficientData.vue"

export default {
  name: "PersonalRecommendationBox",
  components: { InSufficientData, RecommendProblem, FieldCategoryBox },
  data() {
    return {
      recommendation: null,
      noProblemData: false,
    }
  },
  mounted() {
    this.init()
  },
  methods: {
    init() {
      api
        .getPersonalRecommendProblem()
        .then((res) => {
          this.recommendation = res.data.data
        })
        .catch((e) => {
          console.log(e)
        })
    },
  },
  computed: {
    ...mapGetters(["user", "isAuthenticated", "isAdminRole"]),
    FIELD_MAP() {
      return FIELD_MAP
    },
    getGraphColor() {
      return Object.values(this.FIELD_MAP).map((field) => field.boxColor)
    },
    getFieldName() {
      return Object.values(this.FIELD_MAP).map((field) => field.value)
    },
    getScoreList() {
      if (this.recommendation == null) {
        return
      }
      return Object.values(this.recommendation.field_score).map(
        (field) => field.score,
      )
    },
    getGraphData() {
      // 각 영역별로 점수를 배열로 만들어서 반환
      let fieldList = this.getFieldName
      let scoreList = this.getScoreList

      return fieldList.map((field, index) => ({
        value: scoreList[index],
        name: field,
      }))
    },
    getRecommendedField() {
      if (this.recommendation == null) {
        return
      }
      return Object.values(this.recommendation.recommend_problems).map(
        (problem) => problem.field,
      )
    },
    isScoreDataInSufficient() {
      if (this.recommendation == null) {
        return
      }
      let zeroCount = this.recommendation.field_score.filter(
        (item) => item.score == 0,
      ).length
      return zeroCount >= 3
    },
    chartOption() {
      return {
        tooltip: {
          trigger: "item",
          borderRadius: 10,
        },
        legend: {
          top: "5%",
          left: "center",
        },
        series: [
          {
            type: "pie",
            radius: ["30%", "65%"],
            avoidLabelOverlap: false,
            padAngle: 10,
            itemStyle: {
              borderRadius: 10,
              borderWidth: 1,
              borderJoin: "round",
            },
            label: {
              show: false,
              position: "center",
            },
            emptyCircleStyle: {
              color: "lightgray",
              opacity: 1,
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 40,
              },
            },
            labelLine: {
              show: false,
            },
            color: this.getGraphColor,
            data: this.getGraphData,
          },
        ],
      }
    },
  },
}
</script>

<style scoped lang="less">
header {
  padding-top: 8px;
  padding-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--box-background-color);
}

main {
  border-radius: 7px;
  border: 1px solid #dedede;
  background-color: var(--box-background-color);
  width: 100%;
  text-align: center;
  padding: 13px 20px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);

  .personal-recommendation-span-title {
    font-size: 17px;
    font-weight: 650;
    background: linear-gradient(
      to right,
      #344360 20%,
      #376091 30%,
      #295d73 70%,
      #5d3da6 80%
    );
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    text-fill-color: transparent;
    background-size: 500% auto;

    animation: text-shine 5s ease-in-out infinite alternate;
  }

  @keyframes text-shine {
    0% {
      background-position: 0% 50%;
    }
    100% {
      background-position: 100% 50%;
    }
  }
}

main:hover {
  border: 1px solid #cccccc;
}

.no-auth {
  height: 350px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
