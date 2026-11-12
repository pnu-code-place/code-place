<template>
  <div class="problem-preview">
    <div class="preview-content markdown-body">
      <h2>{{ problem._id }}. {{ problem.title }}</h2>
      <p>
        {{ $t("m.Time_Limit") }}: {{ problem.time_limit }} ms ·
        {{ $t("m.Memory_Limit") }}: {{ problem.memory_limit }} MB
      </p>
      <section v-for="field in descriptionFields" :key="field.key">
        <h3>{{ field.title }}</h3>
        <div v-html="problem[field.key]" v-katex v-highlight-code></div>
      </section>
      <section v-for="(sample, index) in problem.samples" :key="index">
        <div class="sample">
          <div>
            <h3>{{ $t("m.Input_Samples") }} {{ index + 1 }}</h3>
            <pre>{{ sample.input }}</pre>
          </div>
          <div>
            <h3>{{ $t("m.Output_Samples") }} {{ index + 1 }}</h3>
            <pre>{{ sample.output }}</pre>
          </div>
        </div>
      </section>
      <section v-if="problem.hint">
        <h3>{{ $t("m.Hint") }}</h3>
        <div v-html="problem.hint" v-katex v-highlight-code></div>
      </section>
    </div>
  </div>
</template>

<script>
export default {
  name: "ProblemPreview",
  props: {
    problem: { type: Object, required: true },
  },
  computed: {
    descriptionFields() {
      return [
        { key: "description", title: this.$t("m.Description") },
        { key: "input_description", title: this.$t("m.Input_Description") },
        { key: "output_description", title: this.$t("m.Output_Description") },
      ]
    },
  },
}
</script>

<style scoped lang="less">
.problem-preview {
  /deep/ .preview-content {
    @import "../../../../styles/markdown.less";
  }

  max-height: 70vh;
  overflow-y: auto;
  padding-right: 16px;

  /deep/ img {
    max-width: 100%;
    height: auto;
  }
}

.sample {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}
</style>
