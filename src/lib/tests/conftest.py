from pathlib import Path

import pytest

test_data = Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def data() -> Path:
    return test_data
