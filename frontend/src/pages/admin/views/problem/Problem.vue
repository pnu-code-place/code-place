<template>
  <div class="problem view">
    <Panel
      :title="mode === 'edit' ? $t('m.Edit_Problem') : $t('m.Create_Problem')"
    >
      <div class="detailCard">
        <div class="header-input-container">
          <div class="header-question-id">
            <!-- 문제 번호 글자 -->
            <label class="custom-label"
              ><span class="required-asterisk">*</span
              >{{ $t("m.Display_ID") }}</label
            >
            <!-- 문제 번호 input 칸 -->
            <el-input
              class="id_input"
              v-model="problem._id"
              :placeholder="$t('m.Display_ID')"
            />
            <!-- 중복확인 버튼 -->
            <button
              class="duplicate-check-btn"
              @click="checkDuplicateProblemId"
            >
              {{ $t("m.Check_ID_Duplication") }}
            </button>
          </div>
          <div class="header-title">
            <!-- 문제 제목 글자 -->
            <label class="custom-label"
              ><span class="required-asterisk">*</span
              >{{ $t("m.Question_Title") }}</label
            >
            <!-- 문제 제목 input 칸 -->
            <el-input
              class="title_input"
              v-model="problem.title"
              :placeholder="$t('m.Question_Title')"
            />
          </div>
        </div>

        <div class="meta-data">
          <!-- 난이도 -->
          <div class="form-group difficulty-field">
            <label class="custom-label"
              ><span class="required-asterisk">*</span
              >{{ $t("m.Difficulty") }}</label
            >
            <div class="difficulty-row">
              <el-select
                class="difficulty-select"
                size="small"
                :placeholder="$t('m.Difficulty')"
                v-model="problem.difficulty"
              >
                <el-option :label="$t('m.VeryLow')" value="VeryLow"></el-option>
                <el-option :label="$t('m.Low')" value="Low"></el-option>
                <el-option :label="$t('m.Mid')" value="Mid"></el-option>
                <el-option :label="$t('m.High')" value="High"></el-option>
                <el-option
                  :label="$t('m.VeryHigh')"
                  value="VeryHigh"
                ></el-option>
              </el-select>
            </div>
          </div>

          <!-- 언어 선택 -->
          <div class="form-group language-field">
            <label class="custom-label"
              ><span class="required-asterisk">*</span
              >{{ $t("m.Languages") }}</label
            >
            <div class="language-container">
              <el-tooltip
                v-for="lang in allLanguage.languages"
                :key="'spj' + lang.name"
                effect="dark"
                :content="lang.description"
                placement="top-start"
              >
                <div
                  class="language-btn"
                  :class="{ active: problem.languages.includes(lang.name) }"
                  @click="toggleLanguage(lang.name)"
                >
                  <i
                    v-if="problem.languages.includes(lang.name)"
                    class="el-icon-check check-icon"
                  ></i>
                  <span v-else class="empty-box"></span>
                  <span class="lang-text" :data-text="lang.name">{{
                    lang.name
                  }}</span>
                </div>
              </el-tooltip>
            </div>
            <div class="el-form-item__error" v-if="error.languages">
              {{ error.languages }}
            </div>
          </div>
        </div>

        <!-- 설명 -->
        <div class="description-box">
          <!-- Description -->
          <div class="form-group">
            <label class="custom-label"
              ><span class="required-asterisk">*</span
              >{{ $t("m.Description") }}</label
            >
            <Simditor v-model="problem.description"></Simditor>
          </div>
          <!-- Input Description -->
          <div class="form-group">
            <label class="custom-label"
              ><span class="required-asterisk">*</span
              >{{ $t("m.Input_Description") }}</label
            >
            <Simditor v-model="problem.input_description"></Simditor>
          </div>
          <!-- Output Description -->
          <div class="form-group">
            <label class="custom-label"
              ><span class="required-asterisk">*</span
              >{{ $t("m.Output_Description") }}</label
            >
            <Simditor v-model="problem.output_description"></Simditor>
          </div>
        </div>

        <!-- 예제 입력 / 출력 -->
        <div class="sample-box">
          <div
            v-for="(sample, index) in problem.samples"
            :key="'sample' + index"
            class="sample-item"
          >
            <div class="sample-content">
              <div class="form-group sample-input">
                <label class="custom-label">
                  <span class="required-asterisk">*</span
                  >{{ $t("m.Input_Samples") }} {{ index + 1 }}
                </label>
                <el-input
                  class="sample-textarea"
                  :rows="5"
                  type="textarea"
                  :placeholder="$t('m.Input_Samples') + ' ' + (index + 1)"
                  v-model="sample.input"
                ></el-input>
              </div>
              <div class="form-group sample-output">
                <div class="custom-label-with-btn">
                  <label class="custom-label">
                    <span class="required-asterisk">*</span
                    >{{ $t("m.Output_Samples") }} {{ index + 1 }}
                  </label>
                  <button
                    type="button"
                    class="delete-btn"
                    @click="deleteSample(index)"
                  >
                    <i class="el-icon-delete"> Delete</i>
                  </button>
                </div>
                <el-input
                  class="sample-textarea"
                  :rows="5"
                  type="textarea"
                  :placeholder="$t('m.Output_Samples') + ' ' + (index + 1)"
                  v-model="sample.output"
                ></el-input>
              </div>
            </div>
          </div>
        </div>

        <!-- 예시 추가 버튼 -->
        <div class="add-sample-btn">
          <button type="button" class="add-samples" @click="addSample()">
            <i class="el-icon-plus"></i>{{ $t("m.Add_Sample") }}
          </button>
        </div>

        <!-- 시간 / 메모리 제한 -->
        <div>
          <div class="form-group">
            <label class="custom-label"
              ><span class="required-asterisk">*</span
              >{{ $t("m.Time_Limit") }} (ms)</label
            >
            <el-input
              class="limit-input"
              type="Number"
              :placeholder="$t('m.Time_Limit')"
              v-model="problem.time_limit"
            ></el-input>
          </div>
          <div class="form-group">
            <label class="custom-label"
              ><span class="required-asterisk">*</span
              >{{ $t("m.Memory_limit") }} (MB)</label
            >
            <el-input
              class="limit-input"
              type="Number"
              :placeholder="$t('m.Memory_limit')"
              v-model="problem.memory_limit"
            ></el-input>
          </div>
        </div>

        <!-- 힌트 -->
        <div class="form-group">
          <label class="custom-label">
            {{ $t("m.Hint") }}
          </label>
          <Simditor v-model="problem.hint"></Simditor>
        </div>

        <!-- 종류 / 테케 / 입출력모드 / 배점 설정 -->
        <div class="test-case-settings">
          <div class="settings-row">
            <div class="left-settings">
              <!-- 테스트 케이스 업로드 -->
              <div class="setting-item">
                <div
                  class="form-group"
                  :class="{ 'has-error': error.testCase }"
                >
                  <label class="custom-label col-label">
                    {{ $t("m.TestCase") }}
                    <span v-if="error.testCase" class="error-msg">{{
                      error.testCase
                    }}</span>
                  </label>
                  <div class="upload-container">
                    <el-upload
                      action="/api/admin/test_case"
                      name="file"
                      :data="{ spj: problem.spj }"
                      :show-file-list="true"
                      :on-success="uploadSucceeded"
                      :on-error="uploadFailed"
                    >
                      <button type="button" class="duplicate-btn upload-btn">
                        <i class="el-icon-fa-upload"></i>
                        {{ $t("m.Button_Choose_File") }}
                      </button>
                    </el-upload>
                  </div>
                </div>
              </div>
            </div>

            <div class="right-settings">
              <!-- 종류 선택 -->
              <div class="setting-item">
                <div class="form-group">
                  <label class="custom-label">{{ $t("m.Type") }}</label>
                  <div class="segmented-control">
                    <label class="custom-radio">
                      <input
                        type="radio"
                        value="ACM"
                        v-model="problem.rule_type"
                        :disabled="disableRuleType"
                      />
                      <span class="radio-text">ACM</span>
                    </label>
                    <label class="custom-radio">
                      <input
                        type="radio"
                        value="OI"
                        v-model="problem.rule_type"
                        :disabled="disableRuleType"
                      />
                      <span class="radio-text">OI</span>
                    </label>
                  </div>
                </div>
              </div>
              <!-- 입출력 모드 -->
              <div class="setting-item">
                <div class="form-group">
                  <label class="custom-label">{{ $t("m.IOMode") }}</label>
                  <div class="segmented-control">
                    <label class="custom-radio">
                      <input
                        type="radio"
                        value="Standard IO"
                        v-model="problem.io_mode.io_mode"
                      />
                      <span class="radio-text">Standard IO</span>
                    </label>
                    <label class="custom-radio">
                      <input
                        type="radio"
                        value="File IO"
                        v-model="problem.io_mode.io_mode"
                      />
                      <span class="radio-text">File IO</span>
                    </label>
                  </div>
                </div>
              </div>
              <!-- File IO 입력 파일 -->
              <div
                class="setting-item"
                v-if="problem.io_mode.io_mode == 'File IO'"
              >
                <div class="form-group">
                  <label class="custom-label"
                    ><span class="required-asterisk">*</span
                    >{{ $t("m.InputFileName") }}</label
                  >
                  <input
                    type="text"
                    class="limit-input custom-input"
                    v-model="problem.io_mode.input"
                  />
                </div>
              </div>
              <!-- File IO 출력 파일 -->
              <div
                class="setting-item"
                v-if="problem.io_mode.io_mode == 'File IO'"
              >
                <div class="form-group">
                  <label class="custom-label"
                    ><span class="required-asterisk">*</span
                    >{{ $t("m.OutputFileName") }}</label
                  >
                  <input
                    type="text"
                    class="limit-input custom-input"
                    v-model="problem.io_mode.output"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- 테스트 케이스 표 (테케 업로드 시 생성)-->
          <div
            class="table-container"
            v-if="problem.test_case_score && problem.test_case_score.length > 0"
          >
            <table class="custom-table">
              <colgroup>
                <col class="col-30" />
                <col class="col-30" />
                <col class="col-40" />
              </colgroup>
              <thead>
                <tr>
                  <th>
                    {{ $t("m.Input") }}
                  </th>
                  <th>
                    {{ $t("m.Output") }}
                  </th>
                  <th>
                    {{ $t("m.Score") }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(row, index) in problem.test_case_score"
                  :key="index"
                >
                  <td>
                    {{ row.input_name }}
                  </td>
                  <td>
                    {{ row.output_name }}
                  </td>
                  <td>
                    <input
                      type="number"
                      class="limit-input score-input"
                      :placeholder="$t('m.Score')"
                      v-model="row.score"
                      :disabled="problem.rule_type !== 'OI'"
                    />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 코드 템플릿 -->
        <div class="form-group">
          <label class="custom-label">{{ $t("m.Code_Template") }}</label>
          <div class="template-container">
            <div class="template-tabs">
              <label
                v-for="(v, k, index) in template"
                :key="'template-tab' + k"
                class="custom-checkbox"
                :class="{
                  'is-active-tab':
                    activeTemplateLanguage === k ||
                    (!activeTemplateLanguage && index === 0),
                  'is-disabled-tab': !problem.languages.includes(k),
                }"
                @click="
                  problem.languages.includes(k)
                    ? (activeTemplateLanguage = k)
                    : null
                "
              >
                <input
                  type="checkbox"
                  v-model="v.checked"
                  :disabled="!problem.languages.includes(k)"
                />
                <span class="checkbox-text">
                  <i v-if="v.checked" class="el-icon-check check-icon"></i>
                  <span v-else class="empty-box"></span>
                  <span class="lang-text" :data-text="k">{{ k }}</span>
                </span>
              </label>
            </div>

            <div v-for="(v, k, index) in template" :key="'template-editor' + k">
              <div
                v-if="
                  activeTemplateLanguage === k ||
                  (!activeTemplateLanguage && index === 0)
                "
                class="template-editor-area"
              >
                <div :class="{ 'is-disabled': !v.checked }">
                  <div class="template-editor-header">
                    <span class="editor-lang-badge">{{ k }}</span>
                    <span class="editor-lang-label">코드 템플릿</span>
                  </div>
                  <div class="template-editor">
                    <code-mirror v-model="v.code" :mode="v.mode"></code-mirror>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 스페셜 저지 -->
        <div class="form-group">
          <label class="custom-label">{{ $t("m.Special_Judge") }}</label>
          <div class="spj-toggle-row">
            <span class="spj-toggle-label">{{
              $t("m.Use_Special_Judge")
            }}</span>
            <label class="spj-toggle">
              <input
                type="checkbox"
                :checked="problem.spj"
                @click.prevent="switchSpj()"
              />
              <span
                class="spj-toggle-track"
                :class="{ 'is-on': problem.spj }"
              ></span>
            </label>
          </div>
          <div class="el-form-item__error" v-if="error.spj">
            {{ error.spj }}
          </div>
        </div>

        <!-- 스페셜 저지 코드 -->
        <div v-if="problem.spj" class="form-group">
          <div class="spj-editor-controls">
            <label class="custom-label spj-label">{{
              $t("m.Special_Judge_Code")
            }}</label>
            <span class="spj-lang-label">{{ $t("m.SPJ_language") }}</span>
            <div class="spj-radio-group">
              <label
                v-for="lang in allLanguage.spj_languages"
                :key="lang.name"
                class="spj-radio-btn"
                :class="{ active: problem.spj_language === lang.name }"
                :title="lang.description"
              >
                <input
                  type="radio"
                  :value="lang.name"
                  v-model="problem.spj_language"
                />
                {{ lang.name }}
              </label>
            </div>
            <button
              class="spj-compile-btn"
              @click="compileSPJ"
              :disabled="loadingCompile"
            >
              <i v-if="loadingCompile" class="el-icon-loading"></i>
              <i v-else class="el-icon-fa-random"></i>
              {{ $t("m.Compile") }}
            </button>
          </div>
          <code-mirror v-model="problem.spj_code" :mode="spjMode"></code-mirror>
        </div>

        <!-- 영역 -->
        <div class="form-group category-field section-divider">
          <label class="custom-label"
            ><span class="required-asterisk">*</span
            ><Icon type="ios-pie" color="#F8B193" class="field-icon" />{{
              $t("m.Field")
            }}</label
          >
          <el-select
            class="difficulty-select field-select"
            size="small"
            :placeholder="$t('m.Field')"
            v-model="problem.field"
          >
            <el-option :label="$t('m.Field_Impl')" :value="0"></el-option>
            <el-option :label="$t('m.Field_Math')" :value="1"></el-option>
            <el-option
              :label="$t('m.Field_DataStructure')"
              :value="2"
            ></el-option>
            <el-option :label="$t('m.Field_Search')" :value="3"></el-option>
            <el-option :label="$t('m.Field_Sorting')" :value="4"></el-option>
            <el-option :label="$t('m.Field_Algorithm')" :value="5"></el-option>
          </el-select>
        </div>

        <!-- 태그 -->
        <div class="form-group tag-field section-divider">
          <label class="custom-label"
            ><span class="required-asterisk">*</span
            ><Icon type="ios-pricetag" color="#FF9F9F" class="field-icon" />{{
              $t("m.Tag")
            }}</label
          >
          <div class="tags-container">
            <span v-for="tag in problem.tags" :key="tag" class="tag-chip">
              {{ tag }}
              <button class="tag-chip-close" @click="closeTag(tag)">×</button>
            </span>
            <input
              v-if="inputVisible"
              v-model="tagInput"
              class="tag-input"
              :placeholder="$t('m.New_Tag')"
              @keyup.enter="addTag"
              @blur="addTag"
              ref="tagInputRef"
            />
            <button v-else class="tag-add-btn" @click="inputVisible = true">
              + {{ $t("m.New_Tag") }}
            </button>
          </div>
          <div class="el-form-item__error" v-if="error.tags">
            {{ error.tags }}
          </div>
        </div>

        <!-- 출처 -->
        <div class="form-group section-divider">
          <label class="custom-label"
            ><Icon
              type="paperclip"
              color="#90B8E7"
              class="field-icon"
              size="18"
            />{{ $t("m.Source") }}</label
          >

          <input
            class="source-custom-input source-input"
            :placeholder="$t('m.Source')"
            v-model="problem.source"
          />
        </div>
        <!-- 공개 / 제출 공유 여부 -->
        <div class="form-group">
          <div class="toggle-row">
            <div class="toggle-item">
              <span class="toggle-label">{{ $t("m.Visible") }}</span>
              <label class="spj-toggle">
                <input type="checkbox" v-model="problem.visible" />
                <span
                  class="spj-toggle-track"
                  :class="{ 'is-on': problem.visible }"
                ></span>
              </label>
            </div>
            <div class="toggle-item">
              <span class="toggle-label">{{ $t("m.ShareSubmission") }}</span>
              <label class="spj-toggle">
                <input type="checkbox" v-model="problem.share_submission" />
                <span
                  class="spj-toggle-track"
                  :class="{ 'is-on': problem.share_submission }"
                ></span>
              </label>
            </div>
          </div>
        </div>

        <!-- 제출 -->
        <div class="submit-row">
          <save @click.native="submit()">Save</save>
        </div>
      </div>
    </Panel>
  </div>
