<template>
  <div class="problem-community-wrapper" :class="themeClass">
    <div class="community-header">
      <div class="header-left">
        <h3 class="community-title">
          {{ $t("m.Problem_Community_Question_List") }}
        </h3>
        <span class="question-count">{{ total }}{{ $t("m.Problem_Community_Question_Count") }}</span>
      </div>
      <div class="filter-bar">
        <div class="search-bar">
          <Input v-model="query.keyword" placeholder="검색어를 입력하세요" icon="ios-search-strong" @on-enter="applySearch">
          </Input>
        </div>
        <div class="question-status-bar">
          <Dropdown @on-click="filterByQuestionStatus" trigger="click" class="dropdown">
            <span style="font-weight: bold; font-size: 15px; padding-right: 10px">
              {{ query.question_status === 'ALL' ? '전체' : QUESTION_STATUS[query.question_status].name }}
            </span>
            <Icon type="arrow-down-b"></Icon>
            <Dropdown-menu slot="list">
              <Dropdown-item name="ALL">전체</Dropdown-item>
              <Dropdown-item v-for="(val, k) in QUESTION_STATUS" :key="k" :name="k">
                {{ val.name }}
              </Dropdown-item>
            </Dropdown-menu>
          </Dropdown>
        </div>
        <Button type="primary" size="default" @click="showCreateModal = true" class="create-btn">
          {{ $t("m.Problem_Community_Create_Question") }}
        </Button>
      </div>
    </div>

    <div v-if="isLoading" class="loading-state">
      <Spin size="large"></Spin>
    </div>

    <div v-else-if="error" class="error-state">
      <Icon type="ios-alert-outline" size="48"></Icon>
      <p>{{ error }}</p>
    </div>

    <div v-else-if="posts.length === 0" class="empty-state">
      <h4>{{ $t("m.Problem_Community_No_Questions") }}</h4>
      <p class="empty-subtitle">{{ $t("m.Problem_Community_No_Questions_Subtitle") }}</p>
      <Button type="primary" @click="showCreateModal = true" class="empty-action-btn">
        {{ $t("m.Problem_Community_First_Question") }}
      </Button>
    </div>

    <div v-else class="posts-list">
      <div v-for="post in posts" :key="post.id" class="post-item" @click="goToPost(post.id)">
        <div class="post-header">
          <div class="post-meta">
            <span class="post-id">#{{ post.id }}</span>
            <span v-if="isNewPost(post)" class="new-badge">NEW</span>
            <span v-if="post.post_type === 'QUESTION' && QUESTION_STATUS[post.question_status]"
              class="question-status-badge" :style="{
                backgroundColor: QUESTION_STATUS[post.question_status].color,
                color: QUESTION_STATUS[post.question_status].textColor
              }">
              {{ QUESTION_STATUS[post.question_status].name }}
            </span>
          </div>
          <h4 class="post-title">{{ post.title }}</h4>
        </div>
        <div v-if="post.content_preview" class="post-preview" v-html="post.content_preview"></div>
        <div class="post-footer">
          <div class="author-info">
            <img class="avatar" :src="post.author_avatar || defaultAvatar" alt="avatar" />
            <span class="author-name">{{ post.author_name }}</span>
          </div>
          <div class="post-stats">
            <span class="post-date">
              <Icon type="ios-time-outline"></Icon>
              {{ post.created_at | localtime("MM.DD HH:mm") }}
            </span>
            <span class="comment-count">
              <Icon type="ios-chatbubble"></Icon>
              {{ post.comment_count || 0 }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <Modal v-model="showCreateModal" :footer-hide="true" :closable="true" :mask-closable="false" width="800"
      class-name="create-question-modal">
      <div class="modal-header">
        <h2 class="modal-title">
          {{ $t("m.Problem_Community_Modal_Title") }}
        </h2>
        <div class="problem-info-card">
          <div class="problem-info-label">
            {{ $t("m.Problem_Community_Modal_Problem_Label") }}
          </div>
          <div class="problem-info-content">
            <span class="problem-number">{{ problem._id }}.</span>
            <span class="problem-title">{{ problem.title }}</span>
          </div>
        </div>
      </div>
      <Form :label-width="0" class="question-form">
        <FormItem class="form-item">
          <div class="input-label">
            {{ $t("m.Problem_Community_Modal_Title_Label") }}
          </div>
          <Input v-model="newPost.title" :placeholder="$t('m.Problem_Community_Modal_Title_Placeholder')"
            maxlength="100" show-word-limit size="large" />
        </FormItem>
        <FormItem class="form-item">
          <div class="input-label">
            {{ $t("m.Problem_Community_Modal_Content_Label") }}
          </div>
          <TiptapEditor v-model="newPost.content" minHeight="300px" :editable="true"
            :placeholder="$t('m.Problem_Community_Modal_Content_Placeholder')" />
        </FormItem>
      </Form>
      <div class="modal-footer">
        <Button @click="showCreateModal = false" size="large" class="cancel-btn">{{
          $t("m.Problem_Community_Modal_Cancel") }}</Button>
        <Button type="primary" @click="createPost" :loading="isCreating" size="large" class="submit-btn">
          {{ $t("m.Problem_Community_Modal_Submit") }}
        </Button>
      </div>
    </Modal>

    <div v-if="total > query.limit" class="pagination-wrapper">
      <Page :total="total" :page-size="query.limit" :current="query.page" @on-change="handlePageChange" size="small"
        show-total />
    </div>
  </div>
</template>

<script>
import api from "@oj/api"
import { DEFAULT_AVATAR, QUESTION_STATUS } from "@/utils/constants"
import { mapGetters } from "vuex"
import TiptapEditor from "../../../../components/TiptapEditor.vue"

export default {
  name: "ProblemCommunity",
  components: {
    TiptapEditor
  },
  props: {
    problemID: {
      type: String,
      required: true,
    },
    problem: {
      type: Object,
      required: true,
    },
    isDarkMode: {
      type: Boolean,
      default: false,
    }
  },
  data() {
    return {
      posts: [],
      total: 0,
      isLoading: false,
      error: null,
      showCreateModal: false,
      isCreating: false,
      newPost: {
        title: "",
        content: "",
      },
      query: {
        page: 1,
        limit: 10,
        keyword: "",
        question_status: "ALL",
      },
    }
  },
  mounted() {
    // problem.id가 로드 된 후 fetchPosts 호출
    if (this.problem && this.problem.id) {
      this.fetchPosts()
    }
  },
  computed: {
    ...mapGetters(["user"]),
    themeClass() {
      return this.isDarkMode ? "dark-theme" : "light-theme"
    },
    QUESTION_STATUS() {
      return QUESTION_STATUS
    },
    defaultAvatar() {
      return DEFAULT_AVATAR
    },
  },
  watch: {
    // NOTE: problem prop이 변경될 때 (로드될 때) fetchPosts 호출
    // 이 로직이 없으면 문제 정보가 로드되기 전에 mounted 훅에서
    // fetchPosts가 호출되어 문제 ID가 undefined 인 경우가 발생합니다.
    'problem.id': {
      handler(newVal) {
        if (newVal) {
          this.fetchPosts()
        }
      },
      immediate: false
    }
  },
  methods: {
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
      this.error = null

      const offset = (this.query.page - 1) * this.query.limit
      const questionStatus = this.query.question_status === "ALL" ? "" : this.query.question_status

      try {
        // problem_id를 파라미터로 전달하여 해당 문제의 질문만 가져옴
        const res = await api.getCommunityPostList(
          offset,
          this.query.limit,
          'QUESTION',
          questionStatus,
          this.problem.id,
          null,
          this.query.keyword,
          null
        )
        this.posts = res.data.data.results
        this.total = res.data.data.total
      } catch (err) {
        this.error = this.$i18n.t("m.Problem_Community_Error")
        console.error("Failed to fetch posts:", err)
      } finally {
        this.isLoading = false
      }
    },
    handlePageChange(page) {
      this.query.page = page
      this.fetchPosts()
    },
    goToPost(postId) {
      this.$router.push({ name: "community-detail", params: { postId } })
    },
    async createPost() {
      if (!this.newPost.title.trim()) {
        this.$error(this.$i18n.t("m.Problem_Community_Title_Required"))
        return
      }
      if (!this.newPost.content.trim()) {
        this.$error(this.$i18n.t("m.Problem_Community_Content_Required"))
        return
      }

      this.isCreating = true
      try {
        // 질문 생성 시 problem_id를 포함하여 전송
        await api.createPost({
          title: this.newPost.title,
          content: this.newPost.content,
          post_type: "QUESTION",
          problem_id: this.problem.id,
        })
        this.$success(this.$i18n.t("m.Problem_Community_Create_Success"))
        this.showCreateModal = false
        this.newPost = {
          title: "",
          content: "",
        }
        this.query.page = 1
        this.fetchPosts()
      } catch (err) {
        const errorMsg = (err.response && err.response.data && err.response.data.data) || this.$i18n.t("m.Problem_Community_Create_Failed")
        this.$error(errorMsg)
      } finally {
        this.isCreating = false
      }
    },
    applySearch() {
      this.query.page = 1
      this.fetchPosts()
    },
    filterByQuestionStatus(questionStatus) {
      this.query.question_status = questionStatus
      this.query.page = 1
      this.fetchPosts()
    }
  },
}
</script>

<style lang="less" scoped>
.light-theme {
  --hover-bg: #f5f6fa;
  --pagination-bg: #fff;
  --pagination-border: #dcdee2;
  --pagination-hover-bg: #f5f6fa;
  --pagination-active-bg: var(--point-color);
  --pagination-active-color: #fff;
  --pagination-text: #515a6e;
  --input-bg: #fff;
  --input-border: #dcdee2;
  --input-text: #515a6e;
}

.dropdown {
  cursor: pointer;
  padding-top: 4px;
  padding-bottom: 4px;
  padding-left: 15px;
  padding-right: 15px;

  background-color: var(--input-bg);
  border: 1px solid var(--input-border);
  color: var(--input-text);

  border-radius: 7px;
  display: flex;
  align-items: center;

  transition: border 0.3s;

  &:hover {
    border-color: var(--point-color);
  }
}

.dark-theme {
  --hover-bg: #3a3f4d;
  --pagination-bg: #2b2f3a;
  --pagination-border: #3a3a4a;
  --pagination-hover-bg: #3a3f4d;
  --pagination-active-bg: var(--point-color);
  --pagination-active-color: #fff;
  --pagination-text: #e6e6e6;
  --input-bg: #2b2f3a;
  --input-border: #3a3a4a;
  --input-text: #e6e6e6;
}

