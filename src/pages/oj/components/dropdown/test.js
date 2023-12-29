let collegeDto = [{id: 1, name: "공과대학"},{id: 2, name: "자연대학"},{id: 3, name: "의과대학"},{id: 4, name: "나노대학"}]
let majorDto = [{id: 1, name: "정보컴퓨터공학전공"},{id: 2, name: "인공지능전공"},{id: 3, name: "기계공학"},{id: 4, name: "생명공학"}]
const DropDownType = {
  COLLEGE: "단과대학 선택",
  MAJOR: "학과 선택",
}
module.exports={
  collegeDto, majorDto, DropDownType
}
