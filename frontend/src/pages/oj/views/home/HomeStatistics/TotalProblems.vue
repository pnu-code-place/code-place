<script>
import Time from "../../../../../utils/time";

export default {
  data() {
    return {
      itemTimer: null,
      numberTimer: null,
      MAX_ITEMS: 16,
      displayNumber: 0,
      countingTime: 1.7,
      stackingTime: 2.0,
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
    numberInterval() {
      return (this.countingTime * 1000 / this.steps).toFixed(0);
    },
    currentTime() {
      return Time.utcToLocal()
    },
    itemInterval() {
      return Math.max((this.stackingTime * 1000 / this.MAX_ITEMS).toFixed(0), 1);
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
        this.itemArray = [];
        this.numberTimer = setInterval(() => {
          if (this.displayNumber < this.totalProblems) {
            this.displayNumber += this.countingInterval;
          } else {
            this.displayNumber = this.totalProblems;
            clearInterval(this.numberTimer);
          }
        }, this.numberInterval);
        this.itemTimer = setInterval(() => {
          if (this.itemArray.length < this.MAX_ITEMS) {
            this.itemArray.push(1);
          } else {
            clearInterval(this.itemTimer);
          }
        }, this.itemInterval);
      }
      else {
        this.displayNumber = 0;
        this.itemArray = [];
        clearInterval(this.numberTimer);
        clearInterval(this.itemTimer);
      }
    },
  }
}
</script>

<template>
  <div class="held-contests">
    <span class="number" v-if="extended">{{ this.displayNumber }}<span class="problem">{{
        $t('m.Problems')
      }}</span></span>
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
.held-contests {
  height: var(--statistics-extend-height);
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
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column-reverse;
    align-items: flex-end;
    gap: 5px;
    flex-wrap: wrap;
    padding-bottom: 36px;
  }
}

.problem {
  font-size: 40px;
  font-weight: 600;
}

.standard {
  position: absolute;
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
  width: 49%;
  height: 16px;
  background-color: var(--submission-result-btn-color);
  border-radius: 5px;
  transition: all 0.5s ease-in-out;
  list-style-type: none;
}

.item-enter-active, .item-leave-active {
  transition: all 0.6s;
}

.item-enter, .item-leave-to {
  transform: translateY(-200%);
  opacity: 0;
}

.item-enter-to, .item-leave {
  transform: translateY(0);
  opacity: 1;
}

</style>
