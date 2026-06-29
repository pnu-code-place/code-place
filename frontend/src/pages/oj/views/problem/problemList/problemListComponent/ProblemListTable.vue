<template>
  <table>
    <thead>
      <tr>
        <th class="th-first">{{ $t("m.Th_Problem_Id") }}</th>
        <th class="th-second">{{ $t("m.Th_Problem_Title") }}</th>
        <th class="th-third">
          <button
            type="button"
            class="sort-header-button"
            @click="changeSort('difficulty')"
          >
            {{ $t("m.Th_Problem_Difficulty") }}
            <i :class="sortIconClass('difficulty')"></i>
          </button>
        </th>
        <th class="th-fourth">
          <button
            type="button"
            class="sort-header-button"
            @click="changeSort('accepted')"
          >
            {{ $t("m.Th_Problem_Num_Success") }}
            <i :class="sortIconClass('accepted')"></i>
          </button>
        </th>
        <th class="th-fifth">
          <button
            type="button"
            class="sort-header-button"
            @click="changeSort('ac_rate')"
          >
            {{ $t("m.Th_Problem_AC_Rate") }}
            <i :class="sortIconClass('ac_rate')"></i>
          </button>
        </th>
      </tr>
    </thead>
    <template v-if="this.problemList.length !== 0">
      <tbody>
        <tr v-for="problem in this.problemList" :key="problem._id">
          <td class="td-first">{{ problem._id }}</td>
          <td
            class="td-second"
            @click="enterProblemDetail(problem._id, problem.title)"
          >
            <span class="problemTitle">
              {{ problem.title }}
            </span>
            <br />
            <div v-if="showTags" class="problem-meta-row">
              <FieldCategoryBox
                :boxType="true"
                :value="FIELD_MAP[problem.field].value"
                :boxColor="FIELD_MAP[problem.field].boxColor"
              />
              <button
                v-for="category in getProblemTags(problem)"
                :key="problem._id + '-' + category"
                type="button"
                class="tag-filter-button"
                @click.stop="selectTag(category)"
              >
                <FieldCategoryBox
                  :boxType="false"
                  :value="'#' + category"
                  :boxColor="'#ffffff'"
                />
              </button>
            </div>
          </td>
          <td class="td-third" style="font-weight: bold; font-size: 14px">
            <div
              class="difficulty-badge"
              :style="{
                borderColor: DIFFICULTY_MAP[problem.difficulty].textColor,
              }"
            >
              {{ DIFFICULTY_MAP[problem.difficulty].value }}
            </div>
          </td>
          <td class="td-fourth" style="font-size: 13px">
            {{ problem.accepted_number + "명" }}
          </td>
          <td class="td-fifth" style="font-size: 13px">
            {{
              problem.submission_number == 0
                ? "없음"
                : Math.floor(
                    (problem.accepted_number / problem.submission_number) * 100,
                  ) + "%"
            }}
          </td>
        </tr>
      </tbody>
    </template>
  </table>
</template>

<script>
import { mapActions } from "vuex"
import FieldCategoryBox from "../../../../components/FieldCategoryBox.vue"
import { DIFFICULTY_MAP, FIELD_MAP } from "../../../../../../utils/constants"

export default {
  name: "ProblemListTable",
  components: { FieldCategoryBox },
  props: {
    problemList: {
      type: Array,
      default: () => [],
    },
    showTags: {
      type: Boolean,
      default: true,
    },
    sort: {
      type: String,
      default: "",
    },
  },
  methods: {
    ...mapActions(["changeProblemSolvingState"]),
    enterProblemDetail(problemId, problemTitle) {
      this.changeProblemSolvingState(true)
      this.$router.push({
        name: "problem-details",
        params: { problemID: problemId, problemTitle: problemTitle },
      })
    },
    selectTag(category) {
      this.$emit("select-tag", category)
    },
    getProblemTags(problem) {
      return Array.isArray(problem.tags) ? problem.tags : []
    },
    changeSort(field) {
      const defaultDirection = field === "difficulty" ? "asc" : "desc"
      const ascSort = `${field}_asc`
      const descSort = `${field}_desc`
      const defaultSort = `${field}_${defaultDirection}`
      const reverseSort = defaultDirection === "asc" ? descSort : ascSort
      const nextSort =
        this.sort === defaultSort
          ? reverseSort
          : this.sort === reverseSort
            ? ""
            : defaultSort
      this.$emit("sort-change", nextSort)
    },
    sortIconClass(field) {
      if (this.sort === `${field}_asc`) {
        return "fas fa-sort-up active"
      }
      if (this.sort === `${field}_desc`) {
        return "fas fa-sort-down active"
      }
      return "fas fa-sort"
    },
  },
  computed: {
    DIFFICULTY_MAP() {
      return DIFFICULTY_MAP
    },
    FIELD_MAP() {
      return FIELD_MAP
    },
  },
}
</script>

<style scoped lang="less">
.problemListTable {
  background-color: #ffffff;
  border-radius: 7px;
  border: 1px solid #dedede;
  width: 100%;
  padding-left: 30px;
  padding-right: 30px;
  margin-bottom: 20px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  overflow-x: auto;

  @media (max-width: 768px) {
    padding-left: 12px;
    padding-right: 12px;
  }
}

.noProblemListBox {
  width: 100%;
  padding: 30px;
  text-align: center;
}

table {
  background-color: var(--box-background-color);
  border: 1px solid #dedede;
  padding-right: 20px;
  padding-left: 20px;
  font-size: 0.9em;
  width: 100%;
  border-radius: 7px;
  border-spacing: 0;
  overflow: hidden;
}
table:hover {
  border: 1px solid #cccccc;
}

th {
  font-size: 1.3em;
}

.sort-header-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 0;
  color: inherit;
  font: inherit;
  font-weight: bold;
  white-space: nowrap;
  background: transparent;
  border: 0;
  cursor: pointer;
}

.sort-header-button i {
  color: #a5adba;
  font-size: 11px;
}

.sort-header-button i.active,
.sort-header-button:hover i {
  color: #4a86c0;
}

th:first-child {
  text-align: center;
}

th {
  text-align: center;
}

thead {
  font-weight: bold;
  color: #7e7e7e;

  .th-second {
    width: 400px;
  }
}

tbody {
  tr {
    font-size: 1.05em;
    td:first-child {
      font-size: 1.2em;
      text-align: center;
      font-weight: bold;
    }

    td:nth-child(2) {
      text-align: left;
      padding-left: 70px;
    }

    td {
      text-align: center;
    }

    .problemTitle {
      font-weight: bold;
      cursor: pointer;
      font-size: medium;
    }

    .problemTitle:hover {
      color: #4a86c0;
    }

    .problem-meta-row {
      display: flex;
      flex-wrap: wrap;
      gap: 4px 3px;
      align-items: center;
    }

    .problem-meta-row /deep/ .box {
      margin: 0;
    }

    .tag-filter-button {
      border: 0;
      padding: 0;
      margin: 0;
      background: transparent;
      cursor: pointer;
      font: inherit;
    }
  }
}

td,
th {
  padding: 1.3em 0.5em;
  vertical-align: center;
}

td {
  background: #fff;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

td:nth-child(2) {
  cursor: pointer;
}

.difficulty-badge {
  white-space: nowrap;
}
</style>
