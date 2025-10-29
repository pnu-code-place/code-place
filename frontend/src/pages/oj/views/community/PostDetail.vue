<template>
  <main>
    <div class="contents" v-if="post">
      <div class="post-header">
        <h1 class="post-title" v-if="!isEditing">{{ post.title }}</h1>
        <Input v-else v-model="editedTitle" size="large" :placeholder="$t('m.Community_Title_Placeholder')"
          class="edit-title-input" />
        <div class="post-meta">
          <div class="user-info">
            <router-link :to="{
              name: 'user-home',
              params: { username: post.author_name },
            }">
              <img class="avatar" :src="post.author_avatar || defaultAvatar" alt="avatar" />
              <span>{{ post.author_name }}</span>
            </router-link>
          </div>
          <div class="post-actions">
            <div class="post-date">
              {{ post.created_at | localtime("YYYY-MM-DD HH:mm") }}
            </div>
            <div v-if="isAuthor && !isEditing" class="post-edit-actions">
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
import { DEFAULT_AVATAR, POST_TYPE } from "@/utils/constants"
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
    }
  },
  computed: {
    ...mapGetters(["user", "isSuperAdmin"]),
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
  margin: 40px auto;
  background-color: #ffffff;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  min-height: 70vh;
}

.post-header {
  border-bottom: 1px solid #e8e8e8;
  padding-bottom: 24px;
  margin-bottom: 24px;
}

.post-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 16px;
  color: #333;
}

.edit-title-input {
  margin-bottom: 16px;

  /deep/ input {
    font-size: 32px;
    font-weight: 700;
    color: #333;
    border: 1px solid #e8e8e8;
    border-radius: 4px;
    padding: 24px 16px;

    &:focus {
      border-color: #2d8cf0;
      box-shadow: 0 0 0 2px rgba(45, 140, 240, 0.1);
    }
  }
}

.post-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  color: #888;
}

.post-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.post-edit-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.post-edit-btn,
.post-delete-btn,
.post-save-btn,
.post-cancel-btn {
  padding: 6px 14px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
  font-weight: 500;
}

.post-edit-btn {
  color: #2d8cf0;
  border-color: #2d8cf0;
}

.post-edit-btn:hover {
  background: #2d8cf0;
  color: white;
}

.post-delete-btn {
  color: #ed4014;
  border-color: #ed4014;
}

.post-delete-btn:hover {
  background: #ed4014;
  color: white;
}

.post-save-btn {
  background: #2d8cf0;
  color: white;
  border-color: #2d8cf0;
}

.post-save-btn:hover {
  background: #2573d0;
  border-color: #2573d0;
}

.post-save-btn:disabled {
  background: #ccc;
  border-color: #ccc;
  cursor: not-allowed;
}

.post-cancel-btn {
  color: #666;
  border-color: #ddd;
}

.post-cancel-btn:hover {
  background: #f5f5f5;
}

.edit-actions {
  display: flex;
  gap: 8px;
}

.post-edit-form {
  margin-bottom: 40px;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-info a {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #555;
  font-weight: 500;
  transition: color 0.3s;
}

.user-info a:hover {
  color: #2d8cf0;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  margin-right: 12px;
  border: 2px solid #f0f0f0;
}

.post-content {
  font-size: 16px;
  line-height: 1.8;
  color: #444;
  margin-bottom: 40px;
  min-height: 200px;
  white-space: pre-wrap;
}

.edit-content-input {
  margin-bottom: 40px;

  /deep/ textarea {
    font-size: 16px;
    line-height: 1.8;
    color: #444;
    border: 1px solid #e8e8e8;
    border-radius: 4px;
    padding: 12px;

    &:focus {
      border-color: #2d8cf0;
    }
  }
}

.post-comments h2 {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 24px;
  border-bottom: 2px solid #2d8cf0;
  padding-bottom: 12px;
  color: #333;
}

.comment-form {
  margin-bottom: 30px;
  text-align: right;
}

.comment-form textarea {
  width: 100%;
  min-height: 100px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
  resize: vertical;
  margin-bottom: 10px;
}

.comment-form button {
  padding: 10px 20px;
  background-color: #2d8cf0;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.comment-form button:hover {
  background-color: #57a3f3;
}

.post-comments {
  padding-top: 20px;
}

.comment {
  // position: relative;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.comment:last-child {
  border-bottom: none;
}

.comment-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.comment-date {
  font-size: 12px;
  color: #aaa;
}

.comment-body {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-left: 48px;
}

.comment-content {
  font-size: 15px;
  color: #555;
  white-space: pre-wrap;
  line-height: 1.7;
  flex-grow: 1;
}

.comment-actions {
  display: flex;
  gap: 8px;
  margin-left: 12px;
  flex-shrink: 0;
  opacity: 0;
  visibility: hidden;
  transition:
    opacity 0.2s,
    visibility 0.2s;
}

.comment:hover .comment-actions {
  opacity: 1;
  visibility: visible;
}

.comment-edit-textarea {
  flex-grow: 1;
  width: 100%;
  min-height: 80px;
  padding: 8px 12px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  font-size: 15px;
  color: #555;
  line-height: 1.7;
  resize: vertical;
  font-family: inherit;
}

.comment-edit-textarea:focus {
  outline: none;
  border-color: #2d8cf0;
}

.reply-icon-btn,
.edit-icon-btn,
.delete-icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  font-size: 13px;
  color: #666;
  transition: color 0.2s;
}

.reply-icon-btn:hover,
.edit-icon-btn:hover {
  color: #2d8cf0;
}

.delete-icon-btn:hover {
  color: #ed4014;
}

.save-btn,
.cancel-btn {
  padding: 4px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.save-btn {
  background: #2d8cf0;
  color: white;
  border-color: #2d8cf0;
}

.save-btn:hover {
  background: #2573d0;
}

.cancel-btn {
  background: white;
  color: #666;
}

.cancel-btn:hover {
  background: #f5f5f5;
}

.reply-icon-btn svg {
  width: 20px;
  height: 20px;
  stroke: #555;
}

.reply-form {
  margin-left: 48px;
  margin-top: 16px;
  background-color: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
}

.reply-form textarea {
  min-height: 80px;
  border: 1px solid #e0e0e0;
}

.reply-form-actions {
  text-align: right;
  margin-top: 10px;
}

.reply-form-actions button {
  padding: 8px 18px;
  font-size: 14px;
  margin-left: 10px;
}

.reply-form-actions button:last-child {
  background-color: #aaa;
}

.reply-form-actions button:last-child:hover {
  background-color: #bbb;
}

.replies {
  margin-top: 20px;
  margin-left: 18px;
  padding-left: 30px;
  border-left: 2px solid #eef1f6;
}

.reply {
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin-top: 12px;
  border-bottom: none;
}

.reply .comment-body {
  padding-left: 0;
}
</style>
