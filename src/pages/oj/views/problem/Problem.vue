<template>
  <div class="flex-container">
    <splitpanes>
      <pane :size="43" style="border:none; padding-right: 5px">
        <div class="problemDetailContainer">
          <Panel :padding="45" class="detailCard" dis-hover style="transition: 0.3s">
            <div slot="title"
                 style="border-bottom: 1px solid #e7e7e7; padding-bottom: 14px; padding-left: 18px; font-weight: bold">
              {{ problem.title }}
            </div>
            <div id="problem-content" class="markdown-body" v-katex>
              <div style="display: flex; justify-content: space-between;">
                <div style="display: flex">
                  <div class="headerDetailBtn" style="background-color: var(--difficulty-color)">
                    {{ difficultyMap[problem.difficulty].value }}
                  </div>
                  <div class="headerDetailBtn" @click="scrollField">
                    <Icon type="ios-pie" color="#F8B193"/>
                    영역
                  </div>
                  <div class="headerDetailBtn" @click="scrollCategory">
                    <Icon type="ios-pricetag" color="#FF9F9F"/>
                    카테고리
                  </div>
                </div>
                <div class="headerDetailBtn" @click="noticeUnReadyFeature">
                  <i class="fas fa-comments" style="color: #90B8E7"></i>
                  토론하기 (24)
                </div>
              </div>
              <p class="title" style="margin-top: 25px">{{ $t('m.Description') }}</p>
              <p class="content" v-html=problem.description></p>
              <p class="title">{{ $t('m.Input') }} <span
                v-if="problem.io_mode.io_mode=='File IO'">({{ $t('m.FromFile') }}: {{ problem.io_mode.input }})</span>
              </p>
              <p class="content" v-html=problem.input_description></p>

              <p class="title">{{ $t('m.Output') }} <span
                v-if="problem.io_mode.io_mode=='File IO'">({{ $t('m.ToFile') }}: {{ problem.io_mode.output }})</span>
              </p>
              <p class="content" v-html=problem.output_description></p>
              <div v-for="(sample, index) of problem.samples" :key="index">
                <div class="sample">
                  <div class="sample-input">
                    <p class="title" style="text-decoration: none; margin-bottom: 0px">{{ $t('m.Sample_Input') }}
                      {{ index + 1 }}
                      <a class="copy"
                         v-clipboard:copy="sample.input"
                         v-clipboard:success="onCopy"
                         v-clipboard:error="onCopyError">
                        <Icon type="clipboard"></Icon>
                      </a>
                    </p>
                    <pre>{{ sample.input }}</pre>
                  </div>
                  <div class="sample-output">
                    <p class="title" style="text-decoration: none; margin-bottom: 0px">{{ $t('m.Sample_Output') }}
                      {{ index + 1 }}</p>
                    <pre>{{ sample.output }}</pre>
                  </div>
                </div>
              </div>
              <p class="title" style="text-decoration: none">제약사항</p>
              <li style="padding-left: 20px">
                <code>
                  {{ $t('m.Time_Limit') + "   " + problem.time_limit + 'ms' }}
                </code>
              </li>
              <li style="padding-left: 20px">
                <code>
                  {{ $t('m.Memory_Limit') + "   " + problem.memory_limit + 'mb' }}
                </code>
              </li>
              <div v-if="problem.hint">
                <p class="title">{{ $t('m.Hint') }}</p>
                <Card dis-hover>
                  <div class="content" v-html=problem.hint></div>
                </Card>
              </div>
              <div class="detailInfoBox">
                <div class="detailInfoBoxHeader" @click="toggleDropdown('field')">
                  <p class="title" style="text-decoration: none; margin-top: 0px" ref="field">
                    <Icon type="ios-pie" color="#F8B193" style="margin-right: 5px"/>
                    영역
                  </p>
                  <i class="fas fa-chevron-down" v-if="!dropdown.openFieldDropdown"></i>
                  <i class="fas fa-chevron-up" v-else></i>
                </div>
                <div class="detailInfoBoxHeader" v-if="dropdown.openFieldDropdown">
                  <FieldCategoryBox :boxType="true" :value="fieldMap[problem.field].value"
                                    :boxColor="fieldMap[problem.field].boxColor"/>
                </div>
              </div>

              <div class="detailInfoBox">
                <div class="detailInfoBoxHeader" @click="toggleDropdown('category')">
                  <p class="title" style="text-decoration: none; margin-top: 0px;" ref="category">
                    <Icon type="ios-pricetag" color="#FF9F9F" style="margin-right: 5px"/>
                    카테고리
                  </p>
                  <i class="fas fa-chevron-down" v-if="!dropdown.openCategoryDropdown"></i>
                  <i class="fas fa-chevron-up" v-else></i>
                </div>

                <div v-if="dropdown.openCategoryDropdown" style="display: flex">
                  <template v-for="(category, idx) in problem.tags">
                    <FieldCategoryBox :boxType="false" :value="'#' + category" :boxColor="'#FFFFFF'"/>
                  </template>
                </div>
              </div>

              <div class="detailInfoBox">
                <div class="detailInfoBoxHeader">
                  <p class="title" style="text-decoration: none; margin-top: 0px;">
                    <Icon type="ios-contact" color="#90B8E7" style="margin-right: 5px"/>
                    문제를 등록한 사람
                  </p>
                  <p class="title" style="text-decoration: none; margin-top: 0px;">
                    {{ problem.created_by.username + '님' }}
                  </p>
                </div>
              </div>

              <div class="detailInfoBox" v-if="problem.source">
                <div class="detailInfoBoxHeader">
                  <p class="title" style="text-decoration: none; margin-top: 0px;">
                    <i class="fas fa-paperclip" style="margin-right: 5px; color: #424f66"></i>
                    출처
                  </p>
                  <p class="title" style="text-decoration: none; margin-top: 0px;">
                    {{ problem.source }}
                  </p>
                </div>
              </div>
            </div>
          </Panel>
        </div>
      </pane>
      <pane style="border: none; padding-left: 5px" min-size="30" :size="57">
        <splitpanes horizontal style="height: calc(100vh - 80px);">
          <pane min-size="30" :size="75" style="margin-bottom: 5px">
            <div class="container-header">
              <div>
                <Icon type="code"></Icon>
                <span>
                    코드 작성
                  </span>
              </div>
              <div style="display: flex; justify-content: space-between; align-items: center">
                <Tooltip :content="'언어 선택'" placement="bottom">
                  <Dropdown @on-click="changeLanguage" trigger="click" class="dropdown">
                          <span style="font-size: 13px; padding-right: 3px; font-weight: 450">
                            {{ language }}
                          </span>
                    <i class="fas fa-chevron-down"></i>
                    <Dropdown-menu slot="list">
                      <Dropdown-item :name="item" v-for="item in problem.languages" :key="item">{{
                          item
                        }}
                      </Dropdown-item>
                    </Dropdown-menu>
                  </Dropdown>
                </Tooltip>
                <Tooltip :content="this.$i18n.t('m.Reset_to_default_code_definition')" placement="bottom-end">
                  <CustomIconBtn @click="check()" :wrapperSize="30" iconClass="fas fa-tags"/>
                </Tooltip>
                <Tooltip :content="'글자 크기 키우기'" placement="bottom-end">
                  <CustomIconBtn @click="changeFontSize(fontSize+1)" :wrapperSize="30" iconClass="fas fa-plus"/>
                </Tooltip>
                <Tooltip :content="'글자 크기 줄이기'" placement="bottom-end">
                  <CustomIconBtn @click="changeFontSize(fontSize-1)" :wrapperSize="30" iconClass="fas fa-minus"/>
                </Tooltip>
                <Tooltip :content="this.$i18n.t('m.Reset_to_default_code_definition')" placement="bottom-end">
                  <CustomIconBtn @click="onResetToTemplate" :wrapperSize="30" iconClass="fas fa-undo"/>
                </Tooltip>
              </div>
            </div>
            <CodeMirrorTest :value.sync="code"
                            :languages="problem.languages"
                            :language="language"
                            :cursorPos.sync="cursorPos"
                            :fontSize.sync="fontSize"
                            :theme.sync="theme"
                            ref="myCm"/>
            <div class="sticky_ln_col">Ln {{this.cursorPos.ln}}, Col {{this.cursorPos.ch}}</div>
          </pane>
          <pane min-size="20" :size="25" style="margin-top: 5px; padding-bottom: 10px">
            <div class="container-header">
              <div>
                <Icon type="ios-pulse"></Icon>
                <span>
                  실행 결과
                </span>
                  <i class="fas fa-circle-notch fa-spin" style="margin-left: 7px;color: #e39530"></i>
                <i class="far fa-check-circle" style="color: #38c27b;"></i>
                <i class="far fa-times-circle" style="color: #dd3131;"></i>
              </div>
              <div class="submitBtn" @click="submitCode">
                <i class="fas fa-file-upload"></i>
                <span style="font-size: small;margin-left: 4px;">제출</span>
              </div>
            </div>
            <div style="width: 100%;height: 70%; display: flex; font-size: small; text-align: center;">
              <span>테스트 케이스 및 실행 결과가 표시됩니다.</span>
