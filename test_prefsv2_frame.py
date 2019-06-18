"""
This is a small app that does nothing to test the preferences frame.
"""

import Tkinter as tk
from material_ui import MaterialAlertsListPreferencesFrame, MaterialAlertListSettings


class Application(tk.Frame):
    """
    Test application.
    """

    def __init__(self, testSettings, master=None):
        tk.Frame.__init__(self, master, width=400, height=300)
        self.master = master
        self.testSettings = testSettings
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        """Create widgets."""

        MaterialAlertsListPreferencesFrame(self, self.testSettings)


TESTLIST = ["As>=2.0", "Po>=2.5"]
TESTSETTINGS = MaterialAlertListSettings.translate_from_settings(TESTLIST)

ROOT = tk.Tk()
APP = Application(TESTSETTINGS, master=ROOT)
APP.mainloop()
