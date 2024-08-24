<template>
  <div style="display: flex; gap: 6px">
    <div class="search-input-wrapper">
      <input
        id="keyword"
        class="search-input"
        @keyup.enter="onKeywordChangeEventEmit"
        v-model="keyword"
        :placeholder="$t('m.Contest_Search_Keyword')"
      />
      <button class="search-input-icon" @click="onKeywordChangeEventEmit">
        <Icon type="ios-search-strong"></Icon>
      </button>
    </div>
    <button class="search-button" @click="onKeywordChangeEventEmit">
      {{ $t("m.Search") }}
    </button>
  </div>
</template>

<script>
export default {
  name: "App",
  data() {
    return {
      keyword: "",
    };
  },
  methods: {
    onKeywordChangeEventEmit() {
      this.$emit("onKeywordChange", this.keyword);
    },
  },
};
</script>

<style scoped lang="less">
.search-input-wrapper {
  width: 200px;
  height: 35px;
  font-size: 14px;
  padding: 5px 10px;
  background-color: white;
  border: 1px solid var(--container-border-color);
  border-radius: var(--container-border-radius);
  .search-input {
    width: 90%;
    height: 100%;
    border: none;
    outline: none;
  }
  .search-input-icon {
    background-color: transparent;
    border: none;
    font-size: 15px;
  }
}
.search-button {
  width: 45px;
  height: 35px;
  border-radius: var(--container-border-radius);
  font-size: 13px;
  color: white;
  background-color: var(--point-color);
}
</style>
