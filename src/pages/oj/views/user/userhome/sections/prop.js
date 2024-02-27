// Description: OJ 페이지의 섹션들의 prop을 정의합니다.
// 기존 계획은 상위 router-page에서 데이터를 받아와서 하위 컴포넌트에게 전달하는 방식이었으나,
// vue2에서는 inject, provide의 업데이트가 router-view를 따라 적용되지 않는 문제가 있었습니다.
// 때문에 기존에 하나였던 api를 tab의 각각의 섹션으로 나누어서 4개의 api를 호출하는 방식으로 변경하였습니다.


// OJ 대시보드의 섹션들의 prop을 정의합니다.
// /api/profile/dashboard?username=<username> GET
export const DashboardSectionProp = {

  ojStatus: {
    rank_image: "https://cdn-icons-png.flaticon.com/512/473/473406.png", // 랭킹 이미지
    rank_tier: "Gold I", // 랭킹 티어
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

  categoryInfo: { // 카테고리별 정보를 표시합니다.
    data_structure: {
      score: 34, // 점수
      ranking: 60, // 랭킹
      ranking_percent: 0.3, // 랭킹 퍼센트 - 상위 30%
      max: 100
    },
    mathematics: {
      score: 20,
      ranking: 101,
      ranking_percent: 0.505,
      max: 100
    },
    sorting: {
      score: 45,
      ranking: 34,
      ranking_percent: 0.17,
      max: 100
    },
    implementation: {
      score: 61,
      ranking: 20,
      ranking_percent: 0.101,
      max: 100
    },
    searching: {
      score: 3,
      ranking: 190,
      ranking_percent: 0.95,
      max: 100
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
      id: 1, // 업적의 id
      title: "업적", // 업적의 제목
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png", // 업적 뱃지 이미지
      description: "10문제 이상 풀이하십시오.", // 업적의 설명 ( 달성 목표 )
      acquireTime: "2024-01-07T08:34:09.209734Z", // 달성한 날짜
    },
    {
      id: 2,
      title: "업적",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "업적은 아래와 같이 표시됩니다.",
      acquireTime: "2024-01-07T08:34:09.209734Z",
    }
  ]
}

// 유저가 푼 문제들의 섹션의 prop을 정의합니다.
// /api/profile/problem?username=<username> GET
export const ProblemSectionProp = {
  ranking_percent: 0.3,
  solved: { // 해결한 문제들을 표시합니다.
    count: 4,
    problems: [
      {
        id: 1001, // 문제의 id
        title: 'A+B', // 문제의 제목
        submitTime: '2021-07-02T08:25:49.443682Z', // 제출 시간
        difficulty: 'easy',   // 난이도
      },
      {
        id: 1002,
        title: 'A-B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1003,
        title: 'A*B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1004,
        title: 'A/B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1001, // 문제의 id
        title: 'A+B', // 문제의 제목
        submitTime: '2021-07-02T08:25:49.443682Z', // 제출 시간
        difficulty: 'easy',   // 난이도
      },
      {
        id: 1002,
        title: 'A-B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1003,
        title: 'A*B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1004,
        title: 'A/B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      }, {
        id: 1001, // 문제의 id
        title: 'A+B', // 문제의 제목
        submitTime: '2021-07-02T08:25:49.443682Z', // 제출 시간
        difficulty: 'easy',   // 난이도
      },
      {
        id: 1002,
        title: 'A-B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1003,
        title: 'A*B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1004,
        title: 'A/B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      }, {
        id: 1001, // 문제의 id
        title: 'A+B', // 문제의 제목
        submitTime: '2021-07-02T08:25:49.443682Z', // 제출 시간
        difficulty: 'easy',   // 난이도
      },
      {
        id: 1002,
        title: 'A-B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1003,
        title: 'A*B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1004,
        title: 'A/B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      }, {
        id: 1001, // 문제의 id
        title: 'A+B', // 문제의 제목
        submitTime: '2021-07-02T08:25:49.443682Z', // 제출 시간
        difficulty: 'easy',   // 난이도
      },
      {
        id: 1002,
        title: 'A-B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1003,
        title: 'A*B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1004,
        title: 'A/B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
    ],
  },
  failed: { // 시도했으나 풀지 못한 문제들을 표시합니다.
    count: 4,
    problems: [
      {
        id: 1001,
        title: 'A+B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1002,
        title: 'A-B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1003,
        title: 'A*B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1004,
        title: 'A/B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
    ],
  }
}

// 유저의 업적 정보들을 조회합니다.
// /api/profile/achievement?username=<username> GET
export const AchievementSectionProp = {
  acquired: [
    {
      id: 1, // 업적의 id
      title: "수학자 Step1", // 업적의 제목
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png", // 업적 뱃지 이미지
      description: "수학 카테고리에서 10문제 이상 풀이하십시오.", // 업적의 설명 ( 달성 목표 )
      acquireTime: '2021-07-02T08:25:49.443682Z', // 달성한 날짜
    }, {
      id: 2,
      title: "업적의 제목이 제법 길 수도 있겠죠!!!!",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "업적은 아래와 같이 표시됩니다. 업적의 설명이 아주 길 수도 있겠죠 아주아주아주 길수도 있겠죠",
      acquireTime: '2021-07-02T08:25:49.443682Z',
    },
    {
      id: 1, // 업적의 id
      title: "수학자 Step1", // 업적의 제목
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png", // 업적 뱃지 이미지
      description: "수학 카테고리에서 10문제 이상 풀이하십시오.", // 업적의 설명 ( 달성 목표 )
      acquireTime: '2021-07-02T08:25:49.443682Z', // 달성한 날짜
    }, {
      id: 2,
      title: "업적의 제목이 제법 길 수도 있겠죠!!!!",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "업적은 아래와 같이 표시됩니다. 업적의 설명이 아주 길 수도 있겠죠 아주아주아주 길수도 있겠죠",
      acquireTime: '2021-07-02T08:25:49.443682Z',
    }, {
      id: 1, // 업적의 id
      title: "수학자 Step1", // 업적의 제목
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png", // 업적 뱃지 이미지
      description: "수학 카테고리에서 10문제 이상 풀이하십시오.", // 업적의 설명 ( 달성 목표 )
      acquireTime: '2021-07-02T08:25:49.443682Z', // 달성한 날짜
    }, {
      id: 2,
      title: "업적의 제목이 제법 길 수도 있겠죠!!!!",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "업적은 아래와 같이 표시됩니다. 업적의 설명이 아주 길 수도 있겠죠 아주아주아주 길수도 있겠죠",
      acquireTime: '2021-07-02T08:25:49.443682Z',
    }, {
      id: 1, // 업적의 id
      title: "수학자 Step1", // 업적의 제목
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png", // 업적 뱃지 이미지
      description: "수학 카테고리에서 10문제 이상 풀이하십시오.", // 업적의 설명 ( 달성 목표 )
      acquireTime: '2021-07-02T08:25:49.443682Z', // 달성한 날짜
    }, {
      id: 2,
      title: "업적의 제목이 제법 길 수도 있겠죠!!!!",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "업적은 아래와 같이 표시됩니다. 업적의 설명이 아주 길 수도 있겠죠 아주아주아주 길수도 있겠죠",
      acquireTime: '2021-07-02T08:25:49.443682Z',
    }, {
      id: 1, // 업적의 id
      title: "수학자 Step1", // 업적의 제목
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png", // 업적 뱃지 이미지
      description: "수학 카테고리에서 10문제 이상 풀이하십시오.", // 업적의 설명 ( 달성 목표 )
      acquireTime: '2021-07-02T08:25:49.443682Z', // 달성한 날짜
    }, {
      id: 2,
      title: "업적의 제목이 제법 길 수도 있겠죠!!!!",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "업적은 아래와 같이 표시됩니다. 업적의 설명이 아주 길 수도 있겠죠 아주아주아주 길수도 있겠죠",
      acquireTime: '2021-07-02T08:25:49.443682Z',
    }, {
      id: 1, // 업적의 id
      title: "수학자 Step1", // 업적의 제목
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png", // 업적 뱃지 이미지
      description: "수학 카테고리에서 10문제 이상 풀이하십시오.", // 업적의 설명 ( 달성 목표 )
      acquireTime: '2021-07-02T08:25:49.443682Z', // 달성한 날짜
    }, {
      id: 2,
      title: "업적의 제목이 제법 길 수도 있겠죠!!!!",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "업적은 아래와 같이 표시됩니다. 업적의 설명이 아주 길 수도 있겠죠 아주아주아주 길수도 있겠죠",
      acquireTime: '2021-07-02T08:25:49.443682Z',
    }, {
      id: 1, // 업적의 id
      title: "수학자 Step1", // 업적의 제목
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png", // 업적 뱃지 이미지
      description: "수학 카테고리에서 10문제 이상 풀이하십시오.", // 업적의 설명 ( 달성 목표 )
      acquireTime: '2021-07-02T08:25:49.443682Z', // 달성한 날짜
    }, {
      id: 2,
      title: "업적의 제목이 제법 길 수도 있겠죠!!!!",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "업적은 아래와 같이 표시됩니다. 업적의 설명이 아주 길 수도 있겠죠 아주아주아주 길수도 있겠죠",
      acquireTime: '2021-07-02T08:25:49.443682Z',
    }, {
      id: 1, // 업적의 id
      title: "수학자 Step1", // 업적의 제목
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png", // 업적 뱃지 이미지
      description: "수학 카테고리에서 10문제 이상 풀이하십시오.", // 업적의 설명 ( 달성 목표 )
      acquireTime: '2021-07-02T08:25:49.443682Z', // 달성한 날짜
    }, {
      id: 2,
      title: "업적의 제목이 제법 길 수도 있겠죠!!!!",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "업적은 아래와 같이 표시됩니다. 업적의 설명이 아주 길 수도 있겠죠 아주아주아주 길수도 있겠죠",
      acquireTime: '2021-07-02T08:25:49.443682Z',
    },
  ],
  not_acquired: [
    {
      id: 2,
      title: "달성하지 못한 업적",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "업적은 아래와 같이 표시됩니다.",
      goal: 100, // 목표
      current: 50, // 현재 달성
      acquireTime: ""
    }
  ]
}

// /api/user_rank?offset=<offset>&limit=<limit> GET
// 유저의 랭킹 정보를 조회합니다.
// offset: 랭킹의 시작점
// limit: 랭킹의 갯수
export const UserRankListProp = {
  total: 201, // 전체 유저의 수
  results: [
    {
      rank: 1, // 랭킹
      avatar: "https://picsum.photos/200/300", // 유저의 아바타
      username: "user1", // 유저의 이름
      mood: '안녕하세요, 저는 user1입니다. 잘 부탁드립니다.', // 유저의 상태 메시지
      score: 10000, // 현재 점수
      major: "정보컴퓨터공학부", // 전공
      tier: "Gold I", // 티어
      solved: 100, // 해결한 문제 수
      accuracy: 0.9, // 정확도
    },
    {
      rank: 2,
      avatar: "https://picsum.photos/200/200",
      username: "user2",
      mood: '안녕하세요 user2입니다. 잘 부탁드립니다. 소개가 더 길어질 수도 있겠죠! 아주 아주 긴 소개요',
      score: 10000,
      major: "정보컴퓨터공학부",
      tier: "Gold I",
      solved: 100,
      accuracy: 0.9,
    },
    {
      rank: 3,
      avatar: "https://picsum.photos/202",
      username: "user3andVeryLongName",
      mood: '안녕하세요',
      score: 10000,
      major: "정보컴퓨터공학부",
      tier: "Gold I",
      solved: 100,
      accuracy: 0.9,
    },
    {
      rank: 4,
      avatar: "https://picsum.photos/203",
      username: "user4",
      mood: '안녕하세요',
      score: 10000,
      major: "정보컴퓨터공학부",
      tier: "Gold I",
      solved: 100,
      accuracy: 0.9,
    },
    {
      rank: 5,
      avatar: "https://picsum.photos/204",
      username: "user5",
      mood: '안녕하세요',
      score: 10000,
      major: "정보컴퓨터공학부",
      tier: "Gold I",
      solved: 100,
      accuracy: 0.9,
    },
    {
      rank: 6,
      avatar: "https://picsum.photos/205",
      username: "user6",
      mood: '안녕하세요',
      score: 10000,
      major: "정보컴퓨터공학부",
      tier: "Gold I",
      solved: 100,
      accuracy: 0.9,
    },
    {
      rank: 7,
      avatar: "https://picsum.photos/206",
      username: "user7",
      mood: '안녕하세요',
      score: 10000,
      major: "정보컴퓨터공학부",
      tier: "Gold I",
      solved: 100,
      accuracy: 0.9,
    },
    {
      rank: 8,
      avatar: "https://picsum.photos/207",
      username: "user8",
      mood: '안녕하세요',
      score: 10000,
      major: "정보컴퓨터공학부",
      tier: "Gold I",
      solved: 100,
      accuracy: 0.9,
    },
    {
      rank: 9,
      avatar: "https://picsum.photos/208",
      username: "user9",
      mood: '안녕하세요',
      score: 10000,
      major: "정보컴퓨터공학부",
      tier: "Gold I",
      solved: 100,
      accuracy: 0.9,
    },
    {
      rank: 10,
      avatar: "https://picsum.photos/209",
      username: "user10",
      mood: '안녕하세요',
      score: 10000,
      major: "정보컴퓨터공학부",
      tier: "Gold I",
      solved: 100,
      accuracy: 0.9,
    }
  ].map((user, index) => {
    user.rank = user.rank + 3
    return user
  })
}
// /api/surge_users?limit=<limit> GET
// 급상승 유저들의 정보를 조회합니다.
// limit: 조회할 유저의 수
export const SurgeUserProps = {
  total: 7,
  results: [
    {
      rank: 1, // 상승한 점수에 따른 랭킹
      username: 'surgeUser1', // 유저의 이름
      score: 10000, // 현재 점수
      increasedScore: 1000,  // 상승한 점수
    },
    {
      rank: 2,
      username: 'surgeUser2',
      score: 10000,
      increasedScore: 1000,
    },
    {
      rank: 3,
      username: 'surgeUser3',
      score: 10000,
      increasedScore: 1000,
    },
    {
      rank: 4,
      username: 'surgeUser4',
      score: 10000,
      increasedScore: 1000,
    },
    {
      rank: 5,
      username: 'surgeUser5',
      score: 10000,
      increasedScore: 1000,
    },
    {
      rank: 6,
      username: 'surgeUser6',
      score: 10000,
      increasedScore: 1000,
    },
    {
      rank: 7,
      username: 'surgeUser7',
      score: 10000,
      increasedScore: 1000,
    }
  ]
}

// /api/major_rank_list?limit=<limit>
// 전공별 랭킹 정보를 조회합니다.

export const MajorRankListProp = {
  total: 30, // 기록된 전공의 수
  results: [
    {
      rank: 1, // 랭킹
      major: "정보컴퓨터공학부", // 전공
      score: 10000, // 현재 점수
    },
    {
      rank: 2,
      major: "정보컴퓨터공학부",
      score: 10000,
    },
    {
      rank: 3,
      major: "정보컴퓨터공학부",
      score: 10000,
    },
    {
      rank: 4,
      major: "정보컴퓨터공학부",
      score: 10000,
    },
    {
      rank: 5,
      major: "정보컴퓨터공학부",
      score: 10000,
    },
    {
      rank: 6,
      major: "정보컴퓨터공학부",
      score: 10000,
    },
    {
      rank: 7,
      major: "정보컴퓨터공학부",
      score: 10000,
    },
  ]
}
