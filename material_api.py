"""Helpers/Object Model for the Materializer plugin."""

from __future__ import print_function
import inspect


LOG_ERROR = 2
LOG_WARN = 3
LOG_INFO = 4
LOG_DEBUG = 5

LOG_OUTPUT = {
    1: "CRITICAL",
    2: "ERROR",
    3: "WARNING",
    4: "INFO",
    5: "DEBUG",
    0: "UNKNOWN",
}

FIELD_NAME = "Name"
FIELD_PERCENT = "Percent"

FIELD_EVENT = "event"
FIELD_STAR_SYSTEM = "StarSystem"
FIELD_SYSTEM_ADDRESS = "SystemAddress"
FIELD_SCAN_TYPE = "ScanType"
FIELD_BODY_NAME = "BodyName"
FIELD_LANDABLE = "Landable"
FIELD_MATERIALS = "Materials"

VALUE_EVENT_FSS_DISCOVERY_SCAN = "FSSDiscoveryScan"
VALUE_EVENT_FSDJUMP = "FSDJump"
VALUE_EVENT_SCAN = "Scan"
VALUE_SCAN_TYPE_DETAILED = "Detailed"


class Logger(object):
    """Represent a logger."""

    def __init__(self, log_level=LOG_INFO, log_prefix=''):
        """Initialize the logger."""

        self.logLevel = log_level
        self.logPrefix = log_prefix

    def debug(self, caller, message):
        """Write a debug message for a caller."""
        self.log(caller, LOG_DEBUG, message)

    def info(self, caller, message):
        """Write a info message for a caller."""
        self.log(caller, LOG_INFO, message)

    def warn(self, caller, message):
        """Write a warn message for a caller."""
        self.log(caller, LOG_WARN, message)

    def error(self, caller, message):
        """Write a error message for a caller."""
        self.log(caller, LOG_ERROR, message)

    def log(self, caller, level, message):
        """Log a message for a caller."""

        log_level = self.logLevel
        log_prefix = self.logPrefix
        if hasattr(caller, 'logLevel') and caller.logLevel is not None:
            log_level = caller.logLevel
        if hasattr(caller, 'logPrefix') and caller.logPrefix is not None:
            log_prefix = caller.logPrefix

        if isinstance(level, str):
            from_output = 0
            print_level = level
            for key, value in LOG_OUTPUT.items():
                if level.upper() == value:
                    from_output = key
                    print_level = LOG_OUTPUT.get(from_output)

            level = from_output
        else:
            print_level = LOG_OUTPUT.get(level, 'UNKNOWN')

        if level <= log_level:
            print("{prefix}{level}: {message}".format(prefix=log_prefix, level=print_level, message=message))


LOGGER = Logger()


class MaterialFilter(object):
    """Represents a filter on a certain material based on a threshold."""

    def __init__(self, material, threshold, enabled=True):
        """Create a new `MaterialFilter`.

        :param material: The material we will be matching against.
        :param threshold: Minimum value before we match.
        :param enabled: Enable or disable this rule.
        """
        self.material = material
        self.threshold = threshold
        self.enabled = enabled

    def __str__(self):
        """Return a string representation."""

        if self.enabled:
            return "{m} >= {v}".format(m=self.material.name, v=self.threshold)

        return "{m} >= {v} (disabled)".format(m=self.material.name, v=self.threshold)

    def __eq__(self, other):
        """
        Check if we are equal to another object.

        MaterialFilters are considered equal when they have all the same attribute values.
        :param other: object to test against
        :return: `True` if all attributes of both objects match. `False` in all other cases.
        """

        if not isinstance(other, MaterialFilter):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return other.material == self.material and other.threshold == self.threshold and other.enabled == self.enabled

    def check_matches(self, materials):
        """
        Check if any materials in the list are a match for our threshold.

        :param materials: list of material dicts with a Name and Percent field.
        :return: returns a MaterialMatch or an empty list.
        """
        if self.enabled:
            for material_raw in materials:
                material = Materials.by_name(material_raw[FIELD_NAME])
                percent = material_raw[FIELD_PERCENT]
                if self.material == material and percent >= self.threshold:
                    return MaterialMatch(material, percent)

        return None


class MaterialMatch(object):
    """Represents a match for a material and a threshold."""

    def __init__(self, material, percent):
        """Create a new `MaterialMatch`.

        :param material: `Material` that has matched.
        :param percent: percentage the matched material on a planet.
        """

        self.material = material
        self.percent = percent


class Rarity(object):
    """Represents a certain rarity for materials."""

    def __init__(self, rarity_id, desc, label_color):
        """Create a new rarity.

        :param rarity_id: Unique id for the rarity.
        :param desc: Description.
        :param label_color: Color representation.
        """
        self.rarityId = rarity_id
        self.description = desc
        self.labelColor = label_color

    def __str__(self):
        """Return a string representation of the `Rarity`: its description."""

        return self.description

    def __eq__(self, other):
        """Check if we are equel to an object or not.

        `Rarity`s are considered equal if the rarityId matches.
        """
        if not isinstance(other, Rarity):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.rarityId == other.rarityId


class Rarities(object):
    """Different types of Rarity grades."""

    VERY_COMMON = Rarity(1, 'Very Common', '#5bc0de')
    COMMON = Rarity(2, 'Common', '#62c462')
    RARE = Rarity(3, 'Rare', '#f89406')
    VERY_RARE = Rarity(4, 'Very Rare', '#ee5f5b')


