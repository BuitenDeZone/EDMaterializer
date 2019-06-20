"""
This is a small app that does nothing to test the preferences frame.
"""

import Tkinter as tk
from material_ui import MaterialAlertListSettingsFrame, MaterialAlertListSettings


class Application(tk.Frame):
    """
    Test application.
    """

    def __init__(self, test_settings, master=None):
        tk.Frame.__init__(self, master, width=400, height=300)
        self.master = master
        self.testSettings = test_settings
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        """Create widgets."""

        MaterialAlertListSettingsFrame(self, self.testSettings)


TESTLIST = ["As>=2.0", "Po>=2.5"]
TESTSETTINGS = MaterialAlertListSettings.translate_from_settings(TESTLIST)

ROOT = tk.Tk()
APP = Application(TESTSETTINGS, master=ROOT)
APP.mainloop()
