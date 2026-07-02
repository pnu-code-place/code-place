<template>
  <main class="personal-recommendation-box">
    <header class="personal-recommendation-header">
      <span class="personal-recommendation-span-title">{{
        $t("m.PersonalRecommendation")
      }}</span>
    </header>
    <template v-if="shouldShowSkeleton">
      <div class="recommendation-skeleton" aria-hidden="true">
        <div class="skeleton-chart">
          <span class="skeleton-chart-ring"></span>
        </div>
        <div class="skeleton-copy"></div>
        <div
          v-for="index in 3"
          :key="`recommendation-skeleton-${index}`"
          class="skeleton-problem-card"
        >
          <div class="skeleton-problem-title-row">
            <span class="skeleton-block skeleton-title"></span>
            <span class="skeleton-block skeleton-link"></span>
          </div>
          <div v-if="showTags" class="skeleton-tag-row">
            <span class="skeleton-block skeleton-chip"></span>
            <span class="skeleton-block skeleton-chip skeleton-chip-short"></span>
            <span class="skeleton-block skeleton-chip skeleton-chip-short"></span>
          </div>
        </div>
      </div>
    </template>
    <div v-else-if="!this.isAuthenticated" class="no-auth">
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
            <ECharts :option="chartOption" style="width: 100%; height: 100%" />
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
      <template v-if="recommendation && recommendation.recommend_problems">
        <RecommendProblem
          v-for="recommend_problem in recommendation.recommend_problems"
          :key="recommend_problem._id"
          :recommend_problem="recommend_problem"
          :showTags="showTags"
        />
      </template>
    </template>
  </main>
</template>

<script>
import { mapGetters } from "vuex"
import api from "../../../../api"
import { FIELD_MAP } from "../../../../../../utils/constants"
import RecommendProblem from "./RecommendProblem.vue"
import InSufficientData from "./InSufficientData.vue"

export default {
  name: "PersonalRecommendationBox",
  components: { InSufficientData, RecommendProblem },
  props: {
    showTags: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      recommendation: null,
      loading: false,
    }
  },
  mounted() {
    this.init()
  },
  methods: {
    init() {
      if (!this.isAuthenticated) {
        this.loading = false
        return
      }
      this.loading = true
      api
        .getPersonalRecommendProblem()
        .then((res) => {
          this.recommendation = res.data.data
          this.loading = false
        })
        .catch(() => {
          this.loading = false
        })
    },
  },
  computed: {
    ...mapGetters(["user", "isAuthenticated", "profileResolved"]),
    FIELD_MAP() {
      return FIELD_MAP
    },
    shouldShowSkeleton() {
      return !this.profileResolved || this.loading
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
      let colorList = this.getGraphColor

      return fieldList.map((field, index) => ({
        value: scoreList[index],
        name: field,
        label: {
          color: colorList[index],
        },
        labelLine: {
          lineStyle: {
            color: colorList[index],
          },
        },
      }))
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
          show: false,
        },
        series: [
          {
            type: "pie",
            radius: ["30%", "65%"],
            avoidLabelOverlap: false,
            padAngle: 0,
            itemStyle: {
              borderRadius: 0,
              borderWidth: 0,
            },
            label: {
              show: true,
              position: "outside",
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
              show: true,
            },
            color: this.getGraphColor,
            data: this.getGraphData,
          },
        ],
      }
    },
  },
  watch: {
    isAuthenticated(newVal) {
      if (newVal) {
        this.init()
      }
    },
  },
}
</script>

<style scoped lang="less">
.personal-recommendation-header {
  padding-top: 8px;
  padding-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--box-background-color);
}

.personal-recommendation-box {
  border-radius: 7px;
  border: 1px solid #dedede;
  background-color: var(--box-background-color);
  width: 100%;
  box-sizing: border-box;
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
    color: transparent;
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

.personal-recommendation-box:hover {
  border: 1px solid #cccccc;
}

.no-auth {
  height: 350px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.recommendation-skeleton {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-block,
.skeleton-copy {
  display: inline-block;
  border-radius: 6px;
  background: #f1f3f5;
}

.skeleton-chart {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.skeleton-chart-ring {
  width: 118px;
  height: 118px;
  border-radius: 50%;
  border: 24px solid #f1f3f5;
  box-sizing: border-box;
}

.skeleton-copy {
  width: 78%;
  height: 16px;
  align-self: center;
  margin: 5px 0 4px;
}

.skeleton-problem-card {
  border-radius: 7px;
  background-color: rgba(244, 248, 250, 0.69);
  padding: 10px 20px;
}

.skeleton-problem-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 9px;
}

.skeleton-title {
  width: 132px;
  height: 17px;
}

.skeleton-link {
  width: 58px;
  height: 13px;
}

.skeleton-tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.skeleton-chip {
  width: 72px;
  height: 24px;
  border-radius: 999px;
}

.skeleton-chip-short {
  width: 54px;
}
</style>
