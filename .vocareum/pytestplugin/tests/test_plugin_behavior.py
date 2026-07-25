# tests/test_plugin_behavior.py
import os

from _pytest.pytester import Pytester

DIVIDER = "=" * 119 + "\n"


def test_success_output_with_markers(pytester: Pytester) -> None:
    pytester.makepyfile("""
        import pytest

        @pytest.mark.vocareum_test_name("Test the behaviour of success output using marks")
        @pytest.mark.vocareum_weight(5)
        @pytest.mark.vocareum_success_msg("Success!")
        @pytest.mark.vocareum_failure_msg("Failure!")
        def test_example():
            assert True
    """)

    os.environ["vocareumGradeFile"] = str(pytester.path / "grade.txt")
    os.environ["vocareumReportFile"] = str(pytester.path / "report.txt")

    result = pytester.runpytest()

    result.assert_outcomes(passed=1)

    grade = pytester.path.joinpath("grade.txt").read_text()
    report = pytester.path.joinpath("report.txt").read_text()

    assert grade == "Test the behaviour of success output using marks, 5\n"
    assert report == "Success!\n" + DIVIDER


def test_failure_output_with_markers(pytester: Pytester) -> None:
    pytester.makepyfile("""
        import pytest

        @pytest.mark.vocareum_test_name("Test the behaviour of failure output using marks")
        @pytest.mark.vocareum_weight(5)
        @pytest.mark.vocareum_success_msg("Success!")
        @pytest.mark.vocareum_failure_msg("Failure!")
        def test_example():
            assert False
    """)

    os.environ["vocareumGradeFile"] = str(pytester.path / "grade.txt")
    os.environ["vocareumReportFile"] = str(pytester.path / "report.txt")

    result = pytester.runpytest()

    result.assert_outcomes(failed=1)

    grade = pytester.path.joinpath("grade.txt").read_text()
    report = pytester.path.joinpath("report.txt").read_text()

    assert grade == "Test the behaviour of failure output using marks, 0\n"
    assert report == "Failure!\n" + DIVIDER


def test_success_output_with_defaults(pytester: Pytester) -> None:
    pytester.makepyfile("""
        def test_example_success_function():
            assert True
    """)

    os.environ["vocareumGradeFile"] = str(pytester.path / "grade.txt")
    os.environ["vocareumReportFile"] = str(pytester.path / "report.txt")

    result = pytester.runpytest()

    result.assert_outcomes(passed=1)

    grade = pytester.path.joinpath("grade.txt").read_text()
    report = pytester.path.joinpath("report.txt").read_text()

    assert grade == "Test example success function, 10\n"
    assert report == "Test passed: Test example success function.\n" + DIVIDER


def test_failure_output_with_defaults(pytester: Pytester) -> None:
    pytester.makepyfile("""
        def test_example_failure_function():
            assert False
    """)

    os.environ["vocareumGradeFile"] = str(pytester.path / "grade.txt")
    os.environ["vocareumReportFile"] = str(pytester.path / "report.txt")

    result = pytester.runpytest()

    result.assert_outcomes(failed=1)

    grade = pytester.path.joinpath("grade.txt").read_text()
    report = pytester.path.joinpath("report.txt").read_text()

    assert grade == "Test example failure function, 0\n"
    assert (
        report
        == "Test failed: Test example failure function. Please try again.\n" + DIVIDER
    )
