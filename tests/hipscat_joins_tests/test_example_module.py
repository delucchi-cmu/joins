import os

import pandas as pd
import pytest

from hipscat_joins import example_module

TEST_DIR = os.path.dirname(__file__)


def test_join(test_data_dir):
    """empty"""
    # left_frame = pd.read_csv(os.path.join(test_data_dir, "obj_in_src", "object.csv"))

    # right_frame = pd.read_csv(os.path.join(test_data_dir, "obj_in_src", "source.csv"))

    # example_module.join(left_frame, right_frame)
