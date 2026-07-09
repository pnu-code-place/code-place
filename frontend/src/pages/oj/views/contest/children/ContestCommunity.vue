<script>
import api from "@oj/api"
import { DEFAULT_AVATAR, POST_TYPE, QUESTION_STATUS } from "@/utils/constants"
import { mapActions, mapGetters } from "vuex"
import TiptapEditor from "../../../components/TiptapEditor.vue"

const CONTEST_POST_VISIBILITY = {
  CONTEST_PARTICIPANTS: {
    name: "대회 참여자 전체",
    description: "대회에 참여 중인 사용자와 주최자가 볼 수 있습니다.",
  },
  CONTEST_HOSTS: {
    name: "주최자만",
    description: "대회 운영자와 관리자만 볼 수 있습니다.",
  },
}

export default {
  name: "ContestCommunity",
  components: {
    TiptapEditor,
  },
  data() {
    return {
      activeTab: "all",
      posts: [],
      total: 0,
      isLoading: false,
      isCreating: false,
      showCreateModal: false,
      error: null,
      query: {
        page: 1,
        limit: 10,
      },
      newPost: {
        title: "",
        content: "",
        visibility: "CONTEST_PARTICIPANTS",
      },
    }
  },
  computed: {
    ...mapGetters(["isAuthenticated"]),
    POST_TYPE() {
      return POST_TYPE
    },
    QUESTION_STATUS() {
      return QUESTION_STATUS
    },
    CONTEST_POST_VISIBILITY() {
      return CONTEST_POST_VISIBILITY
    },
    contestID() {
      return this.$route.params.contestID
    },
    defaultAvatar() {
      return DEFAULT_AVATAR
    },
    visiblePosts() {
      if (this.activeTab === "my") {
        return this.posts.filter(
          (post) => post.is_mine && post.post_type === "QUESTION",
        )
      }
      return this.posts
    },
    emptyMessage() {
      if (this.activeTab === "my") {
        return "작성한 대회 질문이 없습니다."
      }
      return "아직 등록된 대회 게시글이 없습니다."
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.total / this.query.limit))
    },
  },
  watch: {
    contestID: {
      handler() {
        this.query.page = 1
        this.fetchPosts()
      },
    },
    activeTab() {
      this.query.page = 1
    },
  },
  mounted() {
    this.fetchPosts()
  },
  methods: {
    ...mapActions(["changeModalStatus"]),
    async fetchPosts() {
      if (!this.contestID) return

      this.isLoading = true
      this.error = null
      const offset = (this.query.page - 1) * this.query.limit

      try {
        const res = await api.getCommunityPostList(
          offset,
          this.query.limit,
          null,
          null,
          null,
          this.contestID,
          null,
          "NEWEST",
        )
        this.posts = res.data.data.results || []
        this.total = res.data.data.total || 0
      } catch (err) {
        this.error =
          (err.response &&
            err.response.data &&
            (err.response.data.data || err.response.data.message)) ||
          "대회 게시글을 불러오지 못했습니다."
        console.error("Failed to fetch contest community posts:", err)
      } finally {
        this.isLoading = false
      }
    },
    openCreateModal() {
      if (!this.isAuthenticated) {
        this.$error(this.$t("m.Please_login_first"))
        this.changeModalStatus({ visible: true, mode: "login" })
        return
      }
      this.showCreateModal = true
    },
    closeCreateModal() {
      if (this.isCreating) return
      this.showCreateModal = false
      this.resetNewPost()
    },
    resetNewPost() {
      this.newPost = {
        title: "",
        content: "",
        visibility: "CONTEST_PARTICIPANTS",
      }
    },
    async submitPost() {
      if (!this.newPost.title.trim()) {
        this.$error(this.$t("m.Community_Title_Required"))
        return
      }
      if (!this.newPost.content.trim()) {
        this.$error(this.$t("m.Community_Content_Required"))
        return
      }

      this.isCreating = true
      try {
        await api.createPost({
          title: this.newPost.title.trim(),
          content: this.newPost.content,
          post_type: "QUESTION",
          contest_id: this.contestID,
          visibility: this.newPost.visibility,
        })
        this.$success("질문이 등록되었습니다.")
        this.showCreateModal = false
        this.resetNewPost()
        this.activeTab = "all"
        this.query.page = 1
        await this.fetchPosts()
      } catch (err) {
        const errorMsg =
          (err.response &&
            err.response.data &&
            (err.response.data.data || err.response.data.message)) ||
          "질문 등록에 실패했습니다."
        this.$error(errorMsg)
      } finally {
        this.isCreating = false
      }
    },
    handlePageChange(page) {
      if (page < 1 || page > this.totalPages || page === this.query.page) {
        return
      }
      this.query.page = page
      this.fetchPosts()
    },
    isLockedPost(post) {
      return post && post.visibility === "CONTEST_HOSTS" && !post.can_view
    },
    goToPost(post) {
      if (this.isLockedPost(post)) {
        this.$Notice.info({
          title: "열람 권한이 없습니다.",
          desc: "관리자 또는 작성자만 볼 수 있는 글입니다.",
        })
        return
      }
      this.$router.push({ name: "community-detail", params: { postId: post.id } })
    },
    isNewPost(post) {
      if (!post || !post.created_at) return false
      const postDate = new Date(post.created_at)
      const now = new Date()
      const diffDays = Math.ceil(
        Math.abs(now - postDate) / (1000 * 60 * 60 * 24),
      )
      return diffDays <= 3
    },
  },
}
</script>

