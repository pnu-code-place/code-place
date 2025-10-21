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
  },
  computed: {
    commentCount() {
      // 댓글 개수는 comments + replies의 합계로 계산합니다.
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
  margin: 20px auto;
  background-color: #fff;
  padding: 20px;
  border-radius: var(--container-border-radius);
  border: 1px solid var(--container-border-color);
  min-height: 70vh;
}

.post-header {
  border-bottom: 1px solid #eee;
  padding-bottom: 20px;
  margin-bottom: 20px;
}

.post-title {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 20px;
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
  color: #333;
  font-weight: 500;
}

.user-info a:hover {
  color: #2d8cf0;
}

.avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  margin-right: 10px;
}

.post-content {
  font-size: 16px;
  line-height: 1.8;
  color: #333;
  margin-bottom: 40px;
  min-height: 200px;
}

.post-comments h2 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.post-comments {
  padding: 20px;
}

.comment {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f5f5f5;
}

.comment:last-child {
  border-bottom: none;
}

.comment-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.comment-date {
  font-size: 12px;
  color: #aaa;
}

.comment-content {
  font-size: 15px;
  color: #555;
  padding-left: 40px;
}

.replies {
  margin-top: 15px;
  padding-left: 40px;
}

.reply {
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 5px;
  margin-top: 10px;
  border-bottom: none;
}
</style>
