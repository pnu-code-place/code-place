# vLLM 배포 가이드

현재 `vLLM`은 `prod` 오버레이에서만 배포됩니다.

- `dev`: 포함되지 않음
- `prod`: 포함됨

## 전제 조건

- 클러스터에 NVIDIA device plugin 이 설치되어 있어야 합니다.
- `vLLM`을 띄울 GPU 노드 정확히 1대에만 아래 라벨이 붙어 있어야 합니다.

```bash
kubectl label node <gpu-node-name> workload.code-place.ai/vllm=true
```

- `prod` 오버레이에는 `vllm-hf-cache` PVC 가 포함되어 있습니다.
- Longhorn 이 정상 동작하면 PVC 는 자동 생성됩니다.

## 배포

```bash
kustomize build kubernetes/overlays/prod | kubectl apply -f -
```

## 확인

```bash
kubectl get pod -n code-place-prod -o wide | grep vllm
kubectl get svc -n code-place-prod vllm
kubectl describe pod -n code-place-prod -l app=vllm
```

정상 배포되면 클러스터 내부에서는 `http://vllm.code-place-prod:8000` 또는 같은 네임스페이스 안에서 `http://vllm:8000` 으로 접근할 수 있습니다.

## 현재 설정

- 이미지: `vllm/vllm-openai:v0.20.0`
- 모델: `Qwen/Qwen3.5-9B`
- 포트: `8000`
- 주요 옵션: `--dtype auto`, `--gpu-memory-utilization 0.9`, `--max-model-len 4096`, `--kv-cache-dtype fp8`, `--calculate-kv-scales`, `--enable-prefix-caching`, `--enable-chunked-prefill`, `--max-num-seqs 60`
- 리소스: `cpu: 16`, `memory: 64Gi`, `nvidia.com/gpu: 1`
- PVC: `vllm-hf-cache`, `storageClassName: longhorn`, `30Gi`, `ReadWriteOnce`

## 운영 메모

- `strategy: Recreate` 를 사용하므로 단일 replica 와 RWO PVC 조합에서 교체가 단순합니다.
- `startupProbe` 는 첫 모델 다운로드와 초기 로딩 시간을 길게 허용합니다.
- `readinessProbe` 가 통과하기 전까지는 서비스 트래픽을 받지 않습니다.
- `livenessProbe` 가 계속 실패하면 쿠버네티스가 컨테이너를 재시작합니다.
- `Service` 는 `ClusterIP` 이므로 외부에 직접 노출되지 않습니다.
- Longhorn replica 수는 YAML 에서 고정하지 않고, 필요하면 Longhorn UI 에서 직접 조정하는 전제를 둡니다.
- `max-num-seqs=60` 은 처리량 위주 값이라, 메모리 압박이나 OOM 이 보이면 가장 먼저 낮춰야 합니다.
- 더 보수적으로 운영하려면 이미지 tag 대신 digest 로 pin 하는 것이 가장 안전합니다.

## Monitoring

vLLM OpenAI-compatible server는 `/metrics`에서 Prometheus metrics를 제공합니다.
CodePlace monitoring kustomization은 prod vLLM Service를 `vllm-service-monitor.yaml`로 scrape합니다.
같은 monitoring kustomization은 `dcgm-exporter.yaml`도 배포해 `workload.code-place.ai/vllm=true` node의 NVIDIA GPU metric을 수집합니다.

```bash
kubectl apply -k kubernetes/monitoring
kubectl -n monitoring get servicemonitor vllm
kubectl -n monitoring get daemonset,servicemonitor dcgm-exporter
```

Grafana에서는 `CodePlace AI Inference` dashboard에서 다음 상태를 확인합니다.

- vLLM scrape up / Pod ready.
- running/waiting request count.
- KV cache usage.
- p95 e2e latency, queue latency, time-to-first-token.
- prompt/generation token throughput.
- `vllm-hf-cache` PVC usage.
- GPU utilization, framebuffer memory usage, temperature, XID error.

알림은 vLLM scrape 실패와 GPU XID error를 P0로 처리합니다. waiting queue 증가, KV cache 90% 초과, p95 latency 60초 초과, DCGM exporter unavailable, GPU utilization 95% 초과, GPU framebuffer memory 90% 초과, GPU temperature 85C 초과는 P1로 처리합니다.
