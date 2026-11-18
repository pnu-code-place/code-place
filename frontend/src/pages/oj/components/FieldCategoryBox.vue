<template>
  <span class="fieldCategoryBox">
    <span
      class="box"
      :class="boxType ? 'fieldBox' : 'categoryBox'"
      :style="boxType ? fieldStyle : null"
    >
      <span class="box-label">{{ value }}</span>
    </span>
  </span>
</template>

<script>
const FIELD_BADGE_STYLES = {
  0: { backgroundColor: "#ffe2ad", color: "#8c6129" },
  1: { backgroundColor: "#e1f2dc", color: "#537748" },
  2: { backgroundColor: "#ffe6d8", color: "#a46642" },
  3: { backgroundColor: "#dfecfc", color: "#5279a3" },
  4: { backgroundColor: "#ede3f7", color: "#84649f" },
  5: { backgroundColor: "#ffe0e5", color: "#b15468" },
}

export default {
  name: "FieldCategoryBox",
  props: {
    boxType: {
      type: Boolean,
      default: false,
    },
    value: {
      type: String,
      default: "",
    },
    boxColor: {
      type: String,
      default: "red",
    },
    field: {
      type: [Number, String],
      default: null,
    },
  },
  computed: {
    fieldStyle() {
      return (
        FIELD_BADGE_STYLES[this.field] || {
          backgroundColor: this.boxColor,
          color: "#667085",
        }
      )
    },
  },
}
</script>

<style lang="less" scoped>
.fieldCategoryBox {
  display: inline-flex;
  min-width: 0;
  max-width: 100%;
  vertical-align: middle;
}

.box {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  max-width: 100%;
  height: 20px;
  padding: 0 6px;
  border: 1px solid transparent;
  border-radius: 999px;
  box-sizing: border-box;
  font-family: inherit;
  font-size: 12px;
  font-weight: 400;
  line-height: 1;
  text-align: center;
  white-space: nowrap;
}

.box-label {
  display: block;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
}

.fieldBox {
  padding: 0 7px;
}

.categoryBox {
  border-color: #dfe1e7;
  background: #fff;
  color: #7d8390;
}
</style>
