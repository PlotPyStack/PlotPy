# content of conftest.py


def pytest_addoption(parser):
    """Add custom options to the pytest command line."""
    parser.addoption(
        "--unattended",
        action="store_true",
        default=None,
        help="Unattended mode for gui tests",
    )
