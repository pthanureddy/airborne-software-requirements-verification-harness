from __future__ import annotations

import argparse
from pathlib import Path

from airborne_vv.baseline import create_manifest, verify_manifest, write_manifest
from airborne_vv.config import load_cases, load_requirements, load_software_config
from airborne_vv.reporting import write_evidence
from airborne_vv.runner import run_campaign
from airborne_vv.sut import AltitudeAlertComputer
from airborne_vv.traceability import validate_traceability


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Requirements-based verification harness")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate configuration and traceability")
    _add_campaign_arguments(validate)

    verify = subparsers.add_parser("verify", help="run verification and write evidence")
    _add_campaign_arguments(verify)
    verify.add_argument("--output-dir", type=Path, required=True)

    baseline = subparsers.add_parser("baseline", help="create a SHA-256 baseline manifest")
    baseline.add_argument("--version", required=True)
    baseline.add_argument("--output", type=Path, required=True)
    baseline.add_argument("paths", nargs="+", type=Path)

    check = subparsers.add_parser("check-baseline", help="verify a baseline manifest")
    check.add_argument("manifest", type=Path)
    return parser


def _add_campaign_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--requirements", type=Path, required=True)
    parser.add_argument("--cases", type=Path, required=True)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "baseline":
        write_manifest(create_manifest(tuple(args.paths), args.version), args.output)
        return 0
    if args.command == "check-baseline":
        passed, failures = verify_manifest(args.manifest)
        for failure in failures:
            print(failure)
        return 0 if passed else 1

    software_level, config = load_software_config(args.config)
    requirements = load_requirements(args.requirements)
    cases = load_cases(args.cases)
    validate_traceability(requirements, cases)
    if args.command == "validate":
        print(f"valid: {len(requirements)} requirements, {len(cases)} cases")
        return 0

    campaign = run_campaign(
        software_level,
        AltitudeAlertComputer(config),
        requirements,
        cases,
    )
    write_evidence(campaign, requirements, args.output_dir)
    print(
        f"{'PASS' if campaign.passed else 'FAIL'}: "
        f"{sum(result.passed for result in campaign.results)}/{len(campaign.results)} cases"
    )
    return 0 if campaign.passed else 1
