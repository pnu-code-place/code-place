// Description: OJ 페이지의 섹션들의 prop을 정의합니다.
// 기존 계획은 상위 router-page에서 데이터를 받아와서 하위 컴포넌트에게 전달하는 방식이었으나,
// vue2에서는 inject, provide의 업데이트가 router-view를 따라 적용되지 않는 문제가 있었습니다.
// 때문에 기존에 하나였던 api를 tab의 각각의 섹션으로 나누어서 4개의 api를 호출하는 방식으로 변경하였습니다.


// OJ 대시보드의 섹션들의 prop을 정의합니다.
// /api/profile/dashboard GET
export const DashboardSectionProp = {

  ojStatus: {
    rank_image: "https://cdn-icons-png.flaticon.com/512/473/473406.png", // 랭킹 이미지
    rank: 1, // 랭킹
    rank_percent: 0.1, // 랭킹 퍼센트 ( 상위 10% )
    score: 101, // 종합 점수
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
    },
    mathematics: {
      score: 20,
      ranking: 101,
      ranking_percent: 0.505,
    },
    sorting: {
      score: 45,
      ranking: 34,
      ranking_percent: 0.17,
    },
    implementation: {
      score: 61,
      ranking: 20,
      ranking_percent: 0.101,
    },
    searching: {
      score: 3,
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
      id: 1, // 업적의 id
      title: "업적", // 업적의 제목
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png", // 업적 뱃지 이미지
      description: "10문제 이상 풀이하십시오.", // 업적의 설명 ( 달성 목표 )
      digression: "업적을 달성하였습니다.", // 업적을 달성한 경우의 설명
      date: "2019-01-01", // 달성한 날짜
    },
    {
      id: 2,
      title: "업적",
      image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
      description: "업적은 아래와 같이 표시됩니다.",
      digression: "업적을 달성하였습니다.",
      date: "2019-01-01",
    }
  ]
}

// 유저가 푼 문제들의 섹션의 prop을 정의합니다.
// /api/profile/problem GET
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

export const archiveSectionProp = {
  achievements: {
    acquired: [
      {
        id: 1, // 업적의 id
        title: "업적", // 업적의 제목
        image: "https://cdn-icons-png.flaticon.com/512/473/473406.png", // 업적 뱃지 이미지
        description: "10문제 이상 풀이하십시오.", // 업적의 설명 ( 달성 목표 )
        digression: "업적을 달성하였습니다.", // 업적을 달성한 경우의 설명
        date: "2019-01-01", // 달성한 날짜
      },
    ],
    not_acquired: [
      {
        id: 1,
        title: "달성하지 못한 업적", // 업적의 제목
        image: "https://cdn-icons-png.flaticon.com/512/473/473406.png", // 업적 뱃지 이미지
        description: "업적은 아래와 같이 표시됩니다.", // 업적의 설명 ( 달성 목표 )
        goal: 100, // 달성 목표
        current: 50 // 현재 달성도
      }
    ]
  },
}
