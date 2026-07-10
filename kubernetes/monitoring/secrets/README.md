# Monitoring Secrets

This directory is reserved for SealedSecret manifests generated per cluster.

Do not commit plaintext Kubernetes Secret manifests or raw Discord webhook URLs.
The AlertmanagerConfig expects the decrypted Secret below to exist in the
`monitoring` namespace:

- Secret: `alertmanager-contact-points`
- Key: `webhook-url`

Generate the SealedSecret with the target cluster public key:

```sh
kubectl -n monitoring create secret generic alertmanager-contact-points \
  --from-literal=webhook-url="$ALERT_WEBHOOK_URL" \
  --dry-run=client -o yaml \
  | kubeseal --controller-namespace kube-system --format yaml \
  > kubernetes/monitoring/secrets/alertmanager-contact-points.sealedsecret.yaml
```

If the SealedSecrets controller runs outside `kube-system`, change
`--controller-namespace` to the actual namespace.
