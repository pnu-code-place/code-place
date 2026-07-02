<template>
  <div class="recommendationBox">
    <div class="recommendationBoxHeader">
      <span class="animation"
        >{{ $t("m.Most_Hard_Problem_In_Last_Week") }}
        <img src="@/assets/fireIcon.png" width="15" style="padding-top: 1px" />
      </span>
    </div>
    <div class="hardProblemRecommendationBoxBody">
      <template v-if="loading">
        <div class="hard-problem-skeleton" aria-hidden="true">
          <div v-if="showTags" class="skeleton-tag-row">
            <span class="skeleton-block skeleton-chip"></span>
            <span class="skeleton-block skeleton-chip skeleton-chip-short"></span>
            <span class="skeleton-block skeleton-chip skeleton-chip-short"></span>
          </div>
          <div class="skeleton-title-row">
            <span class="skeleton-block skeleton-title"></span>
            <span class="skeleton-block skeleton-link"></span>
          </div>
          <div class="skeleton-info-list">
            <div class="skeleton-info-row">
              <span class="skeleton-block skeleton-label"></span>
              <span class="skeleton-block skeleton-value"></span>
            </div>
            <div class="skeleton-info-row">
              <span class="skeleton-block skeleton-label"></span>
              <span class="skeleton-block skeleton-value"></span>
            </div>
            <div class="skeleton-info-row">
              <span class="skeleton-block skeleton-label"></span>
              <span class="skeleton-block skeleton-value"></span>
            </div>
          </div>
        </div>
      </template>
      <template v-else-if="problem">
        <div v-if="showTags" class="hardProblemFieldCategory">
          <FieldCategoryBox
            :boxType="true"
            :value="FIELD_MAP[problem.field].value"
            :boxColor="FIELD_MAP[problem.field].boxColor"
          />
          <FieldCategoryBox
            v-for="category in problem.tags"
            :key="category"
            :boxType="false"
            :value="'#' + category"
            :boxColor="'#ffffff'"
          />
        </div>
        <div
          class="hardProblemFieldCategory"
          style="justify-content: space-between; margin-top: 2px"
        >
          <span style="font-weight: bold; font-size: medium">
            {{ problem.title }}
          </span>
          <a
            style="color: #7a7a7a; text-decoration: underline"
            @click="enterProblemDetail(problem._id)"
            >{{ $t("m.Try_Most_Hard_Problem_In_Last_Week") }}</a
          >
        </div>
        <div class="hardProblemInfo" style="margin-top: 15px">
          <div
            style="
              display: flex;
              justify-content: space-between;
              width: 50%;
              float: right;
            "
          >
            <span>{{ $t("m.Th_Problem_AC_Rate") }}</span>
            <span>{{
              problem.submission_number == 0
                ? "없음"
                : Math.floor(
                    (problem.accepted_number / problem.submission_number) * 100,
                  ) + "%"
            }}</span>
          </div>
        </div>
        <br />
        <div class="hardProblemInfo" style="margin-top: 5px">
          <div
            style="
              display: flex;
              justify-content: space-between;
              width: 50%;
              float: right;
            "
          >
            <span>{{ $t("m.Th_Problem_Num_Success") }}</span>
            <span>{{ problem.accepted_number }}명</span>
          </div>
        </div>
        <br />
        <div
          class="hardProblemInfo"
          style="margin-top: 5px; margin-bottom: 20px"
        >
          <div
            style="
              display: flex;
              justify-content: space-between;
              width: 50%;
              float: right;
            "
          >
            <span>{{ $t("m.Th_Problem_Difficulty") }}</span>
            <span style="color: #c02b2b; font-weight: bolder">{{
              DIFFICULTY_MAP[problem.difficulty].value
            }}</span>
          </div>
        </div>
      </template>
      <template v-else>
        <div
          style="
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
          "
        >
          {{ $t("m.There_Is_No_Data") }}
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import api from "@oj/api"
import { mapActions, mapGetters } from "vuex"
import FieldCategoryBox from "../../../../components/FieldCategoryBox.vue"
import { DIFFICULTY_MAP, FIELD_MAP } from "../../../../../../utils/constants"

export default {
  name: "MostDifficultProblemLastWeekBox",
  components: { FieldCategoryBox },
  props: {
    showTags: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      problem: null,
      loading: true,
    }
  },
  mounted() {
    this.init()
  },
  methods: {
    ...mapActions([
      "getProfile",
      "changeModalStatus",
      "changeProblemSolvingState",
    ]),
    enterProblemDetail(problemId) {
      this.changeProblemSolvingState(true)
      this.$router.push({
        name: "problem-details",
        params: { problemID: problemId },
      })
    },
    init() {
      this.loading = true
      api.getMostDifficultProblem().then(
        (res) => {
          this.problem = res.data.data
          this.loading = false
        },
        () => {
          this.loading = false
        },
      )
    },
  },
  computed: {
    FIELD_MAP() {
      return FIELD_MAP
    },
    DIFFICULTY_MAP() {
      return DIFFICULTY_MAP
    },
    ...mapGetters([
      "website",
      "modalStatus",
      "user",
      "isAuthenticated",
      "isAdminRole",
    ]),
    ...mapGetters(["profile"]),
  },
}
</script>

<style scoped lang="less">
.recommendationBox {
  border-radius: 7px;
  border: 1px solid #dedede;
  background-color: var(--box-background-color);
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
    background-color: #fbfbfb;
    padding: 20px;
    height: 160px;

    .hardProblemFieldCategory {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      align-items: center;
      justify-content: left;

      /deep/ .fieldCategoryBox {
        min-width: 0;
      }

      /deep/ .box {
        max-width: 140px;
        margin-top: 0;
        margin-right: 0;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      /deep/ .box span {
        white-space: nowrap;
      }
    }
  }
}

.recommendationBox:hover {
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

.skeleton-block {
  display: inline-block;
  border-radius: 6px;
  background: #f1f3f5;
}

.hard-problem-skeleton {
  display: flex;
  flex-direction: column;
  gap: 14px;
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

.skeleton-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.skeleton-title {
  width: 118px;
  height: 18px;
}

.skeleton-link {
  width: 60px;
  height: 13px;
}

.skeleton-info-list {
  width: 52%;
  margin-left: auto;
  display: flex;
  flex-direction: column;
  gap: 11px;
}

.skeleton-info-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.skeleton-label {
  width: 54px;
  height: 13px;
}

.skeleton-value {
  width: 34px;
  height: 13px;
}
</style>
