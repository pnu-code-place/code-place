<template>
  <main>
    <ErrorSign v-if="this.error" :code="this.error.code || 404" :description="this.error.description || ''"
      :solution="this.error.solution || ''" />
    <div class="contents" v-else>
      <div class="session-title-wrapper">
        <h1 class="session-title main-title">
          <Icon type="ios-chatbubbles" size="32"></Icon>
          {{ $t("m.Community") }}
        </h1>
        <div class="stats-info">
          <span class="total-posts">총 {{ total }}개의 게시글</span>
        </div>
      </div>
      <div class="box-wrapper">
        <div class="left-container">
          <div class="posts-list">
            <div v-for="post in posts" :key="post.id" @click="goToPost(post.id)" class="post-card">
              <div class="card-left">
                <div class="post-meta">
                  <span class="post-id">#{{ post.id }}</span>
                  <span v-if="POST_TYPE[post.post_type]" class="post-type-label" :style="{
                    backgroundColor: POST_TYPE[post.post_type].color,
                    color: POST_TYPE[post.post_type].textColor
                  }">
                    {{ POST_TYPE[post.post_type].name }}
                  </span>
                  <span v-if="post.post_type === 'QUESTION' && QUESTION_STATUS[post.question_status]"
                    class="question-status-label" :style="{
                      backgroundColor: QUESTION_STATUS[post.question_status].color,
                      color: QUESTION_STATUS[post.question_status].textColor
                    }">
                    {{ QUESTION_STATUS[post.question_status].name }}
                  </span>
                </div>

                <div class="card-content">
                  <h3 class="post-title">{{ post.title }}</h3>
                  <p v-if="post.content_preview" class="post-preview">{{ post.content_preview }}</p>
                </div>

                <div class="card-footer">
                  <div class="author-info">
                    <router-link :to="{
                      name: 'user-home',
                      params: { username: post.author_name },
                    }" @click.native.stop>
                      <img class="avatar"
                        :src="post.author_avatar || 'https://cdn-icons-png.flaticon.com/512/473/473406.png'"
                        alt="avatar" />
                      <span class="author-name">{{ post.author_name }}</span>
                    </router-link>
                  </div>
                  <div class="post-stats">
                    <span class="post-date">
                      <Icon type="ios-time-outline"></Icon>
                      {{ post.created_at | localtime("YYYY.MM.DD") }}
                    </span>
                    <span class="comment-count">
                      <Icon type="ios-chatbubbles-outline"></Icon>
                      {{ post.comment_count || 0 }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <Pagination :total="total" :page-size.sync="query.limit" @on-change="handlePageChange"
            :current.sync="query.page" :show-sizer="true" @on-page-size-change="handleSizeChange"></Pagination>
        </div>
        <div class="right-container">
          <CreatePost />
        </div>
      </div>
    </div>
  </main>
</template>

<script>
import api from "../../api"
import Pagination from "@/pages/admin/components/Pagination.vue"
import ErrorSign from "../general/ErrorSign.vue"
import CreatePost from "./communityComponent/CreatePost.vue";
import { POST_TYPE, QUESTION_STATUS } from "../../../../utils/constants";

export default {
  name: "Community",
  components: {
    CreatePost,
    Pagination,
    ErrorSign,
  },
  mounted() {
    this.fetchPosts()
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
      },
    }
  },
  computed: {
    POST_TYPE() {
      return POST_TYPE;
    },
    QUESTION_STATUS() {
      return QUESTION_STATUS;
    },
  },
  methods: {
    async fetchPosts() {
      this.isLoading = true

      const offset = (this.query.page - 1) * this.query.limit

      api
        .getCommunityPostList(offset, this.query.limit)
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
  },
}
</script>

<style lang="less" scoped>
main {
  width: var(--global-width);

  .session-title-wrapper {
    margin: 0 4px 30px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 10px;
  }

  .session-title {
    font-weight: 700;
    font-size: 32px;
    color: #2c3e50;
    display: flex;
    align-items: center;
    gap: 12px;

    .ivu-icon {
      color: #3498db;
    }
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
}
</style>
