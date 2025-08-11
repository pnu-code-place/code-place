<template>
  <div
    :class="{ 'select-menu': true, 'select-menu active': openState === true }"
  >
    <div class="select-btn" @click="handleOpenState">
      <span class="sBtn-text">{{ selectedOption }}</span>
      <img src="@/assets/chevron-down.png" class="bx bx-chevron-down" />
    </div>
    <ul class="options" v-if="openState == true">
      <li
        v-for="(item, index) in items"
        class="option"
        @click="handleClickItem(item.id, item.name)"
      >
        <span class="option-text">{{ item.name }}</span>
      </li>
    </ul>
  </div>
</template>

<script>
import { collegeDto, DropDownType, majorDto } from "./test"

export default {
  name: "customDropDown_legacy",
  props: {
    dropdownType: DropDownType,
  },
  data() {
    return {
      openState: false,
      selectedOption: this.dropdownType,
      items: this.dropdownType === DropDownType.COLLEGE ? collegeDto : majorDto,
    }
  },
  methods: {
    handleClickItem(itemId, itemName) {
      this.openState = false
      this.selectedOption = itemName
      const dto = {
        id: itemId,
        dropdownType: this.dropdownType,
      }
      this.$emit("handleDropDownChange", dto)
    },
    handleOpenState() {
      if (this.openState === true) {
        this.openState = false
      } else {
        this.openState = true
      }
    },
  },
}
</script>

<style scoped lang="less">
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: "Poppins", sans-serif;
}

body {
  background: #e3f2fd;
}

.select-menu {
  //max-width: 330px;
  margin: 13px auto;
  margin-top: 10px;
}
.select-menu .select-btn {
  display: flex;
  height: 25px;
  background: #fff;
  padding: 20px;
  font-size: 15px;
  font-weight: 400;
  border-radius: 8px;
  align-items: center;
  cursor: pointer;
  justify-content: space-between;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
}
.select-menu .options {
  position: absolute;
  overflow-y: auto;
  max-height: 295px;
  padding: 10px;
  right: 15px;
  margin-top: 5px;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  animation-name: fadeInDown;
  -webkit-animation-name: fadeInDown;
  animation-duration: 0.35s;
  animation-fill-mode: both;
  -webkit-animation-duration: 0.35s;
  -webkit-animation-fill-mode: both;
}
.select-menu .options .option {
  display: flex;
  height: 40px;
  cursor: pointer;
  padding: 0 16px;
  border-radius: 8px;
  align-items: center;
  background: #fff;
}
.select-menu .options .option:hover {
  background: #f2f2f2;
}
.select-menu .options .option i {
  font-size: 25px;
  margin-right: 12px;
}
.select-menu .options .option .option-text {
  font-size: 18px;
  color: #333;
}

.select-btn img {
  font-size: 25px;
  transition: 0.3s;
}

.select-menu.active .select-btn img {
  transform: rotate(-180deg);
}
.select-menu.active .options {
  display: block;
  opacity: 0;
  z-index: 10;
  animation-name: fadeInUp;
  -webkit-animation-name: fadeInUp;
  animation-duration: 0.4s;
  animation-fill-mode: both;
  -webkit-animation-duration: 0.4s;
  -webkit-animation-fill-mode: both;
}

@keyframes fadeInUp {
  from {
    transform: translate3d(0, 30px, 0);
  }
  to {
    transform: translate3d(0, 0, 0);
    opacity: 1;
  }
}
@keyframes fadeInDown {
  from {
    transform: translate3d(0, 0, 0);
    opacity: 1;
  }
  to {
    transform: translate3d(0, 20px, 0);
    opacity: 0;
  }
}
</style>
