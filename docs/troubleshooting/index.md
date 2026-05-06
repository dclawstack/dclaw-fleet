# Troubleshooting

Common issues and solutions for DClaw Fleet.

## Quick Diagnostics

```bash
# Check app pods
kubectl get pods -n dclaw-fleet

# Check logs
kubectl logs -n dclaw-fleet deployment/dclaw-fleet-backend

# Check database
kubectl get clusters -n dclaw-fleet
```

## Sections

- [Common Issues](./common-issues)
- [FAQ](./faq)
