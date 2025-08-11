<script>
import AchievementBadge from "../dashboardSection/AchievementBadge.vue"
import HorizontalGauge from "../dashboardSection/HorizontalGauge.vue"

export default {
  name: "GoalCard",
  components: { AchievementBadge, HorizontalGauge },
  data() {
    return {
      extended: false,
    }
  },
  props: {
    achievement: {
      Object: {
        id: Number,
        title: String,
        image: String,
        description: String,
        acquireTime: {
          type: String,
          default: "",
          required: false,
        },
        goal: Number,
        current: Number,
      },
      required: true,
    },
    acquired: {
      type: Boolean,
      default: false,
    },
    extendReverse: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    extend() {
      this.extended = true
    },
    retract() {
      this.extended = false
    },
  },
  computed: {
    acquireDate() {
      return this.acquired ? this.achievement.acquireTime.split("T")[0] : ""
    },
    progress() {
      return (this.achievement.current / this.achievement.goal).toFixed(1)
    },
    progressPercent() {
      return `${this.progress * 100}%`
    },
  },
}
</script>

<template>
  <li class="goal-card" @mouseover="extend" @mouseleave="retract">
    <div class="goal-card__image">
      <AchievementBadge
        :title="achievement.title"
        :acquireTime="achievement.acquireTime"
        :image="achievement.image"
        :description="achievement.description"
        :greyscale="!acquired"
        :tooltip-disabled="true"
      />
    </div>
    <div class="goal-card__extend">
      <div class="goal-card__info">
        <h3>{{ achievement.title }}</h3>
        <p>{{ achievement.description }}</p>
        <div v-if="acquired" class="goal-card__date goal-card__additional">
          <p>{{ $t("m.Date") }} : {{ acquireDate }}</p>
        </div>
        <div v-else class="goal-card__progress goal-card__additional">
          <p>{{ achievement.current }} / {{ achievement.goal }}</p>
          <div class="progress-wrapper">
            <HorizontalGauge :progress="progress"></HorizontalGauge>
          </div>
          <p>{{ progressPercent }}</p>
        </div>
      </div>
    </div>
  </li>
</template>

<style scoped lang="less">
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(-50%) translateY(0%);
}

.slide-enter-to,
.slide-leave-from {
  transform: translateX(0%) translateY(0%);
}

.goal-card {
  display: flex;
  transition: all 0.3s ease;
  position: relative;
  flex-direction: column;

  .goal-card__image {
    width: 75px;
  }

  .goal-card__extend {
    position: absolute;
    height: 0;
    width: 0;
    left: 50%;
    top: -15%;
    overflow: hidden;
    z-index: 10;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
    background: white;

    .goal-card__info {
      width: 150px;
      height: auto;
      padding: 10px;
      margin-top: 95px;
      display: flex;
      flex-direction: column;
      gap: 5px;
      transform: translateX(-50%);

      h3 {
        font-size: 14px;
        font-weight: 700;
      }

      p {
        font-size: 12px;
        font-weight: 500;
      }
    }
  }
}

.goal-card:hover {
  .goal-card__image {
    z-index: 15;
  }

  .goal-card__extend {
    width: 200%;
    height: auto;
    left: -50%;
    border-color: rgba(222, 222, 222, 1);
    transform: scaleY(1);
    transition: all 0.2s ease;

    .goal-card__info {
      transform: translateX(0);
      transition: all 0.2s ease;

      .progress-wrapper {
        width: 100%;
        height: 8px;
      }
    }
  }
}
</style>