<template>
  <div class="contest-community">
    <div class="community-header">
      <div class="left-section">
        <p>{{ $t("m.Contest_Community") }}</p>
        <div class="filter-toggle">
          <button
            :class="{ active: activeTab === 'all' }"
            @click="activeTab = 'all'"
          >
            전체 글 보기
          </button>
          <button
            :class="{ active: activeTab === 'my' }"
            @click="activeTab = 'my'"
          >
            내 질문 보기
          </button>
        </div>
      </div>
      <Button class="write-btn" @click="openCreateModal">
        {{ $t("m.Community_Create_Comment_Btn") }}
      </Button>
    </div>

    <div v-if="isLoading" class="loading-state">
      <Spin size="large"></Spin>
    </div>

    <div v-else-if="error" class="empty-state error-state">
      <Icon type="ios-alert-outline" size="42"></Icon>
      <p>{{ error }}</p>
    </div>

    <div v-else-if="visiblePosts.length === 0" class="empty-state">
      <Icon type="ios-chatbubbles-outline" size="42"></Icon>
      <p>{{ emptyMessage }}</p>
      <Button type="primary" @click="openCreateModal">질문 작성하기</Button>
    </div>

    <div v-else class="posts-list">
      <div
        v-for="post in visiblePosts"
        :key="post.id"
        @click="goToPost(post)"
        class="post-card"
        :class="{ locked: isLockedPost(post) }"
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
                backgroundColor: QUESTION_STATUS[post.question_status].color,
                color: QUESTION_STATUS[post.question_status].textColor,
              }"
            >
              {{ QUESTION_STATUS[post.question_status].name }}
            </span>
            <span
              v-if="post.visibility === 'CONTEST_HOSTS'"
              class="lock-label"
              title="제한글"
              aria-label="제한글"
            >
              <Icon type="ios-locked-outline"></Icon>
            </span>
          </div>
          <div class="card-content">
            <h3 class="post-title">{{ post.title }}</h3>
            <div v-if="isLockedPost(post)" class="post-preview locked-preview">
              열람 권한이 제한된 글입니다.
            </div>
            <div
              v-else-if="post.content_preview"
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
                  :src="post.author_avatar || defaultAvatar"
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

    <div v-if="total > query.limit" class="pagination-wrapper">
      <Page
        :total="total"
        :page-size="query.limit"
        :current="query.page"
        @on-change="handlePageChange"
        size="small"
        show-total
      />
    </div>

    <Modal
      v-model="showCreateModal"
      :footer-hide="true"
      :mask-closable="!isCreating"
      width="820"
      class-name="contest-question-modal"
      @on-cancel="closeCreateModal"
    >
      <div class="modal-header">
        <h2>대회 질문 작성</h2>
        <p>질문은 현재 대회 커뮤니티에 연결되어 등록됩니다.</p>
      </div>

      <Form :label-width="0" class="question-form">
        <FormItem class="form-item">
          <div class="input-label">제목</div>
          <Input
            v-model="newPost.title"
            size="large"
            :maxlength="100"
            show-word-limit
            placeholder="질문 제목을 입력하세요"
            @keyup.enter.native="submitPost"
          />
        </FormItem>

        <FormItem class="form-item">
          <div class="input-label">열람 권한</div>
          <RadioGroup v-model="newPost.visibility" class="visibility-options">
            <Radio
              v-for="(visibility, key) in CONTEST_POST_VISIBILITY"
              :key="key"
              :label="key"
              class="visibility-option"
            >
              <strong>{{ visibility.name }}</strong>
              <span>{{ visibility.description }}</span>
            </Radio>
          </RadioGroup>
        </FormItem>

        <FormItem class="form-item">
          <div class="input-label">내용</div>
          <TiptapEditor
            v-model="newPost.content"
            height="300px"
            :editable="true"
            placeholder="대회 진행 중 궁금한 내용을 작성하세요"
          />
        </FormItem>
      </Form>

      <div class="modal-footer">
        <Button size="large" class="cancel-btn" @click="closeCreateModal">
          {{ $t("m.Cancel") }}
        </Button>
        <Button
          type="primary"
          size="large"
          class="submit-btn"
          :loading="isCreating"
          @click="submitPost"
        >
          {{ $t("m.Submit") }}
        </Button>
      </div>
    </Modal>
  </div>
