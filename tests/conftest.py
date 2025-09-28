import pytest
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def load_env() -> None:
    """Loads environment variables from .env file before tests run."""
    load_dotenv()