class Material(object):
    """A Material."""

    def __init__(self, name, material_id, symbol, rarity):
        """
        Create a new material.

        :param name: Full name of the material
        :param material_id: Unique id
        :param symbol: Short symbol representation
        :param rarity: `Rarity` grade
        """

        self.name = name
        self.materialId = material_id
        self.symbol = symbol
        self.rarity = rarity

    def __str__(self):
        """Return the string representation: the name."""

        return self.name

    def __eq__(self, other):
        """Check if we are equel to an object or not.

        `Material`s are considered equal if they have the same materialId.
        """

        if not isinstance(other, Material):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.materialId == other.materialId


class Materials(object):
    """List of known planetary materials."""

    # pylint: disable=bad-whitespace
    ANTIMONY    = Material('Antimony', 1, 'Sb', Rarities.VERY_RARE)  # noqa: E221
    ARSENIC     = Material('Arsenic', 2, 'As', Rarities.COMMON)  # noqa: E221
    CADMIUM     = Material('Cadmium', 3, 'Cd', Rarities.RARE)  # noqa: E221
    CARBON      = Material('Carbon', 4, 'C', Rarities.VERY_COMMON)  # noqa: E221
    CHROMIUM    = Material('Chromium', 5, 'Cr', Rarities.COMMON)  # noqa: E221
    GERMANIUM   = Material('Germanium', 6, 'Ge', Rarities.COMMON)  # noqa: E221
    IRON        = Material('Iron', 7, 'Fe', Rarities.VERY_COMMON)  # noqa: E221
    MANGANESE   = Material('Manganese', 8, 'Mn', Rarities.COMMON)  # noqa: E221
    MERCURY     = Material('Mercury', 9, 'Hg', Rarities.RARE)  # noqa: E221
    MOLYBDENUM  = Material('Molybdenum', 10, 'Mo', Rarities.RARE)  # noqa: E221
    NICKEL      = Material('Nickel', 11, 'Ni', Rarities.VERY_COMMON)  # noqa: E221
    NIOBIUM     = Material('Niobium', 12, 'Nb', Rarities.RARE)  # noqa: E221
    PHOSPHORUS  = Material('Phosphorus', 13, 'P', Rarities.VERY_COMMON)  # noqa: E221
    POLONIUM    = Material('Polonium', 14, 'Po', Rarities.VERY_RARE)  # noqa: E221
    RUTHENIUM   = Material('Ruthenium', 15, 'Ru', Rarities.VERY_RARE)  # noqa: E221
    SELENIUM    = Material('Selenium', 16, 'Se', Rarities.COMMON)  # noqa: E221
    SULPHUR     = Material('Sulphur', 17, 'S', Rarities.VERY_COMMON)  # noqa: E221
    TECHNETIUM  = Material('Technetium', 18, 'Tc', Rarities.VERY_RARE)  # noqa: E221
    TELLURIUM   = Material('Tellurium', 19, 'Te', Rarities.VERY_RARE)  # noqa: E221
    TIN         = Material('Tin', 20, 'Sn', Rarities.RARE)  # noqa: E221
    TUNGSTEN    = Material('Tungsten', 21, 'W', Rarities.RARE)  # noqa: E221
    VANADIUM    = Material('Vanadium', 22, 'V', Rarities.COMMON)  # noqa: E221
    YTTRIUM     = Material('Yttrium', 23, 'Y', Rarities.VERY_RARE)  # noqa: E221
    ZINC        = Material('Zinc', 24, 'Zn', Rarities.COMMON)  # noqa: E221
    ZIRCONIUM   = Material('Zirconium', 25, 'Zr', Rarities.COMMON)  # noqa: E221
    RHENIUM     = Material('Rhenium', 26, 'Re', Rarities.VERY_COMMON)  # noqa: E221
    LEAD        = Material('Lead', 27, 'Pb', Rarities.VERY_COMMON)  # noqa: E221
    BORON       = Material('Boron', 28, 'B', Rarities.COMMON)  # noqa: E221
    # pylint: enable=bad-whitespace

    @classmethod
    def by_rarity(cls, rarity):
        """
        Return a list of materials based on `Rarity`.

        :param rarity: Wanted Rarity
        :return: list with `Material`s
        """

        return [material for material in cls.items() if material.rarity == rarity]

    @classmethod
    def by_name(cls, name):
        """
        Find a material by its name (case-insensitive).

        :param name: Name to look for.
        :return: Found `Material` or `None`
        """

        for i in cls.items():
            if str(i.name).lower() == str(name).lower():
                return i
        return None

    @classmethod
    def by_symbol(cls, symbol):
        """
        Find a material by its symbol (case-insensitive).

        :param symbol: Symbol to look for
        :return: Found `Material` or `None`
        """

        for i in cls.items():
            if str(i.symbol).lower() == str(symbol).lower():
                return i
        return None

    @classmethod
    def by_id(cls, material_id):
        """
        Find a material by it's ID.

        :param material_id: `Materials.elementId` to look for.
        :return: Found `Material` or `None`
        """

        for material in cls.items():
            if material.material_id == material_id:
                return material
        return None

    @classmethod
    def items(cls):
        """
        List all materials.

        :return: List of all known `Material`s
        """

        return [x[1] for x in inspect.getmembers(cls) if isinstance(x[1], Material)]

    @classmethod
    def item_names(cls):
        """
        List all materials by their name.

        :return: All material names.
        """

        return [x.name for x in cls.items()]
