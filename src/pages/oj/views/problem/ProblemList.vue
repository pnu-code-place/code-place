<template>
  <div class="mainBox">
    <div class="boxWrapper">
      <div class="left-container">
        <div class="problemListTableHeader">
          <p>문제</p>
          <div style="display: flex; align-items: center; justify-content: center">
            <li style="list-style-type: none; margin-left: 3px;">
              <Input v-model="query.keyword"
                     @on-enter="filterByKeyword"
                     @on-click="filterByKeyword"
                     placeholder="문제 제목 검색"
                     icon="ios-search-strong"/>
            </li>
            <Dropdown @on-click="filterByDifficulty" trigger="click" class="dropdown difficultyDropdown">
                          <span style="font-weight: bold; font-size: 15px; padding-right: 10px">{{
                              query.difficulty === '' ? this.$i18n.t('m.Difficulty') : this.$i18n.t('m.' + query.difficulty)
                            }}
                          </span>
              <Icon type="arrow-down-b"></Icon>
              <Dropdown-menu slot="list">
                <Dropdown-item name="">{{ $t('m.All') }}</Dropdown-item>
                <Dropdown-item name="VeryLow">{{ $t('m.VeryLow') }}</Dropdown-item>
                <Dropdown-item name="Low">{{ $t('m.Low') }}</Dropdown-item>
                <Dropdown-item name="Mid">{{ $t('m.Mid') }}</Dropdown-item>
                <Dropdown-item name="High">{{ $t('m.High') }}</Dropdown-item>
                <Dropdown-item name="VeryHigh">{{ $t('m.VeryHigh') }}</Dropdown-item>
              </Dropdown-menu>
            </Dropdown>
            <Dropdown @on-click="filterByField" trigger="click" class="dropdown fieldDropdown">
                          <span style="font-weight: bold; font-size: 15px; padding-right: 10px">{{
                              query.field === '' ? this.$i18n.t('m.Field') : fieldMap[query.field].value
                            }}
                          </span>
              <Icon type="arrow-down-b"></Icon>
              <Dropdown-menu slot="list">
                <Dropdown-item name="">{{ $t('m.All') }}</Dropdown-item>
                <Dropdown-item name="0">{{ $t('m.Field_Impl') }}</Dropdown-item>
                <Dropdown-item name="2">{{ $t('m.Field_DataStructure') }}</Dropdown-item>
                <Dropdown-item name="1">{{ $t('m.Field_Math') }}</Dropdown-item>
                <Dropdown-item name="3">{{ $t('m.Field_Search') }}</Dropdown-item>
                <Dropdown-item name="4">{{ $t('m.Field_Sorting') }}</Dropdown-item>
              </Dropdown-menu>
            </Dropdown>
            <Dropdown @on-click="filterByTag" trigger="click" class="dropdown difficultyDropdown">
                          <span style="font-weight: bold; font-size: 15px; padding-right: 10px">{{
                              query.tag === '' ? this.$i18n.t('m.Category') : this.$i18n.t('m.' + query.tag)
                            }}
                          </span>
              <Icon type="arrow-down-b"></Icon>
              <Dropdown-menu slot="list">
                <Dropdown-item name="All">{{ $t('m.All') }}</Dropdown-item>
                <template v-for="(problem, idx) in problemList">
                  <template v-for="(problemTag, idx) in problem.tags">
                    <Dropdown-item name="" >{{ problemTag }}</Dropdown-item>
                  </template>
                </template>
              </Dropdown-menu>
            </Dropdown>
            <div class="moreOptionSelector">
              <Icon type="ios-more" size="20" color="#7a7a7a"></Icon>
            </div>

          </div>

        </div>
        <table>
          <thead>
          <tr>
            <th class="th-first">문제번호</th>
            <th class="th-second">제목</th>
            <th class="th-third">난이도</th>
            <th class="th-fourth">완료한 사람</th>
            <th class="th-fifth">정답률</th>
          </tr>
          </thead>

          <template v-if="problemList.length !== 0">
            <tbody>
            <tr v-for="(problem, idx) in this.problemList">
              <td class="td-first">{{ problem._id }}</td>
              <td class="td-second" @click="enterProblemDetail(problem._id)">
                <span class="problemTitle">
                  {{ problem.title }}
                </span>
                <br>
                <div style="display: flex">
                  <FieldCategoryBox :boxType="true" :value="fieldMap[problem.field].value"
                                    :boxColor="fieldMap[problem.field].boxColor"/>
                  <template v-for="(category, idx) in problem.tags">
                    <FieldCategoryBox :boxType="false" :value="'#' + category" :boxColor="white"/>
                  </template>
                </div>
              </td>
              <td class="td-third" style="font-weight: bold; font-size: 12px">{{ difficultyMap[problem.difficulty].value }}</td>
              <!-- 푼 사람 수 기입해야함. 일단 난수 처리 -->
              <td class="td-fourth">{{ Math.floor(Math.random() * 101) }}</td>
              <!-- 정답률 기입해야함. 일단 난수 처리 -->
              <td class="td-fifth">{{ Math.floor(Math.random() * 101) + '%' }}</td>
              <!--              <td class="td-fifth">{{ problem.accepted_number / problem.submission_number }}</td>-->
            </tr>
            </tbody>
          </template>

        </table>
        <template v-if="problemList.length === 0">
          <div class="noProblemListBox">
            문제가 존재하지 않습니다.
          </div>
        </template>
        <Pagination
          :total="total" :page-size.sync="query.limit" @on-change="pushRouter" @on-page-size-change="pushRouter"
          :current.sync="query.page" :show-sizer="true">
        </Pagination>
      </div>
      <div class="right-container">
        <div class="recommendationBox">
          <div class="recommendationBoxHeader">
            <span class="animation">이번 주에 가장 어려웠어요!<img src="@/assets/fireIcon.png" width="15"
                                                        style="padding-top: 1px"/></span>
          </div>
          <div class="hardProblemRecommendationBoxBody">
            <div class="hardProblemFieldCategory">
              <!--              더미 데이터로 문제들 중 첫번째 것 뽑아서 우선 배치해놓겠음.-->
              <FieldCategoryBox :boxType="true" :value="fieldMap[this.problemList[1].field].value"
                                :boxColor="fieldMap[this.problemList[1].field].boxColor"/>
              <template v-for="(category, idx) in this.problemList[1].tags">
                <FieldCategoryBox :boxType="false" :value="'#' + category" :boxColor="white"/>
              </template>
            </div>
            <div class="hardProblemFieldCategory" style="justify-content: space-between; margin-top: 2px">
              <span style="font-weight: bold;font-size: medium">{{ this.problemList[1].title }}</span>
              <a style="color: #7a7a7a; text-decoration: underline" @click="enterProblemDetail(this.problemList[1]._id)">도전하기</a>
            </div>
            <div class="hardProblemInfo" style="margin-top: 15px">
              <div style="display: flex; justify-content: space-between; width: 50%; float: right">
                <span>정답률</span>
                <span>12%</span>
              </div>
            </div>
            <br>
            <div class="hardProblemInfo" style="margin-top: 5px">
              <div style="display: flex; justify-content: space-between; width: 50%; float: right">
                <span>완료한 사람</span>
                <span>7명</span>
              </div>
            </div>
            <br>
            <div class="hardProblemInfo" style="margin-top: 5px; margin-bottom: 20px">
              <div style="display: flex; justify-content: space-between; width: 50%; float: right">
                <span>난이도</span>
                <span style="color: #c02b2b; font-weight: bolder">매우 어려움</span>
              </div>
            </div>
          </div>
        </div>
        <div class="aiRecommendationBox">
          <div class="recommendationBoxHeader">
            <span class="aiRecommendationSpan">AI 추천 문제</span>
            <div>
              <Icon type="ios-information-outline" size="13" color="#7a7a7a"></Icon>
              <span>맞춤 문제를 추천해드려요!</span>
            </div>
          </div>
          <div style="text-align: center; margin-top: 10px; padding-left: 10px">
            <ECharts :options="radarGraph" :initOptions="radarInitOpts"
                     style="height: fit-content; width: fit-content"></ECharts>
          </div>
          <div class="aiSolution">
            <span style="font-weight: bold; padding-right: 4px">{{user.username+' 님, '}}</span>
            <FieldCategoryBox :boxType="true" :value="'수학'" :boxColor="'#B5EAB0'"/>
            <span>영역을 더 풀어보세요!</span>
          </div>
          <div class="aiRecommendProblem">
            <span style="font-weight: bold; font-size: 15px">
              더 크게 합치기
            </span>
            <a style="text-decoration: underline; color: #7a7a7a">
            풀어보기
            </a>
          </div>
          <div class="aiRecommendProblem">
            <span style="font-weight: bold; font-size: 15px">
              주사위 게임 2
            </span>
            <a style="text-decoration: underline; color: #7a7a7a">
              풀어보기
            </a>
          </div>
          <div class="aiRecommendProblem">
            <span style="font-weight: bold; font-size: 15px">
              원소들의 곱과 합
            </span>
            <a style="text-decoration: underline; color: #7a7a7a">
              풀어보기
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!--  <Row type="flex" :gutter="18">-->
  <!--    <Col :span=18>-->
  <!--    <Panel shadow>-->
  <!--      <div slot="title">{{$t('m.Problem_List')}}</div>-->
  <!--      <div slot="extra">-->
  <!--        <ul class="filter">-->
  <!--          <li>-->
  <!--            <Dropdown @on-click="filterByDifficulty">-->
  <!--              <span>{{query.difficulty === '' ? this.$i18n.t('m.Difficulty') : this.$i18n.t('m.' + query.difficulty)}}-->
  <!--                <Icon type="arrow-down-b"></Icon>-->
  <!--              </span>-->
  <!--              <Dropdown-menu slot="list">-->
  <!--                <Dropdown-item name="">{{$t('m.All')}}</Dropdown-item>-->
  <!--                <Dropdown-item name="VeryLow">{{$t('m.VeryLow')}}</Dropdown-item>-->
  <!--                <Dropdown-item name="Low">{{$t('m.Low')}}</Dropdown-item>-->
  <!--                <Dropdown-item name="Mid" >{{$t('m.Mid')}}</Dropdown-item>-->
  <!--                <Dropdown-item name="High">{{$t('m.High')}}</Dropdown-item>-->
  <!--                <Dropdown-item name="VeryHigh">{{$t('m.VeryHigh')}}</Dropdown-item>-->
  <!--              </Dropdown-menu>-->
  <!--            </Dropdown>-->
  <!--          </li>-->
  <!--&lt;!&ndash;          <li>&ndash;&gt;-->
  <!--&lt;!&ndash;            <i-switch size="large" @on-change="handleTagsVisible">&ndash;&gt;-->
  <!--&lt;!&ndash;              <span slot="open">{{$t('m.Tags')}}</span>&ndash;&gt;-->
  <!--&lt;!&ndash;              <span slot="close">{{$t('m.Tags')}}</span>&ndash;&gt;-->
  <!--&lt;!&ndash;            </i-switch>&ndash;&gt;-->
  <!--&lt;!&ndash;          </li>&ndash;&gt;-->
  <!--          <li>-->
  <!--            <Input v-model="query.keyword"-->
  <!--                   @on-enter="filterByKeyword"-->
  <!--                   @on-click="filterByKeyword"-->
  <!--                   placeholder="키워드"-->
  <!--                   icon="ios-search-strong"/>-->
  <!--          </li>-->
  <!--&lt;!&ndash;          <li>&ndash;&gt;-->
  <!--&lt;!&ndash;            <Button type="info" @click="onReset">&ndash;&gt;-->
  <!--&lt;!&ndash;              <Icon type="refresh"></Icon>&ndash;&gt;-->
  <!--&lt;!&ndash;              {{$t('m.Reset')}}&ndash;&gt;-->
  <!--&lt;!&ndash;            </Button>&ndash;&gt;-->
  <!--&lt;!&ndash;          </li>&ndash;&gt;-->
  <!--        </ul>-->
  <!--      </div>-->
  <!--      <Table class="problemListTable"-->
  <!--             :columns="problemTableColumns"-->
  <!--             :data="problemList"-->
  <!--             :loading="loadings.table"-->
  <!--             disabled-hover></Table>-->
  <!--    </Panel>-->
  <!--    <Pagination-->
  <!--      :total="total" :page-size.sync="query.limit" @on-change="pushRouter" @on-page-size-change="pushRouter" :current.sync="query.page" :show-sizer="true"></Pagination>-->
  <!--    </Col>-->

  <!--    <Col :span="6">-->
  <!--    <Panel :padding="10">-->
  <!--      <div slot="title" class="taglist-title">{{$t('m.Tags')}}</div>-->
  <!--      <Button v-for="tag in tagList"-->
  <!--              :key="tag.name"-->
  <!--              @click="filterByTag(tag.name)"-->
  <!--              type="ghost"-->
  <!--              :disabled="query.tag === tag.name"-->
  <!--              shape="circle"-->
  <!--              class="tag-btn">{{tag.name}}-->
  <!--      </Button>-->
  <!--      <div slot="title" class="taglist-title">{{$t('m.Tags')}}</div>-->
  <!--    </Panel>-->

  <!--      <Panel :padding="10">-->
  <!--        <div slot="title" class="taglist-title">{{$t('m.AiRecommendation')}}</div>-->
  <!--        <div>로그인 후 이용 가능합니다.</div>-->
  <!--      </Panel>-->
  <!--    <Spin v-if="loadings.tag" fix size="large"></Spin>-->
  <!--    </Col>-->
  <!--  </Row>-->
