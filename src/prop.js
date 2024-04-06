// Description: OJ 페이지의 섹션들의 prop을 정의합니다.
// 기존 계획은 상위 router-page에서 데이터를 받아와서 하위 컴포넌트에게 전달하는 방식이었으나,
// vue2에서는 inject, provide의 업데이트가 router-view를 따라 적용되지 않는 문제가 있었습니다.
// 때문에 기존에 하나였던 api를 tab의 각각의 섹션으로 나누어서 4개의 api를 호출하는 방식으로 변경하였습니다.


// OJ 대시보드의 섹션들의 prop을 정의합니다.
// /api/profile/dashboard?username=<username> GET
export const DashboardSectionProp = {

  ojStatus: {
    rank_image: "https://cdn-icons-png.flaticon.com/512/473/473406.png", // 랭킹 이미지
    rank_tier: "platinum3", // 랭킹 티어
    rank: 1, // 랭킹
    rank_percent: 0.1, // 랭킹 퍼센트 ( 상위 10% )
    submission_number: 100, // 제출 횟수
    accepted_number: 100, // 맞은 횟수
    total_score: 56000, // 현재 점수
    rank_next: 60000, // 다음 랭킹의 허들
    rank_current: 50000, // 이전 랭킹의 허들
    miracle_current: 10, // 현재 연속 코딩일수
    miracle_record: 20 // 최고 연속 코딩일수
  },

  fieldInfo: { // 카테고리별 정보를 표시합니다.
    data_structure: {
      score: 340, // 점수
      ranking: 60, // 랭킹
      ranking_percent: 0.3, // 랭킹 퍼센트 - 상위 30%
    },
    mathematics: {
      score: 200,
      ranking: 101,
      ranking_percent: 0.505,
    },
    sorting: {
      score: 45,
      ranking: 34,
      ranking_percent: 0.17,
    },
    implementation: {
      score: 610,
      ranking: 20,
      ranking_percent: 0.101,
    },
    searching: {
      score: 30,
      ranking: 190,
      ranking_percent: 0.95,
    }
  },

  difficultyInfo: { // 난이도별 정보를 표시합니다.
    very_easy: {
      solve_number: 33,  // 해결한 문제 수
      total_score: 330,  // 총 점수
    },
    easy: {
      solve_number: 20,
      total_score: 400,
    },
    medium: {
      solve_number: 10,
      total_score: 800,
    },
    hard: {
      solve_number: 4,
      total_score: 640,
    },
    very_hard: {
      solve_number: 1,
      total_score: 320,
    }
  },
  achievements: [ // 달성한 업적을 표시합니다.
    {
      id: 3,
      title: "프로그래밍 마스터",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "프로그래밍 카테고리에서 20문제 이상 풀이",
      acquireTime: '2022-01-01T08:25:49.443682Z',
    },
    {
      id: 4,
      title: "알고리즘 전문가",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "알고리즘 카테고리에서 15문제 이상 풀이",
      acquireTime: '2022-02-01T08:25:49.443682Z',
    },
    {
      id: 5,
      title: "데이터베이스 마스터",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "데이터베이스 카테고리에서 10문제 이상 풀이",
      acquireTime: '2022-03-01T08:25:49.443682Z',
    },
    {
      id: 6,
      title: "웹 개발 전문가",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "웹 개발 카테고리에서 15문제 이상 풀이",
      acquireTime: '2022-04-01T08:25:49.443682Z',
    },
  ]
}

