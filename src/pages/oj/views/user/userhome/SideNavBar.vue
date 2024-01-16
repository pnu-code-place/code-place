<template>
  <nav class="side-nav sticky">
    <ul class="nav-content">
      <li v-for="section in myPageNavItems" @click="gotoSection(section.name)">
        <router-link :to="section.path">{{ section.title }}</router-link>
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
      // 같은 페이지 내에서 이동하는 경우 이동하지 않음
      if (this.$route.name === name) return
      // 현재 페이지가 user-home인 경우 user-home/section-name으로 이동
      if (this.$route.name === 'user-home') {
        this.$router.push(`${this.$route.path}/${name}`)
        return
      }
      // 현재 페이지가 user-home이 아닌 경우 name으로 이동
      this.$router.push(`${name}`)
    }
  }
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


    li {
      text-decoration: none;
      padding: 10px 0;
      font-size: 16px;
      cursor: pointer;
      font-weight: bold;

      &:hover {
        background-color: #eee;
      }

      a {
        color: #495060;
      }
    }
  }
}

</style>
