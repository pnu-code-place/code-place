
<script>
/**
 * CustomDropdown
 * @description: CustomDropdown 컴포넌트는 select 태그를 사용하여 드롭다운을 구현한 컴포넌트입니다.
 * @props selected: 드롭다운에서 선택된 항목의 value값을 설정합니다.
 * @props options: 드롭다운에 표시할 항목들을 배열로 받습니다. 각 항목은 객체로 구성되어야 하며, nameKey와 valueKey를 통해 각 항목의 표시값과 실제 값이 저장된 key값을 지정할 수 있습니다.
 * @props defaultText: 드롭다운의 기본값이 없을 때 표시할 텍스트를 설정합니다. 설정하지 않으면 기본값이 존재하지 않게 됩니다.
 * @props nameKey: 드롭다운에 표시할 항목의 key값을 설정합니다.
 * @props valueKey: 드롭다운에서 선택한 항목으로 넘겨줄 값의 key값을 설정합니다.
 * @emits dropdownChange: 드롭다운에서 선택한 항목의 value값을 부모 컴포넌트로 전달합니다.
 */
export default {
  name: 'CustomDropdown',
  data() {
    return {
      localSelected: this.selected
    }
  },
  props: {
    options: {
      type: Array,
      default: () => []
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
    },
    selected: {
      default : ''
    }
  },
  mounted() {
    this.items = this.options
  },
  watch: {
    selected(newVal) {
      this.localSelected = newVal; // selected prop이 변경될 때 localSelected 업데이트
    },
    localSelected(newVal) {
      this.$emit('dropdownChange', newVal); // localSelected이 변경될 때 부모 컴포넌트에게 이벤트 emit
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
  <select v-model=localSelected class="p-dropdown" :class="localSelected === '' ? 'disabled' : ''">
    <option :value="''" disabled class="disabled">
      {{ defaultText }}
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
