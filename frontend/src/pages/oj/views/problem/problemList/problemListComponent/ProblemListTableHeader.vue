<template>
  <div class="problemListTableHeader">
    <div class="header-title-row">
      <h1 class="main-title">{{ $t("m.Problem_List") }}</h1>
      <button
        type="button"
        class="tag-visibility-toggle"
        :class="{ active: isTagHidden }"
        :aria-pressed="isTagHidden ? 'true' : 'false'"
        @click="toggleTagVisibility"
      >
        <i :class="isTagHidden ? 'fas fa-eye' : 'fas fa-eye-slash'"></i>
        <span>{{ isTagHidden ? $t("m.Show_Tags") : $t("m.Hide_Tags") }}</span>
      </button>
    </div>
    <div class="header-controls">
      <li style="list-style-type: none; margin-left: 3px">
        <Input
          v-model="localKeyword"
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
          >{{ query.tag === "" ? this.$i18n.t("m.Category") : query.tag }}
        </span>
        <Icon type="arrow-down-b"></Icon>
        <Dropdown-menu slot="list" class="problem-dropdown-menu">
          <Dropdown-item name="">{{ $t("m.All") }}</Dropdown-item>
          <Dropdown-item v-for="tag in tagOptions" :key="tag" :name="tag">{{
            tag
          }}</Dropdown-item>
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
  props: {
    query: {
      type: Object,
    },
    tagList: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      localKeyword: this.query.keyword || "",
    }
  },
  watch: {
    "query.keyword"(keyword) {
      this.localKeyword = keyword || ""
    },
  },
  methods: {
    filterByCategory(categoryName) {
      this.$emit("update-query", { tag: categoryName, page: 1 })
    },
    filterByDifficulty(difficulty) {
      this.$emit("update-query", { difficulty, page: 1 })
    },
    filterByField(field) {
      this.$emit("update-query", { field, page: 1 })
    },
    filterByKeyword() {
      this.$emit("update-query", { keyword: this.localKeyword, page: 1 })
    },
    pickOne() {
      this.$emit("pick-one")
    },
    toggleTagVisibility() {
      this.$emit("update-query", {
        hideTag: this.isTagHidden ? "" : "1",
      })
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
    isTagHidden() {
      return this.query.hideTag === "1"
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
  gap: 16px;

  .header-title-row {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
  }

  .main-title {
    margin: 0;
    display: flex;
    align-items: center;
  }

  .header-controls {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    flex-wrap: wrap;
    gap: 5px;
  }

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
}

.filter-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;

  @media (max-width: 768px) {
    width: 100%;
  }
}

.tag-visibility-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 4px;
  border: 1px solid #e2e5ed;
  border-radius: 8px;
  background: #f7f8fa;
  color: #78797d;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  line-height: 1;
  white-space: nowrap;

  transition:
    background 0.15s,
    border-color 0.15s,
    color 0.15s;

  i {
    font-size: 12px;
    opacity: 0.8;
  }

  &:hover {
    background: #eef0f5;
    border-color: #c8ccd6;
    color: #717070;
  }
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
</style>
