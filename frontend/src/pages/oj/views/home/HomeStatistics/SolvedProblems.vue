<script>
import Time from "../../../../../utils/time";

export default {
  data() {
    return {
      animationTimer: null,
      animationTime: 0,
      flipTime: 1.0,
      showNumberTime: 1.5,
    }
  },
  props: {
    extended: {
      type: Boolean,
      default: false
    },
    solvedProblems: {
      type: Number,
      default: 388
    }
  },
  computed: {
    flipped() {
      return this.animationTime > this.flipTime ? "flipped" : ""
    },
    showNumber() {
      return this.animationTime >= this.showNumberTime ? "show-number" : ""
    },
    currentTime() {
      return Time.utcToLocal()
    }
  },
  watch: {
    extended: function (newVal, oldVal) {
      if (newVal) {
        this.animationTime = 0;
        this.animationTimer = setInterval(() => {
          if (this.animationTime < this.showNumberTime) {
            this.animationTime += 0.1;
          } else {
            this.animationTime = this.showNumberTime;
            clearInterval(this.animationTimer);
          }
        }, 100);
      } else {
        this.animationTime = 0;
        clearInterval(this.animationTimer);
      }
    }
  }
}
</script>

<template>
  <div :class="`solved-problems ${this.flipped}`">
    <div class="number-wrapper">
      <transition name="number">
        <div v-if="showNumber" class="number">
          <span>{{ solvedProblems }}</span>
          <span class="problem">{{ $t('m.Problem')}}</span>
        </div>
      </transition>
    </div>
    <div :class="`flip-inner ${flipped} ${showNumber}`">
      <div class="flip-front">
        <transition name="gauge">
          <div v-if="extended" class="gauge">
          </div>
        </transition>
        <span>
        {{ $t('m.Grading') }}
      </span>
      </div>
      <div class="flip-back">
      <span>
        {{ $t('m.Correct') }}
      </span>
      </div>
    </div>
    <div class="standard-wrapper">
    <transition name="standard">
      <div v-if="flipped">
        {{ this.currentTime }} {{ $t('m.Standard') }}
      </div>
    </transition>
    </div>
  </div>
</template>

<style scoped lang="less">
.solved-problems {
  //transform: matrix3d(0.9303999999999999,-0.17,-0.17,0,0.17,0.9303999999999999,-0.17,-0.0011,0.17,0.17,0.9603999999999999,0,-10,-50,0,1);
  transform-origin: center center 0;
  display: flex;
  height: var(--statistics-extend-height);
  align-items: center;
  justify-content: space-around;
  flex-direction: column;
  perspective: 900px;
  transition: all 0.7s ease-in-out;


  .number-wrapper {
    height: 75px;
    .number {
      font-size: 50px;
      font-weight: 900;
    }
  }

  .flip-inner {
    position: relative;
    width: 300px;
    height: 80px;
    transform-style: preserve-3d;
    transition: all 0.7s;
    transform: translateY(-60%);

    .flip-front {
      width: 100%;
      height: 100%;
      background-color: #f3f4f4;
      border-radius: 30px;
      overflow: hidden;
      display: flex;
      position: absolute;
      backface-visibility: hidden;

      .gauge {
        position: absolute;
        height: 100%;
        width: 100%;
        background-color: var(--point-color)
      }

      span {
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        font-size: 30px;
        font-weight: 900;
        color: white;
        text-shadow: 0 0 20px rgba(255, 255, 255, 1);
      }
    }

    .flip-back {
      width: 100%;
      height: 100%;
      position: absolute;
      background-color: #90f363;
      transform: rotateY(180deg);
      backface-visibility: hidden;
      border-radius: 30px;

      span {
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        font-size: 30px;
        font-weight: 900;
        color: white;
        text-shadow: 0 0 20px rgba(255, 255, 255, 1);
      }

      &.show-number {
        animation: hover 1.5s infinite;
      }
    }

    &.flipped {
      transform: rotateY(180deg);
    }
    &.show-number {
      transform: translateY(0) rotateY(180deg) ;
    }
  }
  .standard-wrapper {
    height:12px;
  }
}


.problem {
  font-size: 40px;
  font-weight: 600;
}


.gauge-enter-active {
  transition: all 1.1s ease-in-out;
}

.gauge-leave-active {
  transition: all 0.3s ease-in-out;
}

.gauge-enter, .gauge-leave-to {
  transform: translateX(-100%);
}

.gauge-enter-to, .gauge-leave {
  transform: translateX(0);
}

.number-enter-active {
  transition: all 0.7s ease-in-out;
}

.number-leave-active {
  transition: all 0.3s ease-in-out;
}

.number-enter, .number-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

.number-enter-to, .number-leave {
  transform: translateY(0);
  opacity: 1;
}

.standard-enter, .standard-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

.standard-enter-to, .standard-leave {
  transform: translateY(0);
  opacity: 1;
}

.standard-enter-active, .standard-leave-active {
  transition: all 1s ease-in-out;
}


@keyframes hover {
  0% {
    transform: translateY(7%)
  }
  50% {
    transform: translateY(-7%)
  }
  100% {
    transform: translateY(7%)
  }
}


</style>
