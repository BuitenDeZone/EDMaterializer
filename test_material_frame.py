"""
This is a small app that does nothing to test the materials frame.
"""

import Tkinter as tk

# EDMC Theming
import theme

# Materializer plugin components
from material_ui import MaterialAlertListFrame
from material_api import MaterialMatch, Materials


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

def add_matches():
    """Add test matches."""

    matches = [MaterialMatch(Materials.ARSENIC, 2.3415), MaterialMatch(Materials.IRON, 20.33)]
    APP.materialList.add_matches("1", matches)



ROOT = tk.Tk()
APP = Application(master=ROOT)
APP.after(1000, add_matches)
APP.mainloop()
