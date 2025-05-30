<template>
  <div>
    <section>
      <div class="problem-tab">
        <header class="problem-tab__header">
          <h1 class="main-title">{{ $t('m.Problem_Status') }}</h1>
          <ul class="query-dropdowns">
            <li>
              <DatePicker
                class="date-picker"
                size="large"
                type="daterange"
                input-class="my-datepicker-input"
                split-panels
                :placeholder="$t('m.Date_Range_Filter')"
                v-model="dateRange"
                @on-change="changeDateRange"
              ></DatePicker>
            </li>
            <li>
              <CustomDropdown
                :options="statusOptions"
                @dropdownChange="changeStatus"
                placeholder="Status"
                :default-text="this.$t('m.Is_Solved')"
                :selected="this.query.status"
              ></CustomDropdown>
            </li>
            <li>
              <CustomDropdown
                :options="fieldOptions"
                @dropdownChange="changeField"
                placeholder="Category"
                :default-text="this.$t('m.Field')"
                :selected="this.query.field"
              ></CustomDropdown>
            </li>
            <li>
              <CustomDropdown
                :options="difficultyOptions"
                @dropdownChange="changeDifficulty"
                placeholder="Difficulty"
                :default-text="this.$t('m.Difficulty')"
                :selected="this.query.difficulty"
              ></CustomDropdown>
            </li>
          </ul>
        </header>
      </div>
      <hr>
      <ErrorSign v-if="error !== 0" :code="this.error"></ErrorSign>
      <ProblemSkeleton v-if="isLoading" class="loading-skeleton"></ProblemSkeleton>
      <ErrorSign v-else-if="problem_list.length === 0" code="" :solution="this.$t('m.There_Is_No_Solved_Problem')"></ErrorSign>
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
import utils from "../../../../../../../utils/utils";

export default {
  name: 'problem-section-list',
  components: {CustomDropdown, ErrorSign, ProblemSkeleton, ProblemBadge},
  data() {
    return {
      isLoading: true,
      error: 0,
      query: {
        startDate: '',
        endDate: '',
        field: '',
        difficulty: '',
        status: ''
      },
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
      problem_list: [],
    }
  },
  methods: {
    init() {
      this.initQuery()
      this.optionInit()
      this.requestData()
    },
    initQuery() {
      this.query.startDate = this.$route.query.startDate || ''
      this.query.endDate = this.$route.query.endDate || ''
      this.query.field = this.$route.query.field || ''
      this.query.difficulty = this.$route.query.difficulty || ''
      this.query.status = this.$route.query.status || ''
    },
    optionInit() {
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
    },
    requestData() {
      this.isLoading = true
      api.getUserProblemInfo(this.username, utils.filterEmptyValue(this.query)).then(res => {
        this.problem_list = res.data.data
      }).catch(error =>
        this.error = error.response.status
      ).finally(() =>
        this.isLoading = false
      )
    },
    changeDateRange(dateRange) {
      if (dateRange && dateRange.length === 2) {
        this.query.startDate = dateRange[0]
        this.query.endDate = dateRange[1]
      } else {
        // If the date range is invalid, reset the start and end dates
        this.query.startDate = ''
        this.query.endDate = ''
      }
      this.pushRouter()
    },
    changeField(newVal) {
      this.query.field = newVal
      this.pushRouter()
    },
    changeStatus(newVal) {
      this.query.status = newVal
      this.pushRouter()
    },
    changeDifficulty(newVal) {
      this.query.difficulty = newVal
      this.pushRouter()
    },
    pushRouter() {
      this.$router.push({
        name: 'user-problems',
        params: {username: this.username},
        query: utils.filterEmptyValue(this.query)
      })
      this.requestData()
    },
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
  },
}
</script>

<style scoped lang="less">
section {
  display: flex;
  flex-direction: column;
  background-color: var(--box-background-color);
  border: 1px solid #dedede;
  border-radius: 7px;
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

  /* Style overriding for iview DatePicker */
  /deep/ .ivu-input {
    border: 1px solid #ccc !important;
    width: 200px;
  }

  /deep/ .ivu-input::placeholder {
    color: #aaa;
  }

  hr {
    border: 0.5px solid #dedede;
    margin: 20px 0;
  }

  .problem-list {
    display: flex;
    gap: 10px;
    padding: 18px;
    flex-wrap: wrap;
  }
}
</style>
