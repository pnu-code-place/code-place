<template>
  <div class="flex-container problem-solving-root">
    <transition name="popover-fade">
      <section
        v-if="settingsPopoverOpen"
        ref="settingsPopover"
        class="settings-popover"
        :style="settingsPopoverStyle"
        role="dialog"
        @click.stop
      >
        <div class="settings-popover-body">
          <div class="settings-row">
            <div class="settings-label">
              <i class="fas fa-search settings-label-icon"></i>
              <span>문제 확대</span>
            </div>
            <div class="settings-controls">
              <button
                type="button"
                class="settings-step-button"
                :disabled="problemZoomPercent <= minProblemZoom"
                aria-label="문제 확대 축소"
                @click="setProblemZoom(problemZoomPercent - problemZoomStep)"
              >
                <Icon type="minus-round" />
              </button>
              <span class="settings-control-value">
                {{ problemZoomPercent }}%
              </span>
              <button
                type="button"
                class="settings-step-button"
                :disabled="problemZoomPercent >= maxProblemZoom"
                aria-label="문제 확대 확대"
                @click="setProblemZoom(problemZoomPercent + problemZoomStep)"
              >
                <Icon type="plus-round" />
              </button>
            </div>
          </div>
          <div class="settings-row">
            <div class="settings-label">
              <span class="settings-label-icon settings-label-icon--text">
                Aa
              </span>
              <span>코드 크기</span>
            </div>
            <div class="settings-controls">
              <button
                type="button"
                class="settings-step-button"
                :disabled="codeFontSize <= minCodeFontSize"
                aria-label="코드 글자 축소"
                @click="setCodeFontSize(codeFontSize - codeFontSizeStep)"
              >
                <Icon type="minus-round" />
              </button>
              <span class="settings-control-value">
                {{ codeFontSize }}px
              </span>
              <button
                type="button"
                class="settings-step-button"
                :disabled="codeFontSize >= maxCodeFontSize"
                aria-label="코드 글자 확대"
                @click="setCodeFontSize(codeFontSize + codeFontSizeStep)"
              >
                <Icon type="plus-round" />
              </button>
            </div>
          </div>
        </div>
      </section>
    </transition>
    <section
      v-if="problemError.visible"
      class="problem-error-state"
      role="alert"
    >
      <div class="problem-error-card">
        <div class="problem-error-code">404</div>
        <h2>{{ problemError.title }}</h2>
        <p>{{ problemError.description }}</p>
        <div class="problem-error-actions">
          <button
            type="button"
            class="problem-error-button secondary"
            @click="goBackFromError"
          >
            이전 페이지
          </button>
          <button
            type="button"
            class="problem-error-button primary"
            @click="goProblemListFromError"
          >
            문제 목록
          </button>
        </div>
      </div>
    </section>
    <splitpanes v-else vertical style="height: calc(100vh - 50px)">
      <pane
        :size="50"
        :class="{ 'problem-pane-with-navigator': isContestProblem }"
      >
        <div
          class="left-pain-wrapper"
          :class="{ 'has-contest-navigator': isContestProblem }"
        >
          <ContestProblemNavigator
            v-if="isContestProblem"
            :contestID="contestID"
            :problemID="problemID"
            :problems="contestProblems"
            :loading="contestProblemsLoading"
            @navigate="goContestProblem"
          />
          <div class="problem-content-wrapper">
            <div class="tab-headers">
              <div
                class="tab-header"
                :class="{ active: leftPainActiveTab === 'problem' }"
                @click="leftPainActiveTab = 'problem'"
              >
                문제 설명
              </div>
              <div
                class="tab-header"
                :class="{ active: leftPainActiveTab === 'submission' }"
                @click="leftPainActiveTab = 'submission'"
              >
                제출 현황
              </div>
              <div
                v-if="!isContestProblem"
                class="tab-header tab-header--ask"
                :class="{ active: leftPainActiveTab === 'community' }"
                @click="leftPainActiveTab = 'community'"
              >
                <i class="fi fi-rr-map-marker-question"></i>
                질문하기
              </div>
            </div>
            <div v-if="showAskNudge" class="ask-nudge">
              <span class="ask-nudge-text">
                이 문제에서 막혔나요? 다른 사람에게 질문해보세요.
              </span>
              <div class="ask-nudge-actions">
                <button class="ask-nudge-go" @click="goAsk">질문하기 →</button>
                <button
                  class="ask-nudge-close"
                  aria-label="닫기"
                  @click="showAskNudge = false"
                >
                  ✕
                </button>
              </div>
            </div>
            <div class="tab-content">
              <ProblemDetailFlexibleContainer
                v-show="leftPainActiveTab === 'problem'"
                :problem="problem"
                :contestID="contestID"
                :loading="problemLoading"
                :problemZoomPercent="problemZoomPercent"
                @update:problemZoomPercent="problemZoomPercent = $event"
              />
              <SubmissionList
                v-if="isInitialized && !problemLoading && !problemError.visible"
                :key="`submission-${contestID || 'public'}-${problemID}`"
                v-show="leftPainActiveTab === 'submission'"
                :problemID="problemID"
                :contestID="contestID"
                :lastSubmissionId="lastSubmissionId"
                :isDarkMode="isDarkMode"
              />
              <ProblemCommunity
                v-if="
                  isInitialized &&
                  !problemLoading &&
                  !problemError.visible &&
                  !isContestProblem
                "
                :key="`community-${contestID || 'public'}-${problemID}`"
                v-show="leftPainActiveTab === 'community'"
                :problemID="problemID"
                :problem="problem"
                :isDarkMode="isDarkMode"
              />
            </div>
          </div>
        </div>
      </pane>
      <pane min-size="30" :size="50">
        <div class="editor-pane-wrapper">
          <CodeEditorHeader
            @create-submission="submitCode"
            @change-language="changeLanguage"
            @open-ai="$refs.bottomDrag.show()"
            :problem="problem"
            :language.sync="language"
            :statusVisible="statusVisible"
            :contestID="contestID"
            :result="result"
            :submissionId="submissionId"
            :isSubmitting="submitting"
          />
          <div class="code-editor-area">
            <CodeEditor
              :value.sync="code"
              :languages="problem.languages"
              :language="language"
              :fontSize="codeFontSize"
              :cursorPos.sync="cursorPos"
              :allowPaste="allowPaste"
              ref="myCm"
            />
            <StickyLnCol :cursorPos="cursorPos" />
          </div>
          <BottomDrag
            ref="bottomDrag"
            :result="result"
            :problemID="problemID"
            :contestID="contestID"
            :code="code"
          />
        </div>
      </pane>
    </splitpanes>
  </div>
