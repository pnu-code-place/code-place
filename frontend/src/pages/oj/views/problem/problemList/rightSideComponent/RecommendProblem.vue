<template>
  <div
    class="problem-flex-container"
    @click="enterProblemDetail(recommend_problem._id)"
  >
    <div class="problem-container">
      <div class="problem-title">
        <span class="title-span">
          {{ recommend_problem.title }}
        </span>
        <span class="solve-problem">{{
          $t("m.Try_Personal_Recommendation_Problem")
        }}</span>
      </div>
      <div class="problem-extra">
        <FieldCategoryBox
          :boxType="true"
          :value="FIELD_MAP[recommend_problem.field].value"
          :boxColor="FIELD_MAP[recommend_problem.field].boxColor"
        />
        <template v-for="(category, idx) in recommend_problem.tags">
          <FieldCategoryBox
            :boxType="false"
            :value="'#' + category"
            :boxColor="'#ffffff'"
          />
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from "vue"
import FieldCategoryBox from "../../../../components/FieldCategoryBox.vue"
import { FIELD_MAP } from "../../../../../../utils/constants"
import { mapActions } from "vuex"

export default defineComponent({
  computed: {
    FIELD_MAP() {
      return FIELD_MAP
    },
  },
  props: {
    recommend_problem: Object,
  },
  components: {
    FieldCategoryBox,
  },
  methods: {
    ...mapActions(["changeProblemSolvingState"]),
    enterProblemDetail(problemId) {
      this.changeProblemSolvingState(true)
      this.$router.push({
        name: "problem-details",
        params: { problemID: problemId },
      })
    },
  },
})
</script>

<style scoped lang="less">
.problem-flex-container {
  border-radius: 7px;
  background-color: rgba(244, 248, 250, 0.69);
  margin-top: 10px;
  padding: 10px 20px 10px 20px;
  display: flex;
  cursor: pointer;

  .problem-container {
    width: 100%;
  }

  .problem-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 5px;
    .title-span {
      width: 150px;
      text-align: left;
      font-weight: bold;
      font-size: 16px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .solve-problem {
      text-decoration: underline;
    }
    .solve-problem:hover {
      font-weight: 500;
    }
  }

  .problem-extra {
    display: flex;
    justify-content: left;
    overflow-x: hidden;
  }
}

.problem-flex-container:hover {
  background-color: rgba(239, 246, 250, 0.69);
}
</style>