</template>

<script>
import {mapActions, mapGetters} from 'vuex'
import api from '@oj/api'
import utils from '@/utils/utils'
import {ProblemMixin} from '@oj/components/mixins'
import Pagination from '@oj/components/Pagination'
import FieldCategoryBox from "../../components/FieldCategoryBox.vue";
import {radarGraph} from "./chartData";
import "echarts"


export default {
  name: 'ProblemList',
  mixins: [ProblemMixin],
  components: {
    FieldCategoryBox,
    Pagination,
  },
  data() {
    return {
      tagList: [],
      radarInitOpts: {
        width: '240',
        height: '250'
      },
      radarGraph: radarGraph,
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
          'boxColor': '#F8D093'
        }
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
      problemTableColumns: [
        {
          title: '문제번호',
          key: '_id',
          width: 140,
          render: (h, params) => {
            return h('Button', {
              props: {
                type: 'text',
                size: 'large'
              },
              on: {
                click: () => {
                  this.$router.push({name: 'problem-details', params: {problemID: params.row._id}})
                }
              },
              style: {
                padding: '2px 0'
              }
            }, '#' + params.row._id)
          }
        },
        {
          title: this.$i18n.t('m.Title'),
          width: 200,
          render: (h, params) => {
            return h('Button', {
              props: {
                type: 'text',
                size: 'large'
              },
              on: {
                click: () => {
                  this.$router.push({name: 'problem-details', params: {problemID: params.row._id}})
                }
              },
              style: {
                padding: '2px 0',
                overflowX: 'auto',
                textAlign: 'left',
                width: '100%'
              }
            }, params.row.title)
          }
        },
        {
          title: this.$i18n.t('m.Level'),
          render: (h, params) => {
            let t = params.row.difficulty
            let color = 'blue'
            if (t === 'Low') color = 'green'
            else if (t === 'High') color = 'yellow'
            return h('Tag', {
              props: {
                color: color
              }
            }, this.$i18n.t('m.' + params.row.difficulty))
          }
        },
        // {
        //   title: this.$i18n.t('m.Total'),
        //   key: 'submission_number'
        // },
        {
          title: this.$i18n.t('m.AC_Rate'),
          render: (h, params) => {
            return h('span', this.getACRate(params.row.accepted_number, params.row.submission_number))
          }
        }
      ],
      problemList: [],
      limit: 20,
      total: 0,
      loadings: {
        table: true,
        tag: true
      },
      routeName: '',
      query: {
        keyword: '',
        difficulty: '',
        field: '',
        category: '',
        tag: '',
        page: 1,
        limit: 10
      }
    }
  },
  mounted() {
    this.init()
  },
  methods: {
    ...mapActions(['changeDomTitle','changeProblemSolvingState']),
    init(simulate = false) {
      this.routeName = this.$route.name
      let query = this.$route.query
      this.query.difficulty = query.difficulty || ''
      this.query.keyword = query.keyword || ''
      this.query.field = query.field || ''
      this.query.tag = query.tag || ''
      this.query.page = parseInt(query.page) || 1
      if (this.query.page < 1) {
        this.query.page = 1
      }
      this.query.limit = parseInt(query.limit) || 10
      if (!simulate) {
        this.getTagList()
      }
      this.getProblemList()
    },
    pushRouter() {
      this.$router.push({
        name: 'problem-list',
        query: utils.filterEmptyValue(this.query)
      })
    },
    getProblemList() {
      let offset = (this.query.page - 1) * this.query.limit
      this.loadings.table = true
      api.getProblemList(offset, this.limit, this.query).then(res => {
        this.loadings.table = false
        this.total = res.data.data.total
        this.problemList = res.data.data.results
        console.log(this.problemList)
        if (this.isAuthenticated) {
          this.addStatusColumn(this.problemTableColumns, res.data.data.results)
        }
      }, res => {
        this.loadings.table = false
      })
    },
    enterProblemDetail(problemId) {
      this.changeProblemSolvingState(true)
      this.$router.push({name: 'problem-details', params: {problemID: problemId}})
    },
    getTagList() {
      api.getProblemTagList().then(res => {
        this.tagList = res.data.data
        this.loadings.tag = false
      }, res => {
        this.loadings.tag = false
      })
    },
    filterByTag(tagName) {
      this.query.tag = tagName
      this.query.page = 1
      this.pushRouter()
    },
    filterByCategory(categoryName) {
      this.query.tag = categoryName
      this.query.page = 1
      this.pushRouter()
    },
    filterByDifficulty(difficulty) {
      this.query.difficulty = difficulty
      this.query.page = 1
      this.pushRouter()
    },
    filterByField(field) {
      this.query.field = field
      this.query.page = 1
      this.pushRouter()
    },
    filterByKeyword(keyword) {
      this.query.page = 1
      this.pushRouter()
    },
    handleTagsVisible(value) {
      if (value) {
        this.problemTableColumns.push(
          {
            title: this.$i18n.t('m.Tags'),
            align: 'center',
            render: (h, params) => {
              let tags = []
              params.row.tags.forEach(tag => {
                tags.push(h('Tag', {}, tag))
              })
              return h('div', {
                style: {
                  margin: '8px 0'
                }
              }, tags)
            }
          })
      } else {
        this.problemTableColumns.splice(this.problemTableColumns.length - 1, 1)
      }
    },
    onReset() {
      this.$router.push({name: 'problem-list'})
    },
    pickone() {
      api.pickone().then(res => {
        this.$success('Good Luck')
        this.$router.push({name: 'problem-details', params: {problemID: res.data.data}})
      })
    }
  },
  computed: {
    ...mapGetters(['website', 'modalStatus', 'user', 'isAuthenticated', 'isAdminRole']),
  },
  watch: {
    '$route'(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.init(true)
      }
    },
    'isAuthenticated'(newVal) {
      if (newVal === true) {
        this.init()
      }
    }
  }
}
</script>