</template>

<script>
import { mapGetters, mapActions, mapState } from "vuex"
import { types } from "../../../../../store"
import storage from "@/utils/storage"
import { FormMixin } from "@oj/components/mixins"
import {
  JUDGE_STATUS,
  CONTEST_STATUS,
  buildProblemCodeKey,
} from "@/utils/constants"
import api from "@oj/api"
import { Pane, Splitpanes } from "splitpanes"
import "splitpanes/dist/splitpanes.css"
import { DIFFICULTY_MAP, FIELD_MAP } from "../../../../../utils/constants"
import CodeEditorHeader from "./problemSolvingComponent/CodeEditorHeader.vue"
import ProblemDetailFlexibleContainer from "./problemSolvingComponent/ProblemDetailFlexibleContainer.vue"
import StickyLnCol from "./problemSolvingComponent/StickyLnCol.vue"
import CodeEditor from "./problemSolvingComponent/CodeEditor.vue"
import SubmissionList from "./problemSolvingComponent/SubmissionList.vue"
import ProblemCommunity from "./problemSolvingComponent/ProblemCommunity.vue"
import BottomDrag from "./problemSolvingComponent/BottomDrag.vue"
import ContestProblemNavigator from "./problemSolvingComponent/ContestProblemNavigator.vue"