</template>

<script>
import Simditor from "../../components/Simditor"
import Accordion from "../../components/Accordion"
import CodeMirror from "../../components/CodeMirror"
import api from "../../api"
import { FIELD_MAP } from "../../../../utils/constants"

export default {
  name: "Problem",
  computed: {
    FIELD_MAP() {
      return FIELD_MAP
    },
  },
  components: {
    Simditor,
    Accordion,
    CodeMirror,
  },
  data() {
    return {
      loadingCompile: false,
      mode: "",
      contest: {},
      problem: {
        field: "",
        languages: [],
        io_mode: {
          io_mode: "Standard IO",
          input: "input.txt",
          output: "output.txt",
        },
      },
      reProblem: {
        languages: [],
        io_mode: {
          io_mode: "Standard IO",
          input: "input.txt",
          output: "output.txt",
        },
      },
      testCaseUploaded: false,
      allLanguage: {},
      inputVisible: false,
      tagInput: "",
      template: {},
      activeTemplateLanguage: null,
      title: "",
      spjMode: "",
      disableRuleType: false,
      routeName: "",
      error: {
        tags: "",
        spj: "",
        languages: "",
        testCase: "",
      },
    }
  },
  mounted() {
    this.routeName = this.$route.name
    if (
      this.routeName === "edit-problem" ||
      this.routeName === "edit-contest-problem"
    ) {
      this.mode = "edit"
    } else {
      this.mode = "add"
    }
    api.getLanguages().then((res) => {
      this.problem = this.reProblem = {
        _id: "",
        title: "",
        description: "",
        input_description: "",
        output_description: "",
        time_limit: 1000,
        memory_limit: 256,
        difficulty: "Low",
        visible: true,
        share_submission: false,
        tags: [],
        languages: [],
        template: {},
        samples: [{ input: "", output: "" }],
        spj: false,
        spj_language: "",
        spj_code: "",
        spj_compile_ok: false,
        test_case_id: "",
        test_case_score: [],
        rule_type: "ACM",
        hint: "",
        source: "",
        io_mode: {
          io_mode: "Standard IO",
          input: "input.txt",
          output: "output.txt",
        },
      }
      let contestID = this.$route.params.contestId
      if (contestID) {
        this.problem.contest_id = this.reProblem.contest_id = contestID
        this.disableRuleType = true
        api.getContest(contestID).then((res) => {
          this.problem.rule_type = this.reProblem.rule_type =
            res.data.data.rule_type
          this.contest = res.data.data
        })
      }

      this.problem.spj_language = "C"

      let allLanguage = res.data.data
      this.allLanguage = allLanguage

      // get problem after getting languages list to avoid find undefined value in `watch problem.languages`
      if (this.mode === "edit") {
        this.title = this.$i18n.t("m.Edit_Problem")
        let funcName = {
          "edit-problem": "getProblem",
          "edit-contest-problem": "getContestProblem",
        }[this.routeName]
        api[funcName](this.$route.params.problemId).then((problemRes) => {
          let data = problemRes.data.data
          if (!data.spj_code) {
            data.spj_code = ""
          }
          data.spj_language = data.spj_language || "C"
          this.problem = data
          this.testCaseUploaded = true
        })
      } else {
        this.title = this.$i18n.t("m.Add_Problem")
        for (let item of allLanguage.languages) {
          this.problem.languages.push(item.name)
        }
      }
    })
  },
  watch: {
    $route() {
      this.resetProblem()
    },
    "problem.languages"(newVal) {
      let data = {}
      let selectedLanguages = JSON.parse(JSON.stringify(newVal || [])).sort()

      if (this.allLanguage && this.allLanguage.languages) {
        let allLangs = this.allLanguage.languages.sort((a, b) =>
          a.name.localeCompare(b.name),
        )

        for (let langConfig of allLangs) {
          let langName = langConfig.name
          let isSelected = selectedLanguages.includes(langName)

          if (this.template[langName] === undefined) {
            if (this.problem.template[langName] === undefined) {
              data[langName] = {
                checked: isSelected,
                code: langConfig.config.template,
                mode: langConfig.content_type,
              }
            } else {
              data[langName] = {
                checked: true,
                code: this.problem.template[langName],
                mode: langConfig.content_type,
              }
            }
          } else {
            let existingData = JSON.parse(
              JSON.stringify(this.template[langName]),
            )

            if (!isSelected) {
              existingData.checked = false
            }
            data[langName] = existingData
          }
        }
      }
      this.template = data
    },
    "problem.field"(newVal) {
      console.log(this.problem)
    },
    "problem.spj_language"(newVal) {
      this.spjMode = this.allLanguage.spj_languages.find((item) => {
        return item.name === this.problem.spj_language
      }).content_type
    },
  },
  methods: {
    toggleLanguage(langName) {
      const index = this.problem.languages.indexOf(langName)
      if (index !== -1) {
        this.problem.languages.splice(index, 1)
      } else {
        this.problem.languages.push(langName)
      }
    },
    switchSpj() {
      if (this.testCaseUploaded) {
        this.$confirm(
          "If you change problem judge method, you need to re-upload test cases",
          "Warning",
          {
            confirmButtonText: "Yes",
            cancelButtonText: "Cancel",
            type: "warning",
          },
        )
          .then(() => {
            this.problem.spj = !this.problem.spj
            this.resetTestCase()
          })
          .catch(() => {})
      } else {
        this.problem.spj = !this.problem.spj
      }
    },
    querySearch(queryString, cb) {
      api
        .getProblemTagList({ keyword: queryString })
        .then((res) => {
          let tagList = []
          for (let tag of res.data.data) {
            tagList.push({ value: tag.name })
          }
          cb(tagList)
        })
        .catch(() => {})
    },
    resetTestCase() {
      this.testCaseUploaded = false
      this.problem.test_case_score = []
      this.problem.test_case_id = ""
    },
    addTag() {
      let inputValue = this.tagInput
      if (inputValue) {
        this.problem.tags.push(inputValue)
      }
      this.inputVisible = false
      this.tagInput = ""
    },
    closeTag(tag) {
      this.problem.tags.splice(this.problem.tags.indexOf(tag), 1)
    },
    addSample() {
      this.problem.samples.push({ input: "", output: "" })
    },
    deleteSample(index) {
      this.problem.samples.splice(index, 1)
    },
    uploadSucceeded(response) {
      if (response.error) {
        this.$error(response.data)
        return
      }
      let fileList = response.data.info
      for (let file of fileList) {
        file.score = (100 / fileList.length).toFixed(0)
        if (!file.output_name && this.problem.spj) {
          file.output_name = "-"
        }
      }
      this.problem.test_case_score = fileList
      this.testCaseUploaded = true
      this.problem.test_case_id = response.data.id
    },
    uploadFailed() {
      this.$error("Upload failed")
    },
    checkDuplicateProblemId() {
      let editStatus = false
      this.$route.path.split("/").map((value) => {
        if (value === "edit") {
          editStatus = true
        }
      })

      if (!this.problem._id) {
        this.$error("Problem ID is required")
        return
      }
      let data = {
        _id: this.problem._id,
        edit_status: editStatus,
        problem_id: this.problem.id,
      }

      api
        .checkDuplicateProblemId(data)
        .then((res) => {})
        .catch(() => {})
    },
    compileSPJ() {
      let data = {
        id: this.problem.id,
        spj_code: this.problem.spj_code,
        spj_language: this.problem.spj_language,
      }
      this.loadingCompile = true
      api.compileSPJ(data).then(
        (res) => {
          this.loadingCompile = false
          this.problem.spj_compile_ok = true
          this.error.spj = ""
        },
        (err) => {
          this.loadingCompile = false
          this.problem.spj_compile_ok = false
          const h = this.$createElement
          this.$msgbox({
            title: "Compile Error",
            type: "error",
            message: h("pre", err.data.data),
            showCancelButton: false,
            closeOnClickModal: false,
            customClass: "dialog-compile-error",
          })
        },
      )
    },
    submit() {
      if (this.problem.field == null) {
        this.$error("Field is required")
        return
      }
      if (!this.problem.samples.length) {
        this.$error("Sample is required")
        return
      }
      for (let sample of this.problem.samples) {
        if (!sample.input || !sample.output) {
          this.$error("Sample input and output is required")
          return
        }
      }
      if (!this.problem.tags.length) {
        this.error.tags = "Please add at least one Tag"
        this.$error(this.error.tags)
        return
      }
      if (this.problem.spj) {
        if (!this.problem.spj_code) {
          this.error.spj = "Spj code is required"
          this.$error(this.error.spj)
        } else if (!this.problem.spj_compile_ok) {
          this.error.spj = "SPJ code has not been successfully compiled"
        }
        if (this.error.spj) {
          this.$error(this.error.spj)
          return
        }
      }
      if (!this.problem.languages.length) {
        this.error.languages = "Please choose at least one language for problem"
        this.$error(this.error.languages)
        return
      }
      if (!this.testCaseUploaded) {
        this.error.testCase = "Test case is not uploaded yet"
        this.$error(this.error.testCase)
        return
      }
      if (this.problem.rule_type === "OI") {
        for (let item of this.problem.test_case_score) {
          try {
            if (parseInt(item.score) <= 0) {
              this.$error("Invalid test case score")
              return
            }
          } catch (e) {
            this.$error("Test case score must be an integer")
            return
          }
        }
      }
      this.problem.languages = this.problem.languages.sort()
      this.problem.template = {}
      for (let k in this.template) {
        if (this.template[k].checked) {
          this.problem.template[k] = this.template[k].code
        }
      }
      let funcName = {
        "create-problem": "createProblem",
        "edit-problem": "editProblem",
        "create-contest-problem": "createContestProblem",
        "edit-contest-problem": "editContestProblem",
      }[this.routeName]
      // edit contest problem 时, contest_id会被后来的请求覆盖掉
      if (funcName === "editContestProblem") {
        this.problem.contest_id = this.contest.id
      }
      api[funcName](this.problem)
        .then((res) => {
          if (
            this.routeName === "create-contest-problem" ||
            this.routeName === "edit-contest-problem"
          ) {
            this.$router.push({
              name: "contest-problem-list",
              params: { contestId: this.$route.params.contestId },
            })
          } else {
            this.$router.push({ name: "problem-list" })
          }
        })
        .catch(() => {})
    },
    resetProblem() {
      this.problem = JSON.parse(JSON.stringify(this.reProblem))
      this.template = {}
      this.testCaseUploaded = false
      this.inputVisible = false
      this.tagInput = ""
      this.spjMode = ""
      this.error = {
        tags: "",
        spj: "",
        languages: "",
        testCase: "",
      }
    },
  },
}
</script>