.problem-community-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-color);
  padding: 20px;
  overflow: hidden;
}

.community-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--border-color);

  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .community-title {
    margin: 0;
    font-size: 18px;
    font-weight: 700;
    color: var(--text-color);
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .question-count {
    font-size: 13px;
    color: var(--text-color);
    opacity: 0.6;
    padding: 4px 12px;
    background: var(--border-color);
    border-radius: 12px;
    font-weight: 500;
  }

  .filter-bar {
    display: flex;
    align-items: center;
    gap: 8px;

    .create-btn {
      display: flex;
      align-items: center;
      gap: 6px;
      font-weight: 600;
      border-radius: 8px;
      background: var(--point-color);
      border-color: var(--point-color);
      box-shadow: 0 2px 8px rgba(50, 48, 107, 0.25);
      transition: all 0.3s ease;

      &:hover {
        background: #4a4890;
        border-color: #4a4890;
        box-shadow: 0 4px 12px rgba(50, 48, 107, 0.35);
        transform: translateY(-1px);
      }
    }

    .search-bar {
      width: 190;

      /deep/ .ivu-input {
        background: var(--input-bg);
        color: var(--input-text);
        border: 1px solid var(--input-border);

        &::placeholder {
          color: var(--input-text);
          opacity: 0.4;
        }

        &:focus {
          border-color: var(--point-color);
          box-shadow: 0 0 0 3px rgba(50, 48, 107, 0.25);
        }
      }
    }

    .question-status-bar {
      /deep/ .ivu-select-dropdown {
        background: var(--input-bg);
        border: 1px solid var(--input-border);
      }

      /deep/ .ivu-dropdown-item {
        color: var(--input-text);
        transition: background 0.2s;

        &:hover {
          background: var(--hover-bg);
          color: var(--input-text);
        }
      }
    }

    .search_icon {
      font-size: 23px;
      cursor: pointer;
    }

    .search_icon:hover {
      color: #2d8cf0;
    }

  }

}