export default {
  name: "ProblemPage",
  components: {
    StickyLnCol,
    CodeEditor,
    CodeEditorHeader,
    ProblemDetailFlexibleContainer,
    SubmissionList,
    ProblemCommunity,
    ContestProblemNavigator,
    Splitpanes,
    Pane,
    BottomDrag,
  },
  mixins: [FormMixin],
  data() {
    return {
      cursorPos: {
        ln: 0,
        ch: 0,
      },
      statusVisible: false,
      captchaRequired: false,
      graphVisible: false,
      submissionExists: false,
      captchaCode: "",
      captchaSrc: "",
      contestID: "",
      problemID: "",
      submitting: false,
      code: "",
      language: "C++",
      codePerLanguage: {},
      languages: {
        type: Array,
        default: () => {
          return ["C", "C++", "Java", "Python3"]
        },
      },
      submissionId: "",
      submitted: false,
      result: {
        result: 9,
      },
      problem: {
        title: "",
        description: "",
        hint: "",
        my_status: "",
        template: {},
        languages: [],
        created_by: {
          username: "",
        },
        difficulty: "",
        tags: [],
        io_mode: { io_mode: "Standard IO" },
        allow_paste: true,
      },
      submission: {
        result: "0",
        code: "",
        info: {
          data: [],
        },
        statistic_info: {
          time_cost: "",
          memory_cost: "",
        },
      },
      dropdown: {
        openFieldDropdown: false,
        openCategoryDropdown: false,
      },
      modalCheck: false,
      leftPainActiveTab: "problem",
      showAskNudge: false,
      rightPainActiveTab: "editor",
      lastSubmissionId: null,
      isInitialized: false,
      problemLoading: false,
      contestProblemsLoading: false,
      loadedContestProblemNavigationFor: "",
      problemRequestSeq: 0,
      problemZoomPercent: 100,
      minProblemZoom: 80,
      maxProblemZoom: 140,
      problemZoomStep: 5,
      codeFontSize: 14,
      minCodeFontSize: 12,
      maxCodeFontSize: 22,
      codeFontSizeStep: 1,
      settingsPopoverOpen: false,
      settingsPopoverStyle: {
        top: "58px",
        left: "auto",
        right: "16px",
      },
      problemError: {
        visible: false,
        title: "",
        description: "",
      },
    }
  },
  beforeRouteEnter(to, from, next) {
    next((vm) => {
      vm.registerBeforeUnload()
    })
  },
  mounted() {
    this.$store.commit(types.CHANGE_CONTEST_ITEM_VISIBLE, { menu: false })
    this.init()
    this.registerBeforeUnload()
    window.addEventListener("open-problem-settings", this.openSettingsModal)
    window.addEventListener("resize", this.closeSettingsPopover)
    window.addEventListener("keydown", this.handleSettingsKeydown)
    document.addEventListener("click", this.handleSettingsOutsideClick)
    this.isInitialized = true
  },
  activated() {
    this.registerBeforeUnload()
  },
  deactivated() {
    this.removeBeforeUnload()
  },
  destroyed() {
    window.removeEventListener("open-problem-settings", this.openSettingsModal)
    window.removeEventListener("resize", this.closeSettingsPopover)
    window.removeEventListener("keydown", this.handleSettingsKeydown)
    document.removeEventListener("click", this.handleSettingsOutsideClick)
    this.removeBeforeUnload()
    this.changeProblemSolvingState(false)
  },
  methods: {
    ...mapActions([
      "changeDomTitle",
      "changeProblemSolvingState",
      "changeProblemSolvingTheme",
      "getContestProblems",
    ]),
    setRouteParams(route = this.$route) {
      this.contestID = route.params.contestID
      this.problemID = route.params.problemID
    },
    getEmptyProblem() {
      return {
        title: "",
        description: "",
        hint: "",
        my_status: "",
        template: {},
        languages: [],
        created_by: {
          username: "",
        },
        difficulty: "",
        tags: [],
        io_mode: { io_mode: "Standard IO" },
        allow_paste: true,
      }
    },
    resetProblemState() {
      this.clearSubmissionRefresh()
      this.statusVisible = false
      this.captchaRequired = false
      this.graphVisible = false
      this.submissionExists = false
      this.captchaCode = ""
      this.captchaSrc = ""
      this.submitting = false
      this.code = ""
      this.language = "C++"
      this.codePerLanguage = {}
      this.submissionId = ""
      this.submitted = false
      this.result = { result: 9 }
      this.lastSubmissionId = null
      this.problemLoading = false
      this.leftPainActiveTab = "problem"
      this.showAskNudge = false
      this.modalCheck = false
      this.problemError = {
        visible: false,
        title: "",
        description: "",
      }
      this.problem = this.getEmptyProblem()
    },
    getApiErrorMessage(error) {
      const data =
        (error && error.data) ||
        (error && error.response && error.response.data) ||
        {}
      return data.data || ""
    },
    getProblemLoadErrorMessage(error) {
      const message = String(this.getApiErrorMessage(error)).trim()
      if (message.startsWith("Please login")) {
        return "로그인이 필요합니다."
      }
      return message || "문제를 불러오지 못했습니다."
    },
    isProblemNotFoundError(error) {
      const message = String(this.getApiErrorMessage(error)).trim()
      return [
        "Problem does not exist",
        "Problem does not exist.",
        "Problem doesn't exist",
        "Problem does not exists",
        "Problem not exist",
      ].includes(message)
    },
    showProblemNotFoundError() {
      this.problemError = {
        visible: true,
        title: "문제를 찾을 수 없습니다",
        description: "입력하신 문제 번호가 올바르지 않거나 문제가 삭제되었습니다.",
      }
      this.problem = this.getEmptyProblem()
      this.leftPainActiveTab = "problem"
      this.statusVisible = false
      this.submitting = false
      this.clearSubmissionRefresh()
      this.removeBeforeUnload()
      this.changeDomTitle({ title: "문제를 찾을 수 없습니다" })
    },
    clearSubmissionRefresh() {
      if (this.refreshStatus) {
        clearTimeout(this.refreshStatus)
        this.refreshStatus = null
      }
    },
    saveCurrentCode(problemID = this.problemID, contestID = this.contestID) {
      if (!problemID) {
        return
      }
      storage.set(buildProblemCodeKey(problemID, contestID), {
        code: this.code,
        language: this.language,
      })
    },
    restoreCurrentCode() {
      const problemCode = storage.get(
        buildProblemCodeKey(this.problemID, this.contestID),
      )
      if (!problemCode) {
        return false
      }
      this.language = problemCode.language
      this.code = problemCode.code
      return true
    },
    applyProblemTemplate() {
      this.language = this.problem.languages[0] || "C++"
      let template = this.problem.template
      if (template && template[this.language]) {
        this.code = template[this.language]
      } else {
        this.code = ""
      }
    },
    loadContestProblemNavigation(force = false) {
      if (!this.isContestProblem) {
        return Promise.resolve()
      }
      if (
        !force &&
        this.loadedContestProblemNavigationFor === String(this.contestID) &&
        this.contestProblems.length > 0
      ) {
        return Promise.resolve()
      }
      this.contestProblemsLoading = true
      return this.getContestProblems().then(
        (res) => {
          this.contestProblemsLoading = false
          this.loadedContestProblemNavigationFor = String(this.contestID)
          return res
        },
        (err) => {
          this.contestProblemsLoading = false
          throw err
        },
      )
    },
    init(options = {}) {
      const {
        resetState = false,
        forceLoadNavigation = false,
        restoreCode = true,
      } = options
      this.changeProblemSolvingState(true)
      this.$Loading.start()
      this.problemLoading = true
      this.problemError.visible = false
      this.setRouteParams()
      if (resetState) {
        this.resetProblemState()
        this.problemLoading = true
      }

      const hasStoredCode = restoreCode && this.restoreCurrentCode()
      this.loadContestProblemNavigation(forceLoadNavigation).catch(() => {})
      const requestSeq = ++this.problemRequestSeq

      this.contestID = this.$route.params.contestID
      this.problemID = this.$route.params.problemID

      if (this.contestID) {
        this.$store.dispatch("getContest", this.contestID)
      }

      let func =
        this.$route.name === "problem-details"
          ? "getProblem"
          : "getContestProblem"
      api[func](this.problemID, this.contestID).then(
        (res) => {
          if (requestSeq !== this.problemRequestSeq) {
            return
          }
          this.$Loading.finish()
          this.problemLoading = false
          this.registerBeforeUnload()
          let problem = res.data.data
          this.changeDomTitle({ title: problem.title })
          api.submissionExists(problem.id).then((res) => {
            if (requestSeq !== this.problemRequestSeq) {
              return
            }
            this.submissionExists = res.data.data
          })
          problem.languages = problem.languages.sort()
          this.problem = problem

          if (restoreCode && !hasStoredCode) {
            this.applyProblemTemplate()
          }
        },
        (error) => {
          if (requestSeq !== this.problemRequestSeq) {
            return
          }
          this.$Loading.error()
          this.problemLoading = false
          if (this.isProblemNotFoundError(error)) {
            this.showProblemNotFoundError()
          } else {
            this.$error(this.getProblemLoadErrorMessage(error))
          }
        },
      )
    },
    registerBeforeUnload() {
      if (this._beforeUnloadRegistered) return
      window.addEventListener("beforeunload", this.unLoadEvent)
      this._beforeUnloadRegistered = true
    },
    removeBeforeUnload() {
      if (!this._beforeUnloadRegistered) return
      window.removeEventListener("beforeunload", this.unLoadEvent)
      this._beforeUnloadRegistered = false
    },
    unLoadEvent: function (event) {
      if (this.isLeaveSite || this.problemError.visible) return

      this.saveCurrentCode(this.problemID || this.problem._id, this.contestID)

      event.preventDefault()
      event.returnValue = ""
    },
    changeLanguage(newLang) {
      // 현재 작성 중인 코드 저장
      this.codePerLanguage[this.language] = this.code

      // 변경 언어로 작성된 코드가 존재 하는 경우
      if (this.codePerLanguage[newLang] !== undefined) {
        this.code = this.codePerLanguage[newLang]
      }
      // 변경 언어로 작성된 코드가 존재하지 않음 + 변경언어 template 존재하는 경우
      else if (this.problem.template && this.problem.template[newLang]) {
        this.code = this.problem.template[newLang]
      }
      // 변경 언어로 작성된 코드가 존재하지 않음 + 변경언어 template 존재하지 않는 경우
      else {
        this.code = ""
      }

      this.language = newLang
      this.$refs.myCm.onLangChange(newLang)
    },
    openSettingsModal(event = {}) {
      if (this.settingsPopoverOpen) {
        this.closeSettingsPopover()
        return
      }
      this.updateSettingsPopoverPosition(event.detail && event.detail.anchorRect)
      this.settingsPopoverOpen = true
    },
    closeSettingsPopover() {
      this.settingsPopoverOpen = false
    },
    updateSettingsPopoverPosition(anchorRect) {
      if (!anchorRect) {
        this.settingsPopoverStyle = {
          top: "58px",
          left: "auto",
          right: "16px",
        }
        return
      }
      const popoverWidth = 260
      const viewportMargin = 12
      const top = anchorRect.bottom + 8
      const left = Math.min(
        window.innerWidth - popoverWidth - viewportMargin,
        Math.max(viewportMargin, anchorRect.right - popoverWidth),
      )
      this.settingsPopoverStyle = {
        top: `${top}px`,
        left: `${left}px`,
        right: "auto",
      }
    },
    handleSettingsOutsideClick(event) {
      if (!this.settingsPopoverOpen) return
      const popover = this.$refs.settingsPopover
      if (popover && !popover.contains(event.target)) {
        this.closeSettingsPopover()
      }
    },
    handleSettingsKeydown(event) {
      if (event.key === "Escape") {
        this.closeSettingsPopover()
      }
    },
    setProblemZoom(value) {
      this.problemZoomPercent = this.clampNumber(
        value,
        this.minProblemZoom,
        this.maxProblemZoom,
      )
    },
    setCodeFontSize(value) {
      this.codeFontSize = this.clampNumber(
        value,
        this.minCodeFontSize,
        this.maxCodeFontSize,
      )
    },
    clampNumber(value, min, max) {
      const numericValue = Number(value)
      if (Number.isNaN(numericValue)) return min
      return Math.min(max, Math.max(min, numericValue))
    },
    modalOpen() {
      this.modalCheck = !this.modalCheck
    },
    handleRoute(route) {
      this.$router.push(route)
    },
    goContestProblem(problemID) {
      if (!this.contestID || String(problemID) === String(this.problemID)) {
        return
      }
      this.$router.replace({
        name: "contest-problem-details",
        params: {
          contestID: this.contestID,
          problemID,
        },
      })
    },
    goContestProblemList() {
      if (!this.contestID) {
        return
      }
      this.$router.push({
        name: "contest-problem-list",
        params: {
          contestID: this.contestID,
        },
      })
    },
    goBackFromError() {
      this.$router.go(-1)
    },
    goProblemListFromError() {
      if (this.contestID) {
        this.goContestProblemList()
        return
      }
      this.$router.push({ name: "problem-list" })
    },
    check() {
      alert(this.code)
    },
    goAsk() {
      this.leftPainActiveTab = "community"
      this.showAskNudge = false
    },
    checkSubmissionStatus() {
      // 使用setTimeout避免一些问题
      if (this.refreshStatus) {
        // 如果之前的提交状态检查还没有停止,则停止,否则将会失去timeout的引用造成无限请求
        clearTimeout(this.refreshStatus)
      }
      const checkStatus = () => {
        let id = this.submissionId
        api.getSubmission(id).then(
          (res) => {
            this.result = res.data.data
            if (Object.keys(res.data.data.statistic_info).length !== 0) {
              this.submitting = false
              this.submitted = false

              this.leftPainActiveTab = "submission"
              this.lastSubmissionId = id
              // 통과(Accepted=0)하지 못한 결과면 질문 유도 넛지 표시
              this.showAskNudge = this.result.result !== 0

              clearTimeout(this.refreshStatus)
              this.init({
                restoreCode: false,
                forceLoadNavigation: this.isContestProblem,
              })
            } else {
              this.refreshStatus = setTimeout(checkStatus, 2000)
            }
          },
          () => {
            this.submitting = false
            clearTimeout(this.refreshStatus)
          },
        )
      }
      this.refreshStatus = setTimeout(checkStatus, 2000)
    },
    submitCode() {
      if (this.code.trim() === "") {
        this.$error(this.$i18n.t("m.Code_can_not_be_empty"))
        return
      }
      this.submissionId = ""
      this.result = { result: 9 }
      this.showAskNudge = false
      this.submitting = true
      let data = {
        problem_id: this.problem.id,
        language: this.language,
        code: this.code,
        contest_id: this.contestID,
      }
      if (this.captchaRequired) {
        data.captcha = this.captchaCode
      }
      const submitFunc = (data, detailsVisible) => {
        this.statusVisible = true
        api.submitCode(data).then(
          (res) => {
            this.submissionId = res.data.data && res.data.data.submission_id
            // 定时检查状态
            this.submitting = false
            this.submissionExists = true
            if (!detailsVisible) {
              this.$success(this.$i18n.t("m.Submit_code_successfully"))
              return
            }
            this.submitted = true
            this.checkSubmissionStatus()
          },
          (res) => {
            this.getCaptchaSrc()
            if (res.data.data.startsWith("Captcha is required")) {
              this.captchaRequired = true
            }
            this.submitting = false
            this.statusVisible = false
          },
        )
      }

      if (this.contestRuleType === "OI" && !this.OIContestRealTimePermission) {
        if (this.submissionExists) {
          const confirmed = window.confirm(
            this.$i18n.t(
              "m.You_have_submission_in_this_problem_sure_to_cover_it",
            ),
          )
          if (confirmed) {
            submitFunc(data, false)
          } else {
            this.submitting = false
          }
        } else {
          submitFunc(data, false)
        }
      } else {
        submitFunc(data, true)
      }
    },
  },
  computed: {
    ...mapState({
      contestProblems: (state) => state.contest.contestProblems,
    }),
    FIELD_MAP() {
      return FIELD_MAP
    },
    DIFFICULTY_MAP() {
      return DIFFICULTY_MAP
    },
    ...mapGetters([
      "problemSubmitDisabled",
      "contestRuleType",
      "OIContestRealTimePermission",
      "contestStatus",
      "isDarkMode",
    ]),
    contest() {
      return this.$store.state.contest.contest
    },
    isContestProblem() {
      return this.$route.name === "contest-problem-details" && !!this.contestID
    },
    contestEnded() {
      return this.contestStatus === CONTEST_STATUS.ENDED
    },
    submissionStatus() {
      return {
        text: JUDGE_STATUS[this.result.result]["name"],
        color: JUDGE_STATUS[this.result.result]["color"],
      }
    },
    submissionRoute() {
      if (this.contestID) {
        return {
          name: "contest-submission-list",
          query: { problemID: this.problemID },
        }
      } else {
        return {
          name: "submission-list",
          query: { problemID: this.problemID },
        }
      }
    },
    allowPaste() {
      if (this.problem && this.problem.allow_paste !== undefined) {
        return this.problem.allow_paste
      }
      return true // 만약 정의되어 있지 않은 경우 기본값은 true
    },
  },
  beforeRouteLeave(to, from, next) {
    this.clearSubmissionRefresh()
    this.removeBeforeUnload()
    this.$store.commit(types.CHANGE_CONTEST_ITEM_VISIBLE, { menu: true })
    if (!this.problemError.visible) {
      this.saveCurrentCode(from.params.problemID, from.params.contestID)
    }
    next()
  },
  watch: {
    $route(to, from) {
      if (!this.problemError.visible && from && from.params && from.params.problemID) {
        this.saveCurrentCode(from.params.problemID, from.params.contestID)
      }
      this.init({
        resetState: true,
        forceLoadNavigation: to.params.contestID !== from.params.contestID,
      })
    },
  },
}
</script>

