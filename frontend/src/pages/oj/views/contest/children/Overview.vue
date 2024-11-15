<template>
  <div class="contestBox">
    <div class="contestTitle">
      <p>{{ contest.title }}</p>
      <div slot="extra" style="flex-shrink: 0;">
        <Tag type="dot" :color="countdownColor">
          <span id="countdown">{{ countdown }}</span>
        </Tag>
      </div>
    </div>
    <div class="contestContent">
      <div v-html="contest.description" class="markdown-body"></div>
      <div class="contestPassword" v-if="passwordFormVisible">
        <Input
          v-model="contestPassword"
          type="password"
          :placeholder="$t('m.Contest_Password_Placeholder')"
          class="contestPasswordInput"
          @on-enter="checkPassword"
        />
        <Button type="info" @click="checkPassword">{{
          $t("m.Button_Enter")
        }}</Button>
      </div>
    </div>
    <div class="contestFooter">
      <div style="display: flex; flex-direction: column; gap: 5px">
        <li style="display: inline-block; font-size: 14px">
          <Icon type="calendar" color="#3091f2"></Icon> 시작일 :
          {{ contest.start_time | localtime("YYYY-MM-DD HH:mm") }}
        </li>
        <li style="display: inline-block; font-size: 14px">
          <Icon type="calendar" color="#3091f2"></Icon> 종료일 :
          {{ contest.end_time | localtime("YYYY-MM-DD HH:mm") }}
        </li>
      </div>
      <div style="font-size: 14px">
        {{ $t("m.Contest_Created_by") }} :
        <span style="font-size: 18px; font-weight: bold">
          {{ contest.created_by.username }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import moment from "moment";
import api from "@oj/api";
import { mapState, mapGetters, mapActions } from "vuex";
import { types } from "@/store";
import { CONTEST_STATUS_REVERSE, CONTEST_STATUS } from "@/utils/constants";
import time from "@/utils/time";

export default {
  name: "ContestDetail",
  mounted() {
    this.contestID = this.$route.params.contestID;
  },
  methods: {
    checkPassword() {
      if (this.contestPassword === "") {
        this.$error("Password can't be empty");
        return;
      }
      this.btnLoading = true;
      api.checkContestPassword(this.contestID, this.contestPassword).then(
        (res) => {
          this.$success("Succeeded");
          this.$store.commit(types.CONTEST_ACCESS, { access: true });
          this.btnLoading = false;
        },
        (res) => {
          this.btnLoading = false;
        }
      );
    },
  },
  computed: {
    ...mapState({
      contest: (state) => state.contest.contest,
    }),
    ...mapGetters(["contestStatus", "countdown", "passwordFormVisible"]),
    countdownColor() {
      if (this.contestStatus) {
        return CONTEST_STATUS_REVERSE[this.contestStatus].color;
      }
    },
  },
};
</script>

<style lang="less" scoped>
.contestBox {
  border: 1px solid #e9ece9;
  display: flex;
  flex-direction: column;
  gap: 32px;
  background: var(--box-background-color);
  padding: 15px 20px;
  border-radius: 7px;
}
.contestTitle {
  display: flex;
  justify-content: space-between;
  p {
    text-decoration: none;
    font-size: 24px;
    font-weight: bold;
  }
  #countdown {
    font-size: 16px;
  }
}
.contestContent {
  padding: 0px 10px;
  .contestPassword {
    display: flex;
    gap: 10px;
    .contestPasswordInput {
      width: 200px;
    }
  }
}
.contestFooter {
  display: flex;
  justify-content: space-between;
  align-items: end;
  margin-bottom: 10px;
  .contestTag {
    width: fit-content;
    background-color: #f7f7f7;
    border: 1px solid #dddee1;
    border-radius: 32px;
    margin-left: 4px;
    padding: 2px 7px;
  }
}
</style>
