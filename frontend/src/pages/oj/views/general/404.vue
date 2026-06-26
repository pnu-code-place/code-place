<template>
  <div class="error404 flex-container">
    <section id="main" class="error404-panel">
      <div class="error404-content">
        <div class="error404-body">
          <div class="error404-mark" aria-hidden="true">
            <span>4</span>
            <svg class="error404-compass" viewBox="0 0 96 96">
              <circle cx="48" cy="48" r="35" />
              <path d="M59 25 50 51 28 64 37 38 59 25Z" />
            </svg>
            <span>4</span>
          </div>

          <div class="error404-copy">
            <h2>페이지를 찾을 수 없습니다</h2>
            <p>
              입력하신 주소가 올바르지 않거나 페이지가 이동 또는 삭제되었습니다.
            </p>
            <div class="error404-actions">
              <button
                class="error404-button secondary"
                type="button"
                @click="backPage"
              >
                {{ $t("m.Back") }}
              </button>
              <button
                class="error404-button primary"
                type="button"
                @click="goHome"
              >
                {{ $t("m.Go_Home") }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: "Error404Page",
  methods: {
    backPage() {
      this.$router.go(-1)
    },
    goHome() {
      this.$router.push({
        name: "home",
      })
    },
  },
}
</script>

<style lang="less" scoped>
.error404 {
  width: 100%;
  margin: 0;
  background: #ffffff;

  #main {
    flex: auto;
  }
}

.error404-panel {
  overflow: visible;
  background: #ffffff;
  border: 0;
  border-radius: 0;
}

.error404-content {
  width: 100%;
  max-width: var(--global-width);
  margin: 0 auto;
  padding: 0 32px;
}

.error404-body {
  display: grid;
  grid-template-columns: 420px minmax(320px, 440px);
  align-items: center;
  justify-content: center;
  gap: 72px;
  min-height: calc(
    100vh - var(--header-height) - 28px - var(--footer-height) -
      var(--footer-margin)
  );
  padding: 0 0 32px;
}

.error404-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #5661f6;
  font-size: 148px;
  font-weight: 800;
  line-height: 1;
}

.error404-compass {
  flex: none;
  width: 116px;
  height: 116px;
  color: #5661f6;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 5;

  path {
    fill: #eef1ff;
  }
}

.error404-copy {
  min-width: 0;
  max-width: 440px;

  h2 {
    margin: 0 0 12px;
    color: #303747;
    font-size: 30px;
    font-weight: 800;
    line-height: 1.32;
  }

  p {
    margin: 0;
    color: #697386;
    font-size: 15px;
    font-weight: 500;
    line-height: 1.8;
    overflow-wrap: anywhere;
  }
}

.error404-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 28px;
}

.error404-button {
  height: 38px;
  padding: 0 18px;
  font-size: 14px;
  font-weight: 800;
  border: 0;
  border-radius: 999px;
  cursor: pointer;
  transition:
    color 0.15s ease,
    background-color 0.15s ease,
    box-shadow 0.15s ease;

  &.primary {
    color: #ffffff;
    background: #5661f6;
    box-shadow: 0 8px 20px rgba(86, 97, 246, 0.22);

    &:hover {
      background: #4652ea;
    }
  }

  &.secondary {
    color: #5661f6;
    background: #eef1ff;

    &:hover {
      background: #e3e7ff;
    }
  }
}

@media (max-width: 760px) {
  .error404-content {
    padding: 0 24px;
  }

  .error404-body {
    grid-template-columns: 1fr;
    gap: 28px;
    min-height: 0;
    padding: 42px 0 56px;
  }

  .error404-mark {
    font-size: 88px;
  }

  .error404-compass {
    width: 76px;
    height: 76px;
  }

  .error404-copy h2 {
    font-size: 24px;
  }
}
</style>