<style lang="less">
@code-font-family: "JetBrains Mono", "Noto Sans KR", "Apple SD Gothic Neo",
  "Menlo", "Monaco", "Consolas", monospace;

.settings-popover {
  position: fixed;
  z-index: 1200;
  width: 260px;
  max-width: ~"calc(100vw - 24px)";
  border: 1px solid var(--border-color);
  border-radius: 9px;
  background: var(--ps-content-color);
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.18);
}

.settings-popover-body {
  display: grid;
  gap: 10px;
  padding: 12px;
}

.settings-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
}

.settings-label {
  display: flex;
  align-items: center;
  gap: 7px;
  color: var(--ps-content-text-color);
  font-size: 13px;
  font-weight: 650;
  white-space: nowrap;

  strong {
    color: var(--ps-content-title-color);
    font-size: 14px;
    font-weight: 750;
  }
}

.settings-label-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 16px;
  width: 16px;
  height: 16px;
  color: var(--ps-content-title-color);
  font-size: 12px;
  line-height: 1;
  opacity: 0.78;
}

.settings-label-icon--text {
  font-family: "Inter", "Noto Sans KR", "Apple SD Gothic Neo", sans-serif;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0;
}

.settings-controls {
  display: inline-grid;
  grid-template-columns: 30px 58px 30px;
  align-items: center;
  justify-self: end;
  overflow: hidden;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background: var(--bg-color);
}

