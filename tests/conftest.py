import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: tests that read the 14.5 MB enharmonic CSV")
