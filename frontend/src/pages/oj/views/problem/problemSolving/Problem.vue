<template>
  <div class="flex-container">
    <splitpanes vertical style="height: calc(100vh - 50px)">
      <pane :size="50">
        <div class="left-pain-wrapper">
          <div class="tab-headers">
            <div class="tab-header"
              :class="{ active: leftPainActiveTab === 'problem' }"
              @click="leftPainActiveTab = 'problem'">
              문제 설명
            </div>
            <div class="tab-header"
              :class="{ active: leftPainActiveTab === 'submission' }"
              @click="leftPainActiveTab = 'submission'">
              제출 현황
            </div>
          </div>
          <div class="tab-content">
            <ProblemDetailFlexibleContainer
              v-if="leftPainActiveTab === 'problem'"
              :problem="problem"
              :contestID="contestID"
            />
            <SubmissionList
              v-if="leftPainActiveTab === 'submission'"
              :problemID="problemID"
              :contestID="contestID"
              :theme.sync="theme"
            />
          </div>
        </div>
      </pane>
      <pane min-size="30" :size="50">
        <CodeEditorHeader @create-submission="submitCode"
                          @change-language="changeLanguage"
                          :problem="problem"
                          :language.sync="language"
                          :statusVisible="statusVisible"
                          :contestID="contestID"
                          :result="result"
                          :submissionId="submissionId"
                          :isSubmitting="submitting"/>
        <CodeEditor :value.sync="code"
                        :languages="problem.languages"
                        :language="language"
                        :cursorPos.sync="cursorPos"
                        :theme.sync="theme"
                        ref="myCm"/>
        <StickyLnCol :cursorPos="cursorPos"/>
      </pane>
    </splitpanes>
  </div>
</template>

<script>
import {mapGetters, mapActions} from 'vuex'
import {types} from '../../../../../store'
import storage from '@/utils/storage'
import {FormMixin} from '@oj/components/mixins'
import {JUDGE_STATUS, CONTEST_STATUS, buildProblemCodeKey} from '@/utils/constants'
import api from '@oj/api'
import {Pane, Splitpanes} from "splitpanes";
import 'splitpanes/dist/splitpanes.css'
import FieldCategoryBox from "../../../components/FieldCategoryBox.vue";
import CustomIconBtn from "../../../components/buttons/CustomIconBtn.vue";
import {DIFFICULTY_MAP, FIELD_MAP} from "../../../../../utils/constants";
import CodeEditorHeader from "./problemSolvingComponent/CodeEditorHeader.vue";
import SubmissionStatus from "./problemSolvingComponent/SubmissionStatus.vue";
import ProblemDetailFlexibleContainer from "./problemSolvingComponent/ProblemDetailFlexibleContainer.vue";
import StickyLnCol from "./problemSolvingComponent/StickyLnCol.vue";
import CodeEditor from "./problemSolvingComponent/CodeEditor.vue"
import SubmissionList from './problemSolvingComponent/SubmissionList.vue'

const filtedStatus = ['-1', '-2', '0', '1', '2', '3', '4', '8']

