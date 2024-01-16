import {userProblemData} from "./dummies";

export const myPageSections = {
  "main": {component: "dashboard-section"},
  "problems": {component: "problem-section"},
  "community": {component: "community-section"},
  "user-info": {component: "info-section"},
}

export const myPageNavItems = [
  {
    "title" : "OJ통계",
    "name":"main",
    "path":"./main"
  },
  {
    "title": "문제풀이",
    "name": "problems",
    "path":"./problems"
  },
  {
    "title": "커뮤니티",
    "name": "community",
    "path": "./community"
  },
  {
    "title": "회원정보",
    "name": "user-info",
    "path": "./user-info"
  }
]
