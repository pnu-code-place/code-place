apiVersion: apps/v1
kind: DaemonSet
metadata:
  labels:
    app.kubernetes.io/name: kube-vip-ds
    app.kubernetes.io/version: v1.0.2
  name: kube-vip-ds
  namespace: kube-system
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: kube-vip-ds
  template:
    metadata:
      labels:
        app.kubernetes.io/name: kube-vip-ds
        app.kubernetes.io/version: v1.0.2
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
              - matchExpressions:
                  - key: node-role.kubernetes.io/master
                    operator: Exists
              - matchExpressions:
                  - key: node-role.kubernetes.io/control-plane
                    operator: Exists
      containers:
        - args:
            - manager
          env:
            - name: vip_arp
              value: "true"
            - name: port
              value: "6443"
            - name: vip_nodename
              valueFrom:
                fieldRef:
                  fieldPath: spec.nodeName
            - name: vip_interface
              value: eno3
            - name: vip_subnet
              value: "32"
            - name: dns_mode
              value: first
            - name: cp_enable
              value: "true"
            - name: cp_namespace
              value: kube-system
            - name: svc_enable
              value: "true"
            - name: svc_leasename
              value: plndr-svcs-lock
            - name: vip_leaderelection
              value: "true"
            - name: vip_leasename
              value: plndr-cp-lock
            - name: vip_leaseduration
              value: "5"
            - name: vip_renewdeadline
              value: "3"
            - name: vip_retryperiod
              value: "1"
            - name: address
              value: ##VIP_ADDRESS##
            - name: prometheus_server
              value: :2112
          image: ghcr.io/kube-vip/kube-vip:v1.0.2
          imagePullPolicy: IfNotPresent
          name: kube-vip
          resources: {}
          securityContext:
            capabilities:
              add:
                - NET_ADMIN
                - NET_RAW
              drop:
                - ALL
      hostNetwork: true
      serviceAccountName: kube-vip
      tolerations:
        - effect: NoSchedule
          operator: Exists
        - effect: NoExecute
          operator: Exists
  updateStrategy: {}
