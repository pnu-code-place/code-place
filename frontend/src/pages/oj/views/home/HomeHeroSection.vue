<template>
  <div class="hero-padding">
    <div class="hero-wrap">
      <div class="blob blob1" />
      <div class="blob blob2" />
      <div class="blob blob3" />

      <div class="inner">
        <!-- 좌측 -->
        <div class="left">
          <p class="greeting">
            <template v-if="isAuthenticated">안녕하세요, {{ user.username }}님!</template>
            <template v-else>코드로 성장하는 공간</template>
          </p>
          <h1 class="title">
            문제를 해결하고<br /><span class="title-em">성장하는</span> 개발자 공간
          </h1>
          <p class="desc">
            다양한 문제를 풀고, 실력을 키우고,<br />AI와 함께 더 빠르게 성장하세요.
          </p>
          <button class="btn-go" @click="goProblemList">
            문제 풀러 가기 →
          </button>
        </div>

        <!-- 우측 -->
        <div class="right">
          <div class="badge-float bf1">
            <span class="bf-icon green">✓</span>
            정답률 {{ acceptRateLabel }}
          </div>

          <div class="editor">
            <div class="editor-bar">
              <span class="ed-dot ed1" /><span class="ed-dot ed2" /><span class="ed-dot ed3" />
            </div>
            <div class="editor-body">
              <div class="cl"><span class="ln">1</span><span class="cm"># 투 포인터</span></div>
              <div class="cl"><span class="ln">2</span><span class="kw">def </span><span class="fn">solve</span><span class="nt">(arr):</span></div>
              <div class="cl"><span class="ln">3</span><span class="nt">&nbsp;&nbsp;l, r = </span><span class="st">0</span><span class="nt">, len(arr)-</span><span class="st">1</span></div>
              <div class="cl"><span class="ln">4</span><span class="kw">&nbsp;&nbsp;while </span><span class="nt">l &lt; r:</span></div>
              <div class="cl"><span class="ln">5</span><span class="kw">&nbsp;&nbsp;&nbsp;&nbsp;if </span><span class="fn">check</span><span class="nt">(l, r):</span></div>
              <div class="cl"><span class="ln">6</span><span class="kw">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return </span><span class="st">True</span></div>
            </div>
          </div>

          <div class="badge-float bf2">
            <span class="bf-icon amber">🏆</span>
            {{ solvedBadgeLabel }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex"
import api from "@oj/api"

export default {
  name: "HomeHeroSection",
  data() {
    return {
      totalProblems: null,
    }
  },
  computed: {
    ...mapGetters(["isAuthenticated", "user", "profile"]),
    acceptRateLabel() {
      const sub = (this.profile && this.profile.submission_number) || 0
      const acc = (this.profile && this.profile.accepted_number) || 0
      if (!sub) return "—"
      return Math.round((acc / sub) * 100) + "%"
    },
    solvedBadgeLabel() {
      if (this.isAuthenticated) {
        const acc = (this.profile && this.profile.accepted_number) || 0
        return "해결한 문제 " + acc + "개"
      }
      return this.totalProblems ? "문제 " + this.totalProblems + "개" : "문제 풀기"
    },
  },
  mounted() {
    api.getHomeStatistics().then((res) => {
      const d = res.data.data
      this.totalProblems = d.total_problem_length || d.total_problem_number || null
    }).catch(() => {})
  },
  methods: {
    goProblemList() {
      this.$router.push({ name: "problem-list" })
    },
  },
}
</script>

<style scoped lang="less">
.hero-padding {
  width: 100%;
  padding: 20px 0 0;
}

.hero-wrap {
  position: relative;
  background: #d4d8ff;
  border-radius: 18px;
  overflow: hidden;
  min-height: 260px;
}

.blob {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
}
.blob1 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, #b8beff 0%, transparent 65%);
  top: -150px; right: -60px;
  opacity: 0.65;
}
.blob2 {
  width: 280px; height: 280px;
  background: radial-gradient(circle, #c4b8ff 0%, transparent 65%);
  bottom: -110px; left: 20%;
  opacity: 0.5;
}
.blob3 {
  width: 200px; height: 200px;
  background: radial-gradient(circle, #aac4ff 0%, transparent 65%);
  top: 0; left: -40px;
  opacity: 0.45;
}

.inner {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 44px 52px;
  gap: 32px;
}

/* 좌측 */
.left {
  flex: 1;
  min-width: 0;
}

.greeting {
  font-size: 13px;
  font-weight: 500;
  color: #4a58a8;
  letter-spacing: 0.02em;
  margin-bottom: 10px;
}

.title {
  font-size: 34px;
  font-weight: 900;
  color: #1a1f5e;
  line-height: 1.22;
  margin-bottom: 14px;
  letter-spacing: -0.025em;
}

.title-em {
  color: #4a58a8;
}

.desc {
  font-size: 14px;
  color: #4a5290;
  line-height: 1.75;
  margin-bottom: 28px;
}

.btn-go {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #4a58a8;
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.18s, transform 0.15s;

  &:hover {
    background: #3a4890;
    transform: translateY(-2px);
  }
}

/* 우측 */
.right {
  flex-shrink: 0;
  position: relative;
  width: 250px;
}

.editor {
  background: #1a1f5e;
  border-radius: 14px;
  overflow: hidden;
  width: 100%;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.editor-bar {
  background: #111448;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.ed-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
}
.ed1 { background: #ff5f57; }
.ed2 { background: #febc2e; }
.ed3 { background: #28c840; }

.editor-body {
  padding: 14px 16px;
}

.cl {
  font-family: 'JetBrains Mono', 'Fira Mono', 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.9;
  display: flex;
  gap: 10px;
}

.ln  { color: rgba(255, 255, 255, 0.15); width: 16px; text-align: right; flex-shrink: 0; }
.kw  { color: #9da8ff; }
.fn  { color: #b8aaff; }
.st  { color: #aac8ff; }
.cm  { color: rgba(255, 255, 255, 0.2); }
.nt  { color: rgba(255, 255, 255, 0.8); }

.badge-float {
  position: absolute;
  background: rgba(255, 255, 255, 0.75);
  border-radius: 10px;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  font-weight: 500;
  color: #1a1f5e;
  border: 1px solid rgba(255, 255, 255, 0.95);
  white-space: nowrap;
}

.bf1 {
  top: -14px;
  right: -12px;
  animation: float1 3s ease-in-out infinite;
}

.bf2 {
  bottom: -14px;
  left: -12px;
  animation: float2 3.5s ease-in-out infinite;
}

.bf-icon {
  font-size: 15px;
  font-style: normal;

  &.green { color: #16a34a; }
  &.amber { color: #d97706; }
}

@keyframes float1 {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

@keyframes float2 {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(4px); }
}
</style>
