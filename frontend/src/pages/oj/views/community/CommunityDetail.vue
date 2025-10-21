<template>
  <main>
    <div class="contents" v-if="post">
      <div class="post-header">
        <h1 class="post-title">{{ post.title }}</h1>
        <div class="post-meta">
          <div class="user-info">
            <router-link
              :to="{
                name: 'user-home',
                params: { username: post.author_name },
              }"
            >
              <img
                class="avatar"
                :src="
                  post.author_avatar ||
                  'https://cdn-icons-png.flaticon.com/512/473/473406.png'
                "
                alt="avatar"
              />
              <span>{{ post.author_name }}</span>
            </router-link>
          </div>
          <div class="post-date">
            {{ post.created_at | localtime("YYYY-MM-DD HH:mm") }}
          </div>
        </div>
      </div>
      <div class="post-content" v-html="post.content"></div>
      <div class="post-comments">
        <h2>{{ $t("m.Community_Comments") }} {{ commentCount }}</h2>
        <div class="comment-form">
          <textarea
            v-model="commentContent"
            :placeholder="$t('m.Community_Create_Comment_Placeholder')"
          ></textarea>
          <button @click="submitComment">
            {{ $t("m.Community_Create_Comment_Btn") }}
          </button>
        </div>
        <div v-for="comment in post.comments" :key="comment.id" class="comment">
          <div class="comment-header">
            <div class="user-info">
              <router-link
                :to="{
                  name: 'user-home',
                  params: { username: comment.author_name },
                }"
              >
                <img
                  class="avatar"
                  :src="
                    comment.author_avatar ||
                    'https://cdn-icons-png.flaticon.com/512/473/473406.png'
                  "
                  alt="avatar"
                />
                <span>{{ comment.author_name }}</span>
              </router-link>
            </div>
            <div class="comment-date">
              {{ comment.created_at | localtime("YYYY-MM-DD HH:mm") }}
            </div>
          </div>
          <div class="comment-content">{{ comment.content }}</div>
          <div v-if="comment.replies" class="replies">
            <div
              v-for="reply in comment.replies"
              :key="reply.id"
              class="comment reply"
            >
              <div class="comment-header">
                <div class="user-info">
                  <router-link
                    :to="{
                      name: 'user-home',
                      params: { username: reply.author_name },
                    }"
                  >
                    <img
                      class="avatar"
                      :src="
                        reply.author_avatar ||
                        'https://cdn-icons-png.flaticon.com/512/473/473406.png'
                      "
                      alt="avatar"
                    />
                    <span>{{ reply.author_name }}</span>
                  </router-link>
                </div>
                <div class="comment-date">
                  {{ reply.created_at | localtime("YYYY-MM-DD HH:mm") }}
                </div>
              </div>
              <div class="comment-content">{{ reply.content }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else>
      <ErrorSign
        v-if="error"
        :code="error.code"
        :description="error.description"
        :solution="error.solution"
      />
      <div v-else>Loading...</div>
    </div>
  </main>
</template>

<script>
import api from "../../api"
import ErrorSign from "../general/ErrorSign.vue"

export default {
  name: "CommunityDetail",
  components: {
    ErrorSign,
  },
  data() {
    return {
      post: null,
      error: null,
      isLoading: false,
      commentContent: "",
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
  },
  computed: {
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

.post-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  color: #888;
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

.comment-content {
  font-size: 15px;
  color: #555;
  padding-left: 48px;
  line-height: 1.7;
}

.replies {
  margin-top: 20px;
  padding-left: 48px;
}

.reply {
  padding: 16px;
  background-color: #f7f8fa;
  border-radius: 8px;
  margin-top: 12px;
  border-bottom: none;
}
</style>
