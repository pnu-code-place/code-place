<template>
  <span style="display: none"></span>
</template>

<script>
import api from "../../api.js"

export default {
  name: "OjLogoutPage",
  mounted() {
    api.logout().then((res) => {
      this.$store.dispatch("clearProfile")
      this.$router.replace({
        path: "/",
      })
    })
  },
}
</script>
