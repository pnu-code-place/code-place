<template>
  <div>
    <section>
      <div class="problem-tab">
        <header class="problem-tab__header">
          <h1>{{ $t('m.Problem_Status') }}</h1>
          <ul class="query-dropdowns">
            <li>
              <CustomDropdown
                :options="statusOptions"
                @dropdownChange="changeStatus"
                placeholder="Status"
                :default-text="this.$t('m.Is_Solved')"
              ></CustomDropdown>
            </li>
            <li>
              <CustomDropdown
                :options="fieldOptions"
                @dropdownChange="changeField"
                placeholder="Category"
                :default-text="this.$t('m.Field')"
              ></CustomDropdown>
            </li>
            <li>
              <CustomDropdown
                :options="difficultyOptions"
                @dropdownChange="changeDifficulty"
                placeholder="Difficulty"
                :default-text="this.$t('m.Difficulty')"
              ></CustomDropdown>
            </li>
          </ul>
        </header>
      </div>
      <hr>
      <ErrorSign v-if="error !== 0" :code="this.error"></ErrorSign>
      <ProblemSkeleton v-if="isLoading" class="loading"></ProblemSkeleton>
      <div v-else class="problem-list">
        <ProblemBadge
          v-for="problem in problem_list"
          :key="problem.problem_id"
          :problem="problem"
        ></ProblemBadge>
      </div>
    </section>
  </div>
</template>

<script>
import ProblemBadge from "./ProblemBadge.vue";
import api from "@oj/api";
import ProblemSkeleton from "./ProblemSkeleton.vue";
import {DIFFICULTY_MAP, FIELD_MAP} from "../../../../../../../utils/constants";
import ErrorSign from "../../../../general/ErrorSign.vue";
import CustomDropdown from "../../../../../components/dropdown/CustomDropdown.vue";

export default {
  name: 'problem-section-list',
  components: {CustomDropdown, ErrorSign, ProblemSkeleton, ProblemBadge},
  data() {
    return {
      isLoading: true,
      error: 0,

      fieldOptions: [],
      difficultyOptions: [],
      statusOptions: [
        {
          id: 'All',
          name: this.$t('m.All')
        },
        {
          id: 'Solved',
          name: this.$t('m.Solved_Problems')
        }, {
          id: 'Failed',
          name: this.$t('m.Failed_Problems')
        }],

      problemQuery: {
        difficulty: 'All',
        field: 'All',
        status: 'All',
      },
      problem_list: [],
    }
  },
  methods: {
    init() {
      this.status = this.$route.params.status
      this.difficultyOptions = Object.keys(DIFFICULTY_MAP).map(key => ({
        id: key,
        name: DIFFICULTY_MAP[key].value
      }))
      this.difficultyOptions.unshift({id: 'All', name: this.$t('m.All')})
      this.fieldOptions = Object.keys(FIELD_MAP).map(key => ({
        id: key,
        name: FIELD_MAP[key].value
      }))
      this.fieldOptions.unshift({id: 'All', name: this.$t('m.All')})
      this.refresh()
    },
    changeDifficulty(difficulty) {
      this.problemQuery.difficulty = difficulty
      this.refresh()
    },
    changeField(field) {
      this.problemQuery.field = field
      this.refresh()
    },
    changeStatus(status) {
      this.problemQuery.status = status
      this.refresh()
    },
    refresh() {
      this.isLoading = true
      api.getUserProblemInfo(this.username, this.problemQuery).then(res => {
        this.problem_list = res.data.data
      }).catch(error =>
        this.error = error.response.status
      ).finally(() =>
        this.isLoading = false
      )
    }
  },
  mounted() {
    this.init()
  },
  computed: {
    username() {
      let username = '';

      if (this.$route && this.$route.params && typeof this.$route.params.username === 'string') {
        username = this.$route.params.username;
      }

      if (!username && this.$store && this.$store.state.user && this.$store.state.user.profile && this.$store.state.user.profile.user && typeof this.$store.state.user.profile.user.username === 'string') {
        username = this.$store.state.user.profile.user.username;
      }

      return username;
    }
  }
}
</script>

<style scoped lang="less">
section {
  display: flex;
  flex-direction: column;
  border: 1px solid #dedede;
  border-radius: 0 0 7px 7px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  padding: 20px;

  .problem-tab__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  h1 {
    text-align: left;
  }

  .query-dropdowns {
    display: flex;
    gap: 10px;
    justify-content: flex-end;

    li {
      display: flex;
      align-items: center;
      gap: 10px;

      span {
        white-space: nowrap;
        font-size: 1rem;
        font-weight: 500;
      }
    }
  }

  hr {
    border: 0.5px solid #dedede;
    margin: 30px 20px 30px 0;
  }

  .problem-list {
    display: flex;
    gap: 10px;
    padding: 18px;
    flex-wrap: wrap;
  }
}
</style>
