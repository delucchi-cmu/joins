import os

from almanac import Almanac
from almanac.almanac_data import write_almanac_file


def test_create(tmpdir, test_data_dir):
    """empty"""
    catalog_files = [
        os.path.join(test_data_dir, "small_sky/object"),
        os.path.join(test_data_dir, "small_sky/detections"),
        os.path.join(test_data_dir, "small_sky/object_id_index"),
        os.path.join(test_data_dir, "small_sky/object_neighbor_cache"),
        os.path.join(test_data_dir, "small_sky/object_to_detections"),
    ]

    almanac_file = f"{tmpdir}/almanac.xml"
    write_almanac_file(almanac_file, "foo", catalog_files, False)

    with open(
        almanac_file,
        "r",
        encoding="utf-8",
    ) as metadata_file:
        for line in metadata_file.readlines():
            print(line)

        # print(metadata_file.readlines())

    reg = Almanac(file=almanac_file)
    # reg.object_catalogs()
    # reg.source_catalogs()
