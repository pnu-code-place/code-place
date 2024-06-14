<template>
  <Dropdown class="dropdown" @on-click="onMonthChangeEventEmit">
    <span>
      {{
        month === ""
          ? this.$i18n.t("m.Execute_Month")
          : this.$i18n.t("m." + month)
      }}
      <Icon type="arrow-down-b"></Icon>
    </span>
    <Dropdown-menu slot="list">
      <Dropdown-item name="">{{ $t("m.All") }}</Dropdown-item>
      <Dropdown-item name="JAN">{{ $t("m.JAN") }}</Dropdown-item>
      <Dropdown-item name="FEB">{{ $t("m.FEB") }}</Dropdown-item>
      <Dropdown-item name="MAR">{{ $t("m.MAR") }}</Dropdown-item>
      <Dropdown-item name="APR">{{ $t("m.APR") }}</Dropdown-item>
      <Dropdown-item name="MAY">{{ $t("m.MAY") }}</Dropdown-item>
      <Dropdown-item name="JUN">{{ $t("m.JUN") }}</Dropdown-item>
      <Dropdown-item name="JUL">{{ $t("m.JUL") }}</Dropdown-item>
      <Dropdown-item name="AUG">{{ $t("m.AUG") }}</Dropdown-item>
      <Dropdown-item name="SEP">{{ $t("m.SEP") }}</Dropdown-item>
      <Dropdown-item name="OCT">{{ $t("m.OCT") }}</Dropdown-item>
      <Dropdown-item name="NOV">{{ $t("m.NOV") }}</Dropdown-item>
      <Dropdown-item name="DEC">{{ $t("m.DEC") }}</Dropdown-item>
    </Dropdown-menu>
  </Dropdown>
</template>

<script>
export default {
  name: "App",
  props: {
    month: String,
  },
  methods: {
    onMonthChangeEventEmit(month) {
      this.$emit("onMonthChange", month);
    },
  },
};
</script>

<style>
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
