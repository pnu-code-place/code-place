<template>
  <div class="question-list-widget">
    <div class="widget-header">
      <h3 class="widget-title">
        <Icon type="ios-help-circle" size="20"></Icon>
        {{ $t("m.Community_Question_Title") }}
      </h3>
      <p class="widget-subtitle">{{ $t("m.Community_Question_Subtitle") }}</p>
    </div>

    <div class="question-items">
      <div v-for="question in questions" :key="question.id" class="question-item" @click="goToQuestion(question.id)">
        <div class="question-status">
          <span class="status-badge" :class="question.question_status === 'OPEN' ? 'status-open' : 'status-closed'">
            {{ question.question_status === 'OPEN' ? $t("m.Community_Question_Open") : $t("m.Community_Question_Closed")
            }}
          </span>
        </div>
        <div class="question-content">
          <h4 class="question-title">{{ question.title }}</h4>
          <div class="question-meta">
            <span class="author">
              <img class="avatar"
                :src="question.author_avatar || 'https://cdn-icons-png.flaticon.com/512/473/473406.png'"
                :alt="question.author_name" />
              {{ question.author_name }}
            </span>
            <span class="comments" v-if="question.comment_count > 0">
              <Icon type="ios-chatbubble-outline"></Icon>
              {{ question.comment_count }}
            </span>
          </div>
        </div>
      </div>

      <div v-if="questions.length === 0" class="empty-state">
        <Icon type="ios-help-circle-outline" size="48"></Icon>
        <p>{{ $t("m.Community_Question_No_Questions") }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@oj/api";

export default {
  name: "QuestionList",
  data() {
    return {
      questions: [],
      isLoading: false,
    };
  },
  mounted() {
    this.fetchQuestions();
  },
  methods: {
    async fetchQuestions() {
      this.isLoading = true;
      try {
        const res = await api.getCommunityPostList(0, 5, 'QUESTION', 'OPEN');
        this.questions = res.data.data.results;
      } catch (err) {
        console.error("Failed to fetch questions:", err);
      } finally {
        this.isLoading = false;
      }
    },
    goToQuestion(questionId) {
      this.$router.push({ name: "community-detail", params: { postId: questionId } });
    },
  },
};
</script>

<style lang="less" scoped>
.question-list-widget {
  background: var(--bg-color);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 4px 16px rgba(50, 48, 107, 0.12);
  }
}

.widget-header {
  padding: 20px;
  background: var(--point-color);
  color: white;
  text-align: center;

  .widget-title {
    margin: 0 0 8px;
    font-size: 18px;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }

  .widget-subtitle {
    margin: 0;
    font-size: 13px;
    opacity: 0.9;
    font-weight: 400;
  }
}

.question-items {
  max-height: 500px;
  overflow-y: auto;
  overflow-x: hidden;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: var(--bg-color);
  }

  &::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 3px;

    &:hover {
      background: rgba(50, 48, 107, 0.3);
    }
  }
}

.question-item {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  gap: 12px;

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background: rgba(50, 48, 107, 0.05);

    .question-title {
      color: var(--point-color);
    }
  }
}

.question-status {
  flex-shrink: 0;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;

  &.status-open {
    background: #FFF3E0;
    color: #F57C00;
  }

  &.status-closed {
    background: #E8F5E9;
    color: #43A047;
  }
}

.question-content {
  flex: 1;
  min-width: 0;
}

.question-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.4;
  transition: color 0.3s ease;
}

.question-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--text-color);
  opacity: 0.6;

  span {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .ivu-icon {
    font-size: 13px;
  }

  .avatar {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    object-fit: cover;
    display: flex;
  }
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: var(--text-color);
  opacity: 0.4;

  .ivu-icon {
    margin-bottom: 12px;
    opacity: 0.5;
  }

  p {
    margin: 0;
    font-size: 14px;
  }
}
</style>
