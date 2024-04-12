// Description: OJ 페이지의 섹션들의 prop을 정의합니다.
// 기존 계획은 상위 router-page에서 데이터를 받아와서 하위 컴포넌트에게 전달하는 방식이었으나,
// vue2에서는 inject, provide의 업데이트가 router-view를 따라 적용되지 않는 문제가 있었습니다.
// 때문에 기존에 하나였던 api를 tab의 각각의 섹션으로 나누어서 4개의 api를 호출하는 방식으로 변경하였습니다.


// OJ 대시보드의 섹션들의 prop을 정의합니다.
// /api/profile/dashboard?username=<username> GET
export const DashboardSectionProp = {
  "ojStatus": {
    "accepted_number": 4,
    "submission_number": 5,
    "tier": "platinum3",
    "total_rank": 1,
    "total_rank_percentage": 0.5,
    "total_score": 2160,
    "next_tier_score": 3500,
    "current_tier_score": 1900
  },
  "fieldInfo": {
    "datastructure": {
      "score": 640,
      "ranking": 1,
      "ranking_percent": 0.5
    },
    "math": {
      "score": 0,
      "ranking": 1,
      "ranking_percent": 0.5
    },
    "sorting": {
      "score": 160,
      "ranking": 1,
      "ranking_percent": 0.5
    },
    "implementation": {
      "score": 1280,
      "ranking": 1,
      "ranking_percent": 0.5
    },
    "search": {
      "score": 80,
      "ranking": 1,
      "ranking_percent": 0.5
    }
  },
  "difficultyInfo": {
    "verylow": {
      "solve_number": 0,
      "total_score": 0
    },
    "low": {
      "solve_number": 1,
      "total_score": 0
    },
    "mid": {
      "solve_number": 1,
      "total_score": 160
    },
    "high": {
      "solve_number": 1,
      "total_score": 0
    },
    "veryhigh": {
      "solve_number": 1,
      "total_score": 1280
    }
  }


}

// 특정 유저가 푼 문제를 쿼리에 맞게 불러옵니다.
// query가 없을 경우 필터가 적용되지 않습니다. 예,
// /api/profile/problem?username=minmunui&field=2, GET 요청 시 field가 2인 문제들만 불러옵니다.
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
  total: 201, // 전체 유저 수
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
export const SurgeUserProps = {
  total: 303, // 전체 유저 수
  results: [
    {
      rank: 1, // 랭킹
      avatar: "https://picsum.photos/200/300", // 유저 아바타
      username: "root", // 유저 이름
      mood: '안녕하세요, 저는 Alice입니다. 잘 부탁드립니다.', // 상태메세지
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
      people: 200, // 전공 내의 유저 수
    },
    {
      rank: 2,
      major: "기계공학부",
      score: 11500,
      people: 190,
    },
    {
      rank: 3,
      major: "화학공학부",
      score: 11000,
      people: 180,
    },
    {
      rank: 4,
      major: "건축학부",
      score: 10500,
      people: 170,
    },
    {
      rank: 5,
      major: "환경공학부",
      score: 10000,
      people: 160,
    },
    {
      rank: 6,
      major: "산업공학부",
      score: 9500,
      people: 150,
    },
    {
      rank: 7,
      major: "식품공학부",
      score: 9000,
      people: 140,
    },
  ]
};
