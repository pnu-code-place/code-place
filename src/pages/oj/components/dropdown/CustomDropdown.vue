<script>
export default {
  name: 'CustomDropdown',
  data() {
    return {
      selected: this.defaultValue,
      defaultValue: this.defaultValue
    }
  },

  props: {
    options: {
      type: Array,
      default: () => []
    },
    defaultValue: {
      type: Number,
      default: -1
    },
    defaultText: {
      type: String,
      default: ''
    },
    nameKey: { // nameKey는 options의 표시값을 저장한 key값을 지정
      type: String,
      default: 'name'
    },
    valueKey: { // valueKey는 options의 실제 값이 저장된 key값을 지정 value값은 emit을 통해 부모 컴포넌트로 전달
      type: String,
      default: 'id'
    }
  },
  mounted() {
    this.items = this.options
  },
  watch: {
    selected(newVal, oldVal) {
      this.$emit('dropdownChange', newVal)
    },
    options: {
      handler(newVal, oldVal) {
        this.items = newVal
      },
      deep: true
    }
  },
  emits: ['dropdownChange']
}
</script>

<template>
  <select v-model=selected class="p-dropdown"
          :class="this.selected === -1 && this.defaultText !== '' ? 'disabled' : '' ">
    <option v-if="this.defaultValue === -1 && this.defaultText !== ''" :value="-1" disabled class="disabled">
      {{ this.defaultText }}
    </option>
    <option v-for="item in options" :key="item[valueKey]" :value="item[valueKey]">{{ item[nameKey] }}</option>
  </select>
</template>

<style scoped lang="less">
select {
  width: 100%;
  padding: 6px 7px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 14px;
  color: #495060;

  option {
    font-size: 16px;
  }

  &.disabled {
    color: #aaa;
  }
}
</style>
