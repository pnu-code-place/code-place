<template>
  <div class="problemListTableHeader">
    <h1 class="main-title">{{ $t('m.Problem_List') }}</h1>
    <div style="display: flex; align-items: center; justify-content: center">
      <li style="list-style-type: none; margin-left: 3px;">
        <Input v-model="query.keyword"
               @on-enter="filterByKeyword"
               @on-click="filterByKeyword"
               @input="filterByKeyword"
               :placeholder="$t('m.Search_Problem')"
               icon="ios-search-strong"/>
      </li>
      <Dropdown @on-click="filterByDifficulty" trigger="click" class="dropdown difficultyDropdown">
                          <span style="font-weight: bold; font-size: 15px; padding-right: 10px">{{
                              query.difficulty === '' ? this.$i18n.t('m.Difficulty') : this.$i18n.t('m.' + query.difficulty)
                            }}
                          </span>
        <Icon type="arrow-down-b"></Icon>
        <Dropdown-menu slot="list">
          <Dropdown-item name="">{{ $t('m.All') }}</Dropdown-item>
          <Dropdown-item name="VeryLow">{{ $t('m.VeryLow') }}</Dropdown-item>
          <Dropdown-item name="Low">{{ $t('m.Low') }}</Dropdown-item>
          <Dropdown-item name="Mid">{{ $t('m.Mid') }}</Dropdown-item>
          <Dropdown-item name="High">{{ $t('m.High') }}</Dropdown-item>
          <Dropdown-item name="VeryHigh">{{ $t('m.VeryHigh') }}</Dropdown-item>
        </Dropdown-menu>
      </Dropdown>
      <Dropdown @on-click="filterByField" trigger="click" class="dropdown fieldDropdown">
                          <span style="font-weight: bold; font-size: 15px; padding-right: 10px">{{
                              query.field === '' ? this.$i18n.t('m.Field') : FIELD_MAP[query.field].value
                            }}
                          </span>
        <Icon type="arrow-down-b"></Icon>
        <Dropdown-menu slot="list">
          <Dropdown-item name="">{{ $t('m.All') }}</Dropdown-item>
          <Dropdown-item name="0">{{ $t('m.Field_Impl') }}</Dropdown-item>
          <Dropdown-item name="2">{{ $t('m.Field_DataStructure') }}</Dropdown-item>
          <Dropdown-item name="1">{{ $t('m.Field_Math') }}</Dropdown-item>
          <Dropdown-item name="3">{{ $t('m.Field_Search') }}</Dropdown-item>
          <Dropdown-item name="4">{{ $t('m.Field_Sorting') }}</Dropdown-item>
        </Dropdown-menu>
      </Dropdown>
      <Dropdown @on-click="filterByCategory" trigger="click" class="dropdown difficultyDropdown">
                          <span style="font-weight: bold; font-size: 15px; padding-right: 10px">{{
                              query.tag === '' ? this.$i18n.t('m.Category') : this.$i18n.t(query.tag)
                            }}
                          </span>
        <Icon type="arrow-down-b"></Icon>
        <Dropdown-menu slot="list">
          <Dropdown-item name="">{{ $t('m.All') }}</Dropdown-item>
          <template v-for="(problem, idx) in this.problemList">
            <template v-for="(problemTag, idx) in problem.tags">
              <Dropdown-item :name=problemTag >{{ problemTag }}</Dropdown-item>
            </template>
          </template>
        </Dropdown-menu>
      </Dropdown>
      <Tooltip :content="$t('m.Pick_One')" placement="bottom" style="margin-left: 5px">
        <CustomIconBtn @click="pickOne" iconClass="fas fa-random"/>
      </Tooltip>
    </div>
  </div>
</template>

<script>
import FieldCategoryBox from "../../../../components/FieldCategoryBox.vue";
import {DIFFICULTY_MAP, FIELD_MAP} from "../../../../../../utils/constants";
import Pagination from "../../../../components/Pagination.vue";
import CustomIconBtn from "../../../../components/buttons/CustomIconBtn.vue";

export default {
  name: 'ProblemListTableHeader',
  components: {CustomIconBtn, Pagination, FieldCategoryBox},
  props:{
    query:{
      type: Object
    },
    problemList:{
      type: Object
    }
  },
  methods:{
    filterByCategory(categoryName) {
      this.query.tag = categoryName
      this.query.page = 1
      this.$emit("on-change-header")
    },
    filterByDifficulty(difficulty) {
      this.query.difficulty = difficulty
      this.query.page = 1
      this.$emit("on-change-header")
    },
    filterByField(field) {
      this.query.field = field
      this.query.page = 1
      this.$emit("on-change-header")
    },
    filterByKeyword(keyword) {
      // this.query.keyword = keyword
      this.query.page = 1
      this.$emit("on-change-header")
    },
    pickOne() {
      this.$emit("pick-one")
    }
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
.problemListTableHeader {
  display: flex;
  padding-left: 1%;
  margin-bottom: 25px;
  align-items: center;
  justify-content: space-between;

  p {
    font-weight: bold;
    font-size: 18px;
  }

  .dropdown {
    cursor: pointer;
    padding-top: 4px;
    padding-bottom: 4px;
    padding-left: 15px;
    padding-right: 15px;
    background-color: var(--box-background-color);
    border-radius: 7px;
    border: 1px solid #dedede;
  }

  .dropdown:not(:first-child) {
    margin-left: 5px;
  }

  .difficultyDropdown {
    cursor: pointer;
  }
}
</style>

