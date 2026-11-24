<template>
  <div class="result-code-block">
    <slot />
    <button
      type="button"
      class="result-copy-button"
      :aria-label="label + (copied ? ' 복사됨' : ' 복사')"
      @click="copyText"
    >
      <svg
        v-if="copied"
        class="copy-icon"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
        focusable="false"
      >
        <path d="m20 6-11 11-5-5" />
      </svg>
      <i v-else class="fas fa-copy copy-icon" aria-hidden="true"></i>
      <span class="copy-status" aria-live="polite">{{
        copied ? "복사됨" : ""
      }}</span>
    </button>
  </div>
</template>

<script>
export default {
  name: "RunResultCodeBlock",
  props: {
    text: {
      type: String,
      default: "",
    },
    label: {
      type: String,
      default: "내용",
    },
  },
  data() {
    return {
      copied: false,
      copyVersion: 0,
    }
  },
  watch: {
    text() {
      this.resetCopied()
    },
  },
  beforeDestroy() {
    this.resetCopied()
  },
  methods: {
    resetCopied() {
      clearTimeout(this.copyTimer)
      this.copyVersion += 1
      this.copied = false
    },
    async copyText() {
      this.resetCopied()
      const version = this.copyVersion
      try {
        await this.$copyText(this.text)
        if (version !== this.copyVersion) return
        this.copied = true
        clearTimeout(this.copyTimer)
        this.copyTimer = setTimeout(() => {
          this.copied = false
        }, 1500)
      } catch {
        if (version !== this.copyVersion) return
        this.$error("복사하지 못했습니다. 내용을 선택해 직접 복사해주세요.")
      }
    },
  },
}
</script>

<style scoped>
.result-code-block {
  position: relative;
}

.result-copy-button {
  position: absolute;
  top: 6px;
  right: 6px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  padding: 0;
  border: 0;
  border-radius: 5px;
  background: transparent;
  color: var(--ps-content-text-color);
  font-family: inherit;
  font-size: 13px;
  font-weight: 400;
  line-height: 1;
  white-space: nowrap;
  cursor: pointer;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.15s;
}

.result-code-block:hover .result-copy-button,
.result-code-block:focus-within .result-copy-button {
  opacity: 1;
  pointer-events: auto;
}

.copy-icon {
  opacity: 0.55;
}

.result-copy-button:hover .copy-icon {
  opacity: 0.7;
}

.copy-status {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.result-copy-button:focus-visible {
  outline: 2px solid var(--ps-content-text-color);
  outline-offset: 2px;
}

@media (hover: none), (pointer: coarse) {
  .result-copy-button {
    opacity: 1;
    pointer-events: auto;
  }
}

@media (prefers-reduced-motion: reduce) {
  .result-copy-button {
    transition: none;
  }
}
</style>
