<template>
  <div class="problemDetailFlexibleContainer">
    <section class="detailCard">
      <header
        class="detailTitle"
        :id="`problem-title-${problem._id}`"
        :style="problemZoomStyle"
      >
        <template v-if="loading">
          <div class="skeleton-line skeleton-title"></div>
          <div class="detailTitleMeta">
            <div class="detailTitleMetaLeft">
              <div class="skeleton-pill"></div>
              <div class="skeleton-pill skeleton-pill-short"></div>
              <div class="skeleton-pill skeleton-pill-short"></div>
            </div>
            <div class="detailTitleMetaRight">
              <div class="skeleton-zoom-control"></div>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="detailTitleText">{{ problemTitleText }}</div>
          <div class="detailTitleMeta">
            <div class="detailTitleMetaLeft">
              <div
                class="headerDetailBtn"
                style="background-color: var(--difficulty-color)"
                :id="`problem-difficulty-${problem._id}`"
              >
                {{ getDifficulty }}
              </div>
              <div class="headerDetailBtn" @click="scrollField">
                <Icon type="ios-pie" color="#F8B193" />
                영역
              </div>
              <div class="headerDetailBtn" @click="scrollCategory">
                <Icon type="ios-pricetag" color="#FF9F9F" />
                태그
              </div>
            </div>
            <div class="detailTitleMetaRight">
              <div class="zoom-control" aria-label="문제 설명 확대">
                <button
                  type="button"
                  class="zoom-button"
                  :disabled="problemZoomPercent <= minProblemZoom"
                  aria-label="축소"
                  @click.stop="decreaseProblemZoom"
                >
                  <Icon type="minus-round" />
                </button>
                <span class="zoom-value">{{ problemZoomPercent }}%</span>
                <button
                  type="button"
                  class="zoom-button"
                  :disabled="problemZoomPercent >= maxProblemZoom"
                  aria-label="확대"
                  @click.stop="increaseProblemZoom"
                >
                  <Icon type="plus-round" />
                </button>
              </div>
              <div
                v-if="problem.is_bonus"
                class="headerDetailBtn bonusBadge"
                title="정답 시 점수를 2배로 획득해요!"
              >
                <i class="fas fa-award"></i>
                Bonus x2
              </div>
            </div>
          </div>
        </template>
      </header>
      <div v-if="loading" class="problem-skeleton" aria-busy="true">
        <section class="skeleton-section">
          <div class="skeleton-heading"></div>
          <div class="skeleton-line skeleton-wide"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line skeleton-medium"></div>
        </section>
        <section class="skeleton-section">
          <div class="skeleton-heading skeleton-heading-small"></div>
          <div class="skeleton-line skeleton-wide"></div>
          <div class="skeleton-line skeleton-short"></div>
        </section>
        <section class="skeleton-samples">
          <div class="skeleton-sample-card"></div>
          <div class="skeleton-sample-card"></div>
        </section>
        <section class="skeleton-section">
          <div class="skeleton-heading skeleton-heading-small"></div>
          <div class="skeleton-constraints">
            <div class="skeleton-chip"></div>
            <div class="skeleton-chip"></div>
          </div>
        </section>
      </div>
      <div
        v-else
        id="problem-content"
        class="markdown-body"
        :style="problemZoomStyle"
      >
        <p class="title firstTitle">{{ $t("m.Description") }}</p>
        <div
          class="content"
          v-html="problem.description"
          v-katex
          :id="`problem-description-${problem._id}`"
        ></div>
        <p class="title">
          {{ $t("m.Input") }}
          <span v-if="problem.io_mode.io_mode == 'File IO'"
            >({{ $t("m.FromFile") }}: {{ problem.io_mode.input }})</span
          >
        </p>
        <div
          class="content"
          v-html="problem.input_description"
          v-katex
          :id="`problem-input-desc-${problem._id}`"
        ></div>

        <p class="title">
          {{ $t("m.Output") }}
          <span v-if="problem.io_mode.io_mode == 'File IO'"
            >({{ $t("m.ToFile") }}: {{ problem.io_mode.output }})</span
          >
        </p>
        <div
          class="content"
          v-html="problem.output_description"
          v-katex
          :id="`problem-output-desc-${problem._id}`"
        ></div>

        <div v-for="(sample, index) of problem.samples" :key="index">
          <div class="sample">
            <div class="sample-input">
              <p
                class="title"
                style="text-decoration: none; margin-bottom: 0px"
              >
                {{ $t("m.Sample_Input") }}
                {{ index + 1 }}
                <a
                  class="copy"
                  v-clipboard:copy="sample.input"
                  v-clipboard:success="onCopy"
                  v-clipboard:error="onCopyError"
                >
                  <Icon type="clipboard"></Icon>
                </a>
              </p>
              <pre :id="`problem-sample-input-${problem._id}-${index}`">{{
                sample.input
              }}</pre>
            </div>
            <div class="sample-output">
              <p
                class="title"
                style="text-decoration: none; margin-bottom: 0px"
              >
                {{ $t("m.Sample_Output") }} {{ index + 1 }}
              </p>
              <pre :id="`problem-sample-output-${problem._id}-${index}`">{{
                sample.output
              }}</pre>
            </div>
          </div>
        </div>
        <p class="title" style="text-decoration: none">제약사항</p>
        <div class="constraintList">
          <div
            class="constraintItem"
            :id="`problem-time-limit-${problem._id}`"
          >
            <div class="constraintIcon constraintIcon--time">
              <Icon type="ios-time-outline" />
            </div>
            <div class="constraintBody">
              <span class="constraintLabel">{{ $t("m.Time_Limit") }}</span>
              <span class="constraintValue">
                <span class="constraintNumber">{{ problem.time_limit }}</span>
                <span class="constraintUnit">ms</span>
              </span>
            </div>
          </div>
          <div
            class="constraintItem"
            :id="`problem-memory-limit-${problem._id}`"
          >
            <div class="constraintIcon constraintIcon--memory">
              <Icon type="ios-pulse" />
            </div>
            <div class="constraintBody">
              <span class="constraintLabel">{{ $t("m.Memory_Limit") }}</span>
              <span class="constraintValue">
                <span class="constraintNumber">{{ problem.memory_limit }}</span>
                <span class="constraintUnit">MB</span>
              </span>
            </div>
          </div>
        </div>
        <div v-if="problem.hint">
          <p class="title">{{ $t("m.Hint") }}</p>
          <section class="hintCard">
            <div
              class="hintContent"
              v-html="problem.hint"
              v-katex
              :id="`problem-hint-${problem._id}`"
            ></div>
          </section>
        </div>

        <template v-if="!contestID">
          <div class="detailInfoContainer">
            <div class="detailInfoBox">
              <div class="detailInfoBoxHeader" @click="toggleDropdown('field')">
                <p
                  class="title detailInfoLabel"
                  style="text-decoration: none; margin-top: 0px"
                  ref="field"
                >
                  <Icon
                    type="ios-pie"
                    color="#F8B193"
                    style="margin-right: 5px"
                  />
                  영역
                </p>
                <i
                  class="fas fa-chevron-down"
                  v-if="!dropdown.openFieldDropdown"
                ></i>
                <i class="fas fa-chevron-up" v-else></i>
              </div>
              <transition name="slide">
                <div class="dropdown-content" v-if="dropdown.openFieldDropdown">
                  <div class="dropdown-badge">
                    {{ getFieldLabel }}
                  </div>
                </div>
              </transition>
            </div>

            <div class="detailInfoBox">
              <div
                class="detailInfoBoxHeader"
                @click="toggleDropdown('category')"
              >
                <p
                  class="title detailInfoLabel"
                  style="text-decoration: none; margin-top: 0px"
                  ref="category"
                >
                  <Icon
                    type="ios-pricetag"
                    color="#FF9F9F"
                    style="margin-right: 5px"
                  />
                  태그
                </p>
                <i
                  class="fas fa-chevron-down"
                  v-if="!dropdown.openCategoryDropdown"
                ></i>
                <i class="fas fa-chevron-up" v-else></i>
              </div>
              <transition name="slide">
                <div
                  class="dropdown-content"
                  v-if="dropdown.openCategoryDropdown"
                >
                  <template v-for="category in problem.tags">
                    <div :key="category" class="dropdown-badge">
                      #{{ category }}
                    </div>
                  </template>
                </div>
              </transition>
            </div>

            <div class="detailInfoBox">
              <div class="detailInfoBoxHeader">
                <p
                  class="title detailInfoLabel"
                  style="text-decoration: none; margin-top: 0px"
                >
                  <Icon
                    type="ios-contact"
                    color="#90B8E7"
                    style="margin-right: 5px"
                  />
                  문제를 등록한 사람
                </p>
                <p
                  class="title detailInfoValue"
                  style="text-decoration: none; margin-top: 0px"
                >
                  {{ problem.created_by.username + "님" }}
                </p>
              </div>
            </div>

            <div class="detailInfoBox" v-if="problem.source">
              <div class="detailInfoBoxHeader">
                <p
                  class="title detailInfoLabel"
                  style="text-decoration: none; margin-top: 0px"
                >
                  <i
                    class="fas fa-paperclip"
                    style="margin-right: 5px; color: #424f66"
                  ></i>
                  출처
                </p>
                <p
                  class="title detailInfoValue"
                  style="text-decoration: none; margin-top: 0px"
                  :title="problem.source"
                >
                  {{ problem.source }}
                </p>
              </div>
            </div>
          </div>
        </template>
      </div>
    </section>
  </div>
</template>

<script>
import { defineComponent } from "vue"
import { DIFFICULTY_MAP, FIELD_MAP } from "../../../../../../utils/constants"

export default defineComponent({
  props: {
    problem: Object,
    contestID: [Number, String],
    loading: {
      type: Boolean,
      default: false,
    },
    problemZoomPercent: {
      type: Number,
      default: 100,
    },
  },
  data() {
    return {
      minProblemZoom: 80,
      maxProblemZoom: 140,
      problemZoomStep: 5,
      dropdown: {
        openFieldDropdown: false,
        openCategoryDropdown: false,
      },
    }
  },
  methods: {
    scrollField() {
      this.$refs.field.scrollIntoView({ behavior: "smooth" })
      this.dropdown.openFieldDropdown = true
    },
    scrollCategory() {
      this.$refs.category.scrollIntoView({ behavior: "smooth" })
      this.dropdown.openCategoryDropdown = true
    },
    toggleDropdown(type) {
      if (type === "field") {
        this.dropdown.openFieldDropdown = !this.dropdown.openFieldDropdown
        return
      }
      this.dropdown.openCategoryDropdown = !this.dropdown.openCategoryDropdown
    },
    onCopy() {
      this.$success("Code copied")
    },
    onCopyError() {
      this.$error("Failed to copy code")
    },
    decreaseProblemZoom() {
      this.updateProblemZoom(Math.max(
        this.minProblemZoom,
        this.problemZoomPercent - this.problemZoomStep,
      ))
    },
    increaseProblemZoom() {
      this.updateProblemZoom(Math.min(
        this.maxProblemZoom,
        this.problemZoomPercent + this.problemZoomStep,
      ))
    },
    updateProblemZoom(value) {
      this.$emit("update:problemZoomPercent", value)
    },
  },
  computed: {
    FIELD_MAP() {
      return FIELD_MAP
    },
    DIFFICULTY_MAP() {
      return DIFFICULTY_MAP
    },
    getDifficulty() {
      const difficultyInfo = DIFFICULTY_MAP[this.problem.difficulty]
      return difficultyInfo ? difficultyInfo.value : ""
    },
    getFieldLabel() {
      const fieldInfo = FIELD_MAP[this.problem.field]
      return fieldInfo ? fieldInfo.value : ""
    },
    problemTitleText() {
      if (!this.problem || !this.problem._id) return "\u00A0"
      return `${this.problem._id}. ${this.problem.title}`
    },
    problemZoomStyle() {
      const scale = this.problemZoomPercent / 100
      return {
        "--problem-heading-font-size": `${20 * scale}px`,
        "--problem-title-font-size": `${19 * scale}px`,
        "--problem-content-font-size": `${15 * scale}px`,
        "--problem-code-font-size": `${14 * scale}px`,
        "--problem-constraint-font-size": `${13 * scale}px`,
        "--problem-constraint-icon-size": `${14 * scale}px`,
        "--problem-constraint-label-size": `${12 * scale}px`,
        "--problem-constraint-unit-size": `${11 * scale}px`,
      }
    },
  },
})
</script>