<style lang="less" scoped>
.problem {
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

  .tab-headers {
    display: flex;
    margin-bottom: -1px;
    z-index: 10;
    position: relative;
  }

  .tab-header {
    padding: 10px 25px;
    cursor: pointer;
    border-radius: 5px 5px 0 0;
    border: 1px solid transparent;
    border-bottom: 1px solid #dcdfe6;
    background-color: #f5f7fa;
    color: #909399;
    transition: all 0.3s;
    font-size: 14px;
    font-weight: 500;

    &.active {
      font-weight: 700;
      color: #303133;
      background-color: #ffffff;
      border: 1px solid #dcdfe6;
      border-bottom: 1px solid #ffffff;
      margin-bottom: -1px;
    }

    &:hover:not(.active) {
      color: #409eff;
      background-color: #f5f7fa;
    }
  }

  .tab-content {
    overflow-y: auto;
    border: 1px solid #dcdfe6;
    border-radius: 5px;
    border-top-left-radius: 0;
    padding: 30px 30px 0px 25px;
    background-color: #ffffff;
    min-height: 400px;
  }

  .meta-data {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
    // 요소를 양쪽 끝으로 정렬
    justify-content: space-between;
    width: 100%;
    align-items: flex-start;
  }

  .language-field {
    display: flex;
    flex-direction: column;
    text-align: left;

    .language-container {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    .language-btn {
      padding: 8px 16px;
      border: 1px solid #dcdfe6;
      border-radius: 4px;
      cursor: pointer;
      background-color: #ffffff;
      display: flex;
      align-items: center;
      font-size: 14px;
      color: #606266;
      user-select: none;

      &:hover {
        border-color: #67c23a;
        color: #67c23a;
      }

      &.active {
        border-color: #67c23a;
        background-color: #f0f9eb;
        color: #67c23a;
        font-weight: bold;
      }

      .empty-box {
        display: inline-block;
        box-sizing: border-box;
        width: 16px;
        height: 16px;
        border: 1px solid #dcdfe6;
        border-radius: 2px;
        margin-right: 6px;
        background-color: #ffffff;
      }

      .check-icon {
        display: inline-block;
        width: 16px;
        text-align: center;
        color: #67c23a;
        font-weight: bold;
        margin-right: 6px;
      }

      .lang-text {
        display: inline-flex;
        flex-direction: column;
        align-items: center;
        &::after {
          content: attr(data-text);
          font-weight: bold;
          height: 0;
          visibility: hidden;
          overflow: hidden;
          user-select: none;
          pointer-events: none;
        }
      }
    }
  }
}

.section-divider {
  border-bottom: 1px solid #dcdfe6;
  padding-bottom: 18px;
  margin-bottom: 4px;
}

.sample-box {
  margin-top: 20px;
}

.sample-item {
  margin-bottom: 20px;

  .sample-content {
    display: flex;
    gap: 20px;

    .sample-input,
    .sample-output {
      flex: 1;
      display: flex;
      flex-direction: column;
    }

    .custom-label-with-btn {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .custom-label {
        margin-bottom: 0;
      }
    }

    .delete-btn {
      background-color: #ffffff;
      border: 1px solid #fbc4c4;
      border-radius: 4px;
      color: #f56c6c;
      cursor: pointer;
      font-size: 13px;
      padding: 5px 12px;
      display: flex;
      align-items: center;
      gap: 5px;
      transition: all 0.2s ease;

      i {
        font-size: 14px;
      }

      &:hover {
        background-color: #fef0f0;
        border-color: #f56c6c;
        color: #f56c6c;
        box-shadow: 0 2px 4px rgba(245, 108, 108, 0.1);
      }

      &:active {
        background-color: #fbdada;
      }
    }

    .sample-textarea {
      /deep/ .el-textarea__inner {
        font-family: inherit;
        font-size: 14px;
        line-height: 1.6;
        border: 1px solid #dcdfe6;
        border-radius: 8px;
        padding: 15px;
        background-color: #f9fafb;
        transition: all 0.3s ease;
        min-height: 180px;
        resize: none;

        &:focus {
          background-color: #ffffff;
          border-color: #409eff;
          box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
          outline: 0;
        }

        &::placeholder {
          color: #c0c4cc;
        }
      }
    }
  }
}

.add-sample-btn {
  display: flex;
  justify-content: center;

  .add-samples {
    background-color: #ffffff;
    border: 1px dashed #409eff;
    border-radius: 8px;
    color: #409eff;
    cursor: pointer;
    font-size: 12px;
    padding: 10px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.3s ease;
    font-weight: 600;

    &:hover {
      background-color: #ecf5ff;
    }

    &:active {
      background-color: #d9ecff;
    }
  }
}

.detailCard {
  border: none;
  flex: 1;
  height: max-content;
  background-color: var(--bg-color);

  .header-input-container {
    display: flex;
    align-items: center;
    gap: 50px;

    border-bottom: 1px solid #dcdfe6;
    padding-bottom: 18px;

    .header-title {
      display: flex;
      gap: 20px;
      align-items: flex-start;

      .custom-label {
        line-height: 1.4;
        padding: 0;
        margin-top: 5px;
      }
    }

    .header-question-id {
      display: flex;
      gap: 20px;
      align-items: flex-start;

      .custom-label {
        line-height: 1.4;
        padding: 0;
        margin-top: 5px;
      }
    }
  }

  .required-asterisk {
    color: #f56c6c;
    margin-right: 4px;
  }

  // 헤더 전용 공통 스타일
  .header-common-style() {
    /deep/ .el-input__inner {
      font-size: 16px;
      font-weight: 700;
      color: var(--ps-content-title-color);
      border: none;
      border-bottom: 1px solid var(--border-color);
      border-radius: 0;
      height: 30px;
      padding-left: 0;
      padding-right: 0;
      line-height: normal;
      background-color: transparent;
      box-shadow: none;

      &:focus {
        border-bottom: 1px solid #409eff;
      }
    }
  }

  /deep/ .el-form-item__content {
    margin-left: 0 !important;
  }

  .id_input {
    width: 80px;
    .header-common-style();

    /deep/ .el-input__inner {
      text-align: left;
    }
  }

  .title_input {
    width: 500px;
    .header-common-style();
  }

  .limit-input {
    width: 130px;
  }

  .test-case-settings {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    align-items: flex-start;
    margin-bottom: 20px;

    .settings-row {
      display: flex;
      width: 100%;
      justify-content: space-between;
      gap: 20px;
    }

    .left-settings {
      flex: 0 0 auto;
    }

    .right-settings {
      display: flex;
      flex-wrap: wrap;
      gap: 20px;
      flex: 1;
      justify-content: flex-end;
    }

    .setting-item {
      flex: 0 0 auto;
    }

    .table-container {
      flex: 0 0 100%;
      width: 100%;
    }

    .segmented-control {
      display: inline-flex;
      background-color: #f1f5f9;
      padding: 4px;
      border-radius: 8px;
      gap: 2px;
      margin-top: 10px;
    }

    .custom-radio {
      cursor: pointer;
      display: inline-flex;
      margin: 0;

      input[type="radio"] {
        display: none;
      }

      .radio-text {
        display: inline-block;
        padding: 6px 18px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        color: #64748b;
        transition: all 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
        user-select: none;
      }

      input[type="radio"]:checked + .radio-text {
        background-color: #ffffff;
        color: #0f172a;
        box-shadow:
          0 1px 3px rgba(0, 0, 0, 0.1),
          0 1px 2px rgba(0, 0, 0, 0.06);
      }

      input[type="radio"]:disabled + .radio-text {
        opacity: 0.5;
        cursor: not-allowed;
      }

      &:hover input[type="radio"]:not(:checked):not(:disabled) + .radio-text {
        color: #334155;
      }
    }

    .col-label {
      display: flex;
      flex-direction: column;
    }

    .error-msg {
      color: #f56c6c;
      font-size: 12px;
      margin-top: 4px;
    }

    .upload-container {
      margin-top: 10px;
    }

    .upload-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 6px 14px;
      background-color: #eff6ff;
      color: #1d4ed8;
      border: 1px solid #bfdbfe;
      border-radius: 5px;
      font-size: 13px;
      font-weight: 500;
      letter-spacing: 0.2px;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);

      i {
        margin-right: 6px;
        font-size: 14px;
        color: #3b82f6;
        transition: color 0.2s ease;
      }

      &:hover {
        background-color: #dbeafe;
        border-color: #93c5fd;
        color: #1e40af;
        box-shadow:
          0 2px 4px -1px rgba(59, 130, 246, 0.1),
          0 1px 2px -1px rgba(59, 130, 246, 0.06);
        transform: translateY(-1px);

        i {
          color: #2563eb;
        }
      }

      &:active {
        background-color: #bfdbfe;
        border-color: #60a5fa;
        transform: translateY(0);
        box-shadow: none;
        transition: none;
      }
    }

    .custom-input {
      padding: 8px 12px;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      margin-top: 10px;
      font-size: 14px;
      color: #334155;
      background-color: #ffffff;
      transition: all 0.2s ease;

      &:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
        outline: none;
      }
    }

    .score-input {
      padding: 8px 12px;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      width: 100px;
      color: #334155;
      font-size: 14px;
      font-weight: 500;
      transition: all 0.2s ease;

      &:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
        outline: none;
      }

      &:disabled {
        background-color: #f8fafc;
        color: #94a3b8;
        cursor: not-allowed;
      }
    }

    .template-container {
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-top: 10px;
    }

    .custom-table {
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      text-align: left;
      margin-top: 15px;
      border-radius: 8px;
      border: 1px solid #e2e8f0;
      overflow: hidden;
      table-layout: fixed;

      thead {
        background-color: #f5f7fa !important;
      }

      th {
        padding: 12px 16px;
        background-color: #f5f7fa !important;
        color: #475569;
        font-weight: 600;
        font-size: 13px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        border-bottom: 1px solid #e2e8f0;
      }

      tr {
        background-color: #ffffff;

        &:last-child td {
          border-bottom: none;
        }
      }

      td {
        padding: 12px 16px;
        color: #334155;
        font-size: 14px;
        border-bottom: 1px dashed #cbd5e1;
        vertical-align: middle;
        word-break: break-all;
      }

      .empty-table-data {
        padding: 48px;
        text-align: center;
        color: #94a3b8;
        font-size: 14px;
        background-color: #ffffff;
      }
    }
  }
}

