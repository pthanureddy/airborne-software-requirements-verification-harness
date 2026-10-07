from __future__ import annotations

from collections import Counter

from airborne_vv.models import Requirement, VerificationCase


class TraceabilityError(ValueError):
    pass


def validate_traceability(
    requirements: tuple[Requirement, ...], cases: tuple[VerificationCase, ...]
) -> None:
    requirement_ids = [item.requirement_id for item in requirements]
    case_ids = [item.case_id for item in cases]
    duplicate_requirements = sorted(
        item for item, count in Counter(requirement_ids).items() if count > 1
    )
    duplicate_cases = sorted(item for item, count in Counter(case_ids).items() if count > 1)
    if duplicate_requirements:
        raise TraceabilityError(f"duplicate requirements: {duplicate_requirements}")
    if duplicate_cases:
        raise TraceabilityError(f"duplicate cases: {duplicate_cases}")

    known = set(requirement_ids)
    for requirement in requirements:
        if requirement.parent_id is not None and requirement.parent_id not in known:
            raise TraceabilityError(
                f"{requirement.requirement_id} has unknown parent {requirement.parent_id}"
            )
        if requirement.verification_method != "test":
            raise TraceabilityError(
                f"{requirement.requirement_id} has unsupported verification method "
                f"{requirement.verification_method}"
            )

    referenced = {item for case in cases for item in case.requirement_ids}
    unknown = sorted(referenced - known)
    missing = sorted(known - referenced)
    if unknown:
        raise TraceabilityError(f"cases reference unknown requirements: {unknown}")
    if missing:
        raise TraceabilityError(f"requirements without verification cases: {missing}")