// 특정 유저가 푼 문제를 쿼리에 맞게 불러옵니다.
// query가 없을 경우 필터가 적용되지 않습니다. 예, /api/profile/problem?username=minmunui&field=2, GET 요청 시 field가 2인 문제들만 불러옵니다.
// username: 유저의 이름
// field: 카테고리 | All, 0: implementation, 1: mathematics, 2: data_structure, 3: searching, 4: sorting
// difficulty: 난이도 | All, VeryLow, Low, Mid, High, VeryHigh
// status: 상태 | All, Solved, Failed
// /api/profile/problem?username=<username>&field=<fieldId>&difficulty=<difficulty>&status=<status> GET
export const ProblemSectionProp = [
  {
    id: 2,
    title: '팰린드롬수',
    submitTime: '2021-07-02T08:25:49.443682Z',
    difficulty: 'Low',
    field: 'mathematics'
  },
  {
    id: 3,
    title: '체스판 다시 칠하기',
    submitTime: '2021-07-02T08:25:49.443682Z',
    difficulty: 'VeryLow',
    field: 'implementation'
  },
  {
    id: 4,
    title: '리스트 계산기',
    submitTime: '2021-07-02T08:25:49.443682Z',
    difficulty: 'Mid',
    field: 'mathematics'
  },
  {
    id: 5,
    title: '피보나치 함수',
    submitTime: '2021-07-02T08:25:49.443682Z',
    difficulty: 'Low',
    field: 'data_structure'
  },
  {
    id: 6,
    title: '더블 초콜릿',
    submitTime: '2021-07-02T08:25:49.443682Z',
    difficulty: 'Low',
    field: 'mathematics'
  },
  {
    id: 7,
    title: '리모컨',
    submitTime: '2021-07-02T08:25:49.443682Z',
    difficulty: 'Low',
    field: 'mathematics'
  },
  {
    id: 8,
    title: '동물원 우리',
    submitTime: '2021-07-02T08:25:49.443682Z',
    difficulty: 'Mid',
    field: 'data_structure'
  },
  {
    id: 9,
    title: '비상연락망',
    submitTime: '2021-07-02T08:25:49.443682Z',
    difficulty: 'VeryHigh',
    field: 'implementation'
  },
  {
    id: 10,
    title: '크레인',
    submitTime: '2021-07-02T08:25:49.443682Z',
    difficulty: 'High',
    field: 'mathematics'
  },
  {
    id: 2,
    title: '팰린드롬수',
    submitTime: '2021-07-02T08:25:49.443682Z',
    difficulty: 'Low',
    field: 'mathematics'
  },
  {
    id: 3,
    title: '체스판 다시 칠하기',
    submitTime: '2021-07-02T08:25:49.443682Z',
    difficulty: 'VeryLow',
    field: 'implementation'
  },
  {
    id: 4,
    title: '리스트 계산기',
    submitTime: '2021-07-02T08:25:49.443682Z',
    difficulty: 'Mid',
    field: 'mathematics'
  },
  {
    id: 5,
    title: '피보나치 함수',
    submitTime: '2021-07-02T08:25:49.443682Z',
    difficulty: 'Low',
    field: 'data_structure'
  },
  {
    id: 6,
    title: '더블 초콜릿',
    submitTime: '2021-07-02T08:25:49.443682Z',
    difficulty: 'Low',
    field: 'mathematics'
  },
  {
    id: 7,
    title: '리모컨',
    submitTime: '2021-07-02T08:25:49.443682Z',
    difficulty: 'Low',
    field: 'mathematics'
  },
  {
    id: 8,
    title: '동물원 우리',
    submitTime: '2021-07-02T08:25:49.443682Z',
    difficulty: 'Mid',
    field: 'data_structure'
  },
  {
    id: 9,
    title: '비상연락망',
    submitTime: '2021-07-02T08:25:49.443682Z',
    difficulty: 'VeryHigh',
    field: 'implementation'
  },
  {
    id: 10,
    title: '크레인',
    submitTime: '2021-07-02T08:25:49.443682Z',
    difficulty: 'High',
    field: 'mathematics'
  },
]


