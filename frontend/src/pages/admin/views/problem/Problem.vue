<template>
  <div class="problem">
    <div class="tab-headers">
      <div
        class="tab-header"
        :class="{ active: activeTab === 'edit' }"
        @click="activeTab = 'edit'"
      >
        {{ $t("m.Question_Creation") }}
      </div>
      <div
        class="tab-header"
        :class="{ active: activeTab === 'preview' }"
        @click="activeTab = 'preview'"
      >
        Preview
      </div>
    </div>
    <div class="tab-content">
      <div v-show="activeTab === 'edit'" class="detailCard">
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
            <el-button
              class="duplicate-btn"
              type="primary"
              size="small"
              @click="checkDuplicateProblemId"
            >
              {{ $t("m.Check_ID_Duplication") }}
            </el-button>
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
          <div class="form-group difficulty-field">
            <!-- 난이도 글자 -->
            <label class="custom-label"
              ><span class="required-asterisk">*</span
              >{{ $t("m.Difficulty") }}</label
            >
            <div style="display: flex; align-items: center; gap: 10px">
              <el-select
                class="difficulty-select"
                size="small"
                :placeholder="$t('m.Difficulty')"
                v-model="problem.difficulty"
                style="width: 150px"
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

              <div class="headerDetailBtn">
                <Icon type="ios-pie" color="#F8B193" />
                영역
              </div>
              <div class="headerDetailBtn">
                <Icon type="ios-pricetag" color="#FF9F9F" />
                태그
              </div>
            </div>
          </div>

          <!-- Commented out old Field/Tag inputs as requested -->
          <!-- <div class="form-group category-field">
              <label class="custom-label"><span class="required-asterisk">*</span>{{ $t('m.Field') }}</label>
              <el-select class="difficulty-select" size="small" :placeholder="$t('m.Field')" v-model="problem.field">
                <el-option :label="$t('m.Field_Impl')" :value="0"></el-option>
                <el-option :label="$t('m.Field_Math')" :value="1"></el-option>
                <el-option :label="$t('m.Field_DataStructure')" :value="2"></el-option>
                <el-option :label="$t('m.Field_Search')" :value="3"></el-option>
                <el-option :label="$t('m.Field_Sorting')" :value="4"></el-option>
                <el-option :label="$t('m.Field_Algorithm')" :value="5"></el-option>
              </el-select>
            </div>
            <div class="form-group tag-field">
              <label class="custom-label"><span class="required-asterisk">*</span>{{ $t('m.Tag') }}</label>
              <div class="tags-container">
                <span class="tags">
                  <el-tag v-for="tag in problem.tags" :closable="true" :close-transition="false" :key="tag"
                    type="success" @close="closeTag(tag)">{{ tag }}</el-tag>
                </span>
                <el-autocomplete v-if="inputVisible" size="mini" class="input-new-tag" popper-class="problem-tag-poper"
                  v-model="tagInput" :trigger-on-focus="false" @keyup.enter.native="addTag" @select="addTag"
                  :fetch-suggestions="querySearch">
                </el-autocomplete>
                <el-button class="button-new-tag" v-else size="small" @click="inputVisible = true">+ {{
                  $t("m.New_Tag")
                }}</el-button>
              </div>
              <div class="el-form-item__error" v-if="error.tags">
                {{ error.tags }}
              </div>
            </div> -->
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
                  {{ lang.name }}
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
              type="Number"
              :placeholder="$t('m.Memory_limit')"
              v-model="problem.memory_limit"
            ></el-input>
          </div>
        </div>

        <!-- 공개 / 제출 공유 여부 -->
        <el-row :gutter="20">
          <el-col :span="4">
            <el-form-item :label="$t('m.Visible')">
              <el-switch
                v-model="problem.visible"
                active-text=""
                inactive-text=""
              >
              </el-switch>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item :label="$t('m.ShareSubmission')">
              <el-switch
                v-model="problem.share_submission"
                active-text=""
                inactive-text=""
              >
              </el-switch>
            </el-form-item>
          </el-col>
        </el-row>
        <!-- 힌트 -->
        <el-form-item style="margin-top: 20px" :label="$t('m.Hint')">
          <Simditor v-model="problem.hint" placeholder=""></Simditor>
        </el-form-item>
        <!-- 코드 템플릿 -->
        <el-form-item :label="$t('m.Code_Template')">
          <el-row>
            <el-col :span="24" v-for="(v, k) in template" :key="'template' + k">
              <el-form-item>
                <el-checkbox v-model="v.checked">{{ k }}</el-checkbox>
                <div v-if="v.checked">
                  <code-mirror v-model="v.code" :mode="v.mode"></code-mirror>
                </div>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form-item>
        <!-- 스페셜 저지 -->
        <el-form-item :label="$t('m.Special_Judge')" :error="error.spj">
          <el-col :span="24">
            <el-checkbox
              v-model="problem.spj"
              @click.native.prevent="switchSpj()"
              >{{ $t("m.Use_Special_Judge") }}</el-checkbox
            >
          </el-col>
        </el-form-item>
        <!-- 스페셜 저지 코드 -->
        <el-form-item v-if="problem.spj">
          <Accordion :title="$t('m.Special_Judge_Code')">
            <template slot="header">
              <span>{{ $t("m.SPJ_language") }}</span>
              <el-radio-group v-model="problem.spj_language">
                <el-tooltip
                  class="spj-radio"
                  v-for="lang in allLanguage.spj_languages"
                  :key="lang.name"
                  effect="dark"
                  :content="lang.description"
                  placement="top-start"
                >
                  <el-radio :label="lang.name">{{ lang.name }}</el-radio>
                </el-tooltip>
              </el-radio-group>
              <el-button
                type="primary"
                size="small"
                icon="el-icon-fa-random"
                @click="compileSPJ"
                :loading="loadingCompile"
              >
                {{ $t("m.Compile") }}
              </el-button>
            </template>
            <code-mirror
              v-model="problem.spj_code"
              :mode="spjMode"
            ></code-mirror>
          </Accordion>
        </el-form-item>

        <!-- 종류 / 테케 / 입출력모드 / 배점 설정 -->
        <el-row :gutter="20">
          <el-col :span="4">
            <el-form-item :label="$t('m.Type')">
              <el-radio-group
                v-model="problem.rule_type"
                :disabled="disableRuleType"
              >
                <el-radio label="ACM">ACM</el-radio>
                <el-radio label="OI">OI</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item :label="$t('m.TestCase')" :error="error.testcase">
              <el-upload
                action="/api/admin/test_case"
                name="file"
                :data="{ spj: problem.spj }"
                :show-file-list="true"
                :on-success="uploadSucceeded"
                :on-error="uploadFailed"
              >
                <el-button
                  size="small"
                  type="primary"
                  icon="el-icon-fa-upload"
                  >{{ $t("m.Button_Choose_File") }}</el-button
                >
              </el-upload>
            </el-form-item>
          </el-col>

          <el-col :span="6">
            <el-form-item :label="$t('m.IOMode')">
              <el-radio-group v-model="problem.io_mode.io_mode">
                <el-radio label="Standard IO">Standard IO</el-radio>
                <el-radio label="File IO">File IO</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>

          <el-col :span="4" v-if="problem.io_mode.io_mode == 'File IO'">
            <el-form-item :label="$t('m.InputFileName')" required>
              <el-input type="text" v-model="problem.io_mode.input"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="4" v-if="problem.io_mode.io_mode == 'File IO'">
            <el-form-item :label="$t('m.OutputFileName')" required>
              <el-input type="text" v-model="problem.io_mode.output"></el-input>
            </el-form-item>
          </el-col>

          <el-col :span="24">
            <el-table :data="problem.test_case_score" style="width: 100%">
              <el-table-column prop="input_name" :label="$t('m.Input')">
              </el-table-column>
              <el-table-column prop="output_name" :label="$t('m.Output')">
              </el-table-column>
              <el-table-column prop="score" :label="$t('m.Score')">
                <template slot-scope="scope">
                  <el-input
                    size="small"
                    :placeholder="$t('m.Score')"
                    v-model="scope.row.score"
                    :disabled="problem.rule_type !== 'OI'"
                  >
                  </el-input>
                </template>
              </el-table-column>
            </el-table>
          </el-col>
        </el-row>
        <!-- 출처 -->
        <el-form-item :label="$t('m.Source')">
          <el-input
            :placeholder="$t('m.Source')"
            v-model="problem.source"
          ></el-input>
        </el-form-item>
        <!-- 제출 -->
        <save @click.native="submit()">Save</save>
      </div>

      <div v-show="activeTab === 'preview'" class="preview-content">
        <!-- Preview content will be here -->
        <div class="empty-preview" style="text-align: center; padding: 50px">
          PREVIEW
        </div>
      </div>
    </div>
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
      activeTab: "edit",
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
      this.problem = this.reProblem
    },
    "problem.languages"(newVal) {
      let data = {}
      // use deep copy to avoid infinite loop
      let languages = JSON.parse(JSON.stringify(newVal)).sort()
      for (let item of languages) {
        if (this.template[item] === undefined) {
          let langConfig = this.allLanguage.languages.find((lang) => {
            return lang.name === item
          })
          if (this.problem.template[item] === undefined) {
            data[item] = {
              checked: false,
              code: langConfig.config.template,
              mode: langConfig.content_type,
            }
          } else {
            data[item] = {
              checked: true,
              code: this.problem.template[item],
              mode: langConfig.content_type,
            }
          }
        } else {
          data[item] = this.template[item]
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

      .check-icon {
        margin-right: 5px;
        font-weight: bold;
      }
    }
  }
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
    // margin-bottom: 20px;
    border-bottom: 1px solid #dcdfe6;
    padding-bottom: 18px;

    .header-title {
      display: flex;
      gap: 20px;
      align-items: center;
    }

    .header-question-id {
      display: flex;
      gap: 20px;
      align-items: center;
    }

    .duplicate-btn {
      white-space: nowrap;
    }
  }

  .required-asterisk {
    color: #f56c6c;
    margin-right: 4px;
  }

  // 공통 스타일 Mixin
  .common-input-style() {
    /deep/ .el-input__inner {
      font-size: 20px;
      font-weight: 700;
      color: var(--ps-content-title-color);
      border: none;
      border-bottom: 1px solid var(--border-color);
      border-radius: 0;
      height: auto;
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

  .common-input-style() {
    /deep/ .el-input__inner {
      font-size: 20px;
      font-weight: 700;
      color: var(--ps-content-title-color);
      border: none;
      border-bottom: 1px solid var(--border-color);
      border-radius: 0;
      height: auto;
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
    .common-input-style();

    /deep/ .el-input__inner {
      text-align: left;
    }
  }

  .title_input {
    width: 500px;
    .common-input-style();
  }
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
  margin-bottom: 22px; // Match standard el-form-item margin
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
</style>
