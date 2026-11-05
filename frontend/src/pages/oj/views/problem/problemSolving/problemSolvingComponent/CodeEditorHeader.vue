<template>
  <div ref="header" class="container-header" :class="`compact-${compactLevel}`">
    <div class="header-title" :title="$t('m.Code_Editor_Title')">
      <i class="fas fa-code" />
      <span>{{ $t("m.Code_Editor_Title") }}</span>
    </div>
    <div class="header-actions">
      <div class="language-select" v-click-outside="closeLanguageMenu">
        <button
          type="button"
          class="language-trigger"
          :id="`code-language-${problem._id}`"
          :aria-expanded="String(languageMenuOpen)"
          :aria-label="$t('m.Code_Editor_Language_Select')"
          @click="languageMenuOpen = !languageMenuOpen"
        >
          <span>{{ language }}</span>
          <i class="fas fa-chevron-down"></i>
        </button>
        <transition name="menu-fade">
          <div v-if="languageMenuOpen" class="language-menu" role="menu">
            <button
              v-for="item in problem.languages"
              :key="item"
              type="button"
              class="language-option"
              :class="{ selected: item === language }"
              role="menuitem"
              @click="selectLanguage(item)"
            >
              {{ item }}
            </button>
          </div>
        </transition>
      </div>
      <AIAssistantBtn
        :active="aiVisible"
        :compact="compactLevel >= 2"
        @open-ai="$emit('open-ai')"
      />
      <SubmissionBtn
        :isSubmitting="isSubmitting"
        @create-submission="$emit('create-submission')"
      />
      <SubmissionStatus
        :compact="compactLevel >= 2"
        :statusVisible="statusVisible"
        :contestID="contestID"
        :result="result"
        :submissionId="submissionId"
      />
    </div>
  </div>
</template>

<script>
import { defineComponent } from "vue"
import SubmissionStatus from "./SubmissionStatus.vue"
import SubmissionBtn from "./SubmissionBtn.vue"
import AIAssistantBtn from "./AIAssistantBtn.vue"

// 헤더 너비(px)에 따라 단계적으로 줄임
// 1: "코드 작성" 글자 숨김, 2: AI 조교·제출결과 아이콘만, 3: 제목 아이콘까지 숨김
const COMPACT_BREAKPOINTS = [540, 430, 340]

export default defineComponent({
  props: {
    problem: Object,
    language: {
      type: String,
      default: "C++",
    },
    statusVisible: Boolean,
    contestID: [String, Number],
    result: Object,
    submissionId: String,
    isSubmitting: Boolean,
    aiVisible: {
      type: Boolean,
      default: false,
    },
  },
  components: {
    SubmissionBtn,
    SubmissionStatus,
    AIAssistantBtn,
  },
  data() {
    return {
      languageMenuOpen: false,
      headerWidth: 0,
    }
  },
  computed: {
    compactLevel() {
      if (!this.headerWidth) return 0
      return COMPACT_BREAKPOINTS.filter((bp) => this.headerWidth < bp).length
    },
  },
  mounted() {
    const el = this.$refs.header
    if (!el) return
    this.headerWidth = el.clientWidth
    if (window.ResizeObserver) {
      this._headerResizeObserver = new ResizeObserver((entries) => {
        this.headerWidth = entries[0].contentRect.width
      })
      this._headerResizeObserver.observe(el)
    }
  },
  beforeDestroy() {
    if (this._headerResizeObserver) {
      this._headerResizeObserver.disconnect()
      this._headerResizeObserver = null
    }
  },
  directives: {
    clickOutside: {
      bind(el, binding) {
        el.__problemClickOutside__ = (event) => {
          if (!(el === event.target || el.contains(event.target))) {
            binding.value(event)
          }
        }
        document.addEventListener("click", el.__problemClickOutside__)
      },
      unbind(el) {
        document.removeEventListener("click", el.__problemClickOutside__)
        delete el.__problemClickOutside__
      },
    },
  },
  methods: {
    closeLanguageMenu() {
      this.languageMenuOpen = false
    },
    selectLanguage(newLang) {
      this.languageMenuOpen = false
      this.$emit("change-language", newLang)
    },
    onResetToTemplate() {
      if (
        !window.confirm(
          this.$i18n.t("m.Are_you_sure_you_want_to_reset_your_code"),
        )
      ) {
        return
      }
      let template = this.problem.template
      if (template && template[this.language]) {
        this.code = template[this.language]
      } else {
        this.code = ""
      }
      this.$refs.myCm.resetCM()
    },
  },
})
</script>

<style scoped lang="less">
.container-header {
  display: flex;
  justify-content: space-between;
  height: 50px;
  width: 100%;
  align-items: center;
  border: 1px solid var(--border-color);
  padding-right: 10px;
  padding-left: 20px;
  border-radius: 7px;
  margin-bottom: 10px;
  background-color: var(--ps-content-color);

  .header-title {
    display: flex;
    align-items: center;
    min-width: 0;
  }

  .header-title span {
    margin-left: 10px;
    font-size: medium;
    font-weight: bold;
    white-space: nowrap;
  }

  &.compact-1,
  &.compact-2,
  &.compact-3 {
    padding-left: 14px;

    .header-title span {
      display: none;
    }
  }

  &.compact-3 {
    padding-left: 8px;
    padding-right: 8px;

    .header-title {
      display: none;
    }

    .header-actions {
      gap: 6px;
      margin-left: auto;
    }

    .language-trigger {
      min-width: 0;
      padding: 0 8px;
    }
  }
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  min-width: 0;

  > * {
    flex-shrink: 0;
    white-space: nowrap;
  }
}

.language-select {
  position: relative;
}

.language-trigger {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-width: 88px;
  height: 34px;
  padding: 0 12px;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background: var(--bg-color);
  color: var(--ps-content-title-color);
  cursor: pointer;
  font-size: 13px;
  font-weight: 650;

  span {
    margin-left: 0;
    font-size: 13px;
    font-weight: 650;
  }

  i {
    margin-left: auto;
    font-size: 11px;
    opacity: 0.72;
  }
}

.language-trigger:hover {
  border-color: var(--custom-btn-hover-color);
  background: var(--header-btn-color);
}

.language-menu {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  z-index: 50;
  min-width: 138px;
  padding: 6px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--ps-content-color);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.16);
}

.language-option {
  display: block;
  width: 100%;
  padding: 8px 10px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: var(--ps-content-text-color);
  cursor: pointer;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
}

.language-option:hover,
.language-option.selected {
  background: var(--header-btn-color);
  color: var(--ps-content-title-color);
}

.menu-fade-enter-active,
.menu-fade-leave-active {
  transition:
    opacity 0.12s ease,
    transform 0.12s ease;
}

.menu-fade-enter,
.menu-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