// 유저의 업적 정보들을 조회합니다.
// /api/profile/achievement?username=<username> GET
export const AchievementSectionProp = {
  acquired: [
    {
      id: 3,
      title: "프로그래밍 마스터",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "프로그래밍 카테고리에서 20문제 이상 풀이하십시오.",
      acquireTime: '2022-01-01T08:25:49.443682Z',
    },
    {
      id: 4,
      title: "알고리즘 전문가",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "알고리즘 카테고리에서 15문제 이상 풀이하십시오.",
      acquireTime: '2022-02-01T08:25:49.443682Z',
    },
    {
      id: 5,
      title: "데이터베이스 마스터",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "데이터베이스 카테고리에서 10문제 이상 풀이하십시오.",
      acquireTime: '2022-03-01T08:25:49.443682Z',
    },
    {
      id: 6,
      title: "웹 개발 전문가",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "웹 개발 카테고리에서 15문제 이상 풀이하십시오.",
      acquireTime: '2022-04-01T08:25:49.443682Z',
    },
  ],
  not_acquired: [
    {
      id: 7,
      title: "머신러닝 초보",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "머신러닝 카테고리에서 5문제 이상 풀이하십시오.",
      goal: 5,
      current: 2,
      acquireTime: ""
    },
    {
      id: 8,
      title: "네트워크 초보",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "네트워크 카테고리에서 5문제 이상 풀이하십시오.",
      goal: 5,
      current: 3,
      acquireTime: ""
    }
  ]
}
// /api/user_rank?offset=<offset>&limit=<limit> GET
// 유저의 랭킹 정보를 조회합니다.
// offset: 랭킹의 시작점
// limit: 랭킹의 갯수
export const UserRankListProp = {
  total: 201,
  results: [
    {
      rank: 1, // 랭킹
      avatar: "https://picsum.photos/200/300", // 아바타
      username: "root", // 유저 이름
      mood: '안녕하세요, 저는 Alice입니다. 잘 부탁드립니다.', // 인사말
      score: 12000, // 현재 점수
      major: "전자전기공학부", // 전공
      tier: "diamond1", // 티어
      solved: 150, // 푼 문제 수
      growth: 3000, // 금일 점수 상승량
    },
    {
      rank: 2,
      avatar: "https://picsum.photos/200/200",
      username: "minmunui",
      mood: '안녕하세요, Bob입니다. 잘 부탁드립니다.',
      score: 11500,
      major: "기계공학부",
      tier: "diamond1",
      solved: 140,
      growth: 3000,
    },
    {
      rank: 3,
      avatar: "https://picsum.photos/202",
      username: "Charlie",
      mood: '안녕하세요, Charlie입니다.',
      score: 11000,
      major: "화학공학부",
      tier: "platinum1",
      solved: 130,
      growth: 3000,
    },
    {
      rank: 4,
      avatar: "https://picsum.photos/203",
      username: "David",
      mood: '안녕하세요, David입니다.',
      score: 10500,
      major: "건축학부",
      tier: "platinum1",
      solved: 120,
      growth: 3000,
    },
    {
      rank: 5,
      avatar: "https://picsum.photos/204",
      username: "Eve",
      mood: '안녕하세요, Eve입니다.',
      score: 10000,
      major: "환경공학부",
      tier: "gold1",
      solved: 110,
      growth: 3000,
    },
    {
      rank: 6,
      avatar: "https://picsum.photos/205",
      username: "Frank",
      mood: '안녕하세요, Frank입니다.',
      score: 9500,
      major: "산업공학부",
      tier: "gold1",
      solved: 100,
      growth: 3000,
    },
    {
      rank: 7,
      avatar: "https://picsum.photos/206",
      username: "Grace",
      mood: '안녕하세요, Grace입니다.',
      score: 9000,
      major: "식품공학부",
      tier: "silver1",
      solved: 90,
      growth: 3000,
    },
    {
      rank: 8,
      avatar: "https://picsum.photos/207",
      username: "Harry",
      mood: '안녕하세요, Harry입니다.',
      score: 8500,
      major: "생물공학부",
      tier: "silver2",
      solved: 80,
      growth: 3000,
    },
    {
      rank: 9,
      avatar: "https://picsum.photos/208",
      username: "Ivy",
      mood: '안녕하세요, Ivy입니다.',
      score: 8000,
      major: "농업생명공학부",
      tier: "silver2",
      solved: 70,
      growth: 3000,
    },
    {
      rank: 10,
      avatar: "https://picsum.photos/209",
      username: "Jack",
      mood: '안녕하세요, Jack입니다.',
      score: 7500,
      major: "응용수학부",
      tier: "silver3",
      solved: 60,
      growth: 3000,
    },
    {
      rank: 11,
      avatar: "https://picsum.photos/210",
      username: "Kate",
      mood: '안녕하세요, Kate입니다.',
      score: 7000,
      major: "통계학과",
      tier: "bronze2",
      solved: 50,
      growth: 3000,
    },
    {
      rank: 12,
      avatar: "https://picsum.photos/211",
      username: "Leo",
      mood: '안녕하세요, Leo입니다.',
      score: 6500,
      major: "컴퓨터공학부",
      tier: "bronze2",
      solved: 40,
      growth: 3000,
    },
    {
      rank: 13,
      avatar: "https://picsum.photos/212",
      username: "Mia",
      mood: '안녕하세요, Mia입니다.',
      score: 6000,
      major: "소프트웨어학과",
      tier: "sprout",
      solved: 30,
      growth: 3000,
    },
    {
      rank: 14,
      avatar: "https://picsum.photos/213",
      username: "Nate",
      mood: '안녕하세요, Nate입니다.',
      score: 5500,
      major: "정보통신공학부",
      tier: "bronze3",
      solved: 20,
      growth: 3000,
    },
    {
      rank: 15,
      avatar: "https://picsum.photos/214",
      username: "Olivia",
      mood: '안녕하세요, Olivia입니다.',
      score: 5000,
      major: "전자공학과",
      tier: "bronze2",
      solved: 10,
      growth: 3000,
    },
  ]
};
// /api/surge_users?offset=<offset>&limit=<limit> GET
// 급상승 유저들의 정보를 조회합니다.
// limit: 조회할 유저의 수
// offset: 랭킹의 시작점
// limit: 랭킹의 갯수
export const SurgeUserProps = {
  total: 303,
  results: [
    {
      rank: 1,
      avatar: "https://picsum.photos/200/300",
      username: "root",
      mood: '안녕하세요, 저는 Alice입니다. 잘 부탁드립니다.',
      score: 12000,
      major: "전자전기공학부",
      tier: "diamond1",
      solved: 150,
      growth: 3000,
    },
    {
      rank: 2,
      avatar: "https://picsum.photos/200/200",
      username: "minmunui",
      mood: '안녕하세요, Bob입니다. 잘 부탁드립니다.',
      score: 11500,
      major: "기계공학부",
      tier: "diamond1",
      solved: 140,
      growth: 3000,
    },
    {
      rank: 3,
      avatar: "https://picsum.photos/202",
      username: "Charlie",
      mood: '안녕하세요, Charlie입니다.',
      score: 11000,
      major: "화학공학부",
      tier: "platinum1",
      solved: 130,
      growth: 3000,
    },
    {
      rank: 4,
      avatar: "https://picsum.photos/203",
      username: "David",
      mood: '안녕하세요, David입니다.',
      score: 10500,
      major: "건축학부",
      tier: "platinum1",
      solved: 120,
      growth: 3000,
    },
    {
      rank: 5,
      avatar: "https://picsum.photos/204",
      username: "Eve",
      mood: '안녕하세요, Eve입니다.',
      score: 10000,
      major: "환경공학부",
      tier: "gold1",
      solved: 110,
      growth: 3000,
    },
    {
      rank: 6,
      avatar: "https://picsum.photos/205",
      username: "Frank",
      mood: '안녕하세요, Frank입니다.',
      score: 9500,
      major: "산업공학부",
      tier: "gold1",
      solved: 100,
      growth: 3000,
    },
    {
      rank: 7,
      avatar: "https://picsum.photos/206",
      username: "Grace",
      mood: '안녕하세요, Grace입니다.',
      score: 9000,
      major: "식품공학부",
      tier: "silver1",
      solved: 90,
      growth: 3000,
    },
    {
      rank: 8,
      avatar: "https://picsum.photos/207",
      username: "Harry",
      mood: '안녕하세요, Harry입니다.',
      score: 8500,
      major: "생물공학부",
      tier: "silver2",
      solved: 80,
      growth: 3000,
    },
    {
      rank: 9,
      avatar: "https://picsum.photos/208",
      username: "Ivy",
      mood: '안녕하세요, Ivy입니다.',
      score: 8000,
      major: "농업생명공학부",
      tier: "silver2",
      solved: 70,
      growth: 3000,
    },
    {
      rank: 10,
      avatar: "https://picsum.photos/209",
      username: "Jack",
      mood: '안녕하세요, Jack입니다.',
      score: 7500,
      major: "응용수학부",
      tier: "silver3",
      solved: 60,
      growth: 3000,
    },
    {
      rank: 11,
      avatar: "https://picsum.photos/210",
      username: "Kate",
      mood: '안녕하세요, Kate입니다.',
      score: 7000,
      major: "통계학과",
      tier: "bronze2",
      solved: 50,
      growth: 3000,
    },
    {
      rank: 12,
      avatar: "https://picsum.photos/211",
      username: "Leo",
      mood: '안녕하세요, Leo입니다.',
      score: 6500,
      major: "컴퓨터공학부",
      tier: "bronze2",
      solved: 40,
      growth: 3000,
    },
    {
      rank: 13,
      avatar: "https://picsum.photos/212",
      username: "Mia",
      mood: '안녕하세요, Mia입니다.',
      score: 6000,
      major: "소프트웨어학과",
      tier: "sprout",
      solved: 30,
      growth: 3000,
    },
    {
      rank: 14,
      avatar: "https://picsum.photos/213",
      username: "Nate",
      mood: '안녕하세요, Nate입니다.',
      score: 5500,
      major: "정보통신공학부",
      tier: "bronze3",
      solved: 20,
      growth: 3000,
    },
    {
      rank: 15,
      avatar: "https://picsum.photos/214",
      username: "Olivia",
      mood: '안녕하세요, Olivia입니다.',
      score: 5000,
      major: "전자공학과",
      tier: "bronze2",
      solved: 10,
      growth: 3000,
    },
  ]
};

// /api/major_rank_list?limit=<limit> GET
// 전공별 랭킹 정보를 조회합니다.
// limit: 가져올 전공의 수 ( 아마도 7로 고정 )

export const MajorRankListProp = {
  total: 30,
  results: [
    {
      rank: 1, // 랭킹
      major: "전자전기공학부", // 전공
      score: 12000, // 현재 점수
    },
    {
      rank: 2,
      major: "기계공학부",
      score: 11500,
    },
    {
      rank: 3,
      major: "화학공학부",
      score: 11000,
    },
    {
      rank: 4,
      major: "건축학부",
      score: 10500,
    },
    {
      rank: 5,
      major: "환경공학부",
      score: 10000,
    },
    {
      rank: 6,
      major: "산업공학부",
      score: 9500,
    },
    {
      rank: 7,
      major: "식품공학부",
      score: 9000,
    },
  ]
};
