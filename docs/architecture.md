# Architecture

The repository separates the synthetic software under test from the verification
automation so that expected results are held outside the implementation.

```text
requirements.json ----+
verification-cases.json+--> strict loaders --> traceability check
software-config.json -+                         |
                                                v
input sample --> AltitudeAlertComputer --> actual alert state
      |                                         |
      +------------- expected state ------------+--> verdicts
                                                       |
                                  JSON report + Markdown report + CSV matrix
```

`AltitudeAlertComputer` is deliberately small. It validates two synthetic height
channels and vertical speed, applies inhibit and sensor-disagreement precedence,
then evaluates a configurable pull-up condition. The harness checks configuration,
executes deterministic cases, and retains requirement references in each verdict.

The generated evidence tool is not qualified. A real airborne program would need
approved plans, independence appropriate to the assigned software level, reviews,
complete lifecycle data, target-computer verification where applicable, and formal
configuration and quality-assurance processes.

