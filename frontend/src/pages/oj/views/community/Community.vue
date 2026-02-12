<template>
  <main>
    <ErrorSign
      v-if="this.error"
      :code="this.error.code || 404"
      :description="this.error.description || ''"
      :solution="this.error.solution || ''"
    />
    <div class="contents" v-else>
      <div class="box-wrapper">
        <div class="left-container">
          <div class="community-header">
            <div class="header-left">
              <div class="main-title">
                <h1 class="session-title main-title">{{ pageTitle }}</h1>
              </div>
              <div class="stats-info">
                <span class="total-posts">{{ total }}개의 게시글</span>
              </div>
            </div>
            <div class="header-right">
              <div class="search-bar">
                <Input
                  v-model="query.keyword"
                  placeholder="검색어를 입력하세요"
                  icon="ios-search-strong"
                  @on-enter="applySearch"
                />
              </div>

              <Dropdown @on-click="filter" trigger="click" class="dropdown">
                <span
                  style="
                    font-weight: bold;
                    font-size: 15px;
                    padding-right: 10px;
                  "
                >
                  {{
                    query.post_type === "ALL"
                      ? "전체"
                      : POST_TYPE[query.post_type].name
                  }}
                </span>
                <Icon type="arrow-down-b"></Icon>
                <Dropdown-menu slot="list">
                  <Dropdown-item :name="{ type: 'post_type', value: 'ALL' }"
                    >전체</Dropdown-item
                  >
                  <Dropdown-item
                    v-for="(val, k) in POST_TYPE"
                    :key="k"
                    :name="{ type: 'post_type', value: k }"
                  >
                    {{ val.name }}
                  </Dropdown-item>
                </Dropdown-menu>
              </Dropdown>

              <Dropdown
                v-if="query.post_type === 'QUESTION'"
                @on-click="filter"
                trigger="click"
                class="dropdown"
              >
                <span
                  style="
                    font-weight: bold;
                    font-size: 15px;
                    padding-right: 10px;
                  "
                >
                  {{
                    query.question_status === "ALL"
                      ? "전체"
                      : QUESTION_STATUS[query.question_status].name
                  }}
                </span>
                <Icon type="arrow-down-b"></Icon>
                <Dropdown-menu slot="list">
                  <Dropdown-item
                    :name="{ type: 'question_status', value: 'ALL' }"
                    >전체</Dropdown-item
                  >
                  <Dropdown-item
                    v-for="(val, k) in QUESTION_STATUS"
                    :key="k"
                    :name="{ type: 'question_status', value: k }"
                  >
                    {{ val.name }}
                  </Dropdown-item>
                </Dropdown-menu>
              </Dropdown>

              <Dropdown @on-click="filter" trigger="click" class="dropdown">
                <span
                  style="
                    font-weight: bold;
                    font-size: 15px;
                    padding-right: 10px;
                  "
                >
                  {{
                    SORT_TYPE[query.sort_type]
                      ? SORT_TYPE[query.sort_type].name
                      : "정렬"
                  }}
                </span>
                <Icon type="arrow-down-b"></Icon>
                <Dropdown-menu slot="list">
                  <Dropdown-item
                    v-for="(val, k) in SORT_TYPE"
                    :key="k"
                    :name="{ type: 'sort_type', value: k }"
                  >
                    {{ val.name }}
                  </Dropdown-item>
                </Dropdown-menu>
              </Dropdown>
            </div>
          </div>
          <div class="posts-list">
            <div
              v-for="post in posts"
              :key="post.id"
              @click="goToPost(post.id)"
              class="post-card"
            >
              <div class="card-left">
                <div class="post-meta">
                  <span class="post-id">#{{ post.id }}</span>
                  <span v-if="isNewPost(post)" class="new-badge">NEW</span>
                  <span
                    v-if="POST_TYPE[post.post_type]"
                    class="post-type-label"
                    :style="{
                      backgroundColor: POST_TYPE[post.post_type].color,
                      color: POST_TYPE[post.post_type].textColor,
                    }"
                  >
                    {{ POST_TYPE[post.post_type].name }}
                  </span>
                  <span
                    v-if="
                      post.post_type === 'QUESTION' &&
                      QUESTION_STATUS[post.question_status]
                    "
                    class="question-status-label"
                    :style="{
                      backgroundColor:
                        QUESTION_STATUS[post.question_status].color,
                      color: QUESTION_STATUS[post.question_status].textColor,
                    }"
                  >
                    {{ QUESTION_STATUS[post.question_status].name }}
                  </span>
                </div>
                <div class="card-content">
                  <h3 class="post-title">{{ post.title }}</h3>
                  <div
                    v-if="post.content_preview"
                    class="post-preview"
                    v-html="post.content_preview"
                  ></div>
                </div>

                <div class="card-footer">
                  <div class="author-info">
                    <router-link
                      :to="{
                        name: 'user-home',
                        params: { username: post.author_name },
                      }"
                      @click.native.stop
                    >
                      <img
                        class="avatar"
                        :src="
                          post.author_avatar ||
                          'https://cdn-icons-png.flaticon.com/512/473/473406.png'
                        "
                        alt="avatar"
                      />
                      <span class="author-name">{{ post.author_name }}</span>
                    </router-link>
                  </div>
                  <div class="post-stats">
                    <span class="post-date">
                      <Icon type="ios-time-outline"></Icon>
                      {{ post.created_at | localtime("YYYY.MM.DD") }}
                    </span>
                    <span class="comment-count">
                      <Icon type="ios-chatbubble"></Icon>
                      {{ post.comment_count || 0 }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <Pagination
            :total="total"
            :page-size.sync="query.limit"
            @on-change="handlePageChange"
            :current.sync="query.page"
            :show-sizer="true"
            @on-page-size-change="handleSizeChange"
          ></Pagination>
        </div>
        <div class="right-container">
          <CreatePost />
          <QuestionList />
        </div>
      </div>
    </div>
  </main>
</template>

<script>
import api from "../../api"
import Pagination from "@/pages/admin/components/Pagination.vue"
import ErrorSign from "../general/ErrorSign.vue"
import CreatePost from "./communityComponent/CreatePost.vue"
import {
  POST_TYPE,
  QUESTION_STATUS,
  SORT_TYPE,
} from "../../../../utils/constants"
import QuestionList from "./communityComponent/QuestionList.vue"

export default {
  name: "Community",
  components: {
    CreatePost,
    QuestionList,
    Pagination,
    ErrorSign,
  },
  mounted() {
    this.initRoute()
  },
  // url 변경 여부 탐지
  watch: {
    $route() {
      this.initRoute()
    },
  },
  data() {
    return {
      isLoading: false,
      error: null,
      posts: [],
      total: 0,
      query: {
        page: 1,
        limit: 10,
        post_type: "ALL",
        sort_type: "NEWEST",
        keyword: "",
        question_status: "ALL",
      },
    }
  },
  computed: {
    POST_TYPE() {
      return POST_TYPE
    },
    QUESTION_STATUS() {
      return QUESTION_STATUS
    },
    SORT_TYPE() {
      return SORT_TYPE
    },
    pageTitle() {
      if (this.$route.path === "/community/free") {
        return this.$t("m.Community_Free")
      } else if (this.$route.path === "/community/question") {
        return this.$t("m.Community_Question")
      }
      return this.$t("m.Community")
    },
  },
  created() {
    this.restoreState() // 복구 로직 실행
  },
  beforeRouteEnter(to, from, next) {
    if (from.name !== "community-detail") {
      sessionStorage.removeItem("community_restore_data")
    }
    next()
  },
  methods: {
    /**
     * 게시글이 3일 이내에 작성되었는지 확인
     */
    isNewPost(post) {
      if (!post || !post.created_at) return false
      const postDate = new Date(post.created_at)
      const now = new Date()
      const diffTime = Math.abs(now - postDate)
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      return diffDays <= 3
    },
    async fetchPosts() {
      this.isLoading = true

      const offset = (this.query.page - 1) * this.query.limit
      const serverPostType =
        this.query.post_type === "ALL" ? "" : this.query.post_type
      const questionStatus =
        this.query.question_status === "ALL" ? "" : this.query.question_status
      api
        .getCommunityPostList(
          offset,
          this.query.limit,
          serverPostType,
          questionStatus,
          null,
          null,
          this.query.keyword,
          this.query.sort_type,
        )
        .then((res) => {
          this.posts = res.data.data.results
          this.total = res.data.data.total
        })
        .catch((err) => {
          // TODO: 현재 프론트엔드 버전 상 Optional Chaining 문법을 사용할 수 없습니다.
          // 만약 사용 가능하다면, err?.response?.status 와 같은 문법으로 변경해야 합니다.
          this.error = {
            code: (err.response && err.response.status) || 500,
            description:
              (err.response &&
                err.response.data &&
                err.response.data.message) ||
              this.$t("m.Community_Default_Error_Description"),
            solution: this.$t("m.Community_Default_Error_Solution"),
          }
        })
        .finally(() => {
          this.isLoading = false
        })
    },
    handlePageChange(page) {
      this.query.page = page
      this.fetchPosts()
    },
    handleSizeChange(size) {
      this.query.page = 1
      this.query.limit = size
      this.fetchPosts()
    },
    goToPost(postId) {
      this.$router.push({ name: "community-detail", params: { postId } })
    },
    filter({ type, value }) {
      const q = this.query
      q.page = 1

      if (type === "post_type") {
        q.post_type = value
        if (value !== "QUESTION") {
          q.question_status = "ALL"
        }
      }

      if (type === "sort_type") {
        q.sort_type = value
      }

      if (type === "question_status") {
        q.question_status = value
      }

      this.fetchPosts()
    },
    applySearch() {
      this.query.page = 1
      this.fetchPosts()
    },
    restoreState() {
      const savedJSON = sessionStorage.getItem("communityState")
      if (!savedJSON) return false

      const savedData = JSON.parse(savedJSON)

      if (savedData.routeName === this.$route.name) {
        this.query = savedData.query
        this.fetchPosts()
        return true
      }
      return false
    },
    // mount시, 쿼리통해 라우팅
    initRoute() {
      if (this.restoreState()) {
        return
      }

      this.query.post_type = "ALL"
      this.query.question_status = "ALL"
      this.query.sort_type = "NEWEST"
      if (this.$route.path === "/community/free") {
        this.query.post_type = "ARTICLE"
      } else if (this.$route.path === "/community/question") {
        this.query.post_type = "QUESTION"
        this.query.question_status = "OPEN"
      }
      this.query.page = 1
      this.fetchPosts()
    },
  },
  beforeRouteLeave(to, from, next) {
    if (to.name === "community-detail") {
      const stateToSave = {
        query: this.query,
        routeName: from.name,
      }
      sessionStorage.setItem("communityState", JSON.stringify(stateToSave))
    } else {
      sessionStorage.removeItem("communityState")
    }
    next()
  },
}
</script>

<style lang="less" scoped>
main {
  width: var(--global-width);

  .community-header {
    margin: 0 4px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 10px;
  }

  .session-title {
    font-weight: 700;
  }

  .stats-info {
    .total-posts {
      font-size: 14px;
      color: #7f8c8d;
      background: #ecf0f1;
      padding: 6px 16px;
      border-radius: 20px;
      font-weight: 500;
    }
  }

  .box-wrapper {
    display: flex;
    justify-content: space-between;
    gap: 24px;
  }

  .left-container {
    flex: 1;
    min-width: 0;
  }

  .right-container {
    width: 320px;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .posts-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin-bottom: 30px;
  }

  .post-card {
    background: white;
    border-radius: 12px;
    border: 1px solid #e8ecef;
    padding: 24px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);

    &:hover {
      transform: translateX(4px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
      border-color: #3498db;

      .post-title {
        color: #3498db;
      }
    }

    .card-left {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .post-meta {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .post-id {
      font-size: 13px;
      font-weight: 600;
      color: #95a5a6;
      background: #f8f9fa;
      padding: 4px 10px;
      border-radius: 6px;
    }

    .new-badge {
      font-size: 12px;
      font-weight: 700;
      color: #ffffff;
      background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
      padding: 4px 10px;
      border-radius: 12px;
      white-space: nowrap;
      animation: pulse 2s ease-in-out infinite;
      box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
    }

    @keyframes pulse {
      0%,
      100% {
        transform: scale(1);
      }

      50% {
        transform: scale(1.05);
      }
    }

    .post-type-label {
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      white-space: nowrap;
      transition: all 0.2s ease;
    }

    .question-status-label {
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      white-space: nowrap;
      transition: all 0.2s ease;
    }

    .card-content {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .post-title {
      font-size: 20px;
      font-weight: 600;
      color: #2c3e50;
      line-height: 1.4;
      margin: 0;
      transition: color 0.3s ease;
      word-break: break-word;
    }

    .post-preview {
      font-size: 14px;
      color: #7f8c8d;
      line-height: 1.6;
      margin: 0;
      overflow: hidden;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      line-clamp: 2;
      -webkit-box-orient: vertical;
      text-overflow: ellipsis;
    }

    .card-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 16px;
      border-top: 1px solid #f0f3f7;
    }

    .author-info {
      a {
        display: flex;
        align-items: center;
        text-decoration: none;
        color: #495060;
        transition: all 0.2s ease;
        gap: 10px;

        &:hover {
          color: #3498db;

          .avatar {
            transform: scale(1.1);
            border-color: #3498db;
          }
        }
      }

      .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: 2px solid #f0f3f7;
        transition: all 0.3s ease;
        object-fit: cover;
      }

      .author-name {
        font-size: 14px;
        font-weight: 500;
      }
    }

    .post-stats {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .post-date {
      font-size: 12px;
      color: #95a5a6;
      display: flex;
      align-items: center;
      gap: 5px;
      background: #f8f9fa;
      padding: 4px 10px;
      border-radius: 12px;
      font-weight: 500;

      .ivu-icon {
        font-size: 14px;
      }
    }

    .comment-count {
      font-size: 13px;
      color: #7f8c8d;
      display: flex;
      align-items: center;
      gap: 5px;
      background: #f8f9fa;
      padding: 4px 10px;
      border-radius: 12px;
      font-weight: 500;

      .ivu-icon {
        font-size: 15px;
      }
    }
  }

  .header-right {
    display: flex;
  }

  .header-left {
    display: flex;
    gap: 8px;
    align-items: center;
  }
}

.search-bar {
  width: 190px;

  /deep/ .ivu-input {
    background: #fff;
    color: #515a6e;
    border: 1px solid #dcdee2;

    &::placeholder {
      color: #515a6e;
      opacity: 0.4;
    }

    &:focus {
      border-color: #2d8cf0;
      box-shadow: 0 0 0 3px rgba(45, 140, 240, 0.2);
    }
  }
}

.dropdown {
  cursor: pointer;
  padding-top: 4px;
  padding-bottom: 4px;
  padding-left: 15px;
  padding-right: 15px;
  background-color: #fff;
  border-radius: 7px;
  border: 1px solid #dedede;
  display: flex;
  align-items: center;
}

.dropdown:not(:first-child) {
  margin-left: 5px;
}
</style>