.template-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 12px;
}

.custom-checkbox {
  display: inline-flex;
  cursor: pointer;
  user-select: none;
  align-self: flex-start;
  width: fit-content;

  input[type="checkbox"] {
    display: none !important;
  }

  .checkbox-text {
    display: inline-flex;
    align-items: center;
    padding: 8px 16px;
    background-color: #ffffff;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    color: #606266;
    font-size: 14px;
    transition: all 0.2s ease;
  }

  .empty-box {
    display: inline-block;
    box-sizing: border-box;
    width: 16px;
    height: 16px;
    border: 1px solid #dcdfe6;
    border-radius: 2px;
    margin-right: 6px;
    background-color: #ffffff;
  }

  .check-icon {
    display: inline-block;
    width: 16px;
    text-align: center;
    color: #67c23a;
    font-weight: bold;
    margin-right: 6px;
  }

  .lang-text {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    &::after {
      content: attr(data-text);
      font-weight: bold;
      height: 0;
      visibility: hidden;
      overflow: hidden;
      user-select: none;
      pointer-events: none;
    }
  }

  &:hover .checkbox-text {
    border-color: #67c23a;
    color: #67c23a;
  }

  input[type="checkbox"]:checked + .checkbox-text {
    color: #67c23a;
    border-color: #67c23a;
    background-color: #f0f9eb;
    font-weight: bold;
  }

  &.is-disabled-tab {
    opacity: 0.45;
    cursor: not-allowed;

    .checkbox-text {
      pointer-events: none;
    }

    &:hover .checkbox-text {
      border-color: #dcdfe6;
      color: #606266;
    }
  }
}

