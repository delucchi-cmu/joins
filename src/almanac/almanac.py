"""Single instance of an almanac, and available catalogs in nested namespaces"""

from .almanac_data import parse_almanac_data
from .catalog_data import CatalogData


class Almanac:
    """Single instance of an almanac, and available catalogs in nested namespaces"""

    def __init__(self, file):
        """Create new almanac"""
        self.entries = {}
        self.file = file

        ## Parse text data
        self.text_data = parse_almanac_data(self.file, "")

        ## Initialize catalog data graph from text data
        for included_almanac in self.text_data.included_almanacs:
            self._init_catalog_objects_from_included(included_almanac)
        for namespace in self.text_data.namespaces:
            self._init_catalog_objects(namespace)

        for included_almanac in self.text_data.included_almanacs:
            self._init_catalog_links_from_included(included_almanac)
        for namespace in self.text_data.namespaces:
            self._init_catalog_links(namespace)

    def _init_catalog_objects(self, namespace_text):
        for catalog in namespace_text.catalogs:
            new_entry = CatalogData()
            new_entry.catalog_name = catalog.catalog_name
            new_entry.catalog_path = catalog.catalog_path
            new_entry.catalog_type = catalog.catalog_type
            self.entries[new_entry.catalog_name] = new_entry

    def _init_catalog_objects_from_included(self, included_almanac):
        for namespace in included_almanac.namespaces:
            self._init_catalog_objects(namespace)

    def _init_catalog_links(self, namespace_text):
        for catalog in namespace_text.catalogs:
            catalog_name = catalog.catalog_name
            catalog_type = catalog.catalog_type
            this_catalog = self.entries[catalog_name]

            if catalog_type == "object":
                pass
            elif catalog_type == "source":
                this_catalog.primary = self._get_linked_catalog(
                    catalog.primary, "primary", "source", catalog_name
                )
                this_catalog.primary.sources.append(this_catalog)
            elif catalog_type == "index":
                this_catalog.primary = self._get_linked_catalog(
                    catalog.primary, "primary", "index", catalog_name
                )
                this_catalog.primary.indexes.append(this_catalog)
            elif catalog_type == "neighbor":
                this_catalog.primary = self._get_linked_catalog(
                    catalog.primary, "primary", "neighbor", catalog_name
                )
                this_catalog.primary.neighbors.append(this_catalog)
            elif catalog_type == "association":
                this_catalog.primary = self._get_linked_catalog(
                    catalog.primary, "primary", "association", catalog_name
                )
                this_catalog.primary.associations.append(this_catalog)
                this_catalog.join = self._get_linked_catalog(
                    catalog.join, "join", "association", catalog_name
                )
                this_catalog.join.associations_right.append(this_catalog)
            else:
                raise ValueError(f"Unknown catalog type {catalog_type}")

    def _init_catalog_links_from_included(self, included_almanac):
        for namespace in included_almanac.namespaces:
            self._init_catalog_links(namespace)

    def _get_linked_catalog(self, linked_text, node_type, link_type, catalog_name):
        if not linked_text in self.entries:
            raise ValueError(f"{link_type} {catalog_name} missing {node_type} catalog {linked_text}")
        return self.entries[linked_text]

    def catalogs(self):
        """print top=level catalog names"""
        print("--ALL CATALOGS--")
        for entry in self.entries.values():
            print(entry)

    def object_catalogs(self):
        """print top=level OBJECT catalog names"""
        print("--ALL OBJECT CATALOGS--")
        for entry in self.entries.values():
            if entry.catalog_type == "object":
                print(entry)

    def source_catalogs(self):
        """print top=level SOURCE catalog names"""
        print("--ALL SOURCE CATALOGS--")
        for entry in self.entries.values():
            if entry.catalog_type == "source":
                print(entry)
