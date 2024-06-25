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
      statIndex: -1,
      statistics: {
        totalProblems: 512,
        solvedProblems: 120,
        heldContests: 36
      }
    }
  },
  methods: {
    langSelect(index) {
      this.languageIndex = index
    },
    statSelect(index) {
      this.statIndex = index
    },
    statExtendedClass(index) {
      return this.statIndex === index ? 'extended' : ''
    },
    statExtended(index) {
      return this.statIndex === index
    }
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
    <div class="statistics">
      <div :class="`statistics-contents ${statExtendedClass(0)}`" @mouseenter="statSelect(0)">
        <h3>
          {{ $t('m.NumberOfProblems') }}
        </h3>
        <TotalProblems :extended="statExtended(0)" :total-problems="this.statistics.totalProblems"/>
      </div>
      <hr/>
      <div :class="`statistics-contents ${statExtendedClass(1)}`" @mouseenter="statSelect(1)">

        <h3>
          {{ $t('m.NumberOfSolvedProblems') }}
        </h3>
        <SolvedProblems :extended="statExtended(1)" :solved-problems="this.statistics.solvedProblems"/>
      </div>
      <hr/>
      <div :class="`statistics-contents ${statExtendedClass(2)}`" @mouseenter="statSelect(2)">
        <h3>
          {{ $t('m.NumberOfHeldContests') }}
        </h3>
        <HeldContests :extended="statExtended(2)" :held-contests="this.statistics.heldContests"/>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
h3 {
  font-size: 15px;
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
  height: 428px;
}

.statistics {
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 0 30px 15px 30px;

  .statistics-contents {
    height: 52.5px;
    transition: height 0.3s ease-in-out;
    overflow: hidden;
    display: flex;
    flex-direction: column;

    &.extended {
      height: 100%
    }
  }

}

.languages {
  display: flex;
  flex-direction: column;
  padding: 0 30px 15px 30px;
  width: 358px;
  border-right: 1px solid var(--container-border-color);
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
    width: 744px;
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

  &.extended {
    width: 804px;
  }
}

hr {
  border: 0;
  height: 1px;
  background-color: var(--container-border-color);
  margin: 0;
}
</style>