.template-editor-area {
  animation: fadeIn 0.3s ease;
}

.template-editor-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 4px 4px 0 0;

  .editor-lang-badge {
    font-size: 12px;
    font-weight: 700;
    color: #ffffff;
    background-color: #67c23a;
    padding: 2px 8px;
    border-radius: 3px;
    letter-spacing: 0.03em;
  }

  .editor-lang-label {
    font-size: 12px;
    color: #94a3b8;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.template-editor {
  overflow: hidden;
  transition: opacity 0.3s ease;
}

.is-disabled {
  opacity: 0.6;
  pointer-events: none;
  filter: grayscale(100%);
  transition: opacity 0.3s ease;
}

.spj-toggle {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;

  input[type="checkbox"] {
    display: none;
  }

  .spj-toggle-track {
    position: relative;
    width: 44px;
    height: 24px;
    background-color: #dcdfe6;
    border-radius: 12px;
    transition: background-color 0.25s ease;
    flex-shrink: 0;

    &::after {
      content: "";
      position: absolute;
      top: 3px;
      left: 3px;
      width: 18px;
      height: 18px;
      background-color: #ffffff;
      border-radius: 50%;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
      transition: transform 0.25s ease;
    }
  }

  .spj-toggle-track.is-on {
    background-color: #409eff;

    &::after {
      transform: translateX(20px);
    }
  }

  .spj-toggle-label {
    font-size: 14px;
    color: #606266;
  }
}

