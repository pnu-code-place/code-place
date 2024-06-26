<template>
  <Dropdown class="dropdown" @on-click="onYearChangeEventEmit">
    <span>
      {{ year === "" ? this.$i18n.t("m.Execute_Year") : year + "년" }}
      <Icon type="arrow-down-b"></Icon>
    </span>
    <Dropdown-menu slot="list">
      <Dropdown-item name="">{{ $t("m.All") }}</Dropdown-item>
      <Dropdown-item name="0">{{ new Date().getFullYear() }}</Dropdown-item>
      <Dropdown-item name="1">{{ new Date().getFullYear() - 1 }}</Dropdown-item>
      <Dropdown-item name="2">{{ new Date().getFullYear() - 2 }}</Dropdown-item>
      <Dropdown-item name="3">{{ new Date().getFullYear() - 3 }}</Dropdown-item>
    </Dropdown-menu>
  </Dropdown>
</template>

<script>
export default {
  name: "App",
  props: {
    year: String,
  },
  methods: {
    onYearChangeEventEmit(year) {
      if (year === "") this.$emit("onYearChange", year);
      else {
        let yearFormat = new Date().getFullYear() - parseInt(year);
        this.$emit("onYearChange", yearFormat.toString());
      }
    },
  },
};
</script>

<style scoped lang="less">
.dropdown {
  color: var(--container-font-color);
  font-size: 14px;
  span {
    width: 100px;
    height: 35px;
    padding: 5px 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 700;
    cursor: default;
    background-color: white;
    border: 1px solid var(--container-border-color);
    border-radius: var(--container-border-radius);
  }
}
</style>
