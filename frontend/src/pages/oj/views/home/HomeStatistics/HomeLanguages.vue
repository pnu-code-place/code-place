<script>
import LanguageIcon from "./LanguageIcon.vue";
import {LANGUAGE_INFO} from "../../../../../utils/constants";
import SolvedProblems from "./SolvedProblems.vue";
import TotalProblems from "./TotalProblems.vue";
import HeldContests from "./HeldContests.vue";

export default {
  name: 'HomeStatusBox',
  components: {LanguageIcon, SolvedProblems, TotalProblems, HeldContests},
  data() {
    return {
      languages: LANGUAGE_INFO,
      languageIndex: 0,
    }
  },
  methods: {
    langSelect(index) {
      this.languageIndex = index
    },
  },
  computed: {
    description() {
      return this.languages[this.languageIndex].description
    },
    languageName() {
      return this.languages[this.languageIndex].name
    },
    lectures() {
      return this.languages[this.languageIndex].lectures
    },
    langExtended() {
      return this.languageIndex !== -1
    },
    langExtendedClass() {
      return this.langExtended ? 'extended' : ''
    },
  }
}
</script>

<template>
  <div class="home-status-box">
    <div :class="`languages ${langExtendedClass}`">
      <h3>
        {{ $t('m.UsableLanguages') }}
      </h3>
      <hr/>
      <div class="language-list">
        <LanguageIcon v-for="(language, index) in languages" :key="index" :index="index"
                      :image="language.image" :openIndex="languageIndex" @extend="langSelect" :extended="langExtended"
        />
      </div>
      <div v-if="langExtended" class="description-wrapper">
        <h3>
          {{ this.languageName }}
        </h3>
        <p class="description">
          {{ this.description }}
        </p>
        <h3>
          {{ $t('m.Lecture') }}
        </h3>
        <div class="lectures">
          <div class="lecture-item" v-for="lecture in this.lectures">
            {{ lecture }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
h3 {
  font-size: 18px;
  padding: 15px 0;
  font-weight: 650;
  color: var(--ps-content-text-color)
}

.home-status-box {
  display: flex;
  width: 100%;
  justify-content: space-between;
  border: 1px solid var(--container-border-color);
  border-radius: var(--container-border-radius);
  background-color: var(--box-background-color);
  margin-top: 20px;
  height: 440px;
}

.languages {
  display: flex;
  flex-direction: column;
  padding: 0 30px 15px 30px;
  width: 100%;
  transition: width 0.5s ease-in-out;

  .language-list {
    width: 100%;
    display: flex;
    justify-content: space-evenly;
    flex-wrap: nowrap;
    padding: 15px 0 0 0;
  }

  .description-wrapper {
    overflow: hidden
  }

  .description {
    width: 100%;
    font-size: 14px;
  }

  .lectures {
    display: flex;

    .lecture-item {
      padding: 10px;
      border: 1px solid var(--container-border-color);
      border-radius: 5px;
      margin-right: 10px;
    }
  }
}

hr {
  border: 0;
  height: 1px;
  background-color: var(--container-border-color);
  margin: 0;
}
</style>