.settings-step-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: 0;
  background: transparent;
  color: var(--ps-content-title-color);
  cursor: pointer;
  font-size: 13px;
}

.settings-step-button:hover:not(:disabled) {
  border-color: var(--custom-btn-hover-color);
  background: var(--header-btn-color);
}

.settings-step-button:disabled {
  cursor: not-allowed;
  opacity: 0.42;
}

.settings-control-value {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 30px;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
  color: var(--ps-content-title-color);
  font-size: 12px;
  font-weight: 750;
  line-height: 1;
  white-space: nowrap;
}

.popover-fade-enter-active,
.popover-fade-leave-active {
  transition:
    opacity 0.12s ease,
    transform 0.12s ease;
}

.popover-fade-enter,
.popover-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.problem-solving-root {
  display: flex;
  min-height: calc(100vh - 50px);
  overflow: hidden;
  background: var(--ps-background-color);

  #problem-main {
    flex: auto;
    margin-right: 18px;
  }

  #right-column {
    flex: none;
    width: 220px;
  }

  .CodeMirror,
  .CodeMirror pre,
  .CodeMirror-linenumber,
  pre,
  code,
  .hljs,
  .code-highlight-wrapper {
    font-family: @code-font-family !important;
    font-variant-ligatures: none;
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

.problem-error-state {
  min-height: calc(100vh - 50px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: var(--ps-background-color);
  color: var(--text-color);
}

.problem-error-card {
  width: ~"min(420px, 100%)";
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.problem-error-code {
  margin-bottom: 12px;
  color: #9ca3af;
  font-size: 42px;
  font-weight: 800;
  line-height: 1;
}

.problem-error-card h2 {
  margin: 0;
  color: var(--ps-content-title-color);
  font-size: 24px;
  font-weight: 700;
  line-height: 1.35;
}

.problem-error-card p {
  margin: 12px 0 0;
  color: var(--ps-content-text-color);
  font-size: 15px;
  line-height: 1.6;
}

.problem-error-actions {
  display: flex;
  gap: 8px;
  margin-top: 24px;
}

.problem-error-button {
  min-width: 92px;
  height: 36px;
  border: 0;
  border-radius: 8px;
  padding: 0 14px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.problem-error-button.primary {
  background: var(--submission-primary-btn-bg);
  color: var(--submission-primary-btn-text-color);
}

.problem-error-button.secondary {
  border: 1px solid var(--ps-content-pre-border-color);
  background: var(--ps-content-color);
  color: #475569;
}

.problem-error-button.secondary:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
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

.splitpanes__pane.problem-pane-with-navigator {
  padding-left: 0;
  padding-top: 0;
  padding-bottom: 0;
  border-radius: 0;
}

.splitpanes--vertical > .splitpanes__splitter {
  min-width: 4px !important;
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
  min-height: 0;
  height: 100%;
}

.left-pain-wrapper.has-contest-navigator {
  display: grid;
  grid-template-columns: 60px minmax(0, 1fr);
  gap: 10px;
  position: relative;
}

.problem-content-wrapper {
  min-width: 0;
  min-height: 0;
  height: 100%;
}

.left-pain-wrapper.has-contest-navigator .problem-content-wrapper {
  padding-top: 10px;
  padding-bottom: 10px;
}

.editor-pane-wrapper {
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.editor-pane-wrapper > .container-header {
  flex: 0 0 auto;
}

.code-editor-area {
  position: relative;
  display: flex;
  flex: 1 1 auto;
  min-height: 0;
}

.tab-headers {
  display: flex;
}

.tab-header {
  padding: 10px 20px;
  cursor: pointer;
  font-size: 14px;
  border-radius: 7px 7px 0 0;
  border: 1px solid transparent;
}

.tab-header.active {
  font-weight: 800;
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  border-bottom: none;
  border-radius: 7px 7px 0 0;
  margin-bottom: -1px; // tab-content와 살짝 겹치도록 하여 연결된 것처럼 보이도록 함
}

.tab-header:hover:not(.active) {
  background-color: var(--bg-color);
}

/* 질문하기 탭: 배경은 다른 탭과 동일하게 두고 글자색만 브랜드 강조색 */
.tab-header--ask {
  color: #5b64ed;
  font-weight: 700;
}

/* 오답 후 질문 유도 넛지 */
.ask-nudge {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 8px 0;
  padding: 9px 12px;
  border: 1px solid rgba(91, 100, 237, 0.35);
  background-color: rgba(91, 100, 237, 0.08);
  border-radius: 8px;
  font-size: 13px;
  color: inherit;
}

.ask-nudge-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.ask-nudge-go {
  border: none;
  background-color: #5b64ed;
  color: #fff;
  font-weight: 700;
  font-size: 13px;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  white-space: nowrap;
}

.ask-nudge-go:hover {
  filter: brightness(1.05);
}

.ask-nudge-close {
  border: none;
  background: transparent;
  color: #9999a6;
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
}

.tab-content {
  height: calc(100% - 40px);
  min-height: 0;
  overflow-y: auto;
  border: 1px solid var(--border-color);
  border-radius: 0 7px 7px 7px;
}
</style>