<!--              <div class="status" v-if="statusVisible">-->
<!--                <template v-if="!this.contestID || (this.contestID && OIContestRealTimePermission)">-->
<!--                  <Tag type="dot" :color="submissionStatus.color" @click.native="handleRoute('/status/'+submissionId)">-->
<!--                    {{ $t('m.' + submissionStatus.text.replace(/ /g, "_")) }}-->
<!--                  </Tag>-->
<!--                </template>-->
<!--                <template v-else-if="this.contestID && !OIContestRealTimePermission">-->
<!--                  <Alert type="success" show-icon>{{ $t('m.Submitted_successfully') }}</Alert>-->
<!--                </template>-->
<!--              </div>-->
            </div>

          </pane>
        </splitpanes>
      </pane>
    </splitpanes>
    <!--      <div id="problem-main">-->
    <!--        &lt;!&ndash;problem main&ndash;&gt;-->
    <!--        <Panel :padding="40" shadow>-->
    <!--          <div slot="title">{{problem.title}}</div>-->
    <!--          <div id="problem-content" class="markdown-body" v-katex>-->
    <!--            <p class="title">{{$t('m.Description')}}</p>-->
    <!--            <p class="content" v-html=problem.description></p>-->
    <!--            &lt;!&ndash; {{$t('m.music')}} &ndash;&gt;-->
    <!--            <p class="title">{{$t('m.Input')}} <span v-if="problem.io_mode.io_mode=='File IO'">({{$t('m.FromFile')}}: {{ problem.io_mode.input }})</span></p>-->
    <!--            <p class="content" v-html=problem.input_description></p>-->

    <!--            <p class="title">{{$t('m.Output')}} <span v-if="problem.io_mode.io_mode=='File IO'">({{$t('m.ToFile')}}: {{ problem.io_mode.output }})</span></p>-->
    <!--            <p class="content" v-html=problem.output_description></p>-->

    <!--            <div v-for="(sample, index) of problem.samples" :key="index">-->
    <!--              <div class="flex-container sample">-->
    <!--                <div class="sample-input">-->
    <!--                  <p class="title">{{$t('m.Sample_Input')}} {{index + 1}}-->
    <!--                    <a class="copy"-->
    <!--                       v-clipboard:copy="sample.input"-->
    <!--                       v-clipboard:success="onCopy"-->
    <!--                       v-clipboard:error="onCopyError">-->
    <!--                      <Icon type="clipboard"></Icon>-->
    <!--                    </a>-->
    <!--                  </p>-->
    <!--                  <pre>{{sample.input}}</pre>-->
    <!--                </div>-->
    <!--                <div class="sample-output">-->
    <!--                  <p class="title">{{$t('m.Sample_Output')}} {{index + 1}}</p>-->
    <!--                  <pre>{{sample.output}}</pre>-->
    <!--                </div>-->
    <!--              </div>-->
    <!--            </div>-->

    <!--            <div v-if="problem.hint">-->
    <!--              <p class="title">{{$t('m.Hint')}}</p>-->
    <!--              <Card dis-hover>-->
    <!--                <div class="content" v-html=problem.hint></div>-->
    <!--              </Card>-->
    <!--            </div>-->

    <!--            <div v-if="problem.source">-->
    <!--              <p class="title">{{$t('m.Source')}}</p>-->
    <!--              <p class="content">{{problem.source}}</p>-->
    <!--            </div>-->

    <!--          </div>-->
    <!--        </Panel>-->
    <!--        &lt;!&ndash;problem main end&ndash;&gt;-->
    <!--        <Card :padding="20" id="submit-code" dis-hover>-->
    <!--          <CodeMirror :value.sync="code"-->
    <!--                      :languages="problem.languages"-->
    <!--                      :language="language"-->
    <!--                      :theme="theme"-->
    <!--                      @resetCode="onResetToTemplate"-->
    <!--                      @changeTheme="onChangeTheme"-->
    <!--                      @changeLang="onChangeLang"></CodeMirror>-->
    <!--          <Row type="flex" justify="space-between">-->
    <!--            <Col :span="10">-->
    <!--              <div class="status" v-if="statusVisible">-->
    <!--                <template v-if="!this.contestID || (this.contestID && OIContestRealTimePermission)">-->
    <!--                  <span>{{$t('m.Status')}}</span>-->
    <!--                  <Tag type="dot" :color="submissionStatus.color" @click.native="handleRoute('/status/'+submissionId)">-->
    <!--                    {{$t('m.' + submissionStatus.text.replace(/ /g, "_"))}}-->
    <!--                  </Tag>-->
    <!--                </template>-->
    <!--                <template v-else-if="this.contestID && !OIContestRealTimePermission">-->
    <!--                  <Alert type="success" show-icon>{{$t('m.Submitted_successfully')}}</Alert>-->
    <!--                </template>-->
    <!--              </div>-->
    <!--              <div v-else-if="problem.my_status === 0">-->
    <!--                <Alert type="success" show-icon>{{$t('m.You_have_solved_the_problem')}}</Alert>-->
    <!--              </div>-->
    <!--              <div v-else-if="this.contestID && !OIContestRealTimePermission && submissionExists">-->
    <!--                <Alert type="success" show-icon>{{$t('m.You_have_submitted_a_solution')}}</Alert>-->
    <!--              </div>-->
    <!--              <div v-if="contestEnded">-->
    <!--                <Alert type="warning" show-icon>{{$t('m.Contest_has_ended')}}</Alert>-->
    <!--              </div>-->
    <!--            </Col>-->

    <!--            <Col :span="12">-->
    <!--              <template v-if="captchaRequired">-->
    <!--                <div class="captcha-container">-->
    <!--                  <Tooltip v-if="captchaRequired" content="Click to refresh" placement="top">-->
    <!--                    <img :src="captchaSrc" @click="getCaptchaSrc"/>-->
    <!--                  </Tooltip>-->
    <!--                  <Input v-model="captchaCode" class="captcha-code"/>-->
    <!--                </div>-->
    <!--              </template>-->
    <!--              <Button type="warning" icon="edit" :loading="submitting" @click="submitCode"-->
    <!--                      :disabled="problemSubmitDisabled || submitted"-->
    <!--                      class="fl-right">-->
    <!--                <span v-if="submitting">{{$t('m.Submitting')}}</span>-->
    <!--                <span v-else>{{$t('m.Submit')}}</span>-->
    <!--              </Button>-->
    <!--            </Col>-->
    <!--          </Row>-->
    <!--        </Card>-->
    <!--      </div>-->

    <!--      <div id="right-column">-->
    <!--        <VerticalMenu @on-click="handleRoute">-->
    <!--          <template v-if="this.contestID">-->
    <!--            <VerticalMenu-item :route="{name: 'contest-problem-list', params: {contestID: contestID}}">-->
    <!--              <Icon type="ios-photos"></Icon>-->
    <!--              {{$t('m.Problems')}}-->
    <!--            </VerticalMenu-item>-->

    <!--            <VerticalMenu-item :route="{name: 'contest-announcement-list', params: {contestID: contestID}}">-->
    <!--              <Icon type="chatbubble-working"></Icon>-->
    <!--              {{$t('m.Announcements')}}-->
    <!--            </VerticalMenu-item>-->
    <!--          </template>-->

    <!--          <VerticalMenu-item v-if="!this.contestID || OIContestRealTimePermission" :route="submissionRoute">-->
    <!--            <Icon type="navicon-round"></Icon>-->
    <!--             {{$t('m.Submissions')}}-->
    <!--          </VerticalMenu-item>-->

    <!--          <template v-if="this.contestID">-->
    <!--            <VerticalMenu-item v-if="!this.contestID || OIContestRealTimePermission"-->
    <!--                               :route="{name: 'contest-rank', params: {contestID: contestID}}">-->
    <!--              <Icon type="stats-bars"></Icon>-->
    <!--              {{$t('m.Rankings')}}-->
    <!--            </VerticalMenu-item>-->
    <!--            <VerticalMenu-item :route="{name: 'contest-details', params: {contestID: contestID}}">-->
    <!--              <Icon type="home"></Icon>-->
    <!--              {{$t('m.View_Contest')}}-->
    <!--            </VerticalMenu-item>-->
    <!--          </template>-->
    <!--        </VerticalMenu>-->

    <!--        <Card id="info">-->
    <!--          <div slot="title" class="header">-->
    <!--            <Icon type="information-circled"></Icon>-->
    <!--            <span class="card-title">{{$t('m.Information')}}</span>-->
    <!--          </div>-->
    <!--          <ul>-->
    <!--            <li><p>ID</p>-->
    <!--              <p>{{problem._id}}</p></li>-->
    <!--            <li>-->
    <!--              <p>{{$t('m.Time_Limit')}}</p>-->
    <!--              <p>{{problem.time_limit}}MS</p></li>-->
    <!--            <li>-->
    <!--              <p>{{$t('m.Memory_Limit')}}</p>-->
    <!--              <p>{{problem.memory_limit}}MB</p></li>-->
    <!--            <li>-->
    <!--            <li>-->
    <!--              <p>{{$t('m.IOMode')}}</p>-->
    <!--              <p>{{problem.io_mode.io_mode}}</p>-->
    <!--            </li>-->
    <!--            <li>-->
    <!--              <p>{{$t('m.Created')}}</p>-->
    <!--              <p>{{problem.created_by.username}}</p></li>-->
    <!--            <li v-if="problem.difficulty">-->
    <!--              <p>{{$t('m.Level')}}</p>-->
    <!--              <p>{{$t('m.' + problem.difficulty)}}</p></li>-->
    <!--            <li v-if="problem.total_score">-->
    <!--              <p>{{$t('m.Score')}}</p>-->
    <!--              <p>{{problem.total_score}}</p>-->
    <!--            </li>-->
    <!--            <li>-->
    <!--              <p>{{$t('m.Tags')}}</p>-->
    <!--              <p>-->
    <!--                <Poptip trigger="hover" placement="left-end">-->
    <!--                  <a>{{$t('m.Show')}}</a>-->
    <!--                  <div slot="content">-->
    <!--                    <Tag v-for="tag in problem.tags" :key="tag">{{tag}}</Tag>-->
    <!--                  </div>-->
    <!--                </Poptip>-->
    <!--              </p>-->
    <!--            </li>-->
    <!--          </ul>-->
    <!--        </Card>-->

    <!--        <Card id="pieChart" :padding="0" v-if="!this.contestID || OIContestRealTimePermission">-->
    <!--          <div slot="title">-->
    <!--            <Icon type="ios-analytics"></Icon>-->
    <!--            <span class="card-title">{{$t('m.Statistic')}}</span>-->
    <!--            <Button type="ghost" size="small" id="detail" @click="graphVisible = !graphVisible">Details</Button>-->
    <!--          </div>-->
    <!--          <div class="echarts">-->
    <!--            <ECharts :options="pie"></ECharts>-->
    <!--          </div>-->
    <!--        </Card>-->
    <!--      </div>-->

    <!--      <Modal v-model="graphVisible">-->
    <!--        <div id="pieChart-detail">-->
    <!--          <ECharts :options="largePie" :initOptions="largePieInitOpts"></ECharts>-->
    <!--        </div>-->
    <!--        <div slot="footer">-->
    <!--          <Button type="ghost" @click="graphVisible=false">{{$t('m.Close')}}</Button>-->
    <!--        </div>-->
    <!--      </Modal>-->
  </div>
