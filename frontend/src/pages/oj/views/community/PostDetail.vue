<template>
  <main>
    <div class="contents" v-if="post">
      <div class="post-header">
        <div class="title-section" v-if="!isEditing">
          <h1 class="post-title">{{ post.title }}</h1>
          <div class="badges-container">
            <span v-if="isNewPost" class="new-badge">NEW</span>
            <span v-if="POST_TYPE[post.post_type]" class="post-type-badge" :style="{
              backgroundColor: POST_TYPE[post.post_type].color,
              color: POST_TYPE[post.post_type].textColor
            }">
              {{ POST_TYPE[post.post_type].name }}
            </span>
            <span v-if="post.post_type === 'QUESTION' && QUESTION_STATUS[post.question_status]"
              class="question-status-badge" :style="{
                backgroundColor: QUESTION_STATUS[post.question_status].color,
                color: QUESTION_STATUS[post.question_status].textColor
              }">
              {{ QUESTION_STATUS[post.question_status].name }}
            </span>
          </div>
        </div>
        <Input v-else v-model="editedTitle" size="large" :placeholder="$t('m.Community_Title_Placeholder')"
          class="edit-title-input" />
        <div class="post-meta">
          <div class="post-meta-left">
            <div class="user-info">
              <router-link :to="{
                name: 'user-home',
                params: { username: post.author_name },
              }">
                <img class="avatar" :src="post.author_avatar || defaultAvatar" alt="avatar" />
                <span>{{ post.author_name }}</span>
              </router-link>
            </div>
            <div class="post-date">
              <Icon type="ios-time-outline"></Icon>
              {{ post.created_at | localtime("YYYY-MM-DD HH:mm") }}
            </div>
          </div>
          <div class="post-meta-right">
            <div v-if="isAuthor && !isEditing" class="post-edit-actions">
              <button v-if="post.post_type === 'QUESTION'" class="question-status-toggle-btn" :style="{
                backgroundColor: getQuestionStatusStyle.backgroundColor,
                color: getQuestionStatusStyle.color
              }" @click="toggleQuestionStatus">
                <Icon
                  :type="post.question_status === 'CLOSED' ? 'ios-checkmark-circle' : 'ios-checkmark-circle-outline'">
                </Icon>
                {{ post.question_status === 'CLOSED' ? $t('m.Community_Question_Reopen') :
                  $t('m.Community_Question_Close') }}
              </button>
              <button class="post-edit-btn" @click="enterEditMode">{{ $t('m.Community_Post_Edit') }}</button>
              <button class="post-delete-btn" @click="deletePost(post.id)">{{ $t('m.Community_Post_Delete') }}</button>
            </div>
            <div v-if="isEditing" class="post-edit-actions">
              <Select v-model="editedPostType" size="small" style="width: 120px; margin-right: 8px;">
                <Option v-for="(type, key) in availablePostTypes" :key="key" :value="key">{{ type.name }}</Option>
              </Select>
              <button class="post-save-btn" @click="updatePost" :disabled="isLoading">{{ $t('m.Community_Post_Save')
              }}</button>
              <button class="post-cancel-btn" @click="cancelEdit">{{ $t('m.Community_Post_Cancel') }}</button>
            </div>
          </div>
        </div>
      </div>
      <div class="post-content" v-if="!isEditing" v-html="sanitizedContent"></div>
      <Input v-else v-model="editedContent" type="textarea" :autosize="{ minRows: 10, maxRows: 20 }"
        :placeholder="$t('m.Community_Content_Placeholder')" class="edit-content-input" />
      <div class="post-comments">
        <h2>{{ $t("m.Community_Comments") }} {{ commentCount }}</h2>
        <div class="comment-form">
          <textarea v-model="commentContent" :placeholder="$t('m.Community_Create_Comment_Placeholder')"></textarea>
          <button @click="submitComment">
            {{ $t("m.Community_Create_Comment_Btn") }}
          </button>
        </div>
        <div v-for="comment in post.comments" :key="comment.id" class="comment">
          <div class="comment-header">
            <div class="user-info">
              <router-link :to="{
                name: 'user-home',
                params: { username: comment.author_name },
              }">
                <img class="avatar" :src="comment.author_avatar || defaultAvatar" alt="avatar" />
                <span>{{ comment.author_name }}</span>
              </router-link>
            </div>
            <div class="comment-date">
              <Icon type="ios-time-outline"></Icon>
              {{ comment.created_at | localtime("YYYY-MM-DD HH:mm") }}
            </div>
          </div>
          <div class="comment-body">
            <div v-if="editingCommentId !== comment.id" class="comment-content">{{ comment.content }}</div>
            <textarea v-else v-model="editedCommentContent" class="comment-edit-textarea"></textarea>
            <div class="comment-actions">
              <button v-if="editingCommentId !== comment.id" class="reply-icon-btn" @click="showReplyForm(comment.id)">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="9 14 4 9 9 4"></polyline>
                  <path d="M20 20v-7a4 4 0 0 0-4-4H4"></path>
                </svg>
              </button>
              <button v-if="isCommentAuthor(comment) && editingCommentId !== comment.id" class="edit-icon-btn"
                @click="enterCommentEditMode(comment)">
                {{ $t('m.Community_Comment_Edit') }}
              </button>
              <button v-if="isCommentAuthor(comment) && editingCommentId !== comment.id" class="delete-icon-btn"
                @click="deleteComment(comment.id)">
                {{ $t('m.Community_Comment_Delete') }}
              </button>
              <button v-if="editingCommentId === comment.id" class="save-btn" @click="updateComment(comment.id)">
                {{ $t('m.Community_Comment_Save') }}
              </button>
              <button v-if="editingCommentId === comment.id" class="cancel-btn" @click="cancelCommentEdit">
                {{ $t('m.Community_Comment_Cancel') }}
              </button>
            </div>
          </div>
          <div v-if="comment.replies && comment.replies.length" class="replies">
            <div v-for="reply in comment.replies" :key="reply.id" class="comment reply">
              <div class="comment-header">
                <div class="user-info">
                  <router-link :to="{
                    name: 'user-home',
                    params: { username: reply.author_name },
                  }">
                    <img class="avatar" :src="reply.author_avatar || defaultAvatar" alt="avatar" />
                    <span>{{ reply.author_name }}</span>
                  </router-link>
                </div>
                <div class="comment-date">
                  <Icon type="ios-time-outline"></Icon>
                  {{ reply.created_at | localtime("YYYY-MM-DD HH:mm") }}
                </div>
              </div>
              <div class="comment-body">
                <div v-if="editingCommentId !== reply.id" class="comment-content">{{ reply.content }}</div>
                <textarea v-else v-model="editedCommentContent" class="comment-edit-textarea"></textarea>
                <div class="comment-actions" v-if="isCommentAuthor(reply)">
                  <button v-if="editingCommentId !== reply.id" class="edit-icon-btn"
                    @click="enterCommentEditMode(reply)">
                    {{ $t('m.Community_Comment_Edit') }}
                  </button>
                  <button v-if="editingCommentId !== reply.id" class="delete-icon-btn" @click="deleteComment(reply.id)">
                    {{ $t('m.Community_Comment_Delete') }}
                  </button>
                  <button v-if="editingCommentId === reply.id" class="save-btn" @click="updateComment(reply.id)">
                    {{ $t('m.Community_Comment_Save') }}
                  </button>
                  <button v-if="editingCommentId === reply.id" class="cancel-btn" @click="cancelCommentEdit">
                    {{ $t('m.Community_Comment_Cancel') }}
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div v-if="replyingTo === comment.id" class="comment-form reply-form">
            <textarea v-model="replyContent" :placeholder="$t('m.Community_Create_Comment_Placeholder')"></textarea>
            <div class="reply-form-actions">
              <button @click="submitReply(comment.id)">
                {{ $t("m.Community_Create_Comment_Btn") }}
              </button>
              <button @click="cancelReply">
                {{ $t("m.Community_Create_Comment_Cancel_Btn") }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else>
      <ErrorSign v-if="error" :code="error.code" :description="error.description" :solution="error.solution" />
      <div v-else>Loading...</div>
    </div>
  </main>
</template>

<script>
import api from "../../api"
import ErrorSign from "../general/ErrorSign.vue"
import DOMPurify from "dompurify"
import { DEFAULT_AVATAR, POST_TYPE, QUESTION_STATUS } from "@/utils/constants"
import { mapGetters } from "vuex";

export default {
  name: "PostDetail",
  components: {
    ErrorSign,
  },
  data() {
    return {
      post: null,
      error: null,
      isLoading: false,
      commentContent: "",
      replyingTo: null,
      replyContent: "",
      isEditing: false,
      editedTitle: "",
      editedContent: "",
      editedPostType: "",
      editingCommentId: null,
      editedCommentContent: "",
    }
  },
  created() {
    this.fetchPostDetail()
  },
  methods: {
    fetchPostDetail() {
      this.isLoading = true
      const postId = this.$route.params.postId
      api
        .getCommunityPostDetail(postId)
        .then((res) => {
          this.post = res.data.data
        })
        .catch((err) => {
          this.error = {
            code: (err.response && err.response.status) || 500,
            description:
              (err.response &&
                err.response.data &&
                err.response.data.message) ||
              "Error loading post",
            solution: "Please try again later.",
          }
        })
        .finally(() => {
          this.isLoading = false
        })
    },
    submitComment() {
      if (!this.commentContent.trim()) {
        this.$error("Comment cannot be empty.")
        return
      }
      const postId = this.$route.params.postId
      api
        .createCommunityComment(postId, this.commentContent)
        .then(() => {
          this.commentContent = ""
          this.fetchPostDetail()
        })
        .catch(() => {
          this.$error("Failed to submit comment.")
        })
    },
    showReplyForm(commentId) {
      if (this.replyingTo === commentId) {
        this.replyingTo = null
      } else {
        this.replyingTo = commentId
        this.replyContent = ""
      }
    },
    cancelReply() {
      this.replyingTo = null
      this.replyContent = ""
    },
    submitReply(parentCommentId) {
      if (!this.replyContent.trim()) {
        this.$error("Reply cannot be empty.")
        return
      }
      const postId = this.$route.params.postId
      api
        .createCommunityComment(postId, this.replyContent, parentCommentId)
        .then(() => {
          this.cancelReply()
          this.fetchPostDetail()
        })
        .catch(() => {
          this.$error("Failed to submit reply.")
        })
    },
    enterEditMode() {
      this.isEditing = true
      this.editedTitle = this.post.title
      this.editedContent = this.post.content
      this.editedPostType = this.post.post_type
    },
    cancelEdit() {
      this.isEditing = false
      this.editedTitle = ""
      this.editedContent = ""
      this.editedPostType = ""
    },
    updatePost() {
      if (!this.editedTitle.trim()) {
        this.$error(this.$t("m.Community_Title_Required"))
        return
      }
      if (!this.editedContent.trim()) {
        this.$error(this.$t("m.Community_Content_Required"))
        return
      }

      this.isLoading = true
      const postId = this.$route.params.postId
      const updatedData = {
        title: this.editedTitle,
        content: this.editedContent,
        post_type: this.editedPostType,
      }

      api
        .updateCommunityPost(postId, updatedData)
        .then((res) => {
          this.$success(this.$t("m.Community_Post_Edit_Success"))
          this.post = res.data.data
          this.isEditing = false
        })
        .catch((err) => {
          const errorMsg = (err.response && err.response.data && err.response.data.data) || this.$t("m.Community_Post_Edit_Failed")
          this.$error(errorMsg)
        })
        .finally(() => {
          this.isLoading = false
        })
    },
    isCommentAuthor(comment) {
      return this.user && comment && this.user.id === comment.author
    },
    enterCommentEditMode(comment) {
      this.editingCommentId = comment.id
      this.editedCommentContent = comment.content
    },
    cancelCommentEdit() {
      this.editingCommentId = null
      this.editedCommentContent = ""
    },
    updateComment(commentId) {
      if (!this.editedCommentContent.trim()) {
        this.$error(this.$t("m.Community_Comment_Content_Required"))
        return
      }

      const postId = this.$route.params.postId
      api
        .updateCommunityComment(postId, commentId, this.editedCommentContent)
        .then(() => {
          this.$success(this.$t("m.Community_Comment_Edit_Success"))
          this.editingCommentId = null
          this.editedCommentContent = ""
          this.fetchPostDetail()
        })
        .catch((err) => {
          const errorMsg = (err.response && err.response.data && err.response.data.data) || this.$t("m.Community_Comment_Edit_Failed")
          this.$error(errorMsg)
        })
    },
    deleteComment(commentId) {
      if (!confirm(this.$t("m.Community_Comment_Delete_Confirm"))) {
        return
      }

      const postId = this.$route.params.postId
      api
        .deleteCommunityComment(postId, commentId)
        .then(() => {
          this.$success(this.$t("m.Community_Comment_Delete_Success"))
          this.fetchPostDetail()
        })
        .catch((err) => {
          const errorMsg = (err.response && err.response.data && err.response.data.data) || this.$t("m.Community_Comment_Delete_Failed")
          this.$error(errorMsg)
        })
    },
    deletePost() {
      if (!confirm(this.$t("m.Community_Post_Delete_Confirm"))) {
        return
      }

      this.isLoading = true
      const postId = this.$route.params.postId
      api
        .deleteCommunityPost(postId)
        .then(() => {
          this.$success(this.$t("m.Community_Post_Delete_Success"))
          this.$router.push({ name: "community" })
        })
        .catch((err) => {
          const errorMsg = (err.response && err.response.data && err.response.data.data) || this.$t("m.Community_Post_Delete_Failed")
          this.$error(errorMsg)
        })
        .finally(() => {
          this.isLoading = false
        })
    },
    toggleQuestionStatus() {
      const newStatus = this.post.question_status === 'CLOSED' ? 'OPEN' : 'CLOSED'
      const postId = this.$route.params.postId

      this.isLoading = true
      api
        .updateCommunityPost(postId, { question_status: newStatus })
        .then((res) => {
          this.post = res.data.data
          const message = newStatus === 'CLOSED'
            ? this.$t("m.Community_Question_Closed_Success")
            : this.$t("m.Community_Question_Reopened_Success")
          this.$success(message)
        })
        .catch((err) => {
          const errorMsg = (err.response && err.response.data && err.response.data.data) || this.$t("m.Community_Question_Status_Update_Failed")
          this.$error(errorMsg)
        })
        .finally(() => {
          this.isLoading = false
        })
    }
  },
  computed: {
    ...mapGetters(["user", "isSuperAdmin"]),
    POST_TYPE() {
      return POST_TYPE;
    },
    QUESTION_STATUS() {
      return QUESTION_STATUS;
    },
    /**
     * 게시글이 3일 이내에 작성되었는지 확인
     */
    isNewPost() {
      if (!this.post || !this.post.created_at) return false;
      const postDate = new Date(this.post.created_at);
      const now = new Date();
      const diffTime = Math.abs(now - postDate);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      return diffDays <= 3;
    },
    /**
     * 현재 사용자가 게시글 작성자인지 확인
     */
    isAuthor() {
      return this.user && this.post && this.user.id === this.post.author
    },
    availablePostTypes() {
      // Super Admin이 아닌 경우 ANNOUNCEMENT 타입 제외
      if (!this.isSuperAdmin) {
        const { ANNOUNCEMENT, ...filteredTypes } = POST_TYPE;
        return filteredTypes;
      }
      return POST_TYPE;
    },
    /**
     * 게시글 내용을 표시할 때 v-html을 사용하는데, 이는 XSS 공격에 취약할 수 있습니다.
     * 따라서 DOMPurify를 사용하여 게시글 내용을 안전하게 sanitize하는 작업을 수행합니다.
     */
    sanitizedContent() {
      if (!this.post || !this.post.content) return ""
      return DOMPurify.sanitize(this.post.content)
    },
    defaultAvatar() {
      return DEFAULT_AVATAR
    },
    getQuestionStatusStyle() {
      if (!this.post || !this.post.question_status) {
        return { backgroundColor: '', color: '' }
      }
      const status = QUESTION_STATUS[this.post.question_status]
      if (!status) {
        return { backgroundColor: '', color: '' }
      }
      return {
        backgroundColor: status.color,
        color: status.textColor
      }
    },
    commentCount() {
      if (!this.post || !this.post.comments) return 0

      let count = this.post.comments.length
      this.post.comments.forEach((comment) => {
        if (comment.replies) {
          count += comment.replies.length
        }
      })

      return count
    },
  },
}
</script>

<style lang="less" scoped>
main {
  width: var(--global-width);
  margin: 0 auto;
  padding: 30px 0;
}

.contents {
  background: white;
  border-radius: 12px;
  border: 1px solid #e8ecef;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.post-header {
  padding: 32px 40px 16px 40px;
  border-bottom: 2px solid #f0f3f7;
  background: linear-gradient(to bottom, #fafbfc 0%, #ffffff 100%);
}

.title-section {
  margin-bottom: 28px;
}

.post-title {
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 12px 0;
  line-height: 1.3;
}

.badges-container {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.new-badge {
  padding: 6px 14px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
  color: #ffffff;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
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

.post-type-badge {
  padding: 6px 14px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.question-status-badge {
  padding: 6px 14px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.edit-title-input {
  margin-bottom: 16px;
  width: 100%;

  /deep/ input {
    font-size: 24px;
    font-weight: 600;
    color: #2c3e50;
    border: 1px solid #e8ecef;
    border-radius: 8px;
    padding: 16px;
    transition: all 0.3s ease;

    &:focus {
      border-color: #3498db;
      box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    }
  }
}

.post-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}

.post-meta-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.post-meta-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.post-date {
  font-size: 13px;
  color: #95a5a6;
  display: flex;
  align-items: center;
  gap: 6px;
  background: #f8f9fa;
  padding: 6px 12px;
  border-radius: 12px;
  font-weight: 500;
}

.post-edit-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.post-edit-btn,
.post-delete-btn,
.post-save-btn,
.post-cancel-btn,
.question-status-toggle-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.question-status-toggle-btn {
  transition: all 0.3s ease;

  &:hover {
    filter: brightness(0.95);
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
}

.post-edit-btn {
  background: #ecf5ff;
  color: #3498db;
}

.post-edit-btn:hover {
  background: #3498db;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(52, 152, 219, 0.2);
}

.post-delete-btn {
  background: #ffebee;
  color: #e74c3c;
}

.post-delete-btn:hover {
  background: #e74c3c;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(231, 76, 60, 0.2);
}

.post-save-btn {
  background: #3498db;
  color: white;
}

.post-save-btn:hover {
  background: #2980b9;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(52, 152, 219, 0.3);
}

.post-save-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.post-cancel-btn {
  background: #f8f9fa;
  color: #7f8c8d;
}

.post-cancel-btn:hover {
  background: #ecf0f1;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-info a {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #495060;
  transition: all 0.2s ease;
  gap: 10px;
  font-weight: 500;
}

.user-info a:hover {
  color: #3498db;
}

.user-info a:hover .avatar {
  transform: scale(1.1);
  border-color: #3498db;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid #f0f3f7;
  transition: all 0.3s ease;
  object-fit: cover;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.post-content {
  font-size: 16px;
  line-height: 1.8;
  color: #2c3e50;
  padding: 40px;
  min-height: 200px;
  white-space: pre-wrap;
  word-break: break-word;
}

.edit-content-input {
  padding: 0 40px 40px;

  /deep/ textarea {
    font-size: 16px;
    line-height: 1.8;
    color: #2c3e50;
    border: 1px solid #e8ecef;
    border-radius: 8px;
    padding: 16px;
    transition: all 0.3s ease;

    &:focus {
      border-color: #3498db;
      box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    }
  }
}

.post-comments {
  padding: 32px 40px;
  background: #fafbfc;
  border-top: 2px solid #f0f3f7;

  h2 {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 24px;
    color: #2c3e50;
    display: flex;
    align-items: center;
    gap: 8px;

    &:before {
      content: "💬";
      font-size: 24px;
    }
  }
}

.comment-form {
  margin-bottom: 32px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e8ecef;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);

  textarea {
    width: 100%;
    min-height: 100px;
    padding: 14px;
    border: 1px solid #e8ecef;
    border-radius: 8px;
    font-size: 15px;
    resize: vertical;
    margin-bottom: 12px;
    transition: all 0.3s ease;
    font-family: inherit;
    color: #2c3e50;
    line-height: 1.6;

    &:focus {
      outline: none;
      border-color: #3498db;
      box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    }

    &::placeholder {
      color: #bdc3c7;
    }
  }

  button {
    padding: 10px 24px;
    background: #3498db;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 500;
    font-size: 14px;

    &:hover {
      background: #2980b9;
      transform: translateY(-1px);
      box-shadow: 0 4px 8px rgba(52, 152, 219, 0.3);
    }
  }
}

.comment {
  background: white;
  margin-bottom: 16px;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e8ecef;
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    border-color: #d5dce0;
  }

  &:last-child {
    margin-bottom: 0;
  }
}

.comment-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.comment-date {
  font-size: 12px;
  color: #95a5a6;
  background: #f8f9fa;
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 500;
}

.comment-body {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.comment-content {
  font-size: 15px;
  color: #2c3e50;
  white-space: pre-wrap;
  line-height: 1.7;
  flex-grow: 1;
  word-break: break-word;
}

.comment-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.2s, visibility 0.2s;
}

.comment:hover .comment-actions {
  opacity: 1;
  visibility: visible;
}

.comment-edit-textarea {
  flex-grow: 1;
  width: 100%;
  min-height: 80px;
  padding: 12px;
  border: 1px solid #e8ecef;
  border-radius: 8px;
  font-size: 15px;
  color: #2c3e50;
  line-height: 1.7;
  resize: vertical;
  font-family: inherit;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
  }
}

.reply-icon-btn,
.edit-icon-btn,
.delete-icon-btn {
  background: #f8f9fa;
  border: none;
  cursor: pointer;
  padding: 6px 12px;
  font-size: 13px;
  color: #7f8c8d;
  transition: all 0.2s ease;
  border-radius: 6px;
  font-weight: 500;

  &:hover {
    background: #ecf0f1;
  }
}

.reply-icon-btn:hover,
.edit-icon-btn:hover {
  color: #3498db;
}

.delete-icon-btn:hover {
  color: #e74c3c;
  background: #ffebee;
}

.save-btn,
.cancel-btn {
  padding: 6px 14px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}

.save-btn {
  background: #3498db;
  color: white;

  &:hover {
    background: #2980b9;
  }
}

.cancel-btn {
  background: #f8f9fa;
  color: #7f8c8d;

  &:hover {
    background: #ecf0f1;
  }
}

.reply-icon-btn svg {
  width: 16px;
  height: 16px;
  stroke: currentColor;
}

.reply-form {
  margin-top: 16px;
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e8ecef;

  textarea {
    min-height: 80px;
    background: white;
  }
}

.reply-form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 10px;

  button {
    padding: 8px 18px;
    font-size: 14px;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 500;

    &:first-child {
      background: #3498db;
      color: white;

      &:hover {
        background: #2980b9;
      }
    }

    &:last-child {
      background: #95a5a6;
      color: white;

      &:hover {
        background: #7f8c8d;
      }
    }
  }
}

.replies {
  margin-top: 16px;
  margin-left: 20px;
  padding-left: 20px;
  border-left: 3px solid #e8ecef;
}

.reply {
  background: #fafbfc;
  border: 1px solid #e8ecef;

  &:hover {
    background: white;
  }
}

.reply .comment-body {
  padding-left: 0;
}
</style>
