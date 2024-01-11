import {userProblemData} from "./children/dummies";

export const myPageSections = {
  "problems": {component: "problem-section", propsData: {userProblemData: userProblemData}},
  "community": {component: "community-section", propsData: {posts: []}},
  "user-info": {component: "info-section", propsData: {user: {}}},
}

export const myPageNavItems = [
  {
    "title": "코딩역량",
    "name": "problems",
    "props": {
      problems: [{
        title: "problem1",
        solved: true,
        difficulty: "easy",
        tags: ["tag1", "tag2", "tag3"],
      }]
    }
  },
  {
    "title": "커뮤니티",
    "name": "community",
    "props": {
      posts: [{
        title: "post1",
        author: "author1",
        date: "2020-01-01",
        tags: ["tag1", "tag2", "tag3"],
      }]
    }
  },
  {
    "title": "회원정보",
    "name": "user-info",
    "props": {
      user: {
        name: "user1",
        email: "ehdwls1638@pusan.ac.kr",
        solved: 100,
        tried: 200,
        rank: 1,
      }
    }
  }
]
