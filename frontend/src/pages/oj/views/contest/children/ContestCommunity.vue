<script>
import {
  POST_TYPE,
  QUESTION_STATUS,
  SORT_TYPE,
} from "../../../../../utils/constants"
export default {
  data() {
    return {
      activeTab: "all",
      posts: [
        {
          id: 101,
          title: "대회 시작 전 준비 질문",
          content_preview: "환경설정은 어떤 걸로 하면 좋나요?",
          post_type: "QUESTION",
          question_status: "OPEN",
          author_name: "taekyung",
          author_avatar: "",
          created_at: new Date().toISOString(),
          comment_count: 2,
          is_mine: true,
        },
        {
          id: 102,
          title: "대회 후 풀이 공유합니다",
          content_preview: "3번 문제는 그리디로 풀 수 있어요.",
          post_type: "ARTICLE",
          question_status: null,
          author_name: "admin",
          author_avatar: "",
          created_at: new Date(Date.now() - 86400000 * 2).toISOString(),
          comment_count: 5,
          is_mine: false,
        },
      ],
    }
  },
  methods: {
    goToCreatePost() {
      this.$router.push({
        name: "contest-community-create",
        params: { contestID: this.$route.params.contestID },
      })
    },
    goToPost(postId) {
      this.$router.push({ name: "community-detail", params: { postId } })
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
  },
}
</script>

<template>
  <div class="contest-community">
    <div class="community-header">
      <div class="left-section">
        <p>{{ $t("m.Contest_Community") }}</p>
        <div class="segmented">
          <div class="indicator" :class="{ right: activeTab === 'my' }"></div>
          <button
            :class="{ active: activeTab === 'all' }"
            @click="activeTab = 'all'"
          >
            {{ $t("m.Contest_All_Posts") }}
          </button>
          <button
            :class="{ active: activeTab === 'my' }"
            @click="activeTab = 'my'"
          >
            {{ $t("m.Contest_My_Questions") }}
          </button>
        </div>
      </div>
      <Button class="write-btn" @click="goToCreatePost">{{
        $t("m.Community_Create_Comment_Btn")
      }}</Button>
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
                backgroundColor: QUESTION_STATUS[post.question_status].color,
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
.segmented {
  position: relative;
  display: flex;
  width: 150px;
  height: 30px;
  border-radius: 7px;
  overflow: hidden;
  background: #f3f4f6;
}
.segmented button {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 12px;
  font-weight: medium;
  cursor: pointer;
  z-index: 2;
  transition: color 0.25s ease;
}
.segmented button.active {
  color: white;
  font-weight: 600;
}
.indicator {
  position: absolute;
  top: 0;
  left: 0;
  width: 50%;
  height: 100%;
  background: #494a67;
  border-radius: 7px;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1;
}
.indicator.right {
  transform: translateX(100%);
}
.write-btn {
  background: #3475e0;
  color: white;
  border-radius: 7px;
  font-weight: bold;
  border: none;
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
</style>
