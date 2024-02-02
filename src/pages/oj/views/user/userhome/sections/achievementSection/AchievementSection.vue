<script>
export default {
  name: 'challenge-section',
  data() {
    return {
      errorMedal : "@/assets/challenges/errorMedal.png",
      achievements: {
        acquired: [
          {
            id: 1,
            title: "업적",
            image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
            description: "업적은 아래와 같이 표시됩니다.",
            date: "2019-01-01",
          },
        ],
        not_acquired: [
          {
            id: 1,
            title: "달성하지 못한 업적",
            image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
            description: "업적은 아래와 같이 표시됩니다.",
            progress : 0.8,
          }
        ]
      },
      image : "https://cdn-icons-png.flaticon.com/512/473/47340.png"
    }
  },
  methods: {
    replaceDefaultImage(e) {
      e.target.src = this.errorRequired
    },
    init() {

    }
  },
  mounted() {
    this.init();
  },
  computed : {
    errorRequired() {
      return require('@/assets/challenges/errorMedal.png')
    }
  }
}
</script>

<template>
  <section class="challenge-section">
    <h1>업적</h1>
    <img :src="image" @error="replaceDefaultImage" alt="for test image">
    <div class="challenge-list">
    </div>
  </section>
</template>

<style scoped lang="less">
section {
  border: 1px solid #dedede;
  border-radius: 7px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  padding: 20px;

  h1 {
    margin-bottom: 10px;
    text-align: left;
  }

  h2 {
    margin-bottom: 10px;
  }
}
</style>
