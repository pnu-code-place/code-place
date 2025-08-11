<template>
  <ProblemSectionList></ProblemSectionList>
</template>

<script>
import ProblemBadge from "./ProblemBadge.vue"
import ProblemSkeleton from "./ProblemSkeleton.vue"
import PrimitiveDropdown from "../../../../../components/dropdown/CustomDropdown.vue"
import ErrorSign from "../../../../general/ErrorSign.vue"
import ProblemSectionList from "./ProblemSectionList.vue"

export default {
  name: "problem-section",
  components: {
    ProblemSectionList,
    ErrorSign,
    PrimitiveDropdown,
    ProblemSkeleton,
    ProblemBadge,
  },
  computed: {
    username() {
      let username = ""

      if (
        this.$route &&
        this.$route.params &&
        typeof this.$route.params.username === "string"
      ) {
        username = this.$route.params.username
      }

      if (
        !username &&
        this.$store &&
        this.$store.state.user &&
        this.$store.state.user.profile &&
        this.$store.state.user.profile.user &&
        typeof this.$store.state.user.profile.user.username === "string"
      ) {
        username = this.$store.state.user.profile.user.username
      }

      return username
    },
  },
}
</script>

<style scoped lang="less"></style>