<style scoped lang="less">
.taglist-title {
  margin-left: -10px;
  margin-bottom: -10px;
}

.moreOptionSelector {
  text-align: center;
  padding-top: 7px;
  padding-bottom: 7px;
  padding-left: 10px;
  padding-right: 10px;
  cursor: pointer;
  border-radius: 7px;
  margin-left: 3px;
}

.moreOptionSelector:hover {
  background-color: rgba(221, 221, 221, 0.17);
}

.boxWrapper {
  display: flex;
  justify-content: space-between;
}

.left-container {
  width: 72%;
  height: 100%;
}

.right-container {
  width: 26%;
  height: auto;
}

.problemListTableHeader {
  display: flex;
  padding-left: 1%;
  margin-bottom: 25px;
  align-items: center;
  justify-content: space-between;

  p {
    font-weight: bold;
    font-size: 18px;
  }

  .dropdown {
    cursor: pointer;
    padding-top: 4px;
    padding-bottom: 4px;
    padding-left: 15px;
    padding-right: 15px;
    border-radius: 7px;
    border: 1px solid #dedede;
  }

  .dropdown:not(:first-child) {
    margin-left: 5px;
  }

  .difficultyDropdown {
    cursor: pointer;
  }


}

.problemListTable {
  background-color: #ffffff;
  border-radius: 7px;
  border: 1px solid #dedede;
  width: 100%;
  height: 800px;
  padding-left: 30px;
  padding-right: 30px;
  margin-bottom: 20px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.noProblemListBox {
  width: 100%;
  padding: 30px;
  text-align: center;
}

.recommendationBox {
  border-radius: 7px;
  border: 1px solid #dedede;
  width: 100%;
  height: 240px;
  margin-bottom: 20px;
  text-align: center;
  padding-left: 20px;
  padding-right: 20px;
  padding-top: 13px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);

  .hardProblemRecommendationBoxBody {
    border-radius: 7px;
    background-color: #FBFBFB;
    padding: 20px;

    .hardProblemFieldCategory {
      display: flex;
      align-items: center;
      justify-content: left;
    }

    .hardProblemInfo {

    }

  }
}

