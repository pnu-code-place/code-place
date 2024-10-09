<script>
export default {
  name: "FAQItem",
  data() {
    return {
      extended: false
    }
  },
  props: {
    question: {
      type: String,
    },
  },
  methods: {
    toggleExtend() {
      this.extended = !this.extended;
    }
  },
  computed: {
    contentClass() {
      if (this.extended) {
        return "extend"
      } else {
        return "shrink"
      }
    }
  }
}
</script>

<template>
  <li class="faq-item">
    <div :class="`question ${this.contentClass}`" @click="toggleExtend">
      {{ $props.question }}
    </div>
    <div class="answer" v-if="this.extended">
      <slot>
        <p>{{ $t("m.There_Are_No_Answer_Yet") }}</p>
      </slot>
    </div>
  </li>
</template>

<style scoped lang="less">
.faq-item {
  width: 100%;
  border: 1px solid #dedede;
  background-color: var(--box-background-color);
}

.question {
  cursor: pointer;
  padding: 10px;
  border-bottom: 1px solid #dedede;
  font-weight: bold;
}

.answer {
  overflow: hidden;
  position: relative;
  transition: height 0.3s linear;
  padding: 10px 20px;
}

.content {
  position: absolute;
}

.extend {
  height: auto;
}

.shrink {
  border-bottom: none;
}

li {
  list-style: none;
}
</style>
