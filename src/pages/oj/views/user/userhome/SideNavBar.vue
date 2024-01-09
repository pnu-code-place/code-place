<template>
  <nav class="side-nav">
    <ul class="nav-content sticky">
      <li v-for="section in myPageNavItems" @click="gotoSection(section.name)">
        {{ section.title }}
      </li>
    </ul>
  </nav>
</template>

<script>
import {myPageNavItems} from "./index";

export default {
  computed: {
    myPageNavItems() {
      return myPageNavItems
    }
  },
  data() {
    return {}
  },
  methods: {
    gotoSection(name) {
      if (this.$route.name === name) return
      this.$router.push(`${name}`)
    }
  }
}
</script>

<style scoped lang="less">



.side-nav {
  width: 20%;
  margin-right: 20px;

  .nav-content {
    padding: 0;
    margin: 0;


    li {
      padding: 10px 0;
      font-size: 20px;
      cursor: pointer;
      font-weight: bold;

      &:hover {
        background-color: #eee;
      }
    }
  }
}

</style>
