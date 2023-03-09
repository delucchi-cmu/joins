from hipscat_registry import Registry


def test_load(test_data_dir):
    """empty"""
    reg = Registry(file=f"{test_data_dir}/registry.xml")
    reg.object_catalogs()
    reg.source_catalogs()
    # reg.add_catalog("small_sky", f"{test_data_dir}/small_sky")
    # reg.catalogs()
