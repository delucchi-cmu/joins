"""holder of single entry of catalog data"""


class CatalogData:
    """holder of single entry of catalog data"""

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
