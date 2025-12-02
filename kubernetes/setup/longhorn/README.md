# Longhorn을 이용한 분산 블록 스토리지 구축

이 문서는 K3s 클러스터에 고가용성 분산 블록 스토리지인 Longhorn을 설치하는 방법을 안내합니다.
Longhorn을 통해 각 노드의 로컬 디스크를 하나의 스토리지 풀로 통합하여 Persistent Volume(PV)을 동적으로 프로비저닝할 수 있습니다.

- 설치 공식 문서: https://longhorn.io/docs/1.10.1/deploy/install/install-with-kubectl/

### 1. 노드 환경 사전 설정 (모든 노드 필수)

Longhorn이 정상적으로 작동하기 위해서는 **클러스터 내의 모든 노드(Control Plane & Worker)**에 iSCSI, NFS 관련 패키지와 커널 모듈이 설치되어 있어야 합니다.

#### 1-1. 필수 패키지 설치

스토리지 연결 및 암호화 볼륨 지원을 위한 패키지를 설치하고 서비스를 활성화합니다.

```sh
# 패키지 목록 업데이트
sudo apt-get update

# 필수 패키지 설치 (iSCSI, NFS, 암호화 도구, Multipath 도구)
sudo apt-get install -y open-iscsi nfs-common cryptsetup multipath-tools

# iSCSI 및 Multipath 데몬 활성화
sudo systemctl enable --now iscsid
sudo systemctl enable --now multipathd
```

#### 1-2. 커널 모듈 로드

Longhorn이 사용하는 필수 커널 모듈을 로드합니다.

```sh
# 커널 모듈 로드

sudo modprobe iscsi_tcp
sudo modprobe nfs
sudo modprobe dm_crypt

```

> 참고: 재부팅 후에도 모듈이 유지되도록 /etc/modules 파일에 nfs, dm_crypt 등을 추가하는 것을 권장합니다.

### 2. 환경 점검 (선택 사항)

설치 전에 현재 노드 환경이 Longhorn을 구동하기에 적합한지 검사 도구(longhornctl)를 통해 확인합니다.

#### 2-1. Longhorn CLI 설치

```sh
# longhornctl 바이너리 다운로드 (v1.10.1)
sudo curl -L https://github.com/longhorn/cli/releases/download/v1.10.1/longhornctl-linux-amd64 -o longhornctl

# 실행 권한 부여 및 시스템 경로로 이동
sudo chmod +x longhornctl
sudo mv ./longhornctl /usr/local/bin/longhornctl
```

#### 2-2. 사전 조건 검사

아래 명령어를 실행하여 모든 항목이 Installed 또는 Loaded 상태인지 확인합니다.

```sh
longhornctl check preflight
```

### 3. Longhorn 배포

모든 노드의 준비가 완료되면, **첫 번째 컨트롤 플레인 노드(Master)**에서 Longhorn을 배포합니다.

#### 3-1. 매니페스트 적용

```sh
# Longhorn v1.10.1 배포
kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.10.1/deploy/longhorn.yaml
```

#### 3-2. 설치 확인

모든 파드가 정상적으로 실행될 때까지 기다립니다.

```sh
kubectl get pods -n longhorn-system -w
```

### 4. (참고) 2노드 클러스터 설정

기본적으로 Longhorn은 데이터 안정성을 위해 3개의 복제본(Replica)을 생성합니다.
물리 노드가 3대 미만인 경우(예: 2대), 복제본을 배치할 공간이 부족하여 볼륨 상태가 Degraded로 표시될 수 있습니다.

이 경우 Longhorn UI(Settings > General > Default Replica Count)에서 기본 복제본 수를 2로 변경해야 합니다.
