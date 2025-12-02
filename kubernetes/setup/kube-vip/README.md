# K3s와 Kube-vip을 이용한 고가용성(HA) 클러스터 구성 가이드

이 문서는 K3s와 Kube-vip을 함께 사용하여 여러 컨트롤 플레인 노드에 걸쳐 안정적인 가상 IP(VIP)를 갖는 고가용성 Kubernetes 클러스터를 구축하는 방법을 안내합니다.

### 핵심 파일

- `kube-vip-rbac.yaml`: Kube-vip이 클러스터 리소스에 접근하는 데 필요한 권한(RBAC)을 정의합니다.
- `kube-vip.yaml.tpl`: Kube-vip DaemonSet을 위한 템플릿입니다. 실제 배포 시 가상 IP 주소(`##VIP_ADDRESS##`)를 채워 넣어야 합니다.

---

### 1. 첫 번째 컨트롤 플레인 노드 설정

가장 먼저 클러스터를 초기화할 첫 번째 노드를 설정합니다.

#### 1-1. 환경 변수 설정

사용할 가상 IP(VIP)와 노드의 네트워크 인터페이스를 환경 변수로 지정합니다. 이 값은 **환경에 맞게 반드시 변경**해야 합니다.

```sh
export VIP="192.168.0.100"      # 클러스터에 할당할 가상 IP 주소
export INTERFACE="eno3"        # 노드의 네트워크 인터페이스 이름 (e.g., eth0, eno1)
```

#### 1-2. Kube-vip 매니페스트 준비

K3s가 자동으로 로드할 매니페스트 디렉토리를 만들고, 저장소에 미리 준비된 Kube-vip 설정 파일들을 복사합니다.

```sh
# 매니페스트 디렉토리 생성
sudo mkdir -p /var/lib/rancher/k3s/server/manifests/

# 1. RBAC 설정 파일을 복사합니다.
sudo cp ./kube-vip-rbac.yaml /var/lib/rancher/k3s/server/manifests/kube-vip-rbac.yaml

# 2. DaemonSet 템플릿을 복사하고, 위에서 설정한 VIP 주소로 내용을 교체합니다.
sudo cp ./kube-vip.yaml.tpl /var/lib/rancher/k3s/server/manifests/kube-vip.yaml
sudo sed -i "s/##VIP_ADDRESS##/$VIP/g" /var/lib/rancher/k3s/server/manifests/kube-vip.yaml
```

> **참고:** `sed -i` 명령어는 macOS와 GNU/Linux에서 다르게 동작할 수 있습니다. macOS에서는 `sed -i '' "s/..."` 와 같이 사용해야 할 수 있습니다.

#### 1-3. K3s 설치 및 클러스터 초기화

준비된 매니페스트와 함께 K3s 서버를 설치하여 클러스터를 시작합니다.

```sh
curl -sfL https://get.k3s.io | sh -s - server \
    --cluster-init \
    --tls-san $VIP \
    --disable servicelb \
    --disable-cloud-controller
```

- `--tls-san $VIP`: K3s API 서버의 TLS 인증서에 가상 IP를 추가하여, VIP를 통해 API 서버에 안전하게 접근할 수 있도록 합니다.
- `--disable servicelb`: K3s의 기본 서비스 로드밸런서인 "ServiceLB"를 비활성화합니다. Kube-vip이 이 역할을 대신합니다.

---

### 2. 추가 컨트롤 플레인 노드 합류

첫 번째 노드 설정이 완료되면, 다른 컨트롤 플레인 노드를 클러스터에 추가하여 고가용성 환경을 완성합니다.

#### 2-1. 클러스터 조인 토큰 확인

**첫 번째 노드**에서 다음 명령을 실행하여 클러스터에 합류하는 데 필요한 토큰을 확인하고 변수에 저장합니다.

```sh
export TOKEN=$(sudo cat /var/lib/rancher/k3s/server/node-token)
echo "클러스터 조인 토큰: $TOKEN"
```

#### 2-2. 추가 노드에서 K3s 설치

**추가할 노드**에서 다음 명령어를 실행하여 클러스터에 컨트롤 플레인 노드로 합류합니다.

```sh
# 아래 변수들은 사용자 환경에 맞게 설정해야 합니다.
export VIP="192.168.0.100"          # 첫 번째 노드에서 설정한 것과 동일한 가상 IP
export TOKEN="<your-cluster-token>" # 2-1 단계에서 확인한 클러스터 조인 토큰

curl -sfL https://get.k3s.io | sh -s - server \
    --server https://$VIP:6443 \
    --token ${TOKEN} \
    --tls-san $VIP \
    --disable servicelb \
    --disable-cloud-controller
```
