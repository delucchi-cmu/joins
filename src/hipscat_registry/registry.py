import json
import os
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree


class CatalogEntry:
    """holder of entry"""

    def __init__(self):
        self.catalog_name = ""
        self.catalog_path = ""
        self.catalog_type = ""
        self.primary = None
        self.join = None
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

    def __init__(self, file=None):
        """Create new almanac"""
        self.entries = {}
        if file:
            self.file = file
        self._init_from_tree(ET.parse(self.file).getroot())

    def _init_from_tree(self, root):
        ## Loop over tree once to initialize all the entries.
        for catalog in root.findall("catalog"):
            new_entry = CatalogEntry()
            new_entry.catalog_name = catalog.get("name")
            new_entry.catalog_path = catalog.get("path")
            new_entry.catalog_type = catalog.get("type", default="object")

            metadata_keywords = self._get_metadata_keywords(new_entry.catalog_path)
            catalog_name = metadata_keywords["catalog_name"]
            if new_entry.catalog_name != catalog_name:
                print(
                    "warning - catalog names don't match, which could cause confusion "
                    f"({new_entry.catalog_name} vs {catalog_name})"
                )

            self.entries[new_entry.catalog_name] = new_entry

        ## Loop over again to initialize all the relationships.
        for catalog in root.findall("catalog"):
            catalog_name = catalog.get("name")
            catalog_type = catalog.get("type", default="object")
            this_catalog = self.entries[catalog_name]

            if catalog_type == "object":
                pass
            elif catalog_type == "source":
                this_catalog.primary = self._get_linked_catalog(catalog, "primary", "source", catalog_name)
                this_catalog.primary.sources.append(this_catalog)
            elif catalog_type == "index":
                this_catalog.primary = self._get_linked_catalog(catalog, "primary", "index", catalog_name)
                this_catalog.primary.indexes.append(this_catalog)
            elif catalog_type == "neighbor":
                this_catalog.primary = self._get_linked_catalog(catalog, "primary", "neighbor", catalog_name)
                this_catalog.primary.neighbors.append(this_catalog)
            elif catalog_type == "association":
                this_catalog.primary = self._get_linked_catalog(
                    catalog, "primary", "association", catalog_name
                )
                this_catalog.primary.associations.append(this_catalog)
                this_catalog.join = self._get_linked_catalog(catalog, "join", "association", catalog_name)
                this_catalog.join.associations_right.append(this_catalog)
            else:
                raise ValueError(f"Unknown catalog type {catalog_type}")

    def _get_linked_catalog(self, xml_node, node_type, link_type, catalog_name):
        linked = xml_node.findall(node_type)
        if len(linked) == 0:
            raise ValueError(f"{link_type} {catalog_name} has no many {node_type} catalog")
        if len(linked) > 1:
            raise ValueError(f"{link_type} {catalog_name} has too many {node_type} catalogs")
        linked_text = linked[0].text

        if not linked_text in self.entries:
            raise ValueError(f"{link_type} {catalog_name} missing {node_type} catalog {linked_text}")
        return self.entries[linked_text]

    def _get_metadata_keywords(self, catalog_path):
        """Fetch metadata keywords from catalog_info file."""
        if not os.path.exists(catalog_path):
            raise FileNotFoundError(f"No directory exists at {catalog_path}")
        metadata_filename = os.path.join(catalog_path, "catalog_info.json")
        if not os.path.exists(metadata_filename):
            raise FileNotFoundError(f"No catalog info found where expected: {metadata_filename}")

        with open(metadata_filename, "r", encoding="utf-8") as metadata_info:
            metadata_keywords = json.load(metadata_info)
            return metadata_keywords

    def catalogs(self):
        """print top=level catalog names"""
        print("--ALL REGISTERED CATALOGS--")
        for entry in self.entries.values():
            print(entry)

    def object_catalogs(self):
        """print top=level OBJECT catalog names"""
        print("--ALL REGISTERED OBJECT CATALOGS--")
        for entry in self.entries.values():
            if entry.catalog_type == "object":
                print(entry)

    def source_catalogs(self):
        """print top=level SOURCE catalog names"""
        print("--ALL REGISTERED SOURCE CATALOGS--")
        for entry in self.entries.values():
            if entry.catalog_type == "source":
                print(entry)

    def add_catalog(self, name, path, overwrite=False):
        """add one to entries"""
        if not overwrite and name in self.entries:
            raise ValueError(f"Catalog name {name} already in use")

        metadata_keywords = self._get_metadata_keywords(path)
        catalog_name = metadata_keywords["catalog_name"]
        if name != catalog_name:
            print(
                "warning - catalog names don't match, which could cause confusion "
                f"({name} vs {catalog_name})"
            )

        new_entry = CatalogEntry()
        new_entry.catalog_name = name
        new_entry.catalog_path = path
        new_entry.catalog_type = metadata_keywords.get("catalog_type", "object")
        self.entries[name] = new_entry

    def save_almanac(self):
        """Save the almanac to file."""
        root = ET.Element("registry")

        for catalog_name, entry in self.entries.items():
            catalog = ET.SubElement(
                root,
                "catalog",
                name=catalog_name,
                type=entry.catalog_type,
                path=entry.catalog_path,
            )
            if entry.primary:
                ET.SubElement(catalog, "primary").text = entry.primary.catalog_name
            if entry.join:
                ET.SubElement(catalog, "join").text = entry.join.catalog_name

        tree = ElementTree(root)
        # ET.indent(tree, space="\t", level=0)
        tree.write(self.file)
