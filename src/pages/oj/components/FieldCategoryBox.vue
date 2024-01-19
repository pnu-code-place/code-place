<template>
  <div class="fieldCategoryBox">
    <template v-if="boxType">
      <div class="box fieldBox" :style="{'background-color': boxColor}">
        <span>
          {{value}}
        </span>
      </div>
    </template>
    <template v-else>
      <div class="box categoryBox">
        <span>
          {{value}}
        </span>
      </div>
    </template>
  </div>
</template>

<script>
export default {
  name: 'FieldCategoryBox',
  props: {
    boxType: {
      type: Boolean,
      default: false
    },
    value: {
      type: String,
      default: ''
    },
    boxColor: {
      type: String,
      default: 'red'
    }
  },
  data () {
    return {

    }
  },
}
</script>

<style lang="less" scoped>

.box{
  text-align: center;
  margin-top: 2px;
  margin-right: 3px;
  padding-left: 4px;
  padding-right: 4px;
  border-radius: 30px;
  width: fit-content;
  height: fit-content;
}
.fieldBox{
  color: white;
  font-weight: bold;

  border: 1px solid #ffffff;
}
.categoryBox{
  color: #4E4E4E;
  border: 1px solid #949494;
}
</style>