export default {
  name: 'Problem',
  components: {
    StickyLnCol,
    CodeEditor,
    SubmissionStatus,
    CodeEditorHeader,
    ProblemDetailFlexibleContainer,
    SubmissionList,
    CustomIconBtn,
    FieldCategoryBox,
    Splitpanes,
    Pane
  },
  mixins: [FormMixin],
  data() {
    return {
      cursorPos: {
        ln: 0,
        ch: 0
      },
      statusVisible: false,
      captchaRequired: false,
      graphVisible: false,
      submissionExists: false,
      captchaCode: '',
      captchaSrc: '',
      contestID: '',
      problemID: '',
      submitting: false,
      code: '',
      language: 'C++',
      languages: {
        type: Array,
        default: () => {
          return ['C', 'C++', 'Java', 'Python3']
        }
      },
      theme: false,
      submissionId: '',
      submitted: false,
      result: {
        result: 9
      },
      problem: {
        title: '',
        description: '',
        hint: '',
        my_status: '',
        template: {},
        languages: [],
        created_by: {
          username: ''
        },
        difficulty: '',
        tags: [],
        io_mode: {'io_mode': 'Standard IO'}
      },
      submission: {
        result: '0',
        code: '',
        info: {
          data: []
        },
        statistic_info: {
          time_cost: '',
          memory_cost: ''
        }
      },
      dropdown: {
        openFieldDropdown: false,
        openCategoryDropdown: false
      },
      modalCheck: false,
      leftPainActiveTab: 'problem',
      rightPainActiveTab: 'editor',
    }
  },
  beforeRouteEnter(to, from, next) {
    let problemCode = storage.get(buildProblemCodeKey(to.params.problemID, to.params.contestID))
    let psSettings = storage.get("ProblemSolvingSettings")
    if (psSettings) {
      next(vm => {
        vm.theme = psSettings.theme
      })
    } else {
      next()
    }
    if (problemCode) {
      next(vm => {
        vm.language = problemCode.language
        vm.code = problemCode.code
      })
    } else {
      next()
    }
  },
  mounted() {
    this.$store.commit(types.CHANGE_CONTEST_ITEM_VISIBLE, {menu: false})
    this.init()
    window.addEventListener('beforeunload', this.unLoadEvent);
  },
  beforeUnmount() {
    window.removeEventListener('beforeunload', this.unLoadEvent);
  },
  destroyed() {
    this.changeProblemSolvingState(false)
  },
  methods: {
    ...mapActions(['changeDomTitle', 'changeProblemSolvingState', 'changeProblemSolvingTheme']),
    init() {
      this.changeProblemSolvingState(true)
      this.$Loading.start()
      this.contestID = this.$route.params.contestID
      this.problemID = this.$route.params.problemID
      let func = this.$route.name === 'problem-details' ? 'getProblem' : 'getContestProblem'
      api[func](this.problemID, this.contestID).then(res => {
        this.$Loading.finish()
        let problem = res.data.data
        this.changeDomTitle({title: problem.title})
        api.submissionExists(problem.id).then(res => {
          this.submissionExists = res.data.data
        })
        problem.languages = problem.languages.sort()
        this.problem = problem

        if (this.code !== '') {
          return
        }
        // try to load problem template
        this.language = this.problem.languages[0]
        let template = this.problem.template
        if (template && template[this.language]) {
          this.code = template[this.language]
        }
        this.problem.difficulty = problem.difficulty
      }, () => {
        this.$Loading.error()
      })
    },
    unLoadEvent: function (event) {
      if (this.isLeaveSite) return;

      storage.set(buildProblemCodeKey(this.problem._id, this.contestID), {
        code: this.code,
        language: this.language,
      })

      storage.set("ProblemSolvingSettings", {
        theme: this.theme,
      })

      event.preventDefault();
      event.returnValue = '';
    },
    changeLanguage(newLang) {
      if (this.problem.template[newLang]) {
        if (this.code.trim() === '') {
          this.code = this.problem.template[newLang]
        }
      }
      this.language = newLang
      this.$refs.myCm.onLangChange(newLang)
    },
    modalOpen() {
      this.modalCheck = !this.modalCheck
    },
    handleRoute(route) {
      this.$router.push(route)
    },
    check() {
      alert(this.code)
    },
    onChangeTheme(newTheme) {
      this.theme = newTheme
    },
    checkSubmissionStatus() {
      // 使用setTimeout避免一些问题
      if (this.refreshStatus) {
        // 如果之前的提交状态检查还没有停止,则停止,否则将会失去timeout的引用造成无限请求
        clearTimeout(this.refreshStatus)
      }
      const checkStatus = () => {
        let id = this.submissionId
        api.getSubmission(id).then(res => {
          this.result = res.data.data
          if (Object.keys(res.data.data.statistic_info).length !== 0) {
            this.submitting = false
            this.submitted = false
            clearTimeout(this.refreshStatus)
            this.init()
          } else {
            this.refreshStatus = setTimeout(checkStatus, 2000)
          }
        }, res => {
          this.submitting = false
          clearTimeout(this.refreshStatus)
        })
      }
      this.refreshStatus = setTimeout(checkStatus, 2000)
    },
    submitCode() {
      if (this.code.trim() === '') {
        this.$error(this.$i18n.t('m.Code_can_not_be_empty'))
        return
      }
      this.submissionId = ''
      this.result = {result: 9}
      this.submitting = true
      let data = {
        problem_id: this.problem.id,
        language: this.language,
        code: this.code,
        contest_id: this.contestID
      }
      if (this.captchaRequired) {
        data.captcha = this.captchaCode
      }
      const submitFunc = (data, detailsVisible) => {
        this.statusVisible = true
        api.submitCode(data).then(res => {
          this.submissionId = res.data.data && res.data.data.submission_id
          // 定时检查状态
          this.submitting = false
          this.submissionExists = true
          if (!detailsVisible) {
            this.$Modal.success({
              title: this.$i18n.t('m.Success'),
              content: this.$i18n.t('m.Submit_code_successfully')
            })
            return
          }
          this.submitted = true
          this.checkSubmissionStatus()
        }, res => {
          this.getCaptchaSrc()
          if (res.data.data.startsWith('Captcha is required')) {
            this.captchaRequired = true
          }
          this.submitting = false
          this.statusVisible = false
        })
      }

      if (this.contestRuleType === 'OI' && !this.OIContestRealTimePermission) {
        if (this.submissionExists) {
          this.$Modal.confirm({
            title: '',
            content: '<h3>' + this.$i18n.t('m.You_have_submission_in_this_problem_sure_to_cover_it') + '<h3>',
            onOk: () => {
              // 暂时解决对话框与后面提示对话框冲突的问题(否则一闪而过）
              setTimeout(() => {
                submitFunc(data, false)
              }, 1000)
            },
            onCancel: () => {
              this.submitting = false
            }
          })
        } else {
          submitFunc(data, false)
        }
      } else {
        submitFunc(data, true)
      }
    },
  },
  computed: {
    FIELD_MAP() {
      return FIELD_MAP
    },
    DIFFICULTY_MAP() {
      return DIFFICULTY_MAP
    },
    ...mapGetters(['problemSubmitDisabled', 'contestRuleType', 'OIContestRealTimePermission', 'contestStatus', 'isDarkMode']),
    contest() {
      return this.$store.state.contest.contest
    },
    contestEnded() {
      return this.contestStatus === CONTEST_STATUS.ENDED
    },
    submissionStatus() {
      return {
        text: JUDGE_STATUS[this.result.result]['name'],
        color: JUDGE_STATUS[this.result.result]['color']
      }
    },
    submissionRoute() {
      if (this.contestID) {
        return {name: 'contest-submission-list', query: {problemID: this.problemID}}
      } else {
        return {name: 'submission-list', query: {problemID: this.problemID}}
      }
    }
  },
  beforeRouteLeave(to, from, next) {
    clearInterval(this.refreshStatus)
    this.$store.commit(types.CHANGE_CONTEST_ITEM_VISIBLE, {menu: true})
    storage.set(buildProblemCodeKey(this.problem._id, from.params.contestID), {
      code: this.code,
      language: this.language,
    })
    storage.set("ProblemSolvingSettings", {
      theme: this.theme,
    })
    next()
  },
  watch: {
    '$route'() {
      this.init()
    },
    isDarkMode(value) {
      let customTheme = value ? 'ayu-mirage' : 'github-light'
      this.$refs.myCm.toggleTheme(customTheme)
      this.theme = value
    }
  }
}
</script>

