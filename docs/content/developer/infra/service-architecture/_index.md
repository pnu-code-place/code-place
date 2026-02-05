---
date: 2026-02-05T18:55:49+09:00
draft: false
title: "Service Architecture"
weight: 1
---

{{< callout >}}
이 문서에서는 CodePlace의 전체적인 Service Architecture와 트래픽 처리 흐름에 대해 설명합니다.
{{< /callout >}}

### 0. CodePlace Service-Architecture
<img width="2017" height="747" alt="image" src="https://github.com/user-attachments/assets/07cfc6cb-863b-4bab-99d9-bb990f43e38e" />

---

### 1. Entry Point

서비스의 모든 요청 트래픽은 가장 먼저 `Traefik`을 거치게 됩니다. CodePlace에서 `Traefik`은 크게 두 가지 핵심적인 네트워크 처리를 담당합니다.

- 보안을 위해 HTTP(80) 요청을 강제로 HTTPS(443)로 Redirect합니다.
- 외부에서 암호화되어 들어온 패킷을 여기서 복호화(TLS Termination)하여 내부망으로 전달합니다.

덕분에 내부 컨테이너들은 복잡한 암호화/복호화 연산 없이 효율적으로 통신할 수 있습니다. `Traefik`은 위 과정을 거친 모든 요청을 Frontend 컨테이너 (`Nginx`)로 전달합니다.

---

### 2. Routing

`Traefik`에서 전달된 요청은 Frontend 컨테이너의 `Nginx`에 도달하며, URL 경로에 따라 적절한 서비스로 분기됩니다.

### 1) 페이지 요청 (/)

루트 경로 등 페이지 관련 요청이 들어오면, Nginx는 사전에 빌드된 정적 파일을 브라우저에게 서빙합니다.
이 과정을 이해하기 위해서는 아래의 내용을 이해하여야 합니다.

- **Build Process**
<br>
Frontend 서버의 궁극적인 목표는 **정적파일 서빙**입니다. **배포 전 단계에서** 수행되는, 코드베이스에서 여러 가지로 흩어져 있는 소스코드를 하나로 묶는 과정이 빌드입니다. Build는 Node.js 환경에서 `Webpack`을 통해서 수행됩니다. <br> 빌드는 **코드 난독화, 압축, 번들링** 등 여러 가지를 포함하는데, 그중 JavaScript 버전 문법 호환성은 `Babel`을 통해 해결합니다. <br>
빌드 과정을 거친 결과물(`vendor.js`, `index.html`등)은 **nginx 폴더** 안에 저장이 됩니다. 이 결과물을 Nginx가 브라우저에 서빙하는 것입니다.

<br>

- **SPA (Single Page Application)**
<br>
Code Place는 `SPA`방식을 사용하고 있습니다. `SPA`는 **단일 페이지 애플리케이션**으로, MPA와 대비됩니다. 비교를 위해 `MPA`를 설명하겠습니다. `MPA`는 Multi Page Application으로서, 페이지 이동 시마다 서버에 정적파일을 새로 요청하여 브라우저에 렌더링 하는 방식입니다.<br>
반면 `SPA`는 최초 접속 시, 위의 빌드과정을 통해 사전에 만들어진 애플리케이션 구동에 필요한 모든 자원(`vendor.js`, `index.html` 등)을 한 번에 로드합니다. <br>
이때 모든 정적파일을 모두 다 하나의 파일에 담지는 않습니다. 초기 로딩 속도 최적화를 위해 자주 쓰이지 않거나 무거운 기능은 **Chunk** 단위로 잘라두었다가, 실제 해당 기능이 필요할 때, 브라우저가 요청하여 로드하도록 설계되어 있습니다. <br>
이후 페이지 전환 시에는, 이미 서빙된 **index.html** 파일 위에서 사전에 로드된 혹은 필요 시 Chunk로 로드된 `vendor.js` 등의 자바스크립트가 컴포넌트만 교체하여 화면 전환을 수행합니다. 이를 통해 서버 요청을 최소화하여 MPA에 비해 빠른 사용성을 제공합니다.

이러한 빌드, SPA 방식을 통해서 화면 로드가 일어납니다.

### 2) API 요청 (/api)