<style scoped lang="less">
.problemDetailFlexibleContainer {
  min-height: 0;
  height: 100%;
  overflow-y: auto;
  overscroll-behavior-y: contain;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-color);

  &::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  &::-webkit-scrollbar-track {
    background: var(--dropdown-bg);
    border-radius: 4px;
  }
  &::-webkit-scrollbar-thumb {
    background-color: var(--border-color);
    border-radius: 4px;
    border: 2px solid var(--dropdown-bg);
  }

  .detailCard {
    flex: 1;
    min-height: 100%;
    box-sizing: border-box;
    background-color: var(--bg-color);
    padding: 30px 36px 40px;

    .detailTitle {
      color: var(--ps-content-title-color);
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 16px;
      font-weight: bold;
      min-height: 1.5em;
      line-height: 1.5;

      .detailTitleText {
        margin: 0;
        font-weight: bold;
        font-size: var(--problem-heading-font-size, 20px);
        letter-spacing: 0;
      }

      .detailTitleMeta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 16px;
        margin-top: 10px;
        font-size: 14px;
        font-weight: normal;
        line-height: 1.4;
      }

      .detailTitleMetaLeft,
      .detailTitleMetaRight {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
      }

      .detailTitleMetaLeft {
        flex: 1 1 auto;
        min-width: 0;
      }

      .detailTitleMetaRight {
        flex: 0 0 auto;
        gap: 10px;
      }
    }
  }

