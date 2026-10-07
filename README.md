# Airborne Software Requirements Verification Harness

A deterministic Python test system for a small synthetic altitude-alert component.
It demonstrates requirements-based verification, strict configuration handling,
requirement-to-test traceability, controlled baselines, and reproducible evidence.

The repository applies selected learning concepts associated with DO-178C. It is
not certified airborne software, a compliance claim, a qualified verification
tool, a safety assessment, or evidence from aircraft hardware.

## Implemented behavior

The software under test receives two synthetic height channels, vertical speed,
landing-gear state, and a warning-inhibit flag. It validates ranges and then returns
one of five deterministic states: `NORMAL`, `PULL_UP`, `SENSOR_DISAGREE`,
`INHIBITED`, or `INPUT_INVALID`.

The verification campaign includes normal, robustness, precedence, and exact
boundary cases. Configuration, requirements, cases, and expected results are stored
outside the implementation.

## Verification flow

```text
requirements + cases + configuration
                |
                v
      schema and traceability checks
                |
                v
      deterministic component execution
                |
                v
 JSON evidence + Markdown report + traceability CSV
```

## Quick start

Requires Python 3.11 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"

airborne-vv check-baseline baseline/manifest.json
airborne-vv validate --config config/software-config.json `
  --requirements config/requirements.json `
  --cases config/verification-cases.json
airborne-vv verify --config config/software-config.json `
  --requirements config/requirements.json `
  --cases config/verification-cases.json `
  --output-dir artifacts/generated
```

## Quality gates

```powershell
ruff check .
ruff format --check .
mypy src
pytest --cov=airborne_vv --cov-branch --cov-report=term-missing
python -m build
```

GitHub Actions runs these checks on Python 3.11 and 3.12, verifies the controlled
baseline, and executes the evidence campaign.

## Repository map

```text
src/airborne_vv/   component, loaders, runner, traceability, reporting, CLI
config/            software parameters, requirements, verification cases
tests/             unit, robustness, integration, reporting, and CLI tests
baseline/          hashes for controlled campaign inputs
docs/              architecture, verification, configuration, and learning notes
.github/workflows/ quality, build, baseline, and campaign checks
```

Start with [DO-178C learning notes](docs/do-178c-learning-notes.md), the
[verification plan](docs/verification-plan.md), and the
[configuration-management plan](docs/configuration-management-plan.md).

## Evidence boundary

The component, requirements, thresholds, failure conditions, and assigned software
level are repository-defined. Tests run on a host Python interpreter, not target
hardware. Coverage is a development guardrail and does not establish DO-178C
structural coverage or certification credit.

## License

MIT