`/api`로 시작하는 경로로 들어온 요청일 경우, Nginx는 이를 뒷단의 **Django 서버**로 프록시합니다. 전달받은 요청에 따라 Django 서버는 매핑된 URL 엔드포인트를 통해 비즈니스 로직 (DB 조회, 연산 등)을 수행한 후, 그 결과를 브라우저에게 반환합니다.

---

### 3. Celery

`Celery`는 비동기 작업 큐 프레임워크로서, `Celery Beat`와 `Celery Worker`로 구성됩니다. <br>
백엔드 로직 중 실시간성이 필요하지 않거나 리소스를 많이 점유하는 작업은 Redis를 사용하여 비동기로 처리합니다. <br>주로 *채점*, *이메일 발송*, *세션 관리*, 그리고 *등수/점수 업데이트와 같은 스케줄링 Job*이 여기에 해당합니다.
이 구조의 이해를 돕기 위해 Celery의 두 핵심 컴포넌트를 설명하겠습니다.

- **Celery Worker :** Redis 큐에 쌓인 작업을 실제로 가져가서 수행하는 주체입니다. Django 서버와 실행환경은 유사하지만, Redis 큐에 있는 작업만 처리합니다.
- **Celery Beat :** 정해진 시간마다 주기적으로 실행되어야 하는 작업을 Redis 큐에 자동으로 예약해주는 스케줄러입니다.

<br>

**[동작 프로세스 예시]**

1.  **문제 제출 (`Celery Worker`)** <br>
사용자가 '제출하기' 버튼을 누르면, Django 서버는 직접 채점을 수행하지 않고 **채점 요청 메시지**를 `Redis Queue`에 등록만 하고 즉시 응답을 반환합니다. 대기 중이던 `Celery Worker`가 Redis Queue의 job을 감지하여 가져간 뒤 별도의 격리된 채점 서버와 통신하며 채점을 진행합니다.

2. **통계 업데이트 (`Celery Beat`)**<br>
사용자가 직접 요청하지 않아도 시스템이 수행해야 하는 '랭킹 업데이트' 같은 작업은 `Celery Beat`가 담당합니다. `Celery Beat`는 설정된 시각이 되면 자동으로 Redis에 작업 요청을 넣고, `Celery Worker`가 이를 가져가서 점수를 갱신합니다.

`Celery Worker`는 Django 서버와 본질적으로 유사한 환경(동일한 코드베이스, ORM 사용)을 가집니다.  다만 가장 큰 차이점은 수신 대상이 다르다는 것입니다.

- **Django Server :**  `HTTP Port`로 유입되는 클라이언트의 요청을 수신하여 처리합니다.
- **Celery Worker :** `Redis`에 등록된 비동기 작업을 대기 상태로 감시하다가 새로운 작업이 들어오면 이를 가져와 처리합니다.

<br>

**왜 이렇게 나누었을까요?**

만약 Celery 없이 Django가 모든 작업을 직접 처리한다고 가정해봅시다.

채점 요청이 동시에 1,000개 이상 들어오는 상황에서, CPU 연산량이 크고 실행 시간이 긴 **채점 작업**을 Django 서버 프로세스 안에서 수행하게 되면 요청 처리 흐름이 지연됩니다. 그 결과 로그인, 페이지 조회와 같은 일반적인 사용자 요청까지 영향을 받아 서비스 응답성이 급격히 저하될 수 있습니다.

물론 Django 내부에서도 비동기 처리를 구현할 수는 있습니다.
하지만 채점과 같이 **CPU 사용량이 크고 오래 걸리는 작업**을 HTTP 요청 처리 흐름과 함께 수행할 경우, 여전히 다른 사용자 요청에 영향을 주는 구조적 한계가 존재합니다.

따라서 CodePlace는 이러한 문제를 방지하기 위해, 무거운 작업을 Django 서버와 분리된 별도의 실행 주체인 `Celery Worker`에서 처리하도록 설계하였습니다.

---

### 4. Container

`Frontend 서버`, `Backend 서버`, `Redis`, `PostgreSQL`, `Celery Worker`, `Celery Beat`, `Judge Server` 모두 **Docker Container** 기반으로 운용됩니다.

이를 통해 각 서비스의 실행 환경을 격리시켜 충돌을 방지하고, `docker-compose`를 이용해 각 컨테이너를 일관성 있게 배포하고 관리할 수 있는 확장 가능한 구조를 갖췄습니다.
