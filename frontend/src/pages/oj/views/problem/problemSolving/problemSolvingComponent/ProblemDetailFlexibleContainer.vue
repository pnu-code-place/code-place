<template>
  <div class="problemDetailFlexibleContainer">
    <Panel :padding="45" class="detailCard" dis-hover style="transition: 0.3s">
      <div
        slot="title"
        class="detailTitle"
        :id="`problem-title-${problem._id}`"
      >
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
            <Tooltip
              :content="'정답 시 점수를 2배로 획득해요!'"
              placement="bottom"
            >
              <div
                v-if="problem.is_bonus"
                class="headerDetailBtn"
                style="background-color: rgba(174, 161, 214, 0.25)"
              >
                <i class="fas fa-award" style="color: #895edc"></i>
                Bonus x2
              </div>
            </Tooltip>
          </div>
        </div>
      </div>
      <div id="problem-content" class="markdown-body">
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
          <Card dis-hover class="hintCard">
            <div
              class="hintContent"
              v-html="problem.hint"
              v-katex
              :id="`problem-hint-${problem._id}`"
            ></div>
          </Card>
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
    </Panel>
  </div>
</template>

<script>
import { defineComponent } from "vue"
import { DIFFICULTY_MAP, FIELD_MAP } from "../../../../../../utils/constants"

export default defineComponent({
  props: {
    problem: Object,
    contestID: [Number, String],
  },
  data() {
    return {
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
  },
})
</script>

<style scoped lang="less">
.problemDetailFlexibleContainer {
  min-height: 0;
  height: 100%;
  overflow-y: scroll;
  display: flex;
  flex-direction: column;

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
    border: none;
    flex: 1;
    height: max-content;
    background-color: var(--bg-color);

    /deep/ .ivu-card-body {
      padding-top: 10px !important;
    }

    .detailTitle {
      color: var(--ps-content-title-color);
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 14px;
      padding-left: 18px;
      font-weight: bold;
      min-height: 1.5em;
      line-height: 1.5;

      .detailTitleText {
        font-weight: bold;
      }

      .detailTitleMeta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 10px;
        font-size: 14px;
        font-weight: normal;
        line-height: 1.4;
      }

      .detailTitleMetaLeft,
      .detailTitleMetaRight {
        display: flex;
        align-items: center;
      }
    }
  }

  #problem-content {

    .title {
      font-size: 19px;
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
      font-size: 15px;
      font-weight: 400;
      line-height: 1.6;
      letter-spacing: 0.01em;
      color: var(--ps-content-text-color) !important;

      /deep/ p,
      /deep/ ul,
      /deep/ ol,
      /deep/ li,
      /deep/ span {
        color: var(--ps-content-text-color) !important;
      }
    }

    /deep/ img {
      display: block;
      width: auto;
      max-width: ~"min(100%, 640px)";
      height: auto;
      margin: 12px auto;
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
      background: var(--ps-content-pre-background-color) !important;
      border: 1px solid var(--ps-content-pre-border-color) !important;
      border-radius: 7px;
      color: var(--ps-content-code-text-color) !important;
    }

    /deep/ code {
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

.headerDetailBtn {
  background-color: var(--header-btn-color);
  cursor: pointer;
  font-weight: 550;
  padding: 3px 8px;
  margin-right: 10px;
  border-radius: 8px;

  i {
    margin-right: 5px;
  }
}

.headerDetailBtn:hover {
  color: var(--text-color);
  background-color: var(--custom-btn-hover-color);
}

.hintCard {
  border: 1px solid var(--ps-content-pre-border-color);
  background-color: var(--ps-content-pre-background-color);
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
  font-size: 13px;
  line-height: 1.4;
  color: var(--ps-content-title-color);
}

.constraintIcon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;

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
  font-size: 12px;
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
  font-size: 13px;
  font-weight: 600;
}

.constraintUnit {
  font-size: 11px;
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
</style>
