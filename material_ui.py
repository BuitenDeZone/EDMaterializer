"""
Graphical components for the Materializer plugin.
"""

import Tkinter as tk
import ttk
import tkFont

# EDMC components
import myNotebook as nb
from l10n import Locale
from theme import theme

# Own materializer stuff
from material_api import MaterialAlert, Materials


class MaterialAlertListFrame(tk.Frame):
    """
    A tk frame which displays matching material alerts.
    """

    def __init__(self, master, **kw):

        tk.Frame.__init__(self, master, **kw)

        self.containerFrame = None
        self.planetMatches = dict()
        self.initialize_frame()
        self.grid()

    def initialize_frame(self):
        """
        Initialize the frame.
        """

        if self.containerFrame is None:
            self.containerFrame = tk.Frame(self)
            self.containerFrame.grid()

    def clear_matches(self):
        """
        Clears the frame with matches.
        """
        self.planetMatches = dict()
        self.draw_matches()
        self.containerFrame.configure(background=theme.current['background'])

    def add_matches(self, planet, matches):
        """
        Add a planet with matches to the frame.
        """

        self.planetMatches[planet] = matches
        self.draw_matches()

    def draw_matches(self):

        if self.containerFrame is not None:
            self.containerFrame.grid_forget()
            self.containerFrame.destroy()
            self.containerFrame = None

        # Copy the color configuration from the EDMC theme.
        self.initialize_frame()
        current_row = 0
        for planet in sorted(self.planetMatches):
            matches = self.planetMatches[planet]

            planet_text = "{}:".format(planet)
            label_planet = tk.Label(self.containerFrame, text=planet_text)
            label_planet.configure(
                foreground=theme.current['foreground'],
                background=theme.current['background'],
                activeforeground=theme.current['activeforeground'],
                activebackground=theme.current['activebackground'],
                disabledforeground=theme.current['disabledforeground'],
                font=tkFont.Font(family='Euro Caps', size=9, weight=tkFont.BOLD)
            )
            label_planet.grid(column=0, row=current_row, sticky=tk.E)

            frame_matches = tk.Frame(self.containerFrame)
            frame_matches.configure(background=theme.current['background'])
            frame_matches.grid(column=1, row=current_row, sticky=tk.W)

            for match in matches:
                match_text = "{}: {}%".format(match.material.symbol, Locale.stringFromNumber(match.percent, 1))
                label_color = match.material.rarity.labelColor
                label_match = tk.Label(frame_matches, text=match_text)
                label_match.config(
                    activebackground=label_color, background=label_color,
                    activeforeground="#ffffff", foreground="#ffffff",
                    padx=0, pady=1,
                    borderwidth=1, relief=tk.RIDGE
                )
                label_match.pack(side=tk.LEFT, padx=2, pady=1)

            current_row = current_row + 1
        self.containerFrame.configure(background=theme.current['background'])
        self.containerFrame.grid()


class MaterialAlertListSettings(object):
    """
    Helper class to translate from settings to a list with material alerts.
    """

    @classmethod
    def translate_from_settings(cls, materials):
        """
        Reads a list with Symbol>=Threshold and parses it into proper MaterialAlert objects.
        :param materials: list with material and threshold.
        :return: list of MaterialAlert objects.
        """

        if materials is None:
            return list()

        alerts = list()
        for mat in materials:
            key, threshold = mat.split('>=')
            material = Materials.by_symbol(key)
            if material is None:
                print "ERROR: Unknown material with symbol '{}'. Skipping.".format(key)
            else:
                alert = MaterialAlert(material, Locale.numberFromString(threshold))
                alerts.append(alert)

        return alerts

    @classmethod
    def translate_to_settings(cls, alerts):
        """
        Convert a list of MaterialAlerts into a string only list to store in settings.
        :param alerts: list of MaterialAlert objects.
        :return: list of string representations of MaterialAlerts.
        """

        if alerts is None:
            return list()

        return list("{}>={}".format(a.material.symbol, Locale.stringFromNumber(a.threshold, 2)) for a in alerts)


