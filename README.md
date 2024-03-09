# CSEP Back End

![banner1.png](data%2Fassets%2Fbanner1.png)

[![Python](https://img.shields.io/badge/python-3.8.0-blue.svg?style=flat-square)](https://www.python.org/downloads/release/python-362/)
[![Django](https://img.shields.io/badge/django-3.2.9-blue.svg?style=flat-square)](https://www.djangoproject.com/)
[![Django Rest Framework](https://img.shields.io/badge/django_rest_framework-3.12.0-blue.svg?style=flat-square)](http://www.django-rest-framework.org/)

## 1. 프로젝트 소개
[기존의 운영중인 부산대학교 온라인 저지 웹페이지](http://oj.pusan.ac.kr/)를 개선하는 프로젝트입니다.

[베타 사이트](http://10.125.121.115:8080/)는 현재 부산대학교 내부 네트워크에서만 접속이 가능합니다.

부산대학교 코딩역량강화플랫폼의 백엔드 레포지토리입니다.

기존 [QingdaoU의 OnlineJudge](https://github.com/QingdaoU/OnlineJudge)를 기반으로 개발되었습니다.

### 개발 환경

<details>
  <summary>Python <strong>3.8.0</strong></summary>
  기본 QingdaoU의 Online Judge에 사용된 Python 버전은 <strong>3.8.0</strong> 입니다.
  이 프로젝트는 <strong>3.8.0</strong> 버전으로 개발되었습니다.
</details>

<details>
  <summary>Django <strong>3.2.9</strong></summary>
  기존 QingdaoU Online Judge에 사용된 버전인 <strong>3.2.9</strong> 버전을 사용합니다.
</details>

<details>
  <summary>Django Rest Framework <strong>3.12.0</strong></summary>
  기존 QingdaoU Online Judge에 사용된 버전인 <strong>3.12.0</strong> 버전을 사용합니다.
</details>

### 개발 기간
2023.12 ~ 2024.3 (현재 진행 중)

### 개발 인원
| github                              | 사진                                                              | 역할               | 이메일 주소                | 소속       |
|-------------------------------------|-----------------------------------------------------------------|------------------|-----------------------|----------|
| [hunsy9](https://github.com/hunsy9) | ![유저 아바타](https://avatars.githubusercontent.com/u/101303791?v=4)  | PM, 백엔드 개발 및 배포  | juniper0917@gmail.com | 정보컴퓨터공학부 |
| [Boksam](https://github.com/Boksam) | ![유저 아바타](https://avatars.githubusercontent.com/u/82745129?v=4) | 프로젝트 기획 및 백엔드 개발 | boksam1017@gmail.com  | 정보컴퓨터공학부 |

## 2. 프로젝트 설치
CSEP BE는 기본적으로 Docker, Docker-Compose에 기반합니다.

[Docker Desktop](https://www.docker.com/products/docker-desktop/)을 미리 설치해두고 프로젝트를 설치하는 것을 권장합니다.

### Linux
```bash

# 의존 라이브러리 설치
cd deploy
pip3 install -r requirements.txt

# 데이터베이스 배포 스크립트 실행
sh init_db.sh

# md5sum secret key 초기화 및 django migrate 실행
# super admin 생성(아이디 root, 비밀번호 rootroot로 자동생성됩니다.)
sh init_db.sh --migrate

# 프로젝트를 실행합니다. localhost:8080으로 접속할 수 있습니다.
python3 manage.py runserver


```

아래는 문제 채점 및 제출과 같은 비동기 작업을 처리하는 **dramatiq**를 실행시키는 방법입니다. 

```bash
# 1. 터미널을 하나 더 생성합니다.

# 2. dramitiq를 실행합니다.
python3 manage.py rundramatiq
```

## 3. Package, 디렉토리 구성

Python Package 구성은 다음과 같습니다.

```bash
├── account/                      # 회원 관련 패키지
├── announcement/                 # 공지사항 관련 패키지
├── community/                    # 커뮤니티 관련 패키지
├── contest/                      # 컨테스트 패키지
├── problem/                      # 문제 관련 패키지
├── submission/                   # 문제 제출 관련 패키지
├── utils/                        # 기타 util용 패키지
├── conf/                         # JudgeServer Heartbeat, SMTP등 환경 구성
├── fps/                          # 문제 등록 시 사용되는 데이터 파싱 
├── judge/                        # 문제 채점 시 사용되는 비동기 태스크
├── oj/                           # 개발환경 설정(Dev, Production)
```

Python Package를 제외한 폴더 구조는 다음과 같습니다.

```bash
├── deploy/                      # 배포 설정 파일
├── docs/                        # 문서 파일
├── data/                        # static 파일 및 로그 저장
```

## 4. 라이센스
[MIT](http://opensource.org/licenses/MIT)