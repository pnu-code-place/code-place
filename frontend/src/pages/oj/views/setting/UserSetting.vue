<script>
import CustomDropDown from "../../components/dropdown/CustomDropdown.vue";
import api from "../../api";
import PasswordReset from "./ChangePassword.vue";
import ResetPassword from "../user/ResetPassword.vue";
import ChangeAvatar from "./ChangeAvatar.vue";
import ErrorSign from "../general/ErrorSign.vue";
import {types} from "../../../../store";

export default {
  components: {ErrorSign, ChangeAvatar, ResetPassword, PasswordReset, CustomDropDown},
  data() {
    return {
      MOOD_MAX_LENGTH: 256,

      languageList: [
        {languageName: "C", id: "C",},
        {languageName: "C++", id: "C++",},
        {languageName: "Java", id: "Java",},
        {languageName: "JavaScript", id: "JavaScript",},
        {languageName: "Python3", id: "Python3",},
      ],

      collegeList: [],
      majorList: [],
      formSetting: {
        username: "",
        language: "",
        college: "",
        department: "",
        github: "",
        mood: ""
      },
      oldUsername: "",

      userAvatar: "",

      formError: {
        majorWithoutCollege: false,
        username: "",
      },

      avatarUploadModal: false,
      isDuplicateChecked: false,
      loadingSaveBtn: false,

      loading: false,
      error: false,
    }
  },
  methods: {
    handleCollegeChange(collegeId) {
      this.formSetting.college = collegeId
      this.getDepartmentList(collegeId)
    },
    handleMajorChange(majorId) {
      this.formSetting.department = majorId
    },
    handleLanguageChange(language) {
      this.formSetting.language = language
    },
    async getCollegeList() {
      let res = await api.getCollegeList()
      this.collegeList = res.data.data
    },
    async getDepartmentList(collegeId) {
      let res = await api.getMajorList(collegeId)
      this.majorList = res.data.data
    },
    getUserProfile() {
      this.loading = true
      this.error = false
      api.getUserInfo()
        .then(async res => {
          this.formSetting.username = res.data.data.user.username
          this.oldUsername = res.data.data.user.username
          this.formSetting.language = res.data.data.language
          this.formSetting.mood = res.data.data.mood
          this.formSetting.github = res.data.data.github
          this.userAvatar = res.data.data.avatar
          this.formSetting.college = res.data.data.college
          await this.getDepartmentList(this.formSetting.college)
          this.formSetting.department = res.data.data.department
        })
        .catch(error => {
          this.$error("프로필을 불러오는데 실패했습니다.")
          this.error = error
        })
        .finally(() => {
          this.isDuplicateChecked = true
          this.loading = false
        })
    },
    init() {
      this.getCollegeList()
      this.getUserProfile()
    },
    removeErrorSign(error) {
      this.formError[error] = false
    },
    handleClickMajor() {
      if (this.formSetting.college === "") {
        this.formError.majorWithoutCollege = true
      }
    },
    handleSubmit() {
      this.loadingSaveBtn = true
      if (this.formSetting.username === "") {
        this.formError.username = this.$t('m.Nickname_Required');
        this.loadingSaveBtn = false
        return;
      }
      if (!this.isDuplicateChecked) {
        this.$error("닉네임 중복 확인을 해주세요.")
        this.loadingSaveBtn = false
        return;
      }
      let updateData = this.formSetting
      // let updateData = utils.filterEmptyValue(Object.assign({}, this.formSetting))
      api.updateProfile(updateData).then(res => {
        this.$success(this.$t('m.Profile_Update_Success'))
        this.$store.commit(types.CHANGE_PROFILE, {profile: res.data.data})
        this.loadingSaveBtn = false
      }, _ => {
        this.loadingSaveBtn = false
      })
    },
    handleClickNicknameAuthBtn() {
      if (this.formSetting.username === "") {
        this.formError.username = this.$t('m.Nickname_Required');
        return;
      }
      if (this.formSetting.username === this.oldUsername) {
        this.$success("사용 가능한 닉네임입니다.");
        this.isDuplicateChecked = true;
        return;
      }
      api.nicknameValidCheck(this.formSetting.username)
        .then(() => {
          this.$success("사용 가능한 닉네임입니다.");
          this.isDuplicateChecked = true;
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
    openAvatarModal() {
      this.avatarUploadModal = true;
    },
    closeAvatarModal() {
      this.avatarUploadModal = false;
    },
  },
  mounted() {
    this.init()
  },
  computed: {
    moodLength() {
      if (this.formSetting.mood === null) {
        return 0
      }
      return this.formSetting.mood.length
    },
    moodLengthExceedClass() {
      return this.moodLength > this.MOOD_MAX_LENGTH ? "exceed" : ""
    },
    githubLink() {
      return this.formSetting.github
    },
  },
  watch: {
    'formSetting.username': function (newVal, oldVal) {
      if (newVal !== oldVal) {
        this.isDuplicateChecked = false
      }
    }
  }
}

</script>

<template>
  <main class="setting">
    <h1 class="main-title user-setting">{{ $t('m.User_Setting') }}</h1>
    <div class="setting-container">
      <div v-if="loading" class="loading">
        <Spin size="large"/>
      </div>
      <div v-else-if="error" class="error">
        <ErrorSign :code="this.error"/>
      </div>
      <div v-else>
        <div class="contents">
          <div class="left-column">
            <div class="nickname">
              <label class="nickname__title label" for="nickname">{{ $t('m.Nickname') }}</label>
              <div class="nickname__contents row-flex-box">
                <input placeholder="" type="text" v-model="formSetting.username"
                       @focusout="() => this.formError.username = ''" id="nickname"/>
                <button v-if="!this.isDuplicateChecked" @click="handleClickNicknameAuthBtn" class="button">{{ $t('m.CheckDuplicate') }}</button>
                <button v-else class="button check-button loading">{{ $t('m.CheckDuplicate') }}</button>

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
                                    :selected="this.formSetting.college"
                                    @dropdownChange="handleCollegeChange"
                                    @click="removeErrorSign('majorWithoutCollege')"/>
                  </div>
                  <div class="major">
                    <CustomDropDown :options="this.majorList" nameKey="department_name"
                                    :selected="this.formSetting.department"
                                    @dropdownChange="handleMajorChange" @click="handleClickMajor"/>
                  </div>
                </div>
              </div>
              <div class="language">
                <label class="language__title label" for="language">{{ $t('m.FavoriteLanguage') }}</label>
                <div class="language__contents">
                  <CustomDropDown :options="this.languageList" nameKey="languageName"
                                  :selected="this.formSetting.language"
                                  @dropdownChange="handleLanguageChange" id="language"/>
                </div>
              </div>
            </div>
            <div class="github">
              <label class="github__title label" for="github">Github</label>
              <div class="github__contents">
                <input v-model="formSetting.github" type="text" id="github"/>
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
            <button v-if="this.loadingSaveBtn" class="button loading">{{ $t('m.Submit_Profile') }}</button>
            <button v-else @click="handleSubmit" class="button">{{ $t('m.Submit_Profile') }}</button>
          </div>
          <div class="right-column">
            <h3 class="avatar__title label">{{ $t('m.Profile_Avatar') }}</h3>
            <div class="avatar__contents">
              <div class="avatar-preview">
                <img :src="this.userAvatar" alt="avatar"/>
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
      </div>
    </div>
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
  max-width: var(--global-width);
  width: 100%;


  .setting-container {
    display: flex;
    flex-direction: column;
    width: 100%;
    background-color: var(--box-background-color);
    border-radius: 7px;
    border: 1px solid var(--border-color);
    padding: 15px 30px 45px;
  }


  h1 {
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

        &__title {
          font-size: 20px;
          font-weight: 700;
          margin-bottom: 10px;
        }

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
  font-size: 18px;
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



.button {
  background-color: var(--point-color);
  text-align: center;
  width: 100px;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 5px 10px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 700;

  &.check-button {
    width: 100px
  }

  &.loading {
    cursor: not-allowed;
    opacity: 0.3;
  }
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
