<template>
    <table>
      <thead>
      <tr>
        <th class="th-first">{{ $t('m.Th_Problem_Id') }}</th>
        <th class="th-second">{{ $t('m.Th_Problem_Title') }}</th>
        <th class="th-third">{{ $t('m.Th_Problem_Difficulty') }}</th>
        <th class="th-fourth">{{ $t('m.Th_Problem_Num_Success') }}</th>
        <th class="th-fifth">{{ $t('m.Th_Problem_AC_Rate') }}</th>
      </tr>
      </thead>
      <template v-if="this.problemList.length !== 0">
        <tbody>
        <tr v-for="problem in this.problemList">
          <td class="td-first">{{ problem._id }}</td>
          <td class="td-second" @click="enterProblemDetail(problem._id, problem.title)">
                <span class="problemTitle">
                  {{ problem.title }}
                </span>
            <br>
            <div style="display: flex">
              <FieldCategoryBox :boxType="true" :value="FIELD_MAP[problem.field].value"
                                :boxColor="FIELD_MAP[problem.field].boxColor"/>
              <template v-for="(category, idx) in problem.tags">
                <FieldCategoryBox :boxType="false" :value="'#' + category" :boxColor="'#ffffff'"/>
              </template>
            </div>
          </td>
          <td class="td-third" style="font-weight: bold; font-size: 14px">{{ DIFFICULTY_MAP[problem.difficulty].value }}</td>
          <td class="td-fourth" style="font-size: 13px">{{ problem.accepted_number+'명' }}</td>
          <td class="td-fifth" style="font-size: 13px">{{ problem.submission_number == 0 ? "없음" : Math.floor((problem.accepted_number / problem.submission_number ) * 100) + '%' }}</td>
        </tr>
        </tbody>
      </template>
    </table>
</template>

<script>
import {mapActions} from "vuex";
import FieldCategoryBox from "../../../../components/FieldCategoryBox.vue";
import {DIFFICULTY_MAP, FIELD_MAP} from "../../../../../../utils/constants";
import Pagination from "../../../../components/Pagination.vue";

export default {
  name: 'ProblemListTable',
  components: {Pagination, FieldCategoryBox},
  props:{
    problemList:{
      type: Object
    }
  },
  methods:{
    ...mapActions(['changeProblemSolvingState']),
    enterProblemDetail(problemId, problemTitle) {
      this.changeProblemSolvingState(true)
      this.$router.push({name: 'problem-details', params: {problemID: problemId, problemTitle: problemTitle}})
    },
  },
  computed:{
    DIFFICULTY_MAP() {
      return DIFFICULTY_MAP
    },
    FIELD_MAP() {
      return FIELD_MAP
    },
  }
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
  font-size: .9em;
  width: 100%;
  border-radius: 7px;
  border-spacing: 0;
  overflow: hidden;
}
table:hover{
  border: 1px solid #cccccc;
}

th{
  font-size: 1.3em;
}

th:first-child {
  text-align: center;
}

th {
  text-align: center;
}

thead {
  font-weight: bold;
  color: #7E7E7E;

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
      color: #4A86C0;
    }
  }
}

td, th {
  padding: 1.3em .5em;
  vertical-align: center;
}

td {
  background: #fff;
  border-top: 1px solid rgba(0, 0, 0, .1);
}

td:nth-child(2) {
  cursor: pointer;
}
</style>

