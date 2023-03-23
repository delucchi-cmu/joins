from almanac import Almanac


def test_load(test_data_dir):
    """empty"""
    test_registry_file = f"{test_data_dir}/almanac_flat.xml"
    reg = Almanac(file=test_registry_file)
    # reg.object_catalogs()
    # reg.source_catalogs()


def test_load_nested(test_data_dir):
    """empty"""
    test_registry_file = f"{test_data_dir}/almanac_nested.xml"
    reg = Almanac(file=test_registry_file)
    # reg.object_catalogs()
    # reg.source_catalogs()
