<template>
  <div class="fs-root">
    <div class="fs-header">
      <span class="fs-header-label">FAMILY SITE</span>
      <div class="fs-header-line" />
    </div>
    <div class="fs-grid">
      <a
        class="fs-card"
        v-for="site in sites"
        :key="site.title"
        :href="site.url"
        target="_blank"
        rel="noopener noreferrer"
      >
        <div class="fs-accent" />
        <div class="fs-card-title" v-html="site.title" />
        <div class="fs-card-sub">바로가기 <span class="fs-arrow">→</span></div>
      </a>
    </div>
  </div>
</template>

<script>
export default {
  name: "HomeFamilySite",
  data() {
    return {
      sites: [
        {
          title: "부산대학교<br>AI융합교육원",
          url: "https://swedu.pusan.ac.kr",
        },
        {
          title: "부산대학교<br>학생지원시스템",
          url: "https://onestop.pusan.ac.kr/",
        },
        {
          title: "스마트교육플랫폼<br>PLATO",
          url: "https://plato.pusan.ac.kr",
        },
        {
          title: "온라인강좌<br>인프런",
          url: "https://www.inflearn.com",
        },
        {
          title: "부산대학교<br>SW역량지원시스템",
          url: "https://swcss.pusan.ac.kr/",
        },
      ],
    }
  },
}
</script>

<style scoped lang="less">
.fs-root {
  padding: 40px 0 0;
}

.fs-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.fs-header-label {
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.1em;
  color: #9999a6;
  white-space: nowrap;
}

.fs-header-line {
  height: 1px;
  flex: 1;
  background-color: #e5e5ed;
}

.fs-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;

  @media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.fs-card {
  border-radius: 12px;
  padding: 12px 14px;
  cursor: pointer;
  text-decoration: none;
  display: flex;
  flex-direction: column;
  gap: 5px;
  background-color: #f4f6fb;
  border: 0.5px solid #e2e6f0;
  transition:
    transform 0.16s ease,
    box-shadow 0.16s ease,
    background-color 0.16s ease,
    border-color 0.16s ease;

  &:hover {
    transform: translateY(-2px);
    background-color: #edf0fa;
    box-shadow: 0 6px 18px rgba(90, 110, 200, 0.1);
    border-color: #c8cfea;

    .fs-arrow {
      transform: translateX(2px);
    }
  }
}

.fs-accent {
  width: 20px;
  height: 2px;
  border-radius: 2px;
  background-color: #7c8fd6;
  margin-bottom: 2px;
}

.fs-card-title {
  font-size: 11.5px;
  font-weight: 700;
  line-height: 1.5;
  color: #2d3561;
}

.fs-card-sub {
  font-size: 10px;
  color: #9ba5c9;
  display: flex;
  align-items: center;
  gap: 2px;
}

.fs-arrow {
  display: inline-block;
  transition: transform 0.14s;
}
</style>
