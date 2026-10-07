from __future__ import annotations

import json
from pathlib import Path

from airborne_vv.baseline import create_manifest, verify_manifest, write_manifest
from airborne_vv.cli import main
from airborne_vv.config import load_cases, load_requirements, load_software_config
from airborne_vv.models import AlertState, VerificationCase
from airborne_vv.runner import run_campaign
from airborne_vv.sut import AltitudeAlertComputer

ROOT = Path(__file__).parents[1]


def _arguments() -> list[str]:
    return [
        "--config",
        str(ROOT / "config/software-config.json"),
        "--requirements",
        str(ROOT / "config/requirements.json"),
        "--cases",
        str(ROOT / "config/verification-cases.json"),
    ]


def test_campaign_and_reports(tmp_path: Path) -> None:
    assert main(["verify", *_arguments(), "--output-dir", str(tmp_path)]) == 0
    report = json.loads((tmp_path / "verification-report.json").read_text(encoding="utf-8"))
    assert report["campaign_passed"] is True
    assert report["cases_total"] == 14
    assert report["requirements_coverage_percent"] == 100.0
    assert (tmp_path / "verification-report.md").is_file()
    assert (tmp_path / "traceability.csv").is_file()


def test_validate_command(capsys: object) -> None:
    assert main(["validate", *_arguments()]) == 0
    assert "8 requirements, 14 cases" in capsys.readouterr().out  # type: ignore[attr-defined]


def test_failed_campaign_returns_false() -> None:
    level, config = load_software_config(ROOT / "config/software-config.json")
    requirements = load_requirements(ROOT / "config/requirements.json")
    cases = list(load_cases(ROOT / "config/verification-cases.json"))
    original = cases[0]
    cases[0] = VerificationCase(
        original.case_id,
        original.title,
        original.requirement_ids,
        original.sample,
        AlertState.PULL_UP,
    )
    campaign = run_campaign(level, AltitudeAlertComputer(config), requirements, tuple(cases))
    assert campaign.passed is False
    assert campaign.results[0].as_dict()["passed"] is False


def test_baseline_create_and_check(tmp_path: Path) -> None:
    tracked = tmp_path / "tracked.txt"
    tracked.write_text("baseline\n", encoding="utf-8")
    manifest_path = tmp_path / "manifest.json"
    manifest = create_manifest((tracked,), "0.1.0")
    write_manifest(manifest, manifest_path)
    assert verify_manifest(manifest_path) == (True, ())
    assert main(["check-baseline", str(manifest_path)]) == 0
    tracked.write_text("changed\n", encoding="utf-8")
    passed, failures = verify_manifest(manifest_path)
    assert passed is False
    assert failures == (f"changed:{tracked.as_posix()}",)
    assert main(["check-baseline", str(manifest_path)]) == 1


def test_baseline_command(tmp_path: Path) -> None:
    source = tmp_path / "input.txt"
    source.write_text("content", encoding="utf-8")
    output = tmp_path / "baseline.json"
    assert main(["baseline", "--version", "0.1.0", "--output", str(output), str(source)]) == 0
    assert json.loads(output.read_text(encoding="utf-8"))["software_version"] == "0.1.0"
