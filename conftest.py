# content of conftest.py
import pytest

VALID_ARGS = ["unattended"]


def mode_checker(value):
    msg = "mode must specify a test execution type : 'attended' or 'unattended"
    if value not in VALID_ARGS:
        raise pytest.UsageError(msg)

    return value


def pytest_addoption(parser):
    parser.addoption(
        "--mode",
        action="store",
        default="attended",
        help="Unattended mode for gui tests",
        type=mode_checker,
    )


# XXX: Not used, left here as example
# @pytest.fixture
# def unattended(request):
#     unattended_arg = request.config.getoption("--mode")
#     return unattended_arg.lower() == "unattended"