</template>

<style scoped lang="less">
.contest-community {
  border: 1px solid #e9ece9;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: var(--box-background-color);
  padding: 15px 20px;
  border-radius: 7px;
}
.community-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  p {
    text-decoration: none;
    font-size: 24px;
    font-weight: bold;
  }
}
.left-section {
  display: flex;
  gap: 20px;
  align-items: center;
}
.filter-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 3px;
  border-radius: 7px;
  background: #f3f4f6;
}
.filter-toggle button {
  min-width: 92px;
  height: 30px;
  padding: 0 12px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #60646c;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}
.filter-toggle button.active {
  background: #494a67;
  color: white;
  font-weight: 600;
}
.write-btn {
  background: #3475e0;
  color: white;
  border-radius: 7px;
  font-weight: bold;
  border: none;
}
.loading-state,
.empty-state {
  min-height: 180px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #7f8c8d;
  text-align: center;
}
.error-state {
  color: #d9534f;
}
.posts-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding-bottom: 20px;
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
    flex-wrap: wrap;
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

  .post-type-label,
  .question-status-label,
  .lock-label {
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
    transition: all 0.2s ease;
  }

  .lock-label {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    padding: 0;
    background: #eef0f2;
    color: #7b818a;
  }

  &.locked {
    background: #f7f8fa;
    border-color: #e1e4e8;
    box-shadow: none;

    &:hover {
      border-color: #d6d9de;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);

      .post-title {
        color: #667085;
      }
    }

    .post-title,
    .author-name,
    .post-preview {
      color: #8b929c;
    }
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

  .locked-preview {
    color: #8b929c;
  }

  .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
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
      background: #f0f3f7;
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

  .post-date,
  .comment-count {
    font-size: 12px;
    color: #7f8c8d;
    display: flex;
    align-items: center;
    gap: 5px;
    background: #f8f9fa;
    padding: 4px 10px;
    border-radius: 12px;
    font-weight: 500;
    white-space: nowrap;

    .ivu-icon {
      font-size: 14px;
    }
  }
}

/deep/ .contest-question-modal {
  .ivu-modal-body {
    padding: 28px;
  }
}
.modal-header {
  margin-bottom: 22px;

  h2 {
    margin: 0 0 6px;
    color: #2c3e50;
    font-size: 24px;
    font-weight: 700;
  }

  p {
    margin: 0;
    color: #7f8c8d;
    font-size: 14px;
  }
}
.question-form {
  .form-item {
    margin-bottom: 22px;
  }

  .input-label {
    margin-bottom: 8px;
    color: #2c3e50;
    font-size: 14px;
    font-weight: 600;
  }
}
.visibility-options {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  width: 100%;
}
.visibility-option {
  height: auto;
  margin-right: 0;
  padding: 14px 16px;
  border: 1px solid #e8ecef;
  border-radius: 8px;
  background: #fafbfc;

  /deep/ .ivu-radio {
    margin-right: 8px;
  }

  strong,
  span {
    display: block;
    white-space: normal;
  }

  strong {
    color: #2c3e50;
    font-size: 14px;
    line-height: 1.4;
  }

  span {
    margin-top: 4px;
    color: #7f8c8d;
    font-size: 12px;
    line-height: 1.5;
  }
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 6px;
}
.submit-btn,
.cancel-btn {
  min-width: 96px;
  border-radius: 7px;
}

@media (max-width: 768px) {
  .community-header,
  .left-section,
  .post-card .card-footer {
    align-items: stretch;
    flex-direction: column;
  }

  .filter-toggle {
    align-items: stretch;
    flex-direction: column;
    width: 100%;
  }

  .filter-toggle button {
    width: 100%;
  }

  .post-card {
    padding: 18px;
  }

  .post-stats {
    flex-wrap: wrap;
  }

  .visibility-options {
    grid-template-columns: 1fr;
  }
}
</style>