.spj-lang-label {
  font-size: 14px;
  color: #606266;
  margin-right: 10px;
}

.spj-radio-group {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-right: 12px;
}

.spj-editor-controls {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
  margin-bottom: 10px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  background-color: #f0f9eb;
  border: 1px solid #b3e19d;
  border-radius: 20px;
  font-size: 13px;
  color: #529b2e;
  font-weight: 500;

  .tag-chip-close {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 16px;
    background: none;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    font-size: 14px;
    color: #529b2e;
    padding: 0;
    line-height: 1;
    opacity: 0.6;
    transition: opacity 0.2s;

    &:hover {
      opacity: 1;
      background-color: #b3e19d;
    }
  }
}

.tag-input {
  padding: 4px 10px;
  border: 1px solid #dcdfe6;
  border-radius: 20px;
  font-size: 13px;
  outline: none;
  width: 100px;
  transition: border-color 0.2s;

  &:focus {
    border-color: #67c23a;
  }
}

.tag-add-btn {
  padding: 4px 12px;
  background: none;
  border: 1px dashed #dcdfe6;
  border-radius: 20px;
  font-size: 13px;
  color: #909399;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: #67c23a;
    color: #67c23a;
  }
}

.spj-radio-btn {
  display: inline-flex;
  align-items: center;
  padding: 5px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  color: #606266;
  transition: all 0.2s;
  user-select: none;

  input[type="radio"] {
    display: none;
  }

  &:hover {
    border-color: #67c23a;
    color: #67c23a;
  }

  &.active {
    border-color: #67c23a;
    background-color: #f0f9eb;
    color: #67c23a;
    font-weight: bold;
  }
}

