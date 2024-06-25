<script>
import Time from "../../../../../utils/time";

export default {
  data() {
    return {
      itemTimer: null,
      MAX_ITEMS: 22,
      displayNumber: 0,
      countingTime: 1.5,
      steps: 30,
      itemArray: []
    }
  },
  props: {
    extended: {
      type: Boolean,
      default: false
    },
    totalProblems: {
      type: Number,
      default: 388
    }
  },
  computed: {
    countingInterval() {
      return Math.max((this.totalProblems / (this.steps)).toFixed(0), 1);
    },
    timeInterval() {
      return (this.countingTime * 1000 / this.steps).toFixed(0);
    },
    currentTime() {
      return Time.utcToLocal()
    }
  },
  methods: {
    getRandomColor() {
      const red = Math.floor(Math.random() * 256);
      const green = Math.floor(Math.random() * 256);
      const blue = Math.floor(Math.random() * 256);
      return `rgb(${red}, ${green}, ${blue}, 0.2)`;
    }
  },
  watch: {
    extended: function (newVal, oldVal) {
      if (newVal) {
        this.displayNumber = 0;
        this.itemArray = []
        this.itemTimer = setInterval(() => {
          if (this.displayNumber < this.totalProblems) {
            this.displayNumber += this.countingInterval;
            if (this.itemArray.length < this.MAX_ITEMS) {
              this.itemArray.push(this.displayNumber);
            }
          } else {
            this.displayNumber = this.totalProblems;
            clearInterval(this.itemTimer);
          }
        }, this.timeInterval);
      }
    }
  }
}
</script>

<template>
  <div class="total-problems">
    <span class="number" v-if="extended">{{ this.displayNumber }}<span class="problem">{{ $t('m.Problems') }}</span></span>
    <transition-group name="item" tag="ul" class="stack-wrapper">
      <li class="stack-item" :style="{backgroundColor: getRandomColor()}" v-for="(elem, index) in this.itemArray"
          :key="index"/>
    </transition-group>
    <transition name="standard">
      <div v-if="extended" class="standard">
        {{ this.currentTime }} {{ $t('m.Standard') }}
      </div>
    </transition>
  </div>
</template>

<style scoped lang="less">
.total-problems {
  height: 273px;
  position: relative;

  .number {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 50px;
    font-weight: 900;
    color: #333;
  }

  .stack-wrapper {
    height: 100%;
    display: flex;
    flex-direction: column-reverse;
    align-items: flex-end;
    gap: 5px;
    flex-wrap: wrap;
  }
}

.problem {
  font-size: 40px;
  font-weight: 600;
}

.standard{
  position : absolute;
  bottom: 15px;
  right: 0;
  left: 0;
  width: 100%;
  text-align: center;
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

.stack-item {
  width: 50%;
  height: 20px;
  background-color: var(--submission-result-btn-color);
  border-radius: 5px;
  transition: all 0.5s ease-in-out;
  list-style-type: none;
}

.item-enter-active, .item-leave-active {
  transition: all 0.3s;
}

.item-enter, .item-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}

.item-enter-to, .item-leave {
  transform: translateY(0);
  opacity: 1;
}

</style>
