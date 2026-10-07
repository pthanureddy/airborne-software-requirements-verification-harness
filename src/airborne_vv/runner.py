from __future__ import annotations

from airborne_vv.models import CampaignResult, CaseResult, Requirement, VerificationCase
from airborne_vv.sut import AltitudeAlertComputer
from airborne_vv.traceability import validate_traceability


def run_campaign(
    software_level: str,
    computer: AltitudeAlertComputer,
    requirements: tuple[Requirement, ...],
    cases: tuple[VerificationCase, ...],
) -> CampaignResult:
    validate_traceability(requirements, cases)
    results = tuple(
        CaseResult(
            case_id=case.case_id,
            title=case.title,
            requirement_ids=case.requirement_ids,
            expected_state=case.expected_state,
            actual_state=computer.evaluate(case.sample),
        )
        for case in cases
    )
    return CampaignResult(
        software_level=software_level,
        results=results,
        requirement_ids=tuple(sorted(item.requirement_id for item in requirements)),
    )