.recommendationBoxHeader {

  padding-top: 8px;
  padding-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  //border-bottom: 1px solid #dedede;

  span:first-child {
    font-weight: 650;
    font-size: 15px;
  }

  span:nth-child(2) {
    color: #7a7a7a;
    font-size: 12px;
  }

  .animation {
    display: inline-block;
    transform-origin: center;
    padding: 0 0.5rem;
    animation: animate 2s infinite;
  }

  @keyframes animate {
    0% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.05);
    }
    100% {
      transform: scale(1);
    }
  }
}

.aiRecommendationBox {
  border-radius: 7px;
  border: 1px solid #dedede;
  width: 100%;
  height: fit-content;
  margin-bottom: 20px;
  text-align: center;
  padding-left: 20px;
  padding-right: 20px;
  padding-top: 13px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);

  .aiRecommendationSpan {
    background: linear-gradient(
      to right,
      #7953cd 20%,
      #00affa 30%,
      #0190cd 70%,
      #764ada 80%
    );
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    text-fill-color: transparent;
    background-size: 500% auto;
    animation: textShine 3s ease-in-out infinite alternate;
  }
  @keyframes textShine {
    0% {
      background-position: 0% 50%;
    }
    100% {
      background-position: 100% 50%;
    }
  }
}

.tag-btn {
  margin-right: 5px;
  margin-bottom: 10px;
}

