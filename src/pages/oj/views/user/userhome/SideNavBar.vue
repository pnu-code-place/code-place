<template>
  <nav class="side-nav sticky">
    <ul class="nav-content">
        <router-link v-for="section in myPageNavItems" :to="{name:section.name}" :key="section.name" testProps="I am props">{{ section.title }}</router-link>
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
}
</script>

<style scoped lang="less">

.side-nav {
  width: 20%;
  height: fit-content;
  margin-right: 20px;
  border: 1px solid #dedede;
  border-radius: 7px;
  padding: 10px;

  .nav-content {
    padding: 4px;
    margin: 0;

    a {
      display: block;
      text-decoration: none;
      padding: 10px 0;
      font-size: 16px;
      cursor: pointer;
      font-weight: bold;
      color: #495060;
      border-radius: 20px;

      &:hover {
        background-color: #eee;
      }
    }
    .router-link-exact-active {
      background-color: #44ccff;
    }
  }
}

</style>
