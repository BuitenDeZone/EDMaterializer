"""
This is a small app that does nothing to test the materials frame.
"""

import Tkinter as tk

# EDMC Theming
import theme

# Materializer plugin components
from material_ui import MaterialAlertListFrame
from material_ui import MaterialAlertListSettings
from material_api import MaterialMatch, Materials, Rarities
from load import update_alert_frame


class Application(tk.Frame):
    """
    Test application.
    """

    def __init__(self, master=None):
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
        self.materialList = MaterialAlertListFrame(self)


MATCHES = [MaterialMatch(Materials.ARSENIC, 2.3415), MaterialMatch(Materials.IRON, 20.33)]

def add_matches_1():
    """Add test matches."""
    APP.materialList.add_matches("1", MATCHES)

def add_matches_2():
    """Add test matches."""
    APP.materialList.add_matches("4 b", MATCHES)

def add_matches_3():
    """Add test matches."""
    APP.materialList.add_matches("2 b", MATCHES)

def add_matches_4():
    """Add test matches."""
    APP.materialList.add_matches("2", MATCHES)


TEST_SYSTEM = "Irk"
TEST_MATERIAL_VERY_COMMON_1 = Materials.CARBON
TEST_MATERIAL_VERY_COMMON_2 = Materials.SULPHUR
TEST_MATERIAL_COMMON_1 = Materials.VANADIUM
TEST_MATERIAL_COMMON_2 = Materials.ARSENIC
TEST_MATERIAL_RARE = Materials.CADMIUM
TEST_MATERIAL_VERY_RARE = Materials.POLONIUM

RULES = {
    "C>=10.00", "As>=0.00"
}

TEST_SETS = {
    'Irk 1': [
        {
            "Name": TEST_MATERIAL_VERY_COMMON_1.name.lower(),
            "Percent": 19.242706
        },
        {
            "Name": TEST_MATERIAL_VERY_COMMON_2.name.lower(),
            "Percent": 17.019758
        },
        {
            "Name": TEST_MATERIAL_COMMON_2.name.lower(),
            "Percent": 7.028986
        },
        {
            "Name": TEST_MATERIAL_VERY_RARE.name.lower(),
            "Percent": 1.47208
        }
    ],
    'Irk 2 B': [
        {
            "Name": TEST_MATERIAL_VERY_COMMON_2.name.lower(),
            "Percent": 17.019758
        },
        {
            "Name": TEST_MATERIAL_COMMON_1.name.lower(),
            "Percent": 7.028986
        },
        {
            "Name": TEST_MATERIAL_RARE.name.lower(),
            "Percent": 1.47208
        }
    ],
    'Irk 8 C 3': [
        {
            "Name": TEST_MATERIAL_VERY_COMMON_1.name.lower(),
            "Percent": 7.028986
        },
        {
            "Name": TEST_MATERIAL_VERY_COMMON_2.name.lower(),
            "Percent": 7.028986
        },
        {
            "Name": TEST_MATERIAL_COMMON_1.name.lower(),
            "Percent": 7.028986
        },
        {
            "Name": TEST_MATERIAL_COMMON_2.name.lower(),
            "Percent": 7.028986
        },
        {
            "Name": TEST_MATERIAL_RARE.name.lower(),
            "Percent": 7.028986
        },
        {
            "Name": TEST_MATERIAL_VERY_RARE.name.lower(),
            "Percent": 7.028986
        }
    ]
}

TEST_FILTERS = MaterialAlertListSettings.translate_from_settings(RULES)

def update_materials():
    for planet, materials in TEST_SETS.items():
        update_alert_frame(APP.materialList, TEST_SYSTEM, planet, materials, TEST_FILTERS)


ROOT = tk.Tk()
APP = Application(master=ROOT)
APP.after(1000, update_materials)
#APP.after(2000, add_matches_2)
#APP.after(3000, add_matches_3)
#APP.after(4000, add_matches_4)
APP.mainloop()
