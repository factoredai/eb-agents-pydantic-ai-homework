import os
from pathlib import Path
from typing import Any, Optional

import pytest
from _pytest.config import Config
from _pytest.main import Session
from _pytest.mark.structures import Mark
from _pytest.nodes import Item
from _pytest.reports import TestReport
from _pytest.runner import CallInfo
from dotenv import load_dotenv

# Load .env variables on import from client project
load_dotenv(dotenv_path=Path.cwd() / ".env")


def pytest_configure(config: Config) -> None:
    config.vocareum_results = []  # type: ignore[attr-defined]


def _get_marker_arg(marker: Optional[Mark], default: Any = None) -> Any:
    return marker.args[0] if marker else default


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: Item, call: CallInfo[Any]) -> Any:
    outcome = yield
    report: TestReport = outcome.get_result()

    vocareum_test_name = item.get_closest_marker("vocareum_test_name")
    vocareum_weight = item.get_closest_marker("vocareum_weight")
    vocareum_success_msg = item.get_closest_marker("vocareum_success_msg")
    vocareum_failure_msg = item.get_closest_marker("vocareum_failure_msg")

    # Store as user_properties (official pytest extension mechanism)
    report.user_properties.extend(
        [
            ("vocareum_test_name", _get_marker_arg(vocareum_test_name)),
            ("vocareum_weight", _get_marker_arg(vocareum_weight, 10)),
            ("vocareum_success_msg", _get_marker_arg(vocareum_success_msg)),
            ("vocareum_failure_msg", _get_marker_arg(vocareum_failure_msg)),
            ("vocareum_config", item.config),
        ]
    )


def _get_user_property(report: TestReport, key: str) -> Optional[Any]:
    for k, v in report.user_properties:
        if k == key:
            return v
    return None


def pytest_runtest_logreport(report: TestReport) -> None:
    if report.when != "call":
        return

    config: Optional[Config] = _get_user_property(report, "vocareum_config")
    if config is None:
        return

    default_test_name = report.nodeid.split("::")[-1].replace("_", " ").capitalize()

    test_name = _get_user_property(report, "vocareum_test_name") or default_test_name
    weight = _get_user_property(report, "vocareum_weight") or 10
    success_msg = (
        _get_user_property(report, "vocareum_success_msg")
        or f"Test passed: {default_test_name}."
    )
    failure_msg = (
        _get_user_property(report, "vocareum_failure_msg")
        or f"Test failed: {default_test_name}. Please try again."
    )

    score = weight if report.outcome == "passed" else 0
    summary = success_msg if report.outcome == "passed" else failure_msg

    config.vocareum_results.append(  # type: ignore[attr-defined]
        {"name": test_name, "score": score, "summary": summary}
    )


def pytest_sessionfinish(session: Session, exitstatus: int) -> None:
    results = session.config.vocareum_results  # type: ignore[attr-defined]
    grade_path = os.environ.get("vocareumGradeFile")
    report_path = os.environ.get("vocareumReportFile")
    
    if not grade_path or not report_path:
        raise RuntimeError(
            "Environment variables 'vocareumGradeFile' and/or 'vocareumReportFile' are not set. "
            "Grading output cannot be written. Please contact the lab support team."
        )

    if grade_path:
        os.makedirs(os.path.dirname(grade_path) or ".", exist_ok=True)
        with open(grade_path, "w", encoding="utf-8") as f:
            for r in results:
                f.write(f"{r['name']}, {r['score']}\n")

    if report_path:
        os.makedirs(os.path.dirname(report_path) or ".", exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            for r in results:
                f.write(f"{r['summary']}\n")
                f.write("=" * 119 + "\n")
