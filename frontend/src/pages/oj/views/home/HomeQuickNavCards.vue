<template>
  <div class="quick-nav-padding">
    <p class="section-title">바로가기</p>
    <div class="quick-nav-cards">
      <div class="nav-card" v-for="card in cards" :key="card.title" @click="goRoute(card.route)">
        <div class="card-icon" :style="{ backgroundColor: card.iconBg }">
          <span class="card-icon-emoji">{{ card.icon }}</span>
        </div>
        <p class="card-title">{{ card.title }}</p>
        <p class="card-desc">{{ card.desc }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "HomeQuickNavCards",
  data() {
    return {
      cards: [
        {
          title: "문제 풀이",
          desc: "다양한 알고리즘 문제를 풀어보세요.",
          icon: "💻",
          iconBg: "#ede9ff",
          route: "problem-list",
        },
        {
          title: "콘테스트",
          desc: "정기 콘테스트에 참여하고 실력을 확인하세요.",
          icon: "🏆",
          iconBg: "#fff3de",
          route: "contest-list",
        },
        {
          title: "랭킹",
          desc: "실력 상위 개발자들과 경쟁해보세요.",
          icon: "📊",
          iconBg: "#fde8e8",
          route: "acm-rank",
        },
        {
          title: "커뮤니티",
          desc: "질문하고, 답변하며 함께 성장하세요.",
          icon: "💬",
          iconBg: "#e5f9f2",
          route: "community",
        },
      ],
    }
  },
  methods: {
    goRoute(name) {
      this.$router.push({ name })
    },
  },
}
</script>

<style scoped lang="less">
.quick-nav-padding {
  width: 100%;
  padding: 24px 0 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #14141f;
  margin: 0;
}

.quick-nav-cards {
  display: flex;
  gap: 16px;
}

.nav-card {
  background-color: #ffffff;
  border: 1px solid #e5e5ed;
  border-radius: 16px;
  padding: 20px;
  width: 220px;
  height: 160px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.2s;
  flex: 1;

  &:hover {
    box-shadow: 0 4px 16px rgba(91, 100, 237, 0.1);
    transform: translateY(-2px);
  }
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-icon-emoji {
  font-size: 22px;
  line-height: 1;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: #14141f;
  margin: 0;
}

.card-desc {
  font-size: 12px;
  color: #8c8c9e;
  margin: 0;
  line-height: 1.6;
}
</style>
