<template>
  <div class="view">
    <Panel :title="$t('m.CreateContent')">
      <div class="detailCard">

        <!-- 제목 -->
        <div class="form-group">
          <label class="custom-label">
            <span class="required-asterisk">*</span>{{ $t('m.ContestTitle') }}
          </label>
          <el-input
            v-model="contest.title"
            :placeholder="$t('m.ContestTitle')"
          />
        </div>

        <!-- 설명 -->
        <div class="form-group">
          <label class="custom-label">
            <span class="required-asterisk">*</span>{{ $t('m.ContestDescription') }}
          </label>
          <Simditor v-model="contest.description" />
        </div>

        <!-- 시작/종료 시간 -->
        <div class="form-row">
          <div class="form-group form-col">
            <label class="custom-label">
              <span class="required-asterisk">*</span>{{ $t('m.Contest_Start_Time') }}
            </label>
            <el-date-picker
              v-model="contest.start_time"
              type="datetime"
              style="width: 100%"
              :placeholder="$t('m.Contest_Start_Time')"
            />
          </div>
          <div class="form-group form-col">
            <label class="custom-label">
              <span class="required-asterisk">*</span>{{ $t('m.Contest_End_Time') }}
            </label>
            <el-date-picker
              v-model="contest.end_time"
              type="datetime"
              style="width: 100%"
              :placeholder="$t('m.Contest_End_Time')"
            />
          </div>
        </div>

        <!-- 규칙 유형 -->
        <div class="form-group">
          <label class="custom-label">{{ $t('m.Contest_Rule_Type') }}</label>
          <div class="segmented-control">
            <label class="custom-radio">
              <input type="radio" v-model="contest.rule_type" value="ACM" :disabled="disableRuleType" />
              <span class="radio-text">ACM</span>
            </label>
            <label class="custom-radio">
              <input type="radio" v-model="contest.rule_type" value="OI" :disabled="disableRuleType" />
              <span class="radio-text">OI</span>
            </label>
          </div>
        </div>

        <!-- 스위치 항목들 -->
        <div class="form-group">
          <label class="custom-label">설정</label>
          <div class="toggle-row">
            <div class="toggle-item">
              <span class="toggle-label">
                {{ $t('m.Contest_Status') }}
                <el-tooltip content="활성화하면 참가자에게 대회가 노출됩니다." placement="top">
                  <i class="el-icon-question help-icon"></i>
                </el-tooltip>
              </span>
              <label class="spj-toggle">
                <input type="checkbox" v-model="contest.visible" />
                <span class="spj-toggle-track" :class="{ 'is-on': contest.visible }"></span>
              </label>
            </div>
            <div class="toggle-item">
              <span class="toggle-label">
                {{ $t('m.Real_Time_Rank') }}
                <el-tooltip content="대회 진행 중 실시간으로 순위를 공개합니다." placement="top">
                  <i class="el-icon-question help-icon"></i>
                </el-tooltip>
              </span>
              <label class="spj-toggle">
                <input type="checkbox" v-model="contest.real_time_rank" />
                <span class="spj-toggle-track" :class="{ 'is-on': contest.real_time_rank }"></span>
              </label>
            </div>
            <div class="toggle-item">
              <span class="toggle-label">
                {{ $t('m.Allow_Paste') }}
                <el-tooltip content="에디터에 붙여넣기를 허용합니다." placement="top">
                  <i class="el-icon-question help-icon"></i>
                </el-tooltip>
              </span>
              <label class="spj-toggle">
                <input type="checkbox" v-model="contest.allow_paste" />
                <span class="spj-toggle-track" :class="{ 'is-on': contest.allow_paste }"></span>
              </label>
            </div>
          </div>
        </div>

        <!-- 비밀번호 -->
        <div class="form-group form-half">
          <label class="custom-label">{{ $t('m.Contest_Password') }}</label>
          <el-input
            v-model="contest.password"
            :placeholder="$t('m.Contest_Password')"
          />
        </div>

        <!-- IP 범위 -->
        <div class="form-group">
          <label class="custom-label">
            {{ $t('m.Allowed_IP_Ranges') }}
            <button class="add-btn" @click="addIPRange">
              <i class="el-icon-plus"></i> 추가
            </button>
          </label>
          <div
            v-for="(range, index) in contest.allowed_ip_ranges"
            :key="index"
            class="ip-range-row"
          >
            <el-input
              v-model="range.value"
              :placeholder="$t('m.CIDR_Network')"
              class="ip-input"
            />
            <button
              class="remove-btn"
              :disabled="contest.allowed_ip_ranges.length === 1"
              @click="removeIPRange(range)"
            >
              <i class="el-icon-delete"></i>
            </button>
          </div>
        </div>

      </div>
      <div class="save-wrapper">
        <save @click.native="saveContest"></save>
      </div>
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
        allowed_ip_ranges: [{ value: "" }],
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
        .then(() => {
          this.$router.push({ name: "contest-list", query: { refresh: "true" } })
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
          let ranges = data.allowed_ip_ranges.map((v) => ({ value: v }))
          if (ranges.length === 0) ranges.push({ value: "" })
          if (data.allow_paste === undefined) data.allow_paste = true
          this.contest = data
          this.contest.allowed_ip_ranges = ranges
        })
        .catch(() => {})
    }
  },
}
</script>

