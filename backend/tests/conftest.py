"""
Pytest configuration and test isolation hooks.
Enforces early test environment markers before test collection or execution.
"""
import os
import sys

# Ensure testing flag is established early in test session
os.environ["TESTING"] = "true"


def pytest_configure(config):
    """
    Hook called by pytest after command-line options have been parsed.
    Ensures that test mode is recognized across all layers.
    """
    os.environ["TESTING"] = "true"
