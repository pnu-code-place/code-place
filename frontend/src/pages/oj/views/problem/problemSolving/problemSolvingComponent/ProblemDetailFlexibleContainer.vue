<template>
  <div class="problemDetailFlexibleContainer">
    <Panel :padding="45" class="detailCard" dis-hover style="transition: 0.3s">
      <div
        slot="title"
        class="detailTitle"
        :id="`problem-title-${problem._id}`"
      >
        {{ problem._id + ". " + problem.title }}
      </div>
      <div id="problem-content" class="markdown-body" v-katex>
        <div style="display: flex; justify-content: space-between">
          <div style="display: flex">
            <div
              class="headerDetailBtn"
              style="background-color: var(--difficulty-color)"
              :id="`problem-difficulty-${problem._id}`"
            >
              {{ this.getDifficulty }}
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
          <div style="display: flex">
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
        <p class="title" style="margin-top: 25px">{{ $t("m.Description") }}</p>
        <p
          class="content"
          v-html="problem.description"
          :id="`problem-description-${problem._id}`"
        ></p>
        <p class="title">
          {{ $t("m.Input") }}
          <span v-if="problem.io_mode.io_mode == 'File IO'"
            >({{ $t("m.FromFile") }}: {{ problem.io_mode.input }})</span
          >
        </p>
        <p
          class="content"
          v-html="problem.input_description"
          :id="`problem-input-desc-${problem._id}`"
        ></p>

        <p class="title">
          {{ $t("m.Output") }}
          <span v-if="problem.io_mode.io_mode == 'File IO'"
            >({{ $t("m.ToFile") }}: {{ problem.io_mode.output }})</span
          >
        </p>
        <p
          class="content"
          v-html="problem.output_description"
          :id="`problem-output-desc-${problem._id}`"
        ></p>

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
        <li style="padding-left: 20px">
          <code :id="`problem-time-limit-${problem._id}`">
            {{ $t("m.Time_Limit") + "   " + problem.time_limit + "ms" }}
          </code>
        </li>
        <li style="padding-left: 20px">
          <code :id="`problem-memory-limit-${problem._id}`">
            {{ $t("m.Memory_Limit") + "   " + problem.memory_limit + "mb" }}
          </code>
        </li>
        <div v-if="problem.hint">
          <p class="title">{{ $t("m.Hint") }}</p>
          <Card dis-hover class="hintCard">
            <div
              class="hintContent"
              v-html="problem.hint"
              :id="`problem-hint-${problem._id}`"
            ></div>
          </Card>
        </div>

        <template v-if="!contestID">
          <div class="detailInfoContainer">
            <div class="detailInfoBox">
              <div class="detailInfoBoxHeader" @click="toggleDropdown('field')">
                <p
                  class="title"
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
                    {{ FIELD_MAP[problem.field].value }}
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
                  class="title"
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
                  <template v-for="(category, idx) in problem.tags">
                    <div class="dropdown-badge">#{{ category }}</div>
                  </template>
                </div>
              </transition>
            </div>

            <div class="detailInfoBox">
              <div class="detailInfoBoxHeader">
                <p class="title" style="text-decoration: none; margin-top: 0px">
                  <Icon
                    type="ios-contact"
                    color="#90B8E7"
                    style="margin-right: 5px"
                  />
                  문제를 등록한 사람
                </p>
                <p class="title" style="text-decoration: none; margin-top: 0px">
                  {{ problem.created_by.username + "님" }}
                </p>
              </div>
            </div>

            <div class="detailInfoBox" v-if="problem.source">
              <div class="detailInfoBoxHeader">
                <p class="title" style="text-decoration: none; margin-top: 0px">
                  <i
                    class="fas fa-paperclip"
                    style="margin-right: 5px; color: #424f66"
                  ></i>
                  출처
                </p>
                <p class="title" style="text-decoration: none; margin-top: 0px">
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
import FieldCategoryBox from "../../../../components/FieldCategoryBox.vue"
import { DIFFICULTY_MAP, FIELD_MAP } from "../../../../../../utils/constants"

export default defineComponent({
  props: {
    problem: Object,
    contestID: Number,
  },
  components: { FieldCategoryBox },
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
    onCopy(event) {
      this.$success("Code copied")
    },
    onCopyError(e) {
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
      let difficultyInfo = DIFFICULTY_MAP[this.problem.difficulty]
      return difficultyInfo.value
    },
  },
})
</script>

<style scoped lang="less">
.problemDetailFlexibleContainer {
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

    .detailTitle {
      color: var(--ps-content-title-color);
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 14px;
      padding-left: 18px;
      font-weight: bold;
    }
  }

  #problem-content {
    margin-top: -50px;

    .title {
      font-size: 16.5px;
      font-weight: 750;
      margin: 25px 0 8px 0;
      color: var(--ps-content-title-color) !important;

      .copy {
        padding-left: 8px;
      }
    }

    p.content {
      font-size: 15px;
      font-weight: 600;
      color: var(--ps-content-text-color) !important;
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

    code {
      color: var(--ps-content-code-text-color) !important;
      background-color: var(--ps-content-code-background-color);
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
  }

  .dropdown-content {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
  }

  .dropdown-badge {
    background-color: var(--header-btn-color);
    padding: 3px 8px;
    font-weight: 500;
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