.loading-state,
.error-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;

  p {
    margin: 0;
    font-size: 14px;
    color: var(--text-color);
  }

  .ivu-icon {
    color: var(--text-color);
    opacity: 0.4;
  }
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;

  h4 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--text-color);
  }

  .empty-subtitle {
    margin: 0;
    font-size: 14px;
    color: var(--text-color);
    opacity: 0.6;
  }

  .empty-action-btn {
    margin-top: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 600;
    border-radius: 8px;
    background: var(--point-color);
    border-color: var(--point-color);
    box-shadow: 0 2px 8px rgba(50, 48, 107, 0.25);
    transition: all 0.3s ease;

    &:hover {
      background: #4a4890;
      border-color: #4a4890;
      box-shadow: 0 4px 12px rgba(50, 48, 107, 0.35);
      transform: translateY(-1px);
    }
  }
}

.posts-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
  padding: 2px 5px 0 0;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 3px;

    &:hover {
      background: var(--text-color);
      opacity: 0.3;
    }
  }
}

.post-item {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: background 0.2s ease;

  &:hover {
    background: var(--hover-bg);
  }
}

.post-header {
  margin-bottom: 8px;

  .post-meta {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 10px;
    flex-wrap: wrap;
  }

  .post-id {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-color);
    opacity: 0.5;
    padding: 3px 8px;
    border-radius: 4px;
    background: var(--border-color);
  }

  .new-badge {
    font-size: 10px;
    font-weight: 700;
    color: #ffffff;
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
    padding: 3px 9px;
    border-radius: 10px;
    white-space: nowrap;
    box-shadow: 0 2px 6px rgba(255, 107, 107, 0.3);
  }

  .question-status-badge {
    padding: 3px 10px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
  }

  .post-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-color);
    margin: 0;
    line-height: 1.5;
    transition: color 0.2s ease;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
  }
}