<style lang="less">
.flex-container {
  display: flex;
  overflow: hidden;

  #problem-main {
    flex: auto;
    margin-right: 18px;
  }

  #right-column {
    flex: none;
    width: 220px;
  }

}

#submit-code {
  margin-top: 20px;
  margin-bottom: 20px;

  .status {
    position: sticky;
    float: left;

    span {
      margin-right: 10px;
      margin-left: 10px;
    }
  }
}

.fl-right {
  float: right;
}

.splitpanes {
  background-color: var(--ps-background-color);
}

.splitpanes__pane {
  padding: 10px 10px;
  border-radius: 20px;
  background-color: var(--ps-background-color);
  color: var(--text-color);
}

.splitpanes--vertical > .splitpanes__splitter {
  min-width: 4px!important;
  margin-top: 350px;
  margin-bottom: 350px;
  align-items: center;
  background: rgba(200, 200, 200, 0.67);
  border-radius: 10px;
}

.splitpanes--vertical > .splitpanes__splitter:hover {
  background: rgba(143, 143, 143, 0.67);
}

.submitBtn {
  position: sticky;
  padding: 10px 15px;
  width: 120px;
  font-weight: 700;
  font-size: large;
  bottom: 40px;
  background-color: var(--custom-btn-hover-color);
  border-radius: 7px;
  cursor: pointer;
}

.left-pain-wrapper {
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background-color: var(--bg-color);
  height: 100%;
}

.tab-headers {
  display: flex;
  margin-bottom: 10px;
}

.tab-header {
  padding: 10px 20px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}

.tab-header.active {
  // border-bottom-color: #007bff;
  // color: #007bff;
  font-weight: 800;
}

.tab-header:hover {
  background-color: #f8f9fa;
}

.tab-content {
  height: calc(100% - 50px);
  overflow-y: auto;
}

</style>
