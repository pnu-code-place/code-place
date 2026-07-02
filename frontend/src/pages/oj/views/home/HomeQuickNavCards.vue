<template>
  <div class="quick-nav-padding">
    <p class="section-title">바로가기</p>
    <div class="quick-nav-cards">
      <div
        class="nav-card"
        v-for="card in cards"
        :key="card.title"
        :style="{ backgroundColor: card.cardBg }"
        @click="goRoute(card.route)"
      >
        <div class="card-arrow">→</div>
        <div class="card-top">
          <div class="card-icon" :style="{ backgroundColor: card.iconBg }">
            <span v-if="card.iconText" class="card-icon-text">{{
              card.iconText
            }}</span>
            <Icon v-else :type="card.icon" size="22" color="#ffffff" />
          </div>
          <p class="card-title">{{ card.title }}</p>
          <p class="card-desc">{{ card.desc }}</p>
        </div>
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
          title: "문제 풀기",
          desc: "다양한 알고리즘 문제를\n풀어보세요.",
          iconText: "</>",
          iconBg: "#7b6ef5",
          cardBg: "#eeeaff",
          route: "problem-list",
        },
        {
          title: "대회",
          desc: "대회에 참여하고\n실력을 확인하세요.",
          icon: "trophy",
          iconBg: "#f5a230",
          cardBg: "#fff5e8",
          route: "contest-list",
        },
        {
          title: "랭킹",
          desc: "실력 순위와 상위 유저를\n확인해보세요.",
          icon: "stats-bars",
          iconBg: "#34c175",
          cardBg: "#edf8f2",
          route: "acm-rank",
        },
        {
          title: "커뮤니티",
          desc: "질문하고, 답변하며\n함께 성장하세요.",
          icon: "chatbubbles",
          iconBg: "#8b90f0",
          cardBg: "#eef0fb",
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
  padding: 28px 0 0;
  display: flex;
  flex-direction: column;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #14141f;
  margin: 0;
}

.quick-nav-cards {
  display: flex;
  gap: 16px;
}

.nav-card {
  flex: 1;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  position: relative;
  cursor: pointer;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.75),
    0 2px 8px rgba(0, 0, 0, 0.05);
  transition:
    transform 0.2s,
    box-shadow 0.2s;

  &:hover {
    transform: translateY(-3px);
    box-shadow:
      inset 0 1px 0 rgba(255, 255, 255, 0.75),
      0 10px 28px rgba(0, 0, 0, 0.1);
  }
}

.card-top {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.card-icon-text {
  color: #ffffff;
  font-size: 10px;
  font-weight: 700;
  font-family: monospace;
  letter-spacing: -0.5px;
}

.card-icon {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  flex-shrink: 0;
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  color: #14141f;
  margin: 0 0 4px;
}

.card-desc {
  font-size: 13px;
  color: #6b6b7e;
  margin: 0;
  line-height: 1.65;
  white-space: pre-line;
}

.card-arrow {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: #14141f;
  flex-shrink: 0;
}
</style>