</template>

<script>
import {mapGetters, mapActions} from 'vuex'
import {types} from '../../../../store'
import storage from '@/utils/storage'
import {FormMixin} from '@oj/components/mixins'
import {JUDGE_STATUS, CONTEST_STATUS, buildProblemCodeKey} from '@/utils/constants'
import api from '@oj/api'
import {pie, largePie} from './chartData'
import {Pane, Splitpanes} from "splitpanes";
import 'splitpanes/dist/splitpanes.css'
import FieldCategoryBox from "../../components/FieldCategoryBox.vue";
import CodeMirrorTest from "../../components/CodeMirrorTest.vue";
import CustomIconBtn from "../../components/buttons/CustomIconBtn.vue";

const filtedStatus = ['-1', '-2', '0', '1', '2', '3', '4', '8']

export default {
  name: 'Problem',
  components: {
    CustomIconBtn,
    CodeMirrorTest,
    FieldCategoryBox,
    Splitpanes,
    Pane
  },
  mixins: [FormMixin],
  data() {
    return {
      cursorPos: {
        ln:0,
        ch:0
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
      fontSize: 14,
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
      pie: pie,
      largePie: largePie,
      largePieInitOpts: {
        width: '500',
        height: '480'
      },
      difficultyMap: {
        'VeryLow': {
          'value': '매우 쉬움',
          'textColor': '#95ef4c'
        },
        'Low': {
          'value': '쉬움',
          'textColor': '#B5EAB0'
        },
        'Mid': {
          'value': '보통',
          'textColor': '#7c7878'
        },
        'High': {
          'value': '어려움',
          'textColor': '#ff8828'
        },
        'VeryHigh': {
          'value': '매우 어려움',
          'textColor': '#c02b2b'
        }
      },
      fieldMap: {
        '0': {
          'value': '구현',
          'boxColor': '#F8D093'
        },
        '1': {
          'value': '수학',
          'boxColor': '#B5EAB0'
        },
        '2': {
          'value': '자료구조',
          'boxColor': '#F8B193'
        },
        '3': {
          'value': '탐색',
          'boxColor': '#90B8E7'
        },
        '4': {
          'value': '정렬',
          'boxColor': '#EDC3C3'
        }
      },
      dropdown: {
        openFieldDropdown: false,
        openCategoryDropdown: false
      }
    }
  },
  beforeRouteEnter(to, from, next) {
    let problemCode = storage.get(buildProblemCodeKey(to.params.problemID, to.params.contestID))
    let psSettings = storage.get("ProblemSolvingSettings")
    console.log(problemCode)
    console.log(psSettings)
    console.log("새로고침")
    if(psSettings){
      next(vm => {
        vm.fontSize = psSettings.fontSize
        vm.theme = psSettings.theme
      })
    }
    else{
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
    console.log(this.fontSize)
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
        if (problem.statistic_info) {
          this.changePie(problem)
        }

        // 在beforeRouteEnter中修改了, 说明本地有code，无需加载template
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
    changePie(problemData) {
      // 只显示特定的一些状态
      for (let k in problemData.statistic_info) {
        if (filtedStatus.indexOf(k) === -1) {
          delete problemData.statistic_info[k]
        }
      }
      let acNum = problemData.accepted_number
      let data = [
        {name: 'WA', value: problemData.submission_number - acNum},
        {name: 'AC', value: acNum}
      ]
      this.pie.series[0].data = data
      // 只把大图的AC selected下，这里需要做一下deepcopy
      let data2 = JSON.parse(JSON.stringify(data))
      data2[1].selected = true
      this.largePie.series[1].data = data2

      // 根据结果设置legend,没有提交过的legend不显示
      let legend = Object.keys(problemData.statistic_info).map(ele => JUDGE_STATUS[ele].short)
      if (legend.length === 0) {
        legend.push('AC', 'WA')
      }
      this.largePie.legend.data = legend

      let acCount = problemData.statistic_info['0']
      delete problemData.statistic_info['0']

      let largePieData = []
      Object.keys(problemData.statistic_info).forEach(ele => {
        largePieData.push({name: JUDGE_STATUS[ele].short, value: problemData.statistic_info[ele]})
      })
      largePieData.push({name: 'AC', value: acCount})
      this.largePie.series[0].data = largePieData
    },
    handleRoute(route) {
      this.$router.push(route)
    },
    scrollField() {
      this.$refs.field.scrollIntoView({behavior: 'smooth'})
    },
    scrollCategory() {
      this.$refs.category.scrollIntoView({behavior: 'smooth'})
    },
    changeLanguage(newLang) {
      console.log("newLang : ", newLang)
      if (this.problem.template[newLang]) {
        if (this.code.trim() === '') {
          this.code = this.problem.template[newLang]
        }
      }
      this.language = newLang
      this.$refs.myCm.onLangChange(newLang)
    },
    changeFontSize(value){
      if(value > 18){
        alert("최대 크기입니다")
        return
      }
      if(value < 10){
        alert("최소 크기입니다")
        return
      }
      console.log("폰트변경:",value)
      this.$refs.myCm.changeFontSize(value)
      this.fontSize = value
    },
    check(){
      alert(this.code)
      alert(this.fontSize)
    },
    onChangeTheme(newTheme) {
      this.theme = newTheme
    },
    onResetToTemplate() {
      this.$Modal.confirm({
        content: this.$i18n.t('m.Are_you_sure_you_want_to_reset_your_code'),
        onOk: () => {
          let template = this.problem.template
          if (template && template[this.language]) {
            this.code = template[this.language]
          } else {
            this.code = ''
          }
          this.$refs.myCm.resetCM()
        }
      })
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
    onCopy(event) {
      this.$success('Code copied')
    },
    onCopyError(e) {
      this.$error('Failed to copy code')
    },
    noticeUnReadyFeature(){
      alert("준비 중인 기능입니다.")
    },
    toggleDropdown(type) {
      if (type === 'field') {
        this.dropdown.openFieldDropdown = !this.dropdown.openFieldDropdown
        return
      }
      this.dropdown.openCategoryDropdown = !this.dropdown.openCategoryDropdown
    }
  },
  computed: {
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
    storage.set("ProblemSolvingSettings",{
      theme: this.theme,
      fontsize: this.fontSize
    })
    next()
  },
  watch: {
    '$route'() {
      this.init()
    },
    isDarkMode(value){
      if(value){
        this.$refs.myCm.toggleTheme('ayu-mirage')
      }
      else{
        this.$refs.myCm.toggleTheme('github-light')
      }
      this.theme = value
    }
  }
}
</script>

<style lang="less">
.card-title {
  margin-left: 8px;
}
.detailCard{
  border: none;
  background-color: var(--bg-color);
  color: var(--text-color);
}
.flex-container {
  display: flex;
  //flex-direction: column;

  #problem-main {
    flex: auto;
    margin-right: 18px;
  }

  #right-column {
    flex: none;
    width: 220px;
  }

  .container-header {
    transition: 0.3s;
    display: flex;
    justify-content: space-between;
    height: 40px;
    width: 100%;
    align-items: center;
    border: 1px solid var(--border-color);
    padding-right: 10px;
    padding-left: 20px;
    border-radius: 7px;
    margin-bottom: 10px;
    span {
      margin-left: 10px;
      font-size: medium;
      font-weight: bold;
    }

    .submitBtn {
      padding-left: 10px;
      padding-right: 10px;
      padding-top: 5px;
      padding-bottom: 5px;
      background-color: var(--custom-btn-hover-color);
      border-radius: 7px;
      cursor: pointer;
    }

    .submitBtn:hover {
      background-color: #eaeaea;
    }
  }

  .problemDetailContainer {
    border: 1px solid var(--border-color);
    border-radius: 7px;
    height: calc(100vh - 80px);
    overflow: scroll;
    min-width: 32vw;
    overflow-x: hidden;
  }
}

.headerDetailBtn {
  background-color: var(--header-btn-color);
  cursor: pointer;
  font-weight: 550;
  padding-left: 8px;
  padding-right: 8px;
  padding-top: 3px;
  padding-bottom: 3px;
  margin-right: 10px;
  border-radius: 8px;

  i {
    margin-right: 5px;
  }
}

.headerDetailBtn:hover {
  //background-color: rgba(236, 236, 236, 0.45);
  color: var(--text-color);
  background-color: var(--custom-btn-hover-color);
}

#problem-content {
  margin-top: -50px;

  .title {
    font-size: 16.5px;
    font-weight: 750;
    margin: 25px 0 8px 0;
    color: var(--text--color);
    text-decoration: underline;
    text-decoration-color: rgba(96, 113, 185, 0.55);
    text-decoration-thickness: 2px;
    text-underline-offset: 6px;

    .copy {
      padding-left: 8px;
    }
  }


  p.content {
    font-size: 15px;
    font-weight: 600;
  }

  .sample {
    display: flex;
    justify-content: space-around;
    align-items: stretch;

    &-input, &-output {
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
      //border: var(--border-color);
      background: var(--bg-color);
    }
  }
  code{
    color: #1f2430 !important;
  }
}

