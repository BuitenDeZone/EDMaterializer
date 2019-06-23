"""This is a small app that does nothing to test the materials frame."""

import Tkinter as tk
import os
import json
from pprint import pformat

# EDMC Theming
import theme

# Materializer plugin components
from material_ui import MaterialFilterMatchesFrame
from material_ui import MaterialFilterListConfigTranslator
from material_api import MaterialMatch, Materials
from material_api import LOGGER, LOG_DEBUG


class Application(tk.Frame):
    """Test application."""

    def __init__(self, master=None):
        """Initialize the app."""

        tk.Frame.__init__(self, master, width=400, height=300)
        theme.theme._colors(self, 1)  # pylint: disable=protected-access
        self.master = master
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        """Create widgets."""

        self.testFrame = tk.Frame(self)
        self.testFrame.grid(column=0, row=1)
        self.testFrame.config(background="blue")
        self.lblTest = tk.Label(self.testFrame, text="TESTING")
        self.lblTest.grid()
        self.materialList = MaterialFilterMatchesFrame(self)


MATCHES = [MaterialMatch(Materials.ARSENIC, 2.3415), MaterialMatch(Materials.IRON, 20.33)]


def add_matches_1():
    """Add test matches."""
    APP.materialList._add_matches("1", MATCHES)  # pylint: disable=protected-access


def add_matches_2():
    """Add test matches."""
    APP.materialList._add_matches("4 b", MATCHES)  # pylint: disable=protected-access


def add_matches_3():
    """Add test matches."""
    APP.materialList._add_matches("2 b", MATCHES)  # pylint: disable=protected-access


def add_matches_4():
    """Add test matches."""
    APP.materialList._add_matches("2", MATCHES)  # pylint: disable=protected-access


TEST_SYSTEM = "Irk"
TEST_MATERIAL_VERY_COMMON_1 = Materials.CARBON
TEST_MATERIAL_VERY_COMMON_2 = Materials.SULPHUR
TEST_MATERIAL_COMMON_1 = Materials.VANADIUM
TEST_MATERIAL_COMMON_2 = Materials.ARSENIC
TEST_MATERIAL_RARE = Materials.CADMIUM
TEST_MATERIAL_VERY_RARE = Materials.POLONIUM


TEST_SETS = {
    'Irk 1': [
        {
            "Name": TEST_MATERIAL_VERY_COMMON_1.name.lower(),
            "Percent": 19.242706,
        },
        {
            "Name": TEST_MATERIAL_VERY_COMMON_2.name.lower(),
            "Percent": 17.019758,
        },
        {
            "Name": TEST_MATERIAL_COMMON_2.name.lower(),
            "Percent": 7.028986,
        },
        {
            "Name": TEST_MATERIAL_VERY_RARE.name.lower(),
            "Percent": 1.47208,
        },
    ],
    'Irk 2 B': [
        {
            "Name": TEST_MATERIAL_VERY_COMMON_2.name.lower(),
            "Percent": 17.019758,
        },
        {
            "Name": TEST_MATERIAL_COMMON_1.name.lower(),
            "Percent": 7.028986,
        },
        {
            "Name": TEST_MATERIAL_RARE.name.lower(),
            "Percent": 1.47208,
        },
    ],
    'Irk 8 C 3': [
        {
            "Name": TEST_MATERIAL_VERY_COMMON_1.name.lower(),
            "Percent": 7.028986,
        },
        {
            "Name": TEST_MATERIAL_VERY_COMMON_2.name.lower(),
            "Percent": 7.028986,
        },
        {
            "Name": TEST_MATERIAL_COMMON_1.name.lower(),
            "Percent": 7.028986,
        },
        {
            "Name": TEST_MATERIAL_COMMON_2.name.lower(),
            "Percent": 7.028986,
        },
        {
            "Name": TEST_MATERIAL_RARE.name.lower(),
            "Percent": 7.028986,
        },
        {
            "Name": TEST_MATERIAL_VERY_RARE.name.lower(),
            "Percent": 7.028986,
        },
    ],
}

RULES = {
    "{symbol}>={threshold}".format(symbol=TEST_MATERIAL_VERY_COMMON_1.symbol, threshold="5.00"),
    "{symbol}>={threshold}".format(symbol=TEST_MATERIAL_COMMON_2.symbol, threshold="0.00"),
}

TEST_FILTERS = MaterialFilterListConfigTranslator.translate_from_settings(RULES)


def update_materials():
    """Add test data through update_matches_frame."""

    for planet, materials in TEST_SETS.items():
        LOGGER.debug(None, "Going through test set {planet}".format(planet=planet))
        APP.materialList.process_filter_planet_materials(TEST_SYSTEM, planet, materials)


def update_materials_hash():
    """Update materials by sending through a hash."""

    materials = {
        TEST_MATERIAL_COMMON_2.name: 12.0,
    }
    APP.materialList.process_filter_planet_materials(TEST_SYSTEM, 'Irk 5', materials)


def update_filters():
    """Configure the test filters."""

    LOGGER.debug(None, "Update filters")
    APP.materialList.update_filters(TEST_FILTERS)


def clear_system():
    """Jump to system None."""

    APP.materialList.jump_system(None)


def scan_edsm_bodies_for_matches(system, bodies):
    """Scan materials to the material matches frame."""

    for body in bodies:
        LOGGER.info(APP, "BODY: {name} -> {dump}".format(name=body["name"], dump=pformat(body)))
        planet = body["name"]
        materials = body.get("materials", None)
        APP.materialList.process_filter_planet_materials(system, planet, materials)


def update_by_json():
    """Simulate an update by receiving a edsm result."""
    clear_system()

    if JSON_RESPONSE.get('bodies', None):
        scan_edsm_bodies_for_matches(JSON_RESPONSE['name'], JSON_RESPONSE['bodies'])


with open(os.path.sep.join(['fixtures', 'edsm-system-body-sol.json']), 'r') as f:
    JSON_RESPONSE = json.load(f)


LOGGER.logLevel = LOG_DEBUG

ROOT = tk.Tk()
APP = Application(master=ROOT)

# Basic ui tests:
# APP.after(1000, add_matches_1)
# APP.after(2000, add_matches_2)
# APP.after(3000, add_matches_3)
# APP.after(4000, add_matches_4)

# Dynamic Filter updates:
APP.after(1000, update_filters)
APP.after(2000, update_materials)
# Clear system
APP.after(5000, clear_system)
# Parse materials by hash
APP.after(6000, update_materials_hash)
APP.after(8000, update_by_json)

APP.mainloop()
