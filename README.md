# CSEP Front End
[![vue](https://img.shields.io/badge/vue-2.5.13-blue.svg?style=flat-square)](https://github.com/vuejs/vue)
[![vuex](https://img.shields.io/badge/vuex-3.0.1-blue.svg?style=flat-square)](https://vuex.vuejs.org/)
[![echarts](https://img.shields.io/badge/echarts-3.8.3-blue.svg?style=flat-square)](https://github.com/ecomfe/echarts)
[![iview](https://img.shields.io/badge/iview-2.8.0-blue.svg?style=flat-square)](https://github.com/iview/iview)
[![element-ui](https://img.shields.io/badge/element-2.0.9-blue.svg?style=flat-square)](https://github.com/ElemeFE/element)
[![Build Status](https://travis-ci.org/QingdaoU/OnlineJudgeFE.svg?branch=master)](https://travis-ci.org/QingdaoU/OnlineJudgeFE)

![banner1.png](src%2Fassets%2Fbanner1.png)


## 1.소개
[운영중인 사이트](http://oj.pusan.ac.kr/)

[베타 사이트는 현재 부산대학교 내부에서만 접속이 가능합니다.](http://10.125.121.115:8080/)

부산대학교 코딩역량강화시스템의 프론트엔드 프로젝트입니다.

Vue.js 2.5.13 버전으로 개발된 기존 [QingdaoU의 OnlineJudge 프론트엔드 프로젝트](https://github.com/QingdaoU/OnlineJudge)를 기반으로 개발되었습니다.

### 개발 환경

<details>
  <summary>node.js <strong>16.16.0</strong></summary>
  기본 QingdaoU의 프로젝트에 사용된 node.js 버전은 <strong>v8.12.0</strong> 입니다.
  이 프로젝트는 <strong>v16.16.0</strong> 버전으로 개발되었습니다.
</details>

<details>
  <summary>Vue.js <strong>2.5.13</strong></summary>
  기본 QingdaoU의 사용된 Vue.js버전인 <strong>2.5.13</strong> 버전을 사용합니다.
</details>

<details>
  <summary>Vuex, echarts, iview, element-ui</summary>
  기존 QingdaoU의 프로젝트에서 사용된 라이브러리들을 그대로 사용합니다. 사용법이 까다로워 새로운 UI를 개발할 때에는 사용하지 않는 방향으로 진행하였습니다.
</details>

### 개발 기간
2023.12 ~ 2024.3 (현재 진행 중)

### 개발 인원
| github   | 사진                                                              | 역할                 | 이메일 주소                 | 소속                |
|----------|-----------------------------------------------------------------|--------------------|------------------------|-------------------|
| [hunsy9](https://github.com/hunsy9)   | ![유저 아바타](https://avatars.githubusercontent.com/u/101303791?v=4)  | 프로젝트 메니저, 프론트/백앤드 기획 및 개발 | juniper0917@gmail.com  |
| [minmunui](https://github.com/minmunui) | ![유저 아바타](https://avatars.githubusercontent.com/u/82745129?v=4) | 프론트앤드 기획 및 개발                    | ehdwls1638@pusan.ac.kr |

## 2.프로젝트 설치
서버가 설치되어 있지 않은 경우, [OnlineJudgeBE 프로젝트]()를 이용하여 DB와 서버를 설치해야 합니다.
### Linux
```bash
npm install
# we use webpack DllReference to decrease the build time,
# this command only needs execute once unless you upgrade the package in build/webpack.dll.conf.js
# webpack DllReference를 사용하여 빌드 시간을 줄입니다.
export NODE_ENV=development
npm run build:dll

# the dev-server will set proxy table to your backend
# api를 요청할 사용할 백엔드 서버 주소를 설정합니다.
export TARGET=http://Your-backend

# serve with hot reload at localhost:8080
# 프로젝트를 실행합니다. localhost:8080으로 접속할 수 있습니다.
npm run dev
```

### Windows

```bash
npm install
# we use webpack DllReference to decrease the build time,
# this command only needs execute once unless you upgrade the package in build/webpack.dll.conf.js
set NODE_ENV=development
npm run build:dll

# the dev-server will set proxy table to your backend
set TARGET=http://Your-backend

# serve with hot reload at localhost:8080
npm run dev
```

### 프로덕션 배포
[Deploy.md를 참고해주십시오](https://github.com/PNU-CSEP/CSEP_FE/blob/main/deploy/Deploy.md)

## 4.디렉터리 구조

```bash

├── build/                      # webpack 설정 파일
├── config/                     # 프로젝트 설정 파일
├── deplay/                     # 배포 설정 파일
├── src/                        # 소스 코드
│   ├── assets/                 # 이미지, 폰트 등의 정적 파일
│   ├── i18n/                   # 다국어 지원, 현재는 EN을 한국어로 덮어씌워 사용합니다.
│   ├── pages/                  # 실질적으로 화면에 나타나는 페이지
│   │   ├── admin/              # 관리자 페이지
│   │   ├── oj/                 # 온라인 저지 페이지
│   │   │   ├── components/     # 여러 페이지에서 공통적으로 사용되는 컴포넌트
│   │   │   ├── views/          # 각 페이지별 화면
│   │   │   ├── router/         # 라우터
│   ├── store/                  # vuex store
│   ├── styles/                 # 스타일
│   ├── utils/                  # 유틸리티
├── static/                     # 정적 파일
```
## 5.Troubleshooting

### webpack.dll.conf 에서 fs 관련 에러
webpack.dll.conf.js 파일에서 fs 관련 에러가 발생할 경우, 다음과 같이 수정합니다.
프로젝트를 빌드할 때 설정한 코드가 제대로 동작하지 않아 발생하는 에러입니다.
```javascript
// build/webpack.dll.conf.js :L30
oldDlls.forEach(f => {
  fs.unlink(f, ()=> {})
})
```

## 6.(권장되는) 규칙

일관된 규칙을 적용하고 싶었으나, 기존에 개발된 온라인저지의 컨벤션이 일관적이지 않아 통일하기 어려웠습니다.
그나마 규칙성을 발견하여 아래에 기록했습니다. 새로운 기능을 추가할 때에는 다음과 같은 규칙을 적용하도록 하겠습니다.

### 권장되는 커밋 메세지
- 어느 커밋으로 checkout하더라도 프로젝트가 정상적으로 동작할 수 있도록 커밋을 작성해야 합니다.
- 커밋은 최대한 작은 단위로 나누어 작성해야 합니다.
- 커밋 메세지는 다음과 같은 형식을 따라야 합니다.
```bash
<타입>: <제목>

[본문]

[꼬리말]
```
- 타입은 가급적 소문자로 작성합니다.
  - feat: 새로운 기능 추가
  - fix: 버그 수정
  - docs: 문서 수정
  - style: 페이지의 스타일 수정
  - refact: 코드 리팩토링
  - chore: 빌드 업무 수정, 패키지 매니저 수정

- [커밋 메시지 컨벤션](https://www.conventionalcommits.org/ko/v1.0.0/)

### 작명 규칙
 모든 작명규칙은 기존의 프로젝트에 있던 것들을 참고하여 작성되었습니다. 일관성을 유지하기 위해 기존의 작명규칙을 따르도록 하겠습니다.
- 변수명, 함수명은 camelCase를 따릅니다.
- 컴포넌트명은 PascalCase를 따릅니다.
- 상수는 대문자로 작성하며, 단어 사이는 언더바로 구분합니다. 다른 곳에서 공통적으로 사용될 것으로 예상되는 상수는 `src/utils/constants.js`에 작성합니다.
- 컴포넌트의 파일명은 컴포넌트명과 동일하게 작성합니다.
- 서버로부터 받아온 데이터 object의 key값은 snake_case를 따릅니다.

### 기타 유의사항
1. component에 특정 문자열을 넣을 때에는 `src/i18n/US.js`에 해당 문자열을 추가한 후 사용합니다. 절대로 하드코딩하지 않습니다.
```javascript
// bad
<div>
  안녕하세요
</div>

// good
<div>
  {{ $t('Hello') }}
</div>
```
2. `src/utils`에는 각종 유틸리티 함수를 작성합니다. 다른 곳에서 공통적으로 사용될 것으로 예상되는 함수를 작성합니다.
3. `src/constant`에는 각종 상수를 작성합니다. 다른 곳에서 공통적으로 사용될 것으로 예상되는 상수를 작성합니다. 하드코딩하지 않습니다.
4. 공톡적으로 사용할 수 있는 컴포넌트는 최대한 범용성있게 작성한 후`src/components`에 작성합니다.
5. `src/pages/*/views`에는 범용성이 없는 컴포넌트를 작성합니다. 특정 페이지에 종속되는 경우 해당 페이지의 하위 디렉터리에 작성합니다.
6. router를 사용할 때에는 `url`을 하드코딩하지 않습니다. `src/router`에 작성된 라우트를 vue의 기능을 이용하여 `name`으로 사용합니다.
```javascript
// bad
<router-link :to="problem/1">1번 문제로 가기</router-link>

// good
<router-link :to="{name: 'problem-details', params: {problemId : 1}}">1번 문제로 가기</router-link>
```
7. `src/i18n/US.js`에서 변수를 지정할 때에는 일반적으로 첫 글자 대문자인 Snake_Case를 사용합니다. 단, 특정 맥락이 사용되는 경우 해당 맥락의 이름을 붙여, PascalCase로 작성합니다.

```javascript
// 예를 들어 Solved_Problem이 '해결한 문제'라고 정의되어 있지만, '푼 문제'를 추가하고 싶을 수도 있습니다. 똑같이 영어로는 Solved_Problem입니다.
// 이런 경우, 기본적인 Solved_Problem를 '해결한 문제'로 지정하고, 맥락이 추가되는 경우에는 PascalCase로 작성합니다.

// 기본적인 경우
<div>
  {{ $t('Solved_Problem') }}
</div>
// 새롭게 추가된 맥락
<div class="user-info">
  {{ $t('UserInfoSolvedProblem') }}
</div>
```
## 7.라이센스
[MIT](http://opensource.org/licenses/MIT)