#problem-content {
  padding-top: 22px;

    --problem-title-font-size: 19px;
    --problem-content-font-size: 15px;
    --problem-code-font-size: 14px;
    --problem-constraint-font-size: 13px;
    --problem-constraint-icon-size: 14px;
    --problem-constraint-label-size: 12px;
    --problem-constraint-unit-size: 11px;

    .title {
      font-size: var(--problem-title-font-size);
      font-weight: 600;
      margin: 25px 0 8px 0;
      color: var(--ps-content-title-color) !important;

      .copy {
        padding-left: 8px;
      }

      &.firstTitle {
        margin-top: 0;
      }
    }

    .content {
      font-size: var(--problem-content-font-size);
      font-weight: 400;
      line-height: 1.6;
      letter-spacing: 0.01em;
      color: var(--ps-content-text-color) !important;
    }

    /deep/ p,
    /deep/ ul,
    /deep/ ol,
    /deep/ li,
    /deep/ span {
      color: var(--ps-content-text-color) !important;
      font-size: inherit;
      line-height: inherit;
    }

    /deep/ img {
      display: inline-block;
      width: auto;
      max-width: ~"min(100%, 640px)";
      height: auto;
      vertical-align: middle;
    }

    /deep/ .content img {
      max-width: 100%;
      height: auto;
      object-fit: contain;
    }

    .sample {
      display: flex;
      justify-content: space-around;
      align-items: stretch;

      &-input,
      &-output {
        width: 100%;
        flex: 1 1 auto;
        display: flex;
        flex-direction: column;
        margin-right: 5%;
      }

      pre {
        border-radius: 7px;
        align-self: stretch;
        border-style: solid;
        border: 1px solid var(--ps-content-pre-border-color);
        background: var(--ps-content-pre-background-color);
      }
    }

    /deep/ pre {
      font-size: var(--problem-code-font-size);
      background: var(--ps-content-pre-background-color) !important;
      border: 1px solid var(--ps-content-pre-border-color) !important;
      border-radius: 7px;
      color: var(--ps-content-code-text-color) !important;
    }

    /deep/ code {
      font-size: var(--problem-code-font-size);
      color: var(--ps-content-code-text-color) !important;
      background-color: var(--ps-content-code-background-color) !important;
    }

    /deep/ pre > code {
      background: transparent !important;
      color: var(--ps-content-code-text-color) !important;
    }

    /deep/ .hljs {
      background: var(--ps-content-pre-background-color) !important;
      color: var(--ps-content-code-text-color) !important;
    }
  }
}

.zoom-control {
  display: inline-grid;
  grid-template-columns: 28px 48px 28px;
  align-items: center;
  height: 28px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-color);
  color: var(--ps-content-title-color);
}

.zoom-button {
  width: 28px;
  height: 28px;
  padding: 0;
  border: 0;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font-size: 16px;
  font-weight: 700;
  line-height: 28px;
}

.zoom-button i {
  pointer-events: none;
}

.zoom-button:hover:not(:disabled) {
  background: var(--header-btn-color);
}

.zoom-button:disabled {
  cursor: not-allowed;
  opacity: 0.38;
}

.zoom-value {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 48px;
  height: 28px;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
  font-size: 12px;
  font-weight: 700;
  line-height: 1;
  white-space: nowrap;
}

.headerDetailBtn {
  background-color: var(--header-btn-color);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 28px;
  font-weight: 650;
  padding: 4px 10px;
  border-radius: 999px;

  i {
    margin-right: 0;
  }
}

.headerDetailBtn:hover {
  color: var(--text-color);
  background-color: var(--custom-btn-hover-color);
}

