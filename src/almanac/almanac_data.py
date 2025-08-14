"""Original text from almanac data file."""

from __future__ import annotations

import json
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from xml.etree.ElementTree import ElementTree


@dataclass
class CatalogTextData:
    """holder of the original text data for a catalog's almanac entry"""

    catalog_name: str = ""
    catalog_path: str = ""
    catalog_type: str = ""
    relative_path: str = None
    primary: str = None
    join: str = None
    notes: list[str] = field(default_factory=list)
    contact_info: list[str] = field(default_factory=list)


@dataclass
class AlmanacTextData:
    """Top-level holder of catalog data."""

    namespaces: list[NamespaceTextData] = field(default_factory=list)
    included_almanacs: list[IncludedAlmanacTextData] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    contact_info: list[str] = field(default_factory=list)


@dataclass
class IncludedAlmanacTextData:
    """Holder of catalog data in another almanac."""

    file_path: str = None
    relative_file_path: str = None
    namespaces: list[NamespaceTextData] = field(default_factory=list)
    included_almanacs: list[IncludedAlmanacTextData] = field(default_factory=list)


@dataclass
class NamespaceTextData:
    """Collection of semantically linked catalogs."""

    namespace_part: str = None
    namespace_full: str = None
    catalogs: list[CatalogTextData] = field(default_factory=list)


def _get_linked_catalog_name(xml_node, node_type, link_type, catalog_name):
    linked = xml_node.findall(node_type)
    if len(linked) == 0:
        raise ValueError(f"{link_type} {catalog_name} has no {node_type} catalog")
    if len(linked) > 1:
        raise ValueError(f"{link_type} {catalog_name} has too many {node_type} catalogs")
    return linked[0].text


def _get_metadata_keywords(catalog_path):
    """Fetch metadata keywords from catalog_info file."""
    if not os.path.exists(catalog_path):
        raise FileNotFoundError(f"No directory exists at {catalog_path}")
    metadata_filename = os.path.join(catalog_path, "catalog_info.json")
    if not os.path.exists(metadata_filename):
        raise FileNotFoundError(f"No catalog info found where expected: {metadata_filename}")

    with open(metadata_filename, "r", encoding="utf-8") as metadata_info:
        metadata_keywords = json.load(metadata_info)
        return metadata_keywords


def _parse_catalog_data(filename, catalog_el) -> CatalogTextData:
    catalog_data = CatalogTextData()
    catalog_data.catalog_name = catalog_el.get("name")
    abs_path = catalog_el.get("path")
    if not abs_path:
        rel_path = catalog_el.get("relative_path")
        abs_path = os.path.join(os.path.dirname(filename), rel_path)

    catalog_data.catalog_path = abs_path
    catalog_data.catalog_type = catalog_el.get("type", default="object")

    if catalog_data.catalog_type == "object":
        pass
    elif catalog_data.catalog_type == "source":
        catalog_data.primary = _get_linked_catalog_name(
            catalog_el, "primary", "source", catalog_data.catalog_name
        )
    elif catalog_data.catalog_type == "index":
        catalog_data.primary = _get_linked_catalog_name(
            catalog_el, "primary", "index", catalog_data.catalog_name
        )
    elif catalog_data.catalog_type == "neighbor":
        catalog_data.primary = _get_linked_catalog_name(
            catalog_el, "primary", "neighbor", catalog_data.catalog_name
        )
    elif catalog_data.catalog_type == "association":
        catalog_data.primary = _get_linked_catalog_name(
            catalog_el, "primary", "association", catalog_data.catalog_name
        )
        catalog_data.join = _get_linked_catalog_name(
            catalog_el, "join", "association", catalog_data.catalog_name
        )
    else:
        raise ValueError(f"Unknown catalog type {catalog_data.catalog_type}")

    return catalog_data


def _parse_included_almanac_data(include_el, original_filename, prefix) -> AlmanacTextData:
    """from a file"""
    almanac_data = IncludedAlmanacTextData()

    abs_path = include_el.get("path")
    if not abs_path:
        rel_path = include_el.get("relative_path")
        abs_path = os.path.join(os.path.dirname(original_filename), rel_path)

    root_el = ET.parse(abs_path).getroot()
    for namespace in root_el.findall("namespace"):
        almanac_data.namespaces.append(_parse_namespace_data(abs_path, namespace, prefix))
    return almanac_data


def _parse_namespace_data(filename, namespace_el, prefix) -> NamespaceTextData:
    part = namespace_el.get("prefix")
    print("namespace", part)
    namespace = NamespaceTextData()
    namespace.namespace_part = part
    namespace.namespace_full = f"{prefix}:{part}" if part else prefix
    for catalog_el in namespace_el.findall("catalog"):
        namespace.catalogs.append(_parse_catalog_data(filename, catalog_el))
    ## TODO - linked almanacs
    return namespace


def parse_almanac_data(filename, namespace_prefix) -> AlmanacTextData:
    """from a file"""
    almanac_data = AlmanacTextData()
    root_el = ET.parse(filename).getroot()
    for include_el in root_el.findall("include_almanac"):
        almanac_data.included_almanacs.append(
            _parse_included_almanac_data(include_el, filename, namespace_prefix)
        )
    for namespace in root_el.findall("namespace"):
        almanac_data.namespaces.append(_parse_namespace_data(filename, namespace, namespace_prefix))
    return almanac_data


def write_almanac_file(filename, namespace_prefix, catalog_paths, paths_relative=False):
    """Write a new almanac file, for a list of catalog directories."""
    if paths_relative:
        file_prefix = os.path.dirname(filename)

    root_namespace = NamespaceTextData()
    root_namespace.namespace_part = namespace_prefix

    for catalog_path in catalog_paths:
        catalog_data = CatalogTextData()
        abs_path = catalog_path
        if paths_relative:
            abs_path = os.path.join(file_prefix, catalog_path)
        metadata_keywords = _get_metadata_keywords(abs_path)
        catalog_name = metadata_keywords["catalog_name"]
        catalog_data.catalog_name = catalog_name
        if paths_relative:
            catalog_data.relative_path = catalog_path
        else:
            catalog_data.catalog_path = catalog_path
        catalog_data.catalog_type = metadata_keywords.get("catalog_type", "object")
        catalog_data.primary = metadata_keywords.get("primary_catalog", None)
        catalog_data.join = metadata_keywords.get("join_catalog", None)

        root_namespace.catalogs.append(catalog_data)

    root = ET.Element("almanac")

    root_ns = ET.SubElement(root, "namespace", prefix=root_namespace.namespace_part)

    for catalog in root_namespace.catalogs:
        catalog_el = ET.SubElement(
            root_ns,
            "catalog",
            name=catalog.catalog_name,
            type=catalog.catalog_type,
            path=catalog.catalog_path,
        )
        if catalog.primary:
            ET.SubElement(catalog_el, "primary").text = catalog.primary
        if catalog.join:
            ET.SubElement(catalog_el, "join").text = catalog.join

    tree = ElementTree(root)
    # ET.indent(tree, space="\t", level=0)
    tree.write(filename)
