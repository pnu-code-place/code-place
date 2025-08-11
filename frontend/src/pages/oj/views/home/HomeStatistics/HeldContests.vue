<script>
import Time from "../../../../../utils/time"

export default {
  data() {
    return {
      countingTime: 1.5,
      timer: null,
      steps: 100,
      displayCount: 0,
    }
  },
  props: {
    extended: {
      type: Boolean,
      default: false,
    },
    heldContests: {
      type: Number,
      default: 388,
    },
  },
  computed: {
    countingInterval() {
      return Math.max((this.heldContests / this.steps).toFixed(0), 1)
    },
    timeInterval() {
      return ((this.countingTime * 1000) / this.steps).toFixed(0)
    },
    currentTime() {
      return Time.utcToLocal()
    },
  },
  // extended가 true가 되면, 0부터 388까지 2초 동안 증가하면서 숫자를 보여준다.

  watch: {
    extended: function (newVal, oldVal) {
      if (newVal) {
        this.displayCount = 0
        this.timer = setInterval(() => {
          if (this.displayCount < this.heldContests) {
            this.displayCount += this.countingInterval
          } else {
            this.displayCount = this.heldContests
            clearInterval(this.timer)
          }
        }, this.timeInterval)
      }
    },
  },
}
</script>

<template>
  <div class="held-contests">
    <div>
      <span class="number"
        >{{ this.displayCount
        }}<span class="times">{{ $t("m.Times") }}</span></span
      >
    </div>
    <div class="blocks">
      <transition name="second">
        <div v-if="extended">
          <span>2</span>
        </div>
      </transition>
      <transition name="first">
        <div v-if="extended">
          <span>1</span>
        </div>
      </transition>
      <transition name="third">
        <div v-if="extended">
          <span>3</span>
        </div>
      </transition>
    </div>
    <transition name="standard">
      <div v-if="extended">{{ this.currentTime }} {{ $t("m.Standard") }}</div>
    </transition>
  </div>
</template>

<style scoped lang="less">
.held-contests {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-direction: column;
  height: var(--statistics-extend-height);

  .number {
    font-size: 50px;
    font-weight: 900;
  }

  .blocks {
    display: flex;
    width: 100%;
    align-items: flex-end;

    div {
      width: 100%;
      display: flex;
      justify-content: center;
      padding-top: 15px;

      span {
        font-size: 20px;
        font-weight: 600;
      }

      &:nth-child(1) {
        background: linear-gradient(var(--pale-silver-color), white 100%);
        height: 80px;
      }

      &:nth-child(2) {
        background: linear-gradient(var(--pale-gold-color), white 100%);
        height: 100px;
      }

      &:nth-child(3) {
        background: linear-gradient(var(--pale-bronze-color), white 100%);
        height: 60px;
      }
    }
  }
}

.times {
  font-size: 40px;
  font-weight: 600;
  margin-left: 5px;
}

.second-leave-active,
.second-enter-active {
  transition: all 1s ease-in-out;
}

.first-enter-active,
.third-leave-active {
  transition: all 1.5s ease-in-out;
}

.first-leave-active,
.third-enter-active {
  transition: all 0.7s ease-in-out;
}

.standard-enter-active,
.standard-leave-active {
  transition: all 1s ease-in-out;
}

.first-enter,
.first-leave-to,
.second-enter,
.second-leave-to,
.third-enter,
.third-leave-to,
.standard-enter,
.standard-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

.first-enter-to,
.first-leave,
.second-enter-to,
.second-leave,
.third-enter-to,
.third-leave,
.standard-enter-to,
.standard-leave-to {
  transform: translateY(0);
  opacity: 1;
}
</style>