<style scoped lang="less">
.detailCard {
  padding: 10px 0 20px;
}

.save-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
}

.custom-label {
  font-size: 14px;
  color: #606266;
  line-height: 40px;
  padding: 0 0 10px;
  display: inline-block;
  font-weight: 700;
}

.required-asterisk {
  color: #f56c6c;
  margin-right: 4px;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 22px;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 22px;
}

.form-col {
  flex: 1;
  margin-bottom: 0;
}

.form-half {
  max-width: 360px;
}

/* 라디오 버튼 */
.segmented-control {
  display: inline-flex;
  align-self: flex-start;
  background-color: #f1f5f9;
  padding: 4px;
  border-radius: 8px;
  gap: 2px;
  margin-top: 10px;
}

.custom-radio {
  cursor: pointer;
  display: inline-flex;
  margin: 0;

  input[type="radio"] {
    display: none;
  }

  .radio-text {
    display: inline-block;
    padding: 6px 18px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    color: #64748b;
    transition: all 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
    user-select: none;
  }

  input[type="radio"]:checked + .radio-text {
    background-color: #ffffff;
    color: #0f172a;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  }

  input[type="radio"]:disabled + .radio-text {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &:hover input[type="radio"]:not(:checked):not(:disabled) + .radio-text {
    color: #334155;
  }
}

/* 토글 */
.toggle-row {
  display: flex;
  gap: 32px;
  align-items: center;
  flex-wrap: wrap;
}

.toggle-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.toggle-label {
  font-size: 14px;
  color: #606266;
  user-select: none;
}

.spj-toggle {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  user-select: none;

  input[type="checkbox"] {
    display: none;
  }

  .spj-toggle-track {
    position: relative;
    width: 44px;
    height: 24px;
    background-color: #dcdfe6;
    border-radius: 12px;
    transition: background-color 0.25s ease;
    flex-shrink: 0;

    &::after {
      content: "";
      position: absolute;
      top: 3px;
      left: 3px;
      width: 18px;
      height: 18px;
      background-color: #ffffff;
      border-radius: 50%;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
      transition: transform 0.25s ease;
    }
  }

  .spj-toggle-track.is-on {
    background-color: #409eff;

    &::after {
      transform: translateX(20px);
    }
  }
}

.help-icon {
  margin-left: 4px;
  font-size: 13px;
  color: #909399;
  cursor: pointer;
}

/* IP 범위 */
.ip-range-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.ip-input {
  max-width: 360px;
}

.add-btn {
  margin-left: 12px;
  padding: 2px 10px;
  font-size: 12px;
  font-weight: 600;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
  background: none;
  color: #909399;
  cursor: pointer;
  transition: all 0.2s;
  vertical-align: middle;

  &:hover {
    border-color: #409eff;
    color: #409eff;
  }
}

.remove-btn {
  padding: 6px 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: none;
  color: #f56c6c;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;

  &:hover {
    background-color: #fef0f0;
    border-color: #f56c6c;
  }

  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
}

/deep/ .simditor {
  border-radius: 8px;
  border: 1px solid #dcdfe6;
  overflow: hidden;

  .simditor-toolbar {
    border-radius: 8px 8px 0 0;
    border-bottom: 1px solid #dcdfe6;
    background: #f5f7fa;
  }

  .simditor-body {
    min-height: 200px;
    padding: 15px;
    border-radius: 0 0 8px 8px;
  }
}
</style>
