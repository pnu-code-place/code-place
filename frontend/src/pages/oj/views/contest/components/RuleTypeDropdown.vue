<template>
  <Dropdown class="dropdown" @on-click="onRuleChangeEventEmit">
    <span>
      {{
        rule_type === ""
          ? this.$i18n.t("m.Contest_Type")
          : this.$i18n.t("m." + rule_type)
      }}
      <Icon type="arrow-down-b"></Icon>
    </span>
    <Dropdown-menu slot="list">
      <Dropdown-item name="">{{ $t("m.All") }}</Dropdown-item>
      <Dropdown-item name="OI">{{ $t("m.OI") }}</Dropdown-item>
      <Dropdown-item name="ACM">{{ $t("m.ACM") }}</Dropdown-item>
    </Dropdown-menu>
  </Dropdown>
</template>

<script>
export default {
  name: "App",
  props: {
    rule_type: String,
  },
  methods: {
    onRuleChangeEventEmit(month) {
      this.$emit("onRuleChange", month);
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
