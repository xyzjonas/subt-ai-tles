import os
import pytest

from pathlib import Path


test_data = Path(os.path.dirname(__file__)).parent / "data"

@pytest.fixture(scope="session")
def data():
    return test_data