.header-icon {
  margin-right: 5px;
}

.field-icon {
  color: #f59e0b;
}

.tag-icon {
  color: #ef6461;
}

.author-icon {
  color: #4f8edb;
}

.bonusBadge {
  background-color: rgba(137, 94, 220, 0.13);
  color: #895edc;
}

.hintCard {
  border: 1px solid var(--ps-content-pre-border-color);
  border-radius: 8px;
  background-color: var(--ps-content-pre-background-color);
  padding: 14px 16px;
}

.constraintList {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
}

.constraintItem {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid var(--ps-content-pre-border-color);
  background-color: var(--ps-content-pre-background-color);
  font-size: var(--problem-constraint-font-size);
  line-height: 1.4;
  color: var(--ps-content-title-color);
}

.constraintIcon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: var(--problem-constraint-icon-size);

  &--time {
    color: #f59e0b;
  }

  &--memory {
    color: #3b82f6;
  }
}

.constraintBody {
  display: inline-flex;
  align-items: baseline;
  gap: 6px;
}

.constraintLabel {
  font-size: var(--problem-constraint-label-size);
  font-weight: 500;
  opacity: 0.7;
}

.constraintValue {
  display: inline-flex;
  align-items: baseline;
  gap: 2px;
}

.constraintNumber {
  font-family: "JetBrains Mono", "Noto Sans KR", "Apple SD Gothic Neo", "Menlo",
    "Monaco", "Consolas", monospace;
  font-variant-ligatures: none;
  font-size: var(--problem-constraint-font-size);
  font-weight: 600;
}

.constraintUnit {
  font-size: var(--problem-constraint-unit-size);
  font-weight: 500;
  opacity: 0.7;
}

.detailInfoContainer {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 30px;
}

.detailInfoBox {
  padding-left: 20px;
  padding-right: 30px;
  padding-top: 15px;
  cursor: pointer;
  border-top: 1px solid var(--border-color);

  .detailInfoBoxHeader {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    min-width: 0;
  }

  #problem-content & .detailInfoLabel {
    flex: 0 0 auto;
    font-weight: 650;
    opacity: 1;
    white-space: nowrap;
  }

  #problem-content & .detailInfoValue {
    min-width: 0;
    text-align: right;
    font-weight: 500;
    opacity: 0.78;
    overflow-wrap: anywhere;
    word-break: keep-all;
  }

  .dropdown-content {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
  }

  .dropdown-badge {
    background-color: var(--header-btn-color);
    padding: 3px 8px;
    font-weight: 400;
    margin-right: 10px;
    border-radius: 8px;
  }
}

.problem-skeleton {
  display: flex;
  flex-direction: column;
  gap: 26px;
  padding-top: 22px;
}

.skeleton-line,
.skeleton-heading,
.skeleton-pill,
.skeleton-sample-card,
.skeleton-chip,
.skeleton-zoom-control {
  border-radius: 6px;
  background: var(--ps-content-pre-background-color);
}

.skeleton-title {
  width: ~"min(280px, 64%)";
  height: 24px;
}

.skeleton-pill {
  width: 82px;
  height: 27px;
  margin-right: 10px;
  border-radius: 8px;
}

.skeleton-pill-short {
  width: 58px;
}

.skeleton-zoom-control {
  width: 120px;
  height: 31px;
}

.skeleton-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-heading {
  width: 130px;
  height: 22px;
}

.skeleton-heading-small {
  width: 86px;
}

.skeleton-line {
  width: 86%;
  height: 15px;
}

.skeleton-wide {
  width: 96%;
}

.skeleton-medium {
  width: 70%;
}

.skeleton-short {
  width: 48%;
}

.skeleton-samples {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 24px;
}

.skeleton-sample-card {
  min-height: 92px;
}

.skeleton-constraints {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skeleton-chip {
  width: 118px;
  height: 30px;
  border-radius: 999px;
}

.slide-enter-active,
.slide-leave-active {
  transition:
    max-height 0.3s ease,
    opacity 0.3s ease;
  overflow: hidden;
}

.slide-enter,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
}

.slide-enter-to,
.slide-leave {
  max-height: 100px;
  opacity: 1;
}

@media (max-width: 720px) {
  .problemDetailFlexibleContainer .detailCard {
    padding: 22px 20px 30px;
  }

  .skeleton-samples {
    grid-template-columns: 1fr;
  }
}
</style>
