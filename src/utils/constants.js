import i18n from '@/i18n'

export const JUDGE_COLOR = {
  WRONG: {
    color: '#FFD338',
    textColor: '#454545'
  },
  CORRECT: {
    color: '#AEFF87',
    textColor: '#454545'
  },
  PENDING: {
    color: '#C3EBFF',
    textColor: '#454545'
  },
  ERROR: {
    color: '#FF0031',
    textColor: '#454545'
  },
}

export const JUDGE_STATUS = {
  '-2': {
    name: 'Compile Error',
    short: 'CE',
    ...JUDGE_COLOR.ERROR
  },
  '-1': {
    name: 'Wrong Answer',
    short: 'WA',
    ...JUDGE_COLOR.WRONG
  },
  '0': {
    name: 'Accepted',
    short: 'AC',
    ...JUDGE_COLOR.CORRECT
  },
  '1': {
    name: 'Time Limit Exceeded',
    short: 'TLE',
    ...JUDGE_COLOR.WRONG
  },
  '2': {
    name: 'Time Limit Exceeded',
    short: 'TLE',
    ...JUDGE_COLOR.WRONG
  },
  '3': {
    name: 'Memory Limit Exceeded',
    short: 'MLE',
    ...JUDGE_COLOR.WRONG
  },
  '4': {
    name: 'Runtime Error',
    short: 'RE',
    ...JUDGE_COLOR.ERROR
  },
  '5': {
    name: 'System Error',
    short: 'SE',
    ...JUDGE_COLOR.ERROR
  },
  '6': {
    name: 'Pending',
    color: 'yellow',
    ...JUDGE_COLOR.PENDING
  },
  '7': {
    name: 'Judging',
    color: 'blue',
    type: 'info'
  },
  '8': {
    name: 'Partial Accepted',
    short: 'PAC',
    ...JUDGE_COLOR.WRONG
  },
  '9': {
    name: 'Submitting',
    color: 'yellow',
    ...JUDGE_COLOR.PENDING
  }
}

export const CONTEST_STATUS = {
  'NOT_START': '1',
  'UNDERWAY': '0',
  'ENDED': '-1'
}

export const CONTEST_STATUS_REVERSE = {
  '1': {
    name: i18n.t('m.Contest_Status_Not_Started'),
    color: 'yellow'
  },
  '0': {
    name: i18n.t('m.Contest_Status_Underway'),
    color: 'green'
  },
  '-1': {
    name: i18n.t('m.Contest_Status_Ended'),
    color: 'red'
  }
}

export const RULE_TYPE = {
  ACM: 'ACM',
  OI: 'OI'
}

export const CONTEST_TYPE = {
  PUBLIC: 'Public',
  PRIVATE: 'Password Protected'
}

export const USER_TYPE = {
  REGULAR_USER: 'Regular User',
  ADMIN: 'Admin',
  SUPER_ADMIN: 'Super Admin'
}

export const PROBLEM_PERMISSION = {
  NONE: 'None',
  OWN: 'Own',
  ALL: 'All'
}

export const STORAGE_KEY = {
  AUTHED: 'authed',
  PROBLEM_CODE: 'problemCode',
  languages: 'languages'
}

export const DIFFICULTY_MAP = {
  'VeryLow': {
    'value': '매우 쉬움',
    'textColor': '#95ef4c'
  },
  'Low': {
    'value': '쉬움',
    'textColor': '#B5EAB0'
  },
  'Mid': {
    'value': '보통',
    'textColor': '#7c7878'
  },
  'High': {
    'value': '어려움',
    'textColor': '#ff8828'
  },
  'VeryHigh': {
    'value': '매우 어려움',
    'textColor': '#c02b2b'
  }
}

export const FIELD_MAP = {
  '0': {
    'value': '구현',
    'boxColor': '#F8D093',
    'backgroundImage': require('../assets/fieldBackground/implement.svg'),
    'maxScore': 25600
  },
  '1': {
    'value': '수학',
    'boxColor': '#B5EAB0',
    'backgroundImage': require('../assets/fieldBackground/math.svg'),
    'maxScore': 25600
  },
  '2': {
    'value': '자료구조',
    'boxColor': '#F8B193',
    'backgroundImage': require('../assets/fieldBackground/datastructure.svg'),
    'maxScore': 25600
  },
  '3': {
    'value': '탐색',
    'boxColor': '#90B8E7',
    'backgroundImage': require('../assets/fieldBackground/search.svg'),
    'maxScore': 25600
  },
  '4': {
    'value': '정렬',
    'boxColor': '#d9c9ea',
    'backgroundImage': require('../assets/fieldBackground/sort.svg'),
    'maxScore': 25600
  }
}

export const TierImageSrc = {
  //unranked
  'sprout': require('@/assets/tiers/unranked/sprout.svg'),

  //bronze
  'bronze1': require('@/assets/tiers/bronze/bronze1.svg'),
  'bronze2': require('@/assets/tiers/bronze/bronze2.svg'),
  'bronze3': require('@/assets/tiers/bronze/bronze3.svg'),

  //silver
  'silver1': require('@/assets/tiers/silver/silver1.svg'),
  'silver2': require('@/assets/tiers/silver/silver2.svg'),
  'silver3': require('@/assets/tiers/silver/silver3.svg'),

  //gold
  'gold1': require('@/assets/tiers/gold/gold1.svg'),
  'gold2': require('@/assets/tiers/gold/gold2.svg'),
  'gold3': require('@/assets/tiers/gold/gold3.svg'),

  //platinum
  'platinum1': require('@/assets/tiers/platinum/platinum1.svg'),
  'platinum2': require('@/assets/tiers/platinum/platinum2.svg'),
  'platinum3': require('@/assets/tiers/platinum/platinum3.svg'),

  //diamond
  'diamond1': require('@/assets/tiers/diamond/diamond1.svg'),
  'diamond2': require('@/assets/tiers/diamond/diamond2.svg'),
  'diamond3': require('@/assets/tiers/diamond/diamond3.svg'),
}

export const AwardImageSrc = {
  '1': require('@/assets/awards/first.svg'),
  '2': require('@/assets/awards/second.svg'),
  '3': require('@/assets/awards/third.svg'),
}

export function getTierImageSrc(tier) {
  return TierImageSrc[tier]
}

export function getAwardImageSrc(rank) {
  return AwardImageSrc[rank]
}


export function buildProblemCodeKey(problemID, contestID = null) {
  if (contestID) {
    return `${STORAGE_KEY.PROBLEM_CODE}_${contestID}_${problemID}`
  }
  return `${STORAGE_KEY.PROBLEM_CODE}_NaN_${problemID}`
}

export const GOOGLE_ANALYTICS_ID = 'UA-111499601-1'