.custom-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;

  &::placeholder {
    color: #c0c4cc;
  }

  &:focus {
    border-color: #409eff;
  }
}

.spj-compile-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background-color: #409eff;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background-color: #66b1ff;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.toggle-row {
  display: flex;
  gap: 32px;
  align-items: center;
}

.toggle-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-label {
  font-size: 14px;
  color: #606266;
  user-select: none;
}

.custom-label {
  font-size: 14px;
  color: #606266;
  line-height: 40px;
  padding: 0 0 10px;
  display: inline-block;
  font-weight: 700;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 22px;
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

/deep/ .simditor {
  border-radius: 8px;
  border: 1px solid #dcdfe6;
  overflow: hidden;

  .simditor-toolbar {
    border-radius: 8px 8px 0 0;
    border-bottom: 1px solid #dcdfe6;
    background: #f5f7fa;
  }

  .simditor-body {
    min-height: 200px;
    padding: 15px;
    border-radius: 0 0 8px 8px;
  }
}
</style>

<style>
.problem-tag-poper {
  width: 200px !important;
}

.dialog-compile-error {
  width: auto;
  max-width: 80%;
  overflow-x: scroll;
}

.duplicate-check-btn {
  margin-top: 2px;
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  height: 28px;
  box-sizing: border-box;
  font-size: 12px;
  font-weight: 500;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
  background: #ffffff;
  color: #409eff;
  border: 1px solid #409eff;
  transition: all 0.2s ease;

  &:hover {
    background: #ecf5ff;
    border-color: #66b1ff;
    color: #66b1ff;
  }

  &:active {
    background: #d9ecff;
  }
}

.difficulty-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.difficulty-select {
  width: 110px;
}

.field-select {
  width: 100px;
}

.field-icon {
  margin-right: 5px;
  margin-left: 2px;
}

.source-icon {
  margin-right: 5px;
}

.source-custom-input {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;

  &::placeholder {
    color: #c0c4cc;
  }

  &:focus {
    border-color: #409eff;
  }
}

.source-input {
  width: 200px;
}

.spj-toggle-row {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.spj-label {
  margin-bottom: 0;
  flex: 1;
}

.submit-row {
  display: flex;
  justify-content: flex-end;
}

.col-30 {
  width: 30%;
}

.col-40 {
  width: 40%;
}
</style>