#pick-one {
  margin-top: 10px;
}

.aiSolution {
  display: flex;
  align-items: center;
  justify-content: center;
}

.aiRecommendProblem {
  border-radius: 7px;
  background-color: #FBFBFB;
  margin-top: 10px;
  margin-bottom: 10px;
  padding: 10px;
  padding-left: 10px;
  padding-right: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

table {
  border: 1px solid #dedede;
  padding-right: 20px;
  padding-left: 20px;
  font-size: .9em;
  width: 100%;
  border-radius: 7px;
  border-spacing: 0;
  overflow: hidden;
}

th:first-child {
  text-align: center;
}

th {
  text-align: center;
}

thead {
  font-weight: bold;
  color: #7E7E7E;

  .th-second {
    width: 470px;
  }
}

tbody {
  tr {
    td:first-child {
      text-align: center;
      font-weight: bold;
    }

    td:nth-child(2) {
      text-align: left;
      padding-left: 60px;
    }

    td {
      text-align: center;
    }

    .problemTitle {
      font-weight: bold;
      cursor: pointer;
      font-size: medium;
    }

    .problemTitle:hover {
      color: #4A86C0;
    }
  }
}

td, th {
  padding: 1.3em .5em;
  vertical-align: center;
}

td {
  background: #fff;
  border-top: 1px solid rgba(0, 0, 0, .1);
}

td:nth-child(2) {
  cursor: pointer;
}

@media all and (max-width: 768px) {

  table, thead, tbody, th, td, tr {
    display: block;
  }

  th {
    text-align: right;
  }

  table {
    position: relative;
    padding-bottom: 0;
    border: none;
    box-shadow: 0 0 10px rgba(0, 0, 0, .2);
  }

  thead {
    float: left;
    white-space: nowrap;
  }

  tbody {
    overflow-x: auto;
    overflow-y: hidden;
    position: relative;
    white-space: nowrap;
  }

  tr {
    display: inline-block;
    vertical-align: top;
  }

  th {
    border-bottom: 1px solid #a39485;
  }

  td {
    border-bottom: 1px solid #e5e5e5;
  }

}
</style>
