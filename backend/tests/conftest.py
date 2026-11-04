"""
Pytest configuration and test isolation hooks.
Enforces early test environment markers before test collection or execution.
"""
import os
import sys

# Ensure testing flag is established early in test session
os.environ["TESTING"] = "true"
os.environ.setdefault("TEST_DATABASE_URL", "postgresql+asyncpg://mock:mock@localhost:5432/mock_test")
os.environ.setdefault("APPROVED_TEST_DATABASE_URL", "postgresql+asyncpg://mock:mock@localhost:5432/mock_test")
os.environ.setdefault("REQUIRE_TEST_DB_EXPLICIT_AUTHORIZATION", "true")


def pytest_configure(config):
    """
    Hook called by pytest after command-line options have been parsed.
    Ensures that test mode is recognized across all layers.
    """
    os.environ["TESTING"] = "true"
    os.environ.setdefault("TEST_DATABASE_URL", "postgresql+asyncpg://mock:mock@localhost:5432/mock_test")
    os.environ.setdefault("APPROVED_TEST_DATABASE_URL", "postgresql+asyncpg://mock:mock@localhost:5432/mock_test")
    os.environ.setdefault("REQUIRE_TEST_DB_EXPLICIT_AUTHORIZATION", "true")
