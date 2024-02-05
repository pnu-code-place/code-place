<template>
  <div class="timer">
    <div class="stopwatch">
      <Tooltip :content="'타이머 시작'" placement="bottom" v-if="!running">
        <CustomIconBtn @click="start()" class="far fa-play-circle" v-if="!running"/>
      </Tooltip>
      <Tooltip :content="'일시정지'" placement="bottom" v-if="running">
        <CustomIconBtn @click="pause()" class="far fa-pause-circle" v-if="running"/>
      </Tooltip>
      <div class="time">
        {{ this.time }}
      </div>
      <Tooltip :content="'초기화'" placement="bottom">
        <CustomIconBtn @click="reset()" class="fas fa-sync-alt"/>
      </Tooltip>
    </div>

  </div>
</template>

<script>
import CustomIconBtn from "./buttons/CustomIconBtn.vue";

export default {
  name: "ProblemTimer",
  components: {CustomIconBtn},
  data() {
    return {
      running: false,
      time: "00:00:00",
      intv: null,
      timeBegin: null,
      timeStopped: null,
      stoppedDuration: 0
    }
  },
  methods: {
    start() {
      if(this.running) return;

      if (this.timeBegin === null) {
        this.reset();
        this.timeBegin = new Date();
      }
      if (this.timeStopped !== null) {
        this.stoppedDuration += (new Date() - this.timeStopped);
      }

      this.intv = setInterval(this.clockRunning, 10);
      this.running = true;
    },
    pause() {
      this.running = false
      this.timeStopped = new Date();
      clearInterval(this.intv);
    },
    reset() {
      this.running = false;
      clearInterval(this.intv);
      this.stoppedDuration = 0;
      this.timeBegin = null;
      this.timeStopped = null;
      this.time = "00:00:00";
    },
    clockRunning() {
      let currentTime = new Date()
        , timeElapsed = new Date(currentTime - this.timeBegin - this.stoppedDuration)
        , hour = timeElapsed.getUTCHours()
        , min = timeElapsed.getUTCMinutes()
        , sec = timeElapsed.getUTCSeconds()

      this.time =
        this.zeroPrefix(hour, 2) + ":" +
        this.zeroPrefix(min, 2) + ":" +
        this.zeroPrefix(sec, 2)
    },

    zeroPrefix(num, digit) {
      let zero = '';
      for (let i = 0; i < digit; i++) {
        zero += '0';
      }
      return (zero + num).slice(-digit);
    }
  },

}
</script>

<style lang="less" scoped>
.timer {
  height: 40px;
  width: fit-content;
  display: flex;
  border-radius: 7px;
  align-items: center;
  text-align: center;
  margin: auto;
}

.stopwatch {
  display: flex;
  align-items: center;
  border-radius: 10px;
  justify-content: space-around;
  height: 100%;
  padding-left: 10px;
  padding-right: 10px;
  cursor: pointer;
  width: 170px;
  .time{
    display: flex;
    align-items: center;
    justify-content: center;
    height: 30px;
    border-radius: 10px;
    padding: 10px;

    margin-left: 5px;
    margin-right: 5px;
  }
  .time:hover{
    background-color: #f5f5f5;
  }
}

.stopwatch:hover {
  background-color: rgba(248, 248, 248, 0.49);
  border: 1px solid #f8f8f8;
}
</style>
