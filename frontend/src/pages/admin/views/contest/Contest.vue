<template>
  <div class="view">
    <Panel :title="$t('m.CreateContent')">
      <el-form label-position="top" class="contest-form">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item :label="$t('m.ContestTitle')" required>
              <el-input
                v-model="contest.title"
                :placeholder="$t('m.ContestTitle')"
              ></el-input>
            </el-form-item>
          </el-col>

          <el-col :span="24">
            <el-form-item :label="$t('m.ContestDescription')" required>
              <Simditor v-model="contest.description"></Simditor>
            </el-form-item>
          </el-col>

          <el-col :span="24">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item :label="$t('m.Contest_Start_Time')" required>
                  <el-date-picker
                    v-model="contest.start_time"
                    type="datetime"
                    style="width: 100%"
                    :placeholder="$t('m.Contest_Start_Time')"
                  >
                  </el-date-picker>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item :label="$t('m.Contest_End_Time')" required>
                  <el-date-picker
                    v-model="contest.end_time"
                    type="datetime"
                    style="width: 100%"
                    :placeholder="$t('m.Contest_End_Time')"
                  >
                  </el-date-picker>
                </el-form-item>
              </el-col>
            </el-row>
          </el-col>

          <el-col :span="24">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item :label="$t('m.Contest_Rule_Type')">
                  <el-radio
                    class="radio"
                    v-model="contest.rule_type"
                    label="ACM"
                    :disabled="disableRuleType"
                    >ACM</el-radio
                  >
                  <el-radio
                    class="radio"
                    v-model="contest.rule_type"
                    label="OI"
                    :disabled="disableRuleType"
                    >OI</el-radio
                  >
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item class="switch-item">
                  <template #label>
                    <span>
                      {{ $t("m.Contest_Status") }}
                    </span>

                    <el-tooltip
                      content="활성화하면 참가자에게 대회가 노출됩니다."
                      placement="top"
                    >
                      <i class="el-icon-question help-icon"></i>
                    </el-tooltip>
                  </template>

                  <el-switch
                    v-model="contest.visible"
                    active-text=""
                    inactive-text=""
                  >
                  </el-switch>
                  <span class="switch-state">
                    {{ contest.visible ? "ON" : "OFF" }}
                  </span>
                </el-form-item>
              </el-col>
            </el-row>
          </el-col>

          <el-col :span="24">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item class="switch-item">
                  <template #label>
                    <span>
                      {{ $t("m.Real_Time_Rank") }}
                    </span>

                    <el-tooltip
                      content="대회 진행 중 실시간으로 순위를 공개합니다."
                      placement="top"
                    >
                      <i class="el-icon-question help-icon"></i>
                    </el-tooltip>
                  </template>

                  <el-switch
                    v-model="contest.real_time_rank"
                    active-color="#13ce66"
                    inactive-color="#dc3644"
                  >
                  </el-switch>
                  <span class="switch-state">
                    {{ contest.real_time_rank ? "ON" : "OFF" }}
                  </span>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item class="switch-item">
                  <template #label>
                    <span>
                      {{ $t("m.Allow_Paste") }}
                    </span>

                    <el-tooltip
                      content="에디터에 붙여넣기를 허용합니다. "
                      placement="top"
                    >
                      <i class="el-icon-question help-icon"></i>
                    </el-tooltip>
                  </template>

                  <el-switch
                    v-model="contest.allow_paste"
                    active-color="#13ce66"
                    inactive-color="#dc3644"
                  >
                  </el-switch>
                  <span class="switch-state">
                    {{ contest.allow_paste ? "ON" : "OFF" }}
                  </span>
                </el-form-item>
              </el-col>
            </el-row>
          </el-col>

          <el-col :span="24">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item :label="$t('m.Contest_Password')">
                  <el-input
                    v-model="contest.password"
                    style="width: 100%"
                    :placeholder="$t('m.Contest_Password')"
                  ></el-input>
                </el-form-item>
              </el-col>
            </el-row>
          </el-col>

          <el-col :span="24">
            <el-form-item>
              <template #label>
                <span>{{ $t("m.Allowed_IP_Ranges") }}</span>

                <el-button
                  round
                  size="mini"
                  icon="el-icon-fa-plus"
                  @click="addIPRange"
                  style="margin-left: 8px"
                />
              </template>
              <div
                v-for="(range, index) in contest.allowed_ip_ranges"
                :key="index"
              >
                <el-row :gutter="20" style="margin-bottom: 15px">
                  <el-col :span="8">
                    <el-input
                      v-model="range.value"
                      style="width: 100%"
                      :placeholder="$t('m.CIDR_Network')"
                    ></el-input>
                  </el-col>
                  <el-col :span="10">
                    <el-button
                      size="mini"
                      round
                      icon="el-icon-fa-trash"
                      :disabled="contest.allowed_ip_ranges.length === 1"
                      @click="removeIPRange(range)"
                    ></el-button>
                  </el-col>
                </el-row>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <save @click.native="saveContest"></save>
    </Panel>
  </div>
</template>

<script>
import api from "../../api.js"
import Simditor from "../../components/Simditor.vue"

export default {
  name: "CreateContest",
  components: {
    Simditor,
  },
  data() {
    return {
      title: "Create Contest",
      disableRuleType: false,
      contest: {
        title: "",
        description: "",
        start_time: "",
        end_time: "",
        rule_type: "ACM",
        password: "",
        real_time_rank: true,
        visible: true,
        allow_paste: true,
        allowed_ip_ranges: [
          {
            value: "",
          },
        ],
      },
    }
  },
  methods: {
    saveContest() {
      let funcName =
        this.$route.name === "edit-contest" ? "editContest" : "createContest"
      let data = Object.assign({}, this.contest)
      let ranges = []
      for (let v of data.allowed_ip_ranges) {
        if (v.value !== "") {
          ranges.push(v.value)
        }
      }
      data.allowed_ip_ranges = ranges
      api[funcName](data)
        .then((res) => {
          this.$router.push({
            name: "contest-list",
            query: { refresh: "true" },
          })
        })
        .catch(() => {})
    },
    addIPRange() {
      this.contest.allowed_ip_ranges.push({ value: "" })
    },
    removeIPRange(range) {
      let index = this.contest.allowed_ip_ranges.indexOf(range)
      if (index !== -1) {
        this.contest.allowed_ip_ranges.splice(index, 1)
      }
    },
  },
  mounted() {
    if (this.$route.name === "edit-contest") {
      this.title = "Edit Contest"
      this.disableRuleType = true
      api
        .getContest(this.$route.params.contestId)
        .then((res) => {
          let data = res.data.data
          let ranges = []
          for (let v of data.allowed_ip_ranges) {
            ranges.push({ value: v })
          }
          if (ranges.length === 0) {
            ranges.push({ value: "" })
          }
          data.allowed_ip_ranges = ranges
          if (data.allow_paste === undefined) {
            data.allow_paste = true
          }
          this.contest = data
        })
        .catch(() => {})
    }
  },
}
</script>

<style scoped>
.contest-form ::v-deep .el-form-item__label {
  font-weight: 600;
  color: #303133;
}

.contest-form ::v-deep .el-date-editor,
.contest-form ::v-deep .el-input {
  width: 100%;
}

.switch-item ::v-deep .el-form-item__content {
  display: flex;
  align-items: center;
  min-height: 40px;
}

.switch-item ::v-deep .el-switch {
  transform: scale(0.95);
  transform-origin: left center;
}

.help-icon {
  margin-left: 6px;
  font-size: 14px;
  color: #909399;
  cursor: pointer;
}
</style>
