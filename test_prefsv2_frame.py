"""
This is a small app that does nothing to test the preferences frame.
"""

import sys
import Tkinter as tk
from material_ui import MaterialAlertListSettings
from load import DEFAULT_THRESHOLDS, create_plugin_prefs, create_options_prefs
from pprint import pprint

this = sys.modules[__name__]  # For holding module globals

class Application(tk.Frame):
    """
    Test application.
    """

    def __init__(self, filters, master=None):
        tk.Frame.__init__(self, master, width=400, height=300)
        self.master = master
        self.filters = filters
        self.create_widgets()
        self.grid()
        master.protocol("WM_DELETE_WINDOW", self.exit)

    def create_widgets(self):
        self.prefsFrame = create_plugin_prefs(self, DEFAULT_THRESHOLDS, self.filters)
        self.prefsFrame.grid(column=0, row=0, sticky=tk.N+tk.S+tk.W)
        self.optionsFrame = create_options_prefs(self)
        self.optionsFrame.grid(column=1, row=0, sticky=tk.N+tk.S+tk.W+tk.E)


    def exit(self):
        try:
            print("Bye!")
            pprint(MaterialAlertListSettings.translate_to_settings(self.prefsFrame.get_material_filters()))
        finally:
            self.master.destroy()


TESTLIST = ['Sb>=-100.00',
             'As>=2.00',
             'Cd>=-100.00',
             'C>=-100.00',
             'Cr>=16.40',
             'Ge>=5.60',
             'Fe>=-100.00',
             'Mn>=-100.00',
             'Hg>=-100.00',
             'Mo>=-103.00',
             'Ni>=-100.00',
             'Nb>=-100.00',
             'P>=-100.00',
             'Po>=2.50',
             'Ru>=-100.00',
             'Se>=-100.00',
             'S>=-100.00',
             'Tc>=-100.00',
             'Te>=-100.00',
             'Sn>=-100.00',
             'W>=-100.00',
             'V>=-100.00',
             'Y>=-100.00',
             'Zn>=-100.00',
             'Zr>=-100.00',
             'Re>=-100.00',
             'Pb>=-100.00',
             'B>=-100.00']

TESTSETTINGS = MaterialAlertListSettings.translate_from_settings(TESTLIST)
# print "From test settings:"
# for filter in TESTSETTINGS:
#     pprint(filter.__str__())

ROOT = tk.Tk()
APP = Application(TESTSETTINGS, master=ROOT)
APP.mainloop()