class MaterialAlertListSettingsFrame(nb.Frame):
    """
    Creates a frame to manage the Material Alert List.
    """

    def __init__(self, master, material_alerts_list=None, **kw):

        nb.Frame.__init__(self, master, **kw)

        if material_alerts_list is None:
            material_alerts_list = []

        self.selectedAlert = None
        self.isNewAlert = False
        self.materialAlertsList = material_alerts_list

        self.create_widgets()
        self.grid()

        for value in [m.__str__() for m in self.materialAlertsList]:
            self.listboxAlert.insert(tk.END, value)

    def create_widgets(self):
        """
        Create and initialize all the tk widgets.
        """

        default_pad_x = 10
        default_pad_y = 2

        # ListBox + Scrollbar.
        self.listFrame = tk.Frame(self)  # pylint: disable=
        self.scrollbarListboxAlert = tk.Scrollbar(self.listFrame)
        self.scrollbarListboxAlert.pack(side=tk.RIGHT, fill=tk.Y)
        self.listboxAlert = tk.Listbox(self.listFrame)
        self.listboxAlert.pack(fill=tk.BOTH, expand=True)
        self.listboxAlert.config(yscrollcommand=self.scrollbarListboxAlert.set)
        self.scrollbarListboxAlert.config(command=self.listboxAlert.yview)

        # Buttons
        self.addButton = nb.Button(self, text="Add")
        self.delButton = nb.Button(self, text="Del")
        self.saveButton = nb.Button(self, text="Save")

        # Labels
        self.labelAlerts = nb.Label(self, text="Configured alerts:")
        self.labelMaterial = nb.Label(self, text='Material:')
        self.labelThreshold = nb.Label(self, text='Threshold:')
        self.labelGreater = nb.Label(self, text='>=')

        self.labelWarnings = nb.Label(self, text='')
        self.labelWarnings.config(foreground="red", wraplength=225, justify=tk.LEFT)

        # Entries
        self.comboboxMaterial = ttk.Combobox(self, values=list(Materials.item_names()))
        self.entryThreshold = nb.Entry(self, justify=tk.RIGHT)

        # |                        |
        # |    ,---.,   .,---..   .|---
        # |    ,---||   ||   ||   ||
        # `---'`---^`---|`---'`---'`---'
        #           `---'
        # Left Side
        self.labelAlerts.grid(column=0, row=0, columnspan=3, sticky=tk.W,
                              padx=default_pad_x, pady=default_pad_y)

        self.listFrame.grid(column=0, row=1, rowspan=5, columnspan=3, sticky=tk.N + tk.E + tk.S + tk.W,
                            padx=default_pad_x, pady=default_pad_y)

        self.addButton.grid(column=0, row=6, padx=default_pad_x, pady=default_pad_y)
        self.delButton.grid(column=2, row=6, padx=default_pad_x, pady=default_pad_y)

        # Right side
        self.labelMaterial.grid(column=3, row=1, padx=default_pad_x, pady=default_pad_y)
        self.labelGreater.grid(column=4, row=2, padx=default_pad_x, sticky=tk.E)
        self.labelThreshold.grid(column=3, row=3, padx=default_pad_x, pady=default_pad_y)

        self.comboboxMaterial.grid(column=4, row=1, padx=default_pad_x, pady=default_pad_y, sticky=tk.E + tk.W)
        self.entryThreshold.grid(column=4, row=3, padx=default_pad_x, pady=default_pad_y, sticky=tk.E + tk.W)

        self.saveButton.grid(column=4, row=4, sticky=tk.N + tk.E, padx=default_pad_x, pady=default_pad_y)
        self.labelWarnings.grid(column=3, row=5, columnspan=2, sticky=tk.N + tk.W)
        self.rowconfigure(5, weight=1)

        # ,---.                |
        # |--- .    ,,---.,---.|--- ,---.
        # |     \  / |---'|   ||    `---.
        # `---'  `'  `---'`   '`---'`---'
        self.listboxAlert.bind('<<ListboxSelect>>', self.select_alert)
        self.saveButton.bind('<Button-1>', self.clicked_save_button)
        self.delButton.bind('<Button-1>', self.clicked_delete_button)
        self.addButton.bind('<Button-1>', self.clicked_add_button)

        # Default entry/button state.
        self.enable_disable_buttons()
        self.update_entry_fields()

    def validate_entries(self):
        """
        Validates if the entry fields have correct values.
        """

        all_ok = True
        self.labelWarnings.config(text='')
        warnings_texts = []

        if Materials.by_name(self.comboboxMaterial.get()) is None:
            all_ok = False
            warnings_texts.append('* Unknown material selected.')

        threshold = Locale.numberFromString(self.entryThreshold.get())
        if threshold is None or threshold < 0 or threshold > 100:
            all_ok = False
            warnings_texts.append('* Threshold must be a number >= 0 and <= 100.')

        if all_ok is False:
            warnings_texts.insert(0, 'Input Errors:')

        self.labelWarnings.config(text='\n'.join(warnings_texts))
        return all_ok

    def enable_disable_buttons(self):
        """
        Enables and disables the buttons based on which state we are in.
        """

        if self.isNewAlert:
            self.delButton.config(state=tk.DISABLED)
            self.addButton.config(state=tk.DISABLED)
            self.saveButton.config(state=tk.NORMAL)

        elif self.selectedAlert is None:
            self.addButton.config(state=tk.NORMAL)
            self.saveButton.config(state=tk.DISABLED)
            self.delButton.config(state=tk.DISABLED)
        else:
            self.addButton.config(state=tk.NORMAL)
            self.saveButton.config(state=tk.NORMAL)
            self.delButton.config(state=tk.NORMAL)

    def update_entry_fields(self):
        """
        Update entry fields values and status.
        """

        if self.selectedAlert is not None or self.isNewAlert is True:
            self.comboboxMaterial.config(state=tk.NORMAL)
            self.entryThreshold.config(state=tk.NORMAL)
        else:
            self.comboboxMaterial.config(state=tk.DISABLED)
            self.entryThreshold.config(state=tk.DISABLED)

        if self.selectedAlert is None:
            self.comboboxMaterial.set('')
            self.entryThreshold.config(state=tk.NORMAL)  # Enable for clearing purposes.
            self.entryThreshold.delete(0, tk.END)
            if not self.isNewAlert:
                self.entryThreshold.config(state=tk.DISABLED)  # Disable if its not a new alert we are creating

        else:
            self.comboboxMaterial.set(self.selectedAlert.material.name)
            self.entryThreshold.delete(0, tk.END)
            self.entryThreshold.insert(0, Locale.stringFromNumber(self.selectedAlert.threshold, 2))

    def clicked_add_button(self, _event):
        """
        Add Button event.
        """

        self.listboxAlert.selection_clear(0, tk.END)
        self.selectedAlert = None
        self.isNewAlert = True
        self.update_entry_fields()
        self.enable_disable_buttons()

    def clicked_save_button(self, _event):
        """
        Save button event
        """

        if self.validate_entries():
            material = Materials.by_name(self.comboboxMaterial.get())
            threshold = Locale.numberFromString(self.entryThreshold.get())
            index = tk.END

            if self.isNewAlert:
                alert = MaterialAlert(material, threshold)
                self.materialAlertsList.append(alert)
                self.selectedAlert = alert
                self.listboxAlert.insert(tk.END, alert.__str__())

            else:
                # update it I guess
                self.selectedAlert.material = material
                self.selectedAlert.threshold = threshold
                index = self.materialAlertsList.index(self.selectedAlert)
                self.listboxAlert.delete(index)
                self.listboxAlert.insert(index, self.selectedAlert.__str__())

            self.listboxAlert.select_set(index)
            self.listboxAlert.event_generate('<<ListboxSelect>>')
            self.isNewAlert = False

        self.update_entry_fields()
        self.enable_disable_buttons()

    def clicked_delete_button(self, _event):
        """
        Delete button event.
        """

        selection = self.listboxAlert.curselection()
        if len(selection) >= 1:
            index = selection[0]
        else:
            index = -1

        if index >= 0:
            del self.materialAlertsList[index]
            self.listboxAlert.delete(index)

        self.selectedAlert = None
        self.update_entry_fields()
        self.enable_disable_buttons()

    def select_alert(self, event):
        """
        Event fired when a alert is selected in the listbox.
        """

        widget = event.widget
        if widget == self.listboxAlert:
            selection = widget.curselection()
            if len(selection) >= 1:
                index = selection[0]
            else:
                index = -1

            if index >= 0:
                self.selectedAlert = self.materialAlertsList[index]
            else:
                self.selectedAlert = None

            self.labelWarnings.config(text='')
            self.update_entry_fields()
            self.enable_disable_buttons()
