import xml.etree.ElementTree as ET

from hipscat_registry import Registry


def test_load(test_registry_file, test_data_dir):
    """empty"""
    reg = Registry(file=test_registry_file)
    reg.object_catalogs()
    reg.source_catalogs()
    reg.add_catalog("small_sky2", f"{test_data_dir}/small_sky")
    # reg.catalogs()
    reg.save_almanac()