.post-preview {
  font-size: 13px;
  color: var(--text-color);
  opacity: 0.65;
  line-height: 1.6;
  margin: 0 0 12px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);

  .author-info {
    display: flex;
    align-items: center;
    gap: 8px;

    .avatar {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      object-fit: cover;
      border: 2px solid var(--border-color);
    }

    .author-name {
      font-size: 13px;
      font-weight: 500;
      color: var(--text-color);
      opacity: 0.8;
    }
  }

  .post-stats {
    display: flex;
    align-items: center;
    gap: 12px;

    .post-date,
    .comment-count {
      font-size: 12px;
      color: var(--text-color);
      opacity: 0.6;
      display: flex;
      align-items: center;
      gap: 4px;

      .ivu-icon {
        font-size: 14px;
      }
    }
  }
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
  margin-top: auto;

  /deep/ .ivu-page {
    .ivu-page-item {
      background-color: var(--pagination-bg);
      border: 1px solid var(--pagination-border);
      color: var(--pagination-text);

      &:hover {
        background-color: var(--pagination-hover-bg);
        border-color: var(--point-color);
        color: var(--point-color);
      }

      a {
        color: var(--pagination-text);
      }
    }

    .ivu-page-item-active {
      background-color: var(--pagination-active-bg);
      border-color: var(--pagination-active-bg);

      a {
        color: var(--pagination-active-color);
      }

      &:hover {
        background-color: var(--pagination-active-bg);
        border-color: var(--pagination-active-bg);

        a {
          color: var(--pagination-active-color);
        }
      }
    }

    .ivu-page-prev,
    .ivu-page-next {
      background-color: var(--pagination-bg);
      border: 1px solid var(--pagination-border);

      a {
        color: var(--pagination-text);
      }

      &:hover {
        background-color: var(--pagination-hover-bg);
        border-color: var(--point-color);

        a {
          color: var(--point-color);
        }
      }
    }

    .ivu-page-disabled {
      background-color: var(--pagination-bg);
      border: 1px solid var(--pagination-border);
      opacity: 0.4;

      a {
        color: var(--pagination-text);
      }

      &:hover {
        background-color: var(--pagination-bg);
        border-color: var(--pagination-border);

        a {
          color: var(--pagination-text);
        }
      }
    }

    .ivu-page-total {
      color: var(--pagination-text);
    }
  }
}

// top, bottom 모두 padding 주어 화면 중앙에 모달이 위치하도록 설정
/deep/ .create-question-modal {
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 50px;
  padding-bottom: 50px;

  .ivu-modal {
    top: 0;
  }

  .ivu-modal-content {
    border-radius: 16px;
    overflow: hidden;
    background: var(--bg-color);
  }

  .ivu-modal-body {
    padding: 0;
  }

  .ivu-modal-close {
    .ivu-icon-ios-close {
      color: #ffffff;
      font-size: 32px;
    }
  }
}

.modal-header {
  padding: 32px 40px 24px;
  background: var(--point-color);
  border-bottom: none;

  .modal-title {
    margin: 0 0 20px 0;
    font-size: 24px;
    font-weight: 700;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .problem-info-card {
    background: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 12px;
    padding: 16px 20px;
    backdrop-filter: blur(10px);

    .problem-info-label {
      font-size: 13px;
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      gap: 6px;
      font-weight: 600;
      color: rgba(255, 255, 255, 0.85);
    }

    .problem-info-content {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 18px;
      font-weight: 700;

      .problem-number {
        color: #ffffff;
      }

      .problem-title {
        color: #ffffff;
      }
    }
  }
}

.question-form {
  padding: 32px;
  background: var(--bg-color);

  .form-item {
    margin-bottom: 24px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  .input-label {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-color);
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  /deep/ .ivu-input {
    border-radius: 8px;
    border: 2px solid var(--border-color);
    transition: all 0.3s ease;
    font-size: 14px;
    background: var(--bg-color);
    color: var(--text-color);

    &:focus {
      border-color: var(--point-color);
      box-shadow: 0 0 0 3px rgba(50, 48, 107, 0.15);
    }
  }

  /deep/ textarea.ivu-input {
    resize: vertical;
    line-height: 1.6;
    font-family: inherit;
    background: var(--bg-color);
    color: var(--text-color);

    &::placeholder {
      line-height: 1.6;
      color: var(--text-color);
      opacity: 0.4;
    }
  }
}

.modal-footer {
  padding: 20px 32px 28px;
  background: var(--bg-color);
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 12px;

  .cancel-btn,
  .submit-btn {
    border-radius: 8px;
    font-weight: 600;
  }

  .cancel-btn {
    background: var(--bg-color);
    border: 2px solid var(--border-color);
    color: var(--text-color);

    &:hover {
      background: var(--border-color);
      border-color: var(--border-color);
    }
  }

  .submit-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--point-color);
    border: none;
    color: white;
    transition: all 0.3s ease;

    &:hover {
      background: #4a4890;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(50, 48, 107, 0.4);
    }
  }
}
</style>
