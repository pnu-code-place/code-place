<script>
import CustomDropDown from "../../components/dropdown/CustomDropdown.vue";
import api from "../../api";
import PasswordReset from "./ChangePassword.vue";
import ResetPassword from "../user/ResetPassword.vue";
import ChangeAvatar from "./ChangeAvatar.vue";

export default {
  components: {ChangeAvatar, ResetPassword, PasswordReset, CustomDropDown},
  data() {
    return {
      MOOD_MAX_LENGTH: 256,
      GITHUB_DOMAIN: "https://github.com/",

      languageList: [
        {languageName: "C", id: "C",},
        {languageName: "C++", id: "C++",},
        {languageName: "Java", id: "Java",},
        {languageName: "Javascript", id: "Javascript",},
        {languageName: "Python3", id: "Python3",},
      ],
      collegeList: [],
      majorList: [],
      formSetting: {
        username: "",
        favoriteLanguage: "",
        collegeId: "",
        majorId: "",
        github: "",
        mood: ""
      },
      formError: {
        majorWithoutCollege: false,
        username: "",
      },

      avatarUploadModal: false,
      isDuplicateChecked: false,
      //
      // formProfile: {
      //   real_name: '',
      //   mood: '',
      //   major: '',
      //   blog: '',
      //   school: '',
      //   github: '',
      //   language: ''
      // }
    }
  },
  methods: {
    handleCollegeChange(collegeId) {
      this.formSetting.collegeId = collegeId
      this.getMajorList(collegeId)
    },
    handleMajorChange(majorId) {
      this.formSetting.departmentId = majorId
    },
    handleLanguageChange(language) {
      this.formSetting.favoriteLanguage = language
    },
    async getCollegeList() {
      let res = await api.getCollegeList()
      this.collegeList = res.data.data
    },
    async getMajorList(collegeId) {
      let res = await api.getMajorList(collegeId)
      this.majorList = res.data.data
    },
    init() {
      this.getCollegeList()
      let profile = this.$store.state.user.profile
      console.log(object.keys(profile))

      this.formSetting.username = profile.username
      this.formSetting.favoriteLanguage = profile.favoriteLanguage
      this.formSetting.collegeId = profile.collegeId
      this.formSetting.majorId = profile.majorId
      this.formSetting.github = profile.github
      this.formSetting.mood = profile.mood

      // console.log(username)
      // Object.keys(this.formProfile).forEach(element => {
      //   if (profile[element] !== undefined) {
      //     this.formProfile[element] = profile[element]
      //   }
      // })
    },
    removeErrorSign(error) {
      this.formError[error] = false
    },
    handleClickMajor() {
      if (this.formSetting.collegeId === "") {
        this.formError.majorWithoutCollege = true
      }
    },
    handleSubmit() {
      let form = this.trimForm()
      api.updateProfile(form)
        .then(res => {
          this.$success("프로필이 성공적으로 수정되었습니다.")
        })
        .catch(error => {
          this.$error("프로필 수정에 실패했습니다.")
        })
    },
    handleClickNicknameAuthBtn() {
      if (this.formSetting.username === "") {
        this.formError.username = this.$t('m.Nickname_Required');
        return;
      }
      api.nicknameValidCheck(this.formRegister.username)
        .then(res => {
          this.$success("사용 가능한 닉네임입니다.");
        })
        .catch(error => {
          if (error.response) {
            switch (error.response.status) {
              case 400:
                this.formError.username = this.$t('m.Nickname_Duplicated');
                break;
              default:
                this.formError.username = this.$t('m.Unknown_Error');
            }
          }
        });
    },
    trimForm() {
      return Object.fromEntries(Object.entries(this.formSetting).filter(([_, v]) => v !== ""))
    },
    openAvatarModal() {
      this.avatarUploadModal = true;
    },
    closeAvatarModal() {
      this.avatarUploadModal = false;
    }
  },
  mounted() {
    this.init()
  },
  computed: {
    moodLength() {
      return this.formSetting.mood.length
    },
    moodLengthExceedClass() {
      return this.moodLength > this.MOOD_MAX_LENGTH ? "exceed" : ""
    },
    githubLink() {
      return this.GITHUB_DOMAIN + this.formSetting.github
    },
  }
}

</script>

