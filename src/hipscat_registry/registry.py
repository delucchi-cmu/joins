import json
import os
import xml.etree.ElementTree as ET


class CatalogEntry:
    """holder of entry"""

    def __init__(self):
        self.catalog_name = ""
        self.catalog_path = ""
        self.catalog_type = ""
        self.sources = []
        self.neighbors = []
        self.associations = []
        self.associations_right = []
        self.indexes = []

    def __str__(self):
        formatted_string = f"{self.catalog_name} ({self.catalog_type})\n"
        if self.sources:
            formatted_string += "  sources\n"
            for index in self.sources:
                formatted_string += f"    {index.catalog_name}\n"
        if self.neighbors:
            formatted_string += "  neighbors\n"
            for index in self.neighbors:
                formatted_string += f"    {index.catalog_name}\n"
        if self.associations or self.associations_right:
            formatted_string += "  associations\n"
            for index in self.associations:
                formatted_string += f"    {index.catalog_name}\n"
            for index in self.associations_right:
                formatted_string += f"    ** {index.catalog_name}\n"
        if self.indexes:
            formatted_string += "  indexes\n"
            for index in self.indexes:
                formatted_string += f"    {index.catalog_name}\n"
        return formatted_string


class Registry:
    """holder of catalogs"""

    file = ""
    tree = None
    entries = {}

    def __init__(self, file=None):
        """Cretae new registry"""
        if file:
            self.file = file
        self.tree = ET.parse(self.file)
        self._init_from_tree()

    def _init_from_tree(self):
        root = self.tree.getroot()

        ## Loop over tree once to initialize all the entries.
        for catalog in root.findall("catalog"):
            new_entry = CatalogEntry()
            new_entry.catalog_name = catalog.get("name")
            new_entry.catalog_path = catalog.get("path")
            new_entry.catalog_type = catalog.get("type", default="object")
            self.entries[new_entry.catalog_name] = new_entry

        ## Loop over again to initialize all the relationships.
        for catalog in root.findall("catalog"):
            catalog_name = catalog.get("name")
            catalog_type = catalog.get("type", default="object")
            this_catalog = self.entries[catalog_name]

            if catalog_type == "object":
                pass
            elif catalog_type == "source":
                self._get_linked_catalog(
                    catalog, "primary", "source", catalog_name
                ).sources.append(this_catalog)
            elif catalog_type == "index":
                self._get_linked_catalog(
                    catalog, "primary", "index", catalog_name
                ).indexes.append(this_catalog)
            elif catalog_type == "neighbor":
                self._get_linked_catalog(
                    catalog, "primary", "neighbor", catalog_name
                ).neighbors.append(this_catalog)
            elif catalog_type == "association":
                self._get_linked_catalog(
                    catalog, "primary", "association", catalog_name
                ).associations.append(this_catalog)
                self._get_linked_catalog(
                    catalog, "join", "association", catalog_name
                ).associations_right.append(this_catalog)
            else:
                raise ValueError(f"Unknown catalog type {catalog_type}")

    def _get_linked_catalog(self, xml_node, node_type, link_type, catalog_name):
        linked = xml_node.findall(node_type)
        if len(linked) == 0:
            raise ValueError(
                f"{link_type} {catalog_name} has no many {node_type} catalog"
            )
        if len(linked) > 1:
            raise ValueError(
                f"{link_type} {catalog_name} has too many {node_type} catalogs"
            )
        linked_text = linked[0].text

        if not linked_text in self.entries:
            raise ValueError(
                f"{link_type} {catalog_name} missing {node_type} catalog {linked_text}"
            )
        return self.entries[linked_text]

    def catalogs(self):
        """print top=level catalog names"""
        print("--ALL REGISTERED CATALOGS--")
        for entry in self.entries.values():
            print(entry)

    def object_catalogs(self):
        """print top=level OBJECT catalog names"""
        print("--ALL REGISTERED OBJECT CATALOGS--")
        for entry in self.entries.values():
            if entry.catalog_type == 'object':
                print(entry)

    def source_catalogs(self):
        """print top=level SOURCE catalog names"""
        print("--ALL REGISTERED SOURCE CATALOGS--")
        for entry in self.entries.values():
            if entry.catalog_type == 'source':
                print(entry)

    def add_catalog(self, name, path):
        """add one to entries"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"No directory exists at {path}")
        metadata_filename = os.path.join(path, "catalog_info.json")
        if not os.path.exists(metadata_filename):
            raise FileNotFoundError(
                f"No catalog info found where expected: {metadata_filename}"
            )

        with open(metadata_filename, "r", encoding="utf-8") as metadata_info:
            metadata_keywords = json.load(metadata_info)
        catalog_name = metadata_keywords["catalog_name"]
        if name != catalog_name:
            print(
                "warning - catalog names don't match, which could cause confusion "
                f"({name} vs {catalog_name})"
            )

        new_entry = CatalogEntry()
        new_entry.catalog_name = name
        new_entry.catalog_path = path
        self.entries[name] = new_entry


if __name__ == "__main__":
    reg = Registry(file="/home/delucchi/xmatch/registry.xml")
    reg.catalogs()
    reg.add_catalog("small_sky", "/home/delucchi/xmatch/catalogs/small_sky")
    reg.catalogs()
