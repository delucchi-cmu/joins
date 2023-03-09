import os

import pytest

DATA_DIR_NAME = "data"
TEST_DIR = os.path.dirname(__file__)

# pylint: disable=missing-function-docstring, redefined-outer-name


@pytest.fixture
def test_data_dir():
    return os.path.join(TEST_DIR, DATA_DIR_NAME)
