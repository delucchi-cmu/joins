import os

import pytest

DATA_DIR_NAME = "data"
TEST_DIR = os.path.dirname(__file__)

# pylint: disable=missing-function-docstring, redefined-outer-name


@pytest.fixture
def test_data_dir():
    return os.path.join(TEST_DIR, DATA_DIR_NAME)


@pytest.fixture
def test_registry_file(test_data_dir, tmpdir):
    with open(f"{test_data_dir}/registry.xml", "r", encoding="utf-8") as file:
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace("$DATA_DIR", test_data_dir)

    # Write the file out again
    registry_file = f"{tmpdir}/registry.xml"
    with open(registry_file, "w", encoding="utf-8") as file:
        file.write(filedata)

    return registry_file
