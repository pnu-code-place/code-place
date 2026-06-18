<template>
  <div class="problemListTableHeader">
    <h1 class="main-title">{{ $t("m.Problem_List") }}</h1>
    <div style="display: flex; align-items: center; justify-content: center">
      <li style="list-style-type: none; margin-left: 3px">
        <Input
          v-model="keyword"
          @on-enter="filterByKeyword"
          @on-click="filterByKeyword"
          :placeholder="$t('m.Search_Problem')"
          icon="ios-search-strong"
        />
      </li>
      <Dropdown
        @on-click="filterByDifficulty"
        trigger="click"
        class="dropdown difficultyDropdown"
      >
        <span
          class="dropdown-label"
          style="font-weight: bold; font-size: 15px; padding-right: 10px"
          >{{
            query.difficulty === ""
              ? this.$i18n.t("m.Difficulty")
              : this.$i18n.t("m." + query.difficulty)
          }}
        </span>
        <Icon type="arrow-down-b"></Icon>
        <Dropdown-menu slot="list" class="problem-dropdown-menu">
          <Dropdown-item name="">{{ $t("m.All") }}</Dropdown-item>
          <Dropdown-item name="VeryLow">{{ $t("m.VeryLow") }}</Dropdown-item>
          <Dropdown-item name="Low">{{ $t("m.Low") }}</Dropdown-item>
          <Dropdown-item name="Mid">{{ $t("m.Mid") }}</Dropdown-item>
          <Dropdown-item name="High">{{ $t("m.High") }}</Dropdown-item>
          <Dropdown-item name="VeryHigh">{{ $t("m.VeryHigh") }}</Dropdown-item>
        </Dropdown-menu>
      </Dropdown>
      <Dropdown
        @on-click="filterByField"
        trigger="click"
        class="dropdown fieldDropdown"
      >
        <span
          class="dropdown-label"
          style="font-weight: bold; font-size: 15px; padding-right: 10px"
          >{{
            query.field === ""
              ? this.$i18n.t("m.Field")
              : FIELD_MAP[query.field].value
          }}
        </span>
        <Icon type="arrow-down-b"></Icon>
        <Dropdown-menu slot="list" class="problem-dropdown-menu">
          <Dropdown-item name="">{{ $t("m.All") }}</Dropdown-item>
          <Dropdown-item name="0">{{ $t("m.Field_Impl") }}</Dropdown-item>
          <Dropdown-item name="2">{{
            $t("m.Field_DataStructure")
          }}</Dropdown-item>
          <Dropdown-item name="1">{{ $t("m.Field_Math") }}</Dropdown-item>
          <Dropdown-item name="3">{{ $t("m.Field_Search") }}</Dropdown-item>
          <Dropdown-item name="4">{{ $t("m.Field_Sorting") }}</Dropdown-item>
          <Dropdown-item name="5">{{ $t("m.Field_Algorithm") }}</Dropdown-item>
        </Dropdown-menu>
      </Dropdown>
      <Dropdown
        @on-click="filterByCategory"
        trigger="click"
        class="dropdown categoryDropdown"
      >
        <span
          class="dropdown-label"
          style="font-weight: bold; font-size: 15px; padding-right: 10px"
          >{{
            query.tag === ""
              ? this.$i18n.t("m.Category")
              : query.tag
          }}
        </span>
        <Icon type="arrow-down-b"></Icon>
        <Dropdown-menu slot="list" class="problem-dropdown-menu">
          <Dropdown-item name="">{{ $t("m.All") }}</Dropdown-item>
          <Dropdown-item
            v-for="tag in tagOptions"
            :key="tag"
            :name="tag"
            >{{ tag }}</Dropdown-item
          >
        </Dropdown-menu>
      </Dropdown>
      <Tooltip
        :content="$t('m.Pick_One')"
        placement="bottom"
        style="margin-left: 5px"
      >
        <CustomIconBtn @click="pickOne" iconClass="fas fa-random" />
      </Tooltip>
    </div>
  </div>
</template>

<script>
import { DIFFICULTY_MAP, FIELD_MAP } from "../../../../../../utils/constants"
import CustomIconBtn from "../../../../components/buttons/CustomIconBtn.vue"

export default {
  name: "ProblemListTableHeader",
  components: { CustomIconBtn },
  data() {
    return {
      keyword: this.query.keyword || "",
    }
  },
  props: {
    query: {
      type: Object,
    },
    tagList: {
      type: Array,
      default: () => [],
    },
  },
  methods: {
    filterByCategory(categoryName) {
      this.$emit("on-change-header", { tag: categoryName, page: 1 })
    },
    filterByDifficulty(difficulty) {
      this.$emit("on-change-header", { difficulty, page: 1 })
    },
    filterByField(field) {
      this.$emit("on-change-header", { field, page: 1 })
    },
    filterByKeyword(keyword) {
      this.$emit("on-change-header", { keyword: this.keyword, page: 1 })
    },
    pickOne() {
      this.$emit("pick-one")
    },
  },
  computed: {
    DIFFICULTY_MAP() {
      return DIFFICULTY_MAP
    },
    FIELD_MAP() {
      return FIELD_MAP
    },
    tagOptions() {
      const tagList = Array.isArray(this.tagList) ? this.tagList : []
      const tags = tagList
        .map((tag) => (typeof tag === "string" ? tag : tag.name))
        .filter(Boolean)
      return Array.from(new Set(tags)).sort((a, b) => a.localeCompare(b))
    },
  },
  watch: {
    "query.keyword"(keyword) {
      this.keyword = keyword || ""
    },
  },
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
    display: flex;
    align-items: center;
  }

  .dropdown:not(:first-child) {
    margin-left: 5px;
  }

  .difficultyDropdown {
    cursor: pointer;
  }

  /deep/ .problem-dropdown-menu .ivu-dropdown-item {
    min-width: 100%;
    width: 100%;
  }

  /deep/ .ivu-select-dropdown {
    margin-top: 12px;
  }

  .categoryDropdown /deep/ .ivu-select-dropdown {
    max-height: 320px;
    max-width: 260px;
    overflow-y: auto;
  }

  .categoryDropdown /deep/ .problem-dropdown-menu .ivu-dropdown-item {
    max-width: 260px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
</style>