#submit-code {
  margin-top: 20px;
  margin-bottom: 20px;

  .status {
    float: left;

    span {
      margin-right: 10px;
      margin-left: 10px;
    }
  }

  .captcha-container {
    display: inline-block;

    .captcha-code {
      width: auto;
      margin-top: -20px;
      margin-left: 20px;
    }
  }
}

#info {
  margin-bottom: 20px;
  margin-top: 20px;

  ul {
    list-style-type: none;

    li {
      border-bottom: 1px dotted #e9eaec;
      margin-bottom: 10px;

      p {
        display: inline-block;
      }

      p:first-child {
        width: 90px;
      }

      p:last-child {
        float: right;
      }
    }
  }
}

.fl-right {
  float: right;
}

#pieChart {
  .echarts {
    height: 250px;
    width: 210px;
  }

  #detail {
    position: absolute;
    right: 10px;
    top: 10px;
  }
}

#pieChart-detail {
  margin-top: 20px;
  width: 500px;
  height: 480px;
}

.dropdown {
  cursor: pointer;
  padding-left: 15px;
  padding-right: 15px;
  border-radius: 7px;
  margin-right: 10px;
}

.detailInfoBox {
  margin-top: 30px;
  height: 30px;
  padding-left: 20px;
  padding-right: 30px;
  padding-top: 15px;
  cursor: pointer;
  border-top: 1px solid #e7e7e7;

  .detailInfoBoxHeader {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}

.splitpanes {
  background: var(--bg-color);
}

.splitpanes__pane {
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background-color: var(--bg-color);
  color: var(--text-color);
}

.sticky_ln_col{
  position: sticky;
  float: right;
  right: 10px;
  bottom: 2px;
}

.splitpanes--vertical > .splitpanes__splitter {
  min-width: 4px;
  margin-top: 44vh;
  margin-bottom: 44vh;
  border-radius: 10px;
  background-color: #e7e7e7;
}

.splitpanes--horizontal > .splitpanes__splitter {
  min-height: 4px;
  padding-left: 47%;
  padding-right: 47%;
  border-radius: 10px;
  background-color: #e7e7e7;
  background-clip: content-box;
}

.splitpanes--vertical > .splitpanes__splitter:hover {
  background-color: #b6b6b6;
}

.splitpanes--horizontal > .splitpanes__splitter:hover {
  background-color: #b6b6b6;
}

</style>

