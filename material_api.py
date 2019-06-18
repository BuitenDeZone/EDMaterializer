"""
Helpers for the Materializer plugin.
"""

import inspect

FIELD_NAME = "Name"
FIELD_PERCENT = "Percent"

FIELD_EVENT = "event"
FIELD_STAR_SYSTEM = "StarSystem"
FIELD_SYSTEM_ADDRESS = "SystemAddress"
FIELD_SCAN_TYPE = "ScanType"
FIELD_BODY_NAME = "BodyName"
FIELD_LANDABLE = "Landable"
FIELD_MATERIALS = "Materials"

VALUE_EVENT_FSDJUMP = "FSDJump"
VALUE_EVENT_SCAN = "Scan"
VALUE_SCAN_TYPE_DETAILED = "Detailed"


class MaterialAlert(object):
    """
    Represents a alert on a certain material based on a threshold.
    """

    def __init__(self, material, threshold):
        self.material = material
        self.threshold = threshold

    def __str__(self):
        return "{m} >= {v}".format(m=self.material.name, v=self.threshold)

    def check_matches(self, materials):
        """
        Check if any materials in the list are a match for our threshold.
        :param materials: list of material dicts with a Name and Percent field.
        :return: returns a MaterialMatch or an empty list.
        """

        for material_raw in materials:
            material = Materials.by_name(material_raw[FIELD_NAME])
            percent = material_raw[FIELD_PERCENT]
            if self.material == material and percent >= self.threshold:
                return MaterialMatch(material, percent)

        return None


class MaterialMatch(object):
    """
    Represents a match for a material and a threshold.
    """

    def __init__(self, material, percent):
        self.material = material
        self.percent = percent


class Rarity(object):
    """
    Represents a certain rarity for materials.
    """

    def __init__(self, rarity_id, desc, label_color):
        self.rarityId = rarity_id
        self.description = desc
        self.labelColor = label_color

    def __str__(self):
        return self.description

    def __eq__(self, other):
        if not isinstance(other, Rarity):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.rarityId == other.rarityId


class Rarities(object):
    """
    Different types of Rarity grades.
    """

    VERY_COMMON = Rarity(1, 'Very Common', '#5bc0de')
    COMMON = Rarity(2, 'Common', '#62c462')
    RARE = Rarity(3, 'Rare', '#f89406')
    VERY_RARE = Rarity(4, 'Very Rare', '#ee5f5b')


class Material(object):
    """
    Represents a Material.
    """

    def __init__(self, name, material_id, symbol, rarity):
        self.name = name
        self.materialId = material_id
        self.symbol = symbol
        self.rarity = rarity

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, Material):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.materialId == other.materialId


class Materials(object):
    """
    List of known planetary materials.
    """

    # pylint: disable=bad-whitespace
    ANTIMONY    = Material('Antimony', 1, 'Sb', Rarities.VERY_RARE)
    ARSENIC     = Material('Arsenic', 2, 'As', Rarities.COMMON)
    CADMIUM     = Material('Cadmium', 3, 'Cd', Rarities.RARE)
    CARBON      = Material('Carbon', 4, 'C', Rarities.VERY_COMMON)
    CHROMIUM    = Material('Chromium', 5, 'Cr', Rarities.COMMON)
    GERMANIUM   = Material('Germanium', 6, 'Ge', Rarities.COMMON)
    IRON        = Material('Iron', 7, 'Fe', Rarities.VERY_COMMON)
    MANGANESE   = Material('Manganese', 8, 'Mn', Rarities.COMMON)
    MERCURY     = Material('Mercury', 9, 'Hg', Rarities.RARE)
    MOLYBDENUM  = Material('Molybdenum', 10, 'Mo', Rarities.RARE)
    NICKEL      = Material('Nickel', 11, 'Ni', Rarities.VERY_COMMON)
    NIOBIUM     = Material('Niobium', 12, 'Nb', Rarities.RARE)
    PHOSPHORUS  = Material('Phosphorus', 13, 'P', Rarities.VERY_COMMON)
    POLONIUM    = Material('Polonium', 14, 'Po', Rarities.VERY_RARE)
    RUTHENIUM   = Material('Ruthenium', 15, 'Ru', Rarities.VERY_RARE)
    SELENIUM    = Material('Selenium', 16, 'Se', Rarities.COMMON)
    SULPHUR     = Material('Sulphur', 17, 'S', Rarities.VERY_COMMON)
    TECHNETIUM  = Material('Technetium', 18, 'Tc', Rarities.VERY_RARE)
    TELLURIUM   = Material('Tellurium', 19, 'Te', Rarities.VERY_RARE)
    TIN         = Material('Tin', 20, 'Sn', Rarities.RARE)
    TUNGSTEN    = Material('Tungsten', 21, 'W', Rarities.RARE)
    VANADIUM    = Material('Vanadium', 22, 'V', Rarities.COMMON)
    YTTRIUM     = Material('Yttrium', 23, 'Y', Rarities.VERY_RARE)
    ZINC        = Material('Zinc', 24, 'Zn', Rarities.COMMON)
    ZIRCONIUM   = Material('Zirconium', 25, 'Zr', Rarities.COMMON)
    RHENIUM     = Material('Rhenium', 26, 'Re', Rarities.VERY_COMMON)
    LEAD        = Material('Lead', 27, 'Pb', Rarities.VERY_COMMON)
    BORON       = Material('Boron', 28, 'B', Rarities.COMMON)
    # pylint: enable=bad-whitespace


    @classmethod
    def by_rarity(cls, rarity):
        return [material for material in cls.items() if material.rarity == rarity]

    @classmethod
    def by_name(cls, item):
        """Find a material by its name (case-insensitive)"""

        for i in cls.items():
            if str(i.name).lower() == str(item).lower():
                return i
        return None

    @classmethod
    def by_symbol(cls, symbol):
        """Find a material by its symbol (case-insensitive)"""

        for i in cls.items():
            if str(i.symbol).lower() == str(symbol).lower():
                return i
        return None

    @classmethod
    def by_id(cls, material_id):
        """Find a material by it's ID"""

        for material in cls.items():
            if material.material_id == material_id:
                return material
        return None

    @classmethod
    def items(cls):
        """List all materials"""

        return [x[1] for x in inspect.getmembers(cls) if isinstance(x[1], Material)]

    @classmethod
    def item_names(cls):
        """List all materials by their name"""

        return [x.name for x in cls.items()]