<template>
  <main class="setting">
    <h1 class="user-setting">{{ $t('m.User_Setting') }}</h1>
    <div class="contents">
      <div class="left-column">
        <div class="nickname">
          <label class="nickname__title label" for="nickname">{{ $t('m.Nickname') }}</label>
          <div class="nickname__contents row-flex-box">
            <input placeholder="" type="text" v-model="formSetting.username"
                   @focusout="() => this.formError.username = ''" id="nickname"/>
            <button @click="handleClickNicknameAuthBtn" class="submit-button">{{ $t('m.CheckDuplicate') }}</button>
          </div>
          <p class="nickname__description">{{ $t('m.Nickname_Description') }} <span
            v-if="this.formError.username" class="form-error">{{ this.formError.username }}</span></p>
        </div>
        <div class="language-dept-major">
          <div class="major">
            <div class="major__header">
              <label class="major__title label">{{ $t('m.MajorAndDeparture') }}</label>
              <span class="major__error form-error"
                    v-if="this.formError.majorWithoutCollege">{{ $t('m.College_Required') }}</span>
            </div>
            <div class="major__contents">
              <div class="college">
                <CustomDropDown :options="this.collegeList" nameKey="college_name"
                                @dropdownChange="handleCollegeChange"
                                @click="removeErrorSign('majorWithoutCollege')"/>
              </div>
              <div class="major">
                <CustomDropDown :options="this.majorList" nameKey="department_name"
                                @dropdownChange="handleMajorChange" @click="handleClickMajor"/>
              </div>
            </div>
          </div>
          <div class="language">
            <label class="language__title label" for="language">{{ $t('m.FavoriteLanguage') }}</label>
            <div class="language__contents">
              <CustomDropDown :options="this.languageList" nameKey="languageName"
                              @dropdownChange="handleLanguageChange" id="language"/>
            </div>
          </div>
        </div>
        <div class="github">
          <label class="github__title label" for="github">Github</label>
          <div class="github__contents">
            <span>https://github.com/</span><input v-model="formSetting.github" type="text" id="github"/>
          </div>
          <p class="github__description">{{ $t('m.Github_Description') }}<a target="_blank"
                                                                            :href="this.githubLink">{{
              $t('m.Confirm_Link')
            }}</a>
          </p>
        </div>
        <div class="mood">
          <label class="mood__title label" for="mood">{{ $t('m.Mood') }}</label>
          <div class="mood__contents">
            <textarea v-model="formSetting.mood" class="mood__input" id="mood"/>
          </div>
          <div class="mood__bottom">
            <span class="mood__description">{{ $t('m.Mood_Description') }}</span>
            <span :class="moodLengthExceedClass">{{ this.moodLength }} / {{ this.MOOD_MAX_LENGTH }}</span>
          </div>
        </div>
        <button @click="handleSubmit" class="submit-button">{{ $t('m.Submit') }}</button>
      </div>
      <div class="right-column">
        <h3 class="avatar__title label">{{ $t('m.Profile_Avatar') }}</h3>
        <div class="avatar__contents">
          <div class="avatar-preview">
            <img src="https://via.placeholder.com/150" alt="avatar"/>
            <div class="avatar-overlay" @click="this.openAvatarModal">{{ $t('m.Change_Avatar') }}</div>
          </div>
        </div>
        <Modal v-model="avatarUploadModal"
               :footer-hide="true"
               :width="800">
          <ChangeAvatar @finishCrop="this.closeAvatarModal"/>
        </Modal>
      </div>
    </div>
    <hr/>
    <PasswordReset/>
  </main>
</template>

<style scoped lang="less">

.form-error {
  color: red;
  font-size: 12px;
}

.setting {
  --right-column-width: 33%;
  --column-gap: 20px;

  width: 100%;
  max-width: var(--global-width);
  background-color: var(--box-background-color);
  border-radius: 7px;
  border: 1px solid var(--border-color);
  padding: 15px 30px 45px;
  display: flex;
  flex-direction: column;


  h1 {
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 20px;
  }

  .contents {
    display: flex;
    gap: var(--column-gap);

    .left-column {
      width: calc(100% - var(--right-column-width) - var(--column-gap));
      display: flex;
      flex-direction: column;
      gap: 25px;

      .nickname {
        width: 66%;
      }

      .language-dept-major {
        width: 66%;
        display: flex;
        justify-content: space-between;
        gap: 40px;

        .language {
          width: 30%;
        }

        .major {
          width: 70%;

          &__contents {
            display: flex;
            gap: 20px;

            .college {
              width: 50%;
            }

            .major {
              width: 50%;
            }
          }

          .college {
            width: 50%;
          }

          .major {
            width: 50%;
          }
        }
      }

      .github {
        width: 66%;

        &__contents {
          display: flex;
          align-items: center;
          font-size: 14px;
          gap: 5px;
        }
      }

      .mood {
        // input text를 위로 정렬
        textarea {
          width: 100%;
          height: 100px;
          vertical-align: top;
          padding: 5px;
          border: 1px solid var(--border-color);
          border-radius: 5px;
          font-size: 14px;
          resize: none;
        }

        &__bottom {
          display: flex;
          justify-content: space-between;
        }
      }
    }

    .right-column {
      width: var(--right-column-width);
      display: flex;
      flex-direction: column;

      .avatar {
        width: 100%;

        &__contents {
          display: flex;
          justify-content: center;
          margin-bottom: 30px;

          .avatar-preview {
            position: relative;
            width: 250px;
            height: 250px;
            border-radius: 50%;
            overflow: hidden;
            border: 1px solid var(--border-color);
            box-shadow: 0 0 10px 0 rgba(0, 0, 0, 0.1);

            img {
              width: 100%;
            }

            .avatar-overlay {
              position: absolute;
              top: 0;
              left: 0;
              width: 100%;
              height: 100%;
              background-color: rgba(0, 0, 0, 0.5);
              color: white;
              font-size: 20px;
              display: flex;
              align-items: center;
              justify-content: center;
              opacity: 0;
              transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
              cursor: pointer;

              &:hover {
                opacity: 1;
              }
            }
          }
        }
      }
    }
  }
}

.row-flex-box {
  display: flex;
  justify-content: space-between;
  gap: 20px;
}

.label {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 5px;
}

input {
  width: 100%;
  padding: 5px;
  border: 1px solid var(--border-color);
  border-radius: 5px;
  font-size: 14px;
}

.submit-button {
  background-color: var(--point-color);
  text-align: center;
  width: 80px;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 5px 10px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 700;
}

.exceed {
  color: red;
  font-weight: 600;
}

hr {
  border: none;
  border-top: 1px solid var(--border-color);
  margin: 30px 0;
}
</style>
