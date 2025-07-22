<template>
  <div class="submission-accepted-dropdown">
    <div>
      <p class="sub-title">제출 코드</p>
      <CodeHighlight
        type="code"
        :code="submission.code || ''"
        :language="getHljsLanguage(submission.language)"
        :theme.sync="theme"
      />
    </div>
  </div>
</template>


<script>
import CodeHighlight from './CodeHighlight.vue';
import { HIGHLIGHT_JS_LANGUAGES } from '../../../../../../utils/constants';

export default {
  name: "SubmissionAcceptedDropdown",
  components: {
    CodeHighlight,
  },
  props: {
    submission: {
      type: Object,
    },
    theme: {
      type: Boolean,
      default: false, // Default to light theme
    }
  },
  methods: {
    getHljsLanguage(language) {
      return HIGHLIGHT_JS_LANGUAGES[language] || "plaintext";
    },
  }
}

</script>

<style scoped lang="less">

.sub-title {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 8px;
}
</style>
