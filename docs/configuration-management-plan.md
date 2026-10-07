# Configuration Management Plan

Git records source, requirements, verification cases, documentation, and CI
configuration. Release tags identify reviewable baselines. The `baseline` command
records SHA-256 hashes for selected controlled inputs; `check-baseline` detects
missing or changed files before a campaign is accepted.

The intended local sequence is:

```powershell
airborne-vv check-baseline baseline/manifest.json
airborne-vv validate --config config/software-config.json `
  --requirements config/requirements.json `
  --cases config/verification-cases.json
airborne-vv verify --config config/software-config.json `
  --requirements config/requirements.json `
  --cases config/verification-cases.json `
  --output-dir artifacts/generated
```

Changing a controlled file requires generating and reviewing a new manifest. This
is a small educational mechanism; it does not implement a certification authority's
approved configuration-management process or problem-report workflow.

