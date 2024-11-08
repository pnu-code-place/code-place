<template>
  <div style="padding: 20px; min-width: 1200px">
    PopupManagement
  </div>
</template>

<script>
export default {
  name: "PopupManagement",
  data() {
    return {}
  },
  beforeCreate() {
    console.log( "this")
  },
  created() {

    console.log(this, "Hello")
  },
  mounted() {
    console.log(this, "Hello mounted!")
  }
}
</script>


<style scoped lang="less">

</style>
