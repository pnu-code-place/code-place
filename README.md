<div align="center">
  <img src="./frontend/src/assets/thumbnail.svg" width="830" alt="Code Place Logo"/>
</div>

## 프로젝트 소개
본 프로젝트는 부산대학교 학생들의 프로그래밍 역량 향상을 위해 개발되었으며,

부산대학교의 학생들이 전공과 관계 없이 프로그래밍에 쉽게 접근하고 성장할 수 있는 학습 환경을 조성하는 것이 목표입니다.

현재 부산대학교의 교양필수 과목인 ‘**기초컴퓨터프로그래밍**’ 수업에서 학생들에게 코딩 실습 환경을 제공하기 위해 활용되고 있습니다.
> 위 프로젝트는 QingdaoU OJ 오픈소스 기반으로 개발되었습니다.
<br/>

## 프로젝트 주요 기능
- **코딩테스트 및 대회**: 실력 향상을 위한 실전 환경 제공
- **수준별 알고리즘 문제**: 다양한 난이도의 문제로 단계별 학습 제공
- **온라인 코드 에디터**: 웹에서 바로 코딩과 실행이 가능한 통합 개발 환경 제공
- **개인화된 마이페이지**: 학습 진행 상황 추적 및 개인별 역량 분석 제공

<br/>

## 배포 주소
> 운영 서버 주소 : https://code.pusan.ac.kr/
> 
> 개발(베타) 서버 주소 : https://code-place-dev.site/

<br/>

## 프로젝트 아키텍처

### 서비스 아키텍처
<div align="center">
  <img alt="code-place-arch" src="https://github.com/user-attachments/assets/d1fa97f1-109e-4389-8a4f-b1705a44dac9" />
</div>

### 인프라 아키텍처
<div align="center">
  <img width="1672" height="995" alt="code-place-arch2" src="https://github.com/user-attachments/assets/c2bb781b-05c8-40cd-9558-9a573700af93" />
</div>

## 개발 스택

**Devops/Infra** &nbsp;
<img src="https://img.shields.io/badge/K3s-v1.33.6-FFD506?style=flat-square&logo=kubernetes&logoColor=white"/>
<img src="https://img.shields.io/badge/Kube--Vip-v1.0.2-326CE5?style=flat-square&logo=kubernetes&logoColor=white"/>
<img src="https://img.shields.io/badge/Longhorn-v1.10.1-00A6D3?style=flat-square&logo=cloudnativecomputingfoundation&logoColor=white"/>
<img src="https://img.shields.io/badge/Harbor-v2.14.1-60B932?style=flat-square&logo=harbor&logoColor=white"/>
<img src="https://img.shields.io/badge/Github_Action-000000?style=flat-square&logo=github&logoColor=white"/>

**Database** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://img.shields.io/badge/PostgreSQL_14.12-302E50?style=flat-square&logo=postgresql&logoColor=white"/>
<img src="https://img.shields.io/badge/Redis_7.0.15-C3002F?style=flat-square&logo=redis&logoColor=white"/>

**Backend** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://img.shields.io/badge/Python_3.11-3776AB?style=flat-square&logo=Python&logoColor=white" />
<img src="https://img.shields.io/badge/django_3.2.25-092E20?style=flat-square&logo=django&logoColor=white"/>
<img src="https://img.shields.io/badge/django--rest--framework_3.14.0-092e20?style=flat-square&logo=django&logoColor=white" />

**Frontend** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://img.shields.io/badge/Vue.js_2.5.13-4FC08D?style=flat-square&logo=Vue.js&logoColor=white" />
<img src="https://img.shields.io/badge/Vuex_3.0.1-4FC08D?style=flat-square&logo=Vue.js&logoColor=white" />
<img src="https://img.shields.io/badge/Node.js_16.16.0-339933?style=flat-square&logo=Node.js&logoColor=white" />
<img src="https://img.shields.io/badge/ECharts_3.8.3-F72C5B?style=flat-square" />
<img src="https://img.shields.io/badge/iView_2.8.0-2d8cf0?style=flat-square" />
<img src="https://img.shields.io/badge/Element_2.0.9-409eff?style=flat-square" />

<br/>

## 세부 기능 소개

**문제 추천 기능**
- 보너스 점수 문제와 지난 주에 가장 어려웠던 문제를 선별 후 주 마다 제공
- 사용자가 푼 문제의 난이도, 부족한 영역을 반영한 개인 맞춤 문제 추천

**랭킹 및 티어 시스템**
- 총 점수 기준 사용자 랭킹 제공
- 오늘의 급상승 랭킹(당일 점수가 가장 많이 상승한 사용자 기준) 제공
- 학과별 점수 랭킹 및 상위 5명의 기여자 표기
- 새싹 ~ 다이아몬드 등급의 티어 제공

**문제 풀이 기능**
- 다크모드 및 코드 하이라이팅 지원
- 오픈소스 채점서버를 통한 채점 기능 제공

**어드민(CMS) 기능**
- 홈 배너 관리 기능 
- 사용자 관리 및 통계 대시보드
- 대회 관리 및 모니터링 시스템

<br/>

## 👨‍💻 구성원
### 개발 인원
<table>
  <tr>
    <td align="center">
      <a href="https://github.com/hunsy9">
        <img src="https://github.com/hunsy9.png" width="80" alt="hunsy9"/>
        <br />
        <sub><b>hunsy9</b></sub>
      </a>
      <br />
    </td>
    <td align="center">
      <a href="https://github.com/Boksam">
      <img src="https://github.com/Boksam.png" width="80" alt="Boksam"/>
      <br />
      <sub><b>Boksam</b></sub>
      </a>
      <br />
    </td>
    <td align="center">
      <a href="https://github.com/minmunui">
      <img src="https://github.com/minmunui.png" width="80" alt="minmunui"/>
      <br />
      <sub><b>minmunui</b></sub>
      </a>
      <br />
    </td>
    <td align="center">
      <a href="https://github.com/llddang">
      <img src="https://github.com/llddang.png" width="80" alt="llddang"/>
      <br />
      <sub><b>llddang</b></sub>
      </a>
      <br />
    </td>
    <td align="center">
      <a href="https://github.com/banchan01">
      <img src="https://github.com/banchan01.png" width="80" alt="banchan01"/>
      <br />
      <sub><b>banchan01</b></sub>
      </a>
      <br />
    </td>
  </tr>
</table>

<br />

## 💎 라이센스
해당 프로젝트는 [MIT LICENSE](https://opensource.org/license/MIT) 를 따릅니다.
The MIT License (MIT)

Copyright (c) Code Place Developers

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE A
