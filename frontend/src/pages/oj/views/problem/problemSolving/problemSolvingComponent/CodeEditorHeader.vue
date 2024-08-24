<template>
  <div class="container-header">
    <div>
      <i class="fas fa-code"/>
      <span>코드 작성</span>
    </div>
    <div style="display: flex; justify-content: space-between; align-items: center">
      <Tooltip :content="'언어 선택'" placement="bottom">
        <Dropdown @on-click="changeLanguage" trigger="click" class="dropdown">
                          <span style="font-size: 13px; padding-right: 3px; font-weight: 450">
                            {{ language }}
                          </span>
          <i class="fas fa-chevron-down"></i>
          <Dropdown-menu slot="list">
            <Dropdown-item :name="item" v-for="item in problem.languages" :key="item">{{
                item
              }}
            </Dropdown-item>
          </Dropdown-menu>
        </Dropdown>
      </Tooltip>
      <SubmissionBtn :isSubmitting="isSubmitting" @create-submission="$emit('create-submission')"/>
      <SubmissionStatus :statusVisible="statusVisible"
                        :contestID="contestID"
                        :result="result"
                        :submissionId="submissionId"/>
      <!--      <Tooltip :content="'글자 크기 키우기'" placement="bottom-end">-->
      <!--        <CustomIconBtn @click="changeFontSize(fontSize+1)" :wrapperSize="30" iconClass="fas fa-plus"/>-->
      <!--      </Tooltip>-->
      <!--      <Tooltip :content="'글자 크기 줄이기'" placement="bottom-end">-->
      <!--        <CustomIconBtn @click="changeFontSize(fontSize-1)" :wrapperSize="30" iconClass="fas fa-minus"/>-->
      <!--      </Tooltip>-->
      <!--      <Tooltip :content="this.$i18n.t('m.Reset_to_default_code_definition')" placement="bottom-end">-->
      <!--        <CustomIconBtn @click="onResetToTemplate" :wrapperSize="30" iconClass="fas fa-undo"/>-->
      <!--      </Tooltip>-->
      <!--      <Tooltip :content="'환경설정'" placement="bottom-end">-->
      <!--                <CustomIconBtn :wrapperSize="30" iconClass="fas fa-gear"/>-->
      <!--      </Tooltip>-->
    </div>
  </div>
</template>

<script>
import {defineComponent} from "vue";
import FieldCategoryBox from "../../../../components/FieldCategoryBox.vue";
import CustomIconBtn from "../../../../components/buttons/CustomIconBtn.vue";
import SubmissionStatus from "./SubmissionStatus.vue";
import SubmissionBtn from "./SubmissionBtn.vue";

export default defineComponent({
  props: {
    problem: Object,
    language: String,
    statusVisible: Boolean,
    contestID: String,
    result: Object,
    submissionId: String,
    isSubmitting: Boolean
  },
  components: {SubmissionBtn, SubmissionStatus, CustomIconBtn, FieldCategoryBox},
  data() {
    return {
      language: 'C++',
    }
  },
  methods: {
    changeLanguage(newLang) {
      this.$emit('change-language', newLang)
    },
    onResetToTemplate() {
      this.$Modal.confirm({
        content: this.$i18n.t('m.Are_you_sure_you_want_to_reset_your_code'),
        onOk: () => {
          let template = this.problem.template
          if (template && template[this.language]) {
            this.code = template[this.language]
          } else {
            this.code = ''
          }
          this.$refs.myCm.resetCM()
        }
      })
    },
  }
})
</script>

<style scoped lang="less">
.container-header {
  transition: 0.3s;
  display: flex;
  justify-content: space-between;
  height: 50px;
  width: 100%;
  align-items: center;
  border: 1px solid var(--border-color);
  padding-right: 10px;
  padding-left: 20px;
  border-radius: 7px;
  margin-bottom: 10px;
  background-color: var(--ps-content-color);

  span {
    margin-left: 10px;
    font-size: medium;
    font-weight: bold;
  }
}

.dropdown {
  cursor: pointer;
  padding-left: 15px;
  padding-right: 15px;
  border-radius: 7px;
  margin-right: 10px;
}
</style>
