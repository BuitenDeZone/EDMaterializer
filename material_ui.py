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
from material_api import MaterialAlert, Materials, Rarities


class MaterialAlertsListPreferencesFrame(tk.Frame):
    """
    Creates a frame to manage the Material Alert List.
    """

    def __init__(self, master, default_thresholds, material_alerts_list=None, **kw):
        tk.Frame.__init__(self, master, **kw)

        if material_alerts_list is None:
            material_alerts_list = []

        self.materialAlertsList = material_alerts_list
        self.materialWidgets = dict()
        self.defaultThresholds = default_thresholds
        self.create_widgets()
        self.update_alerts()

    def update_alerts(self):
        """
        Update the UI with the current configured `MaterialAlert`s.
        """

        # Clear all
        for _material, widgets in self.materialWidgets.items():
            widgets[0].set(0)
            widgets[1].delete(0, tk.END)

        # Load all
        for alert in self.materialAlertsList:
            if alert.enabled:
                self.materialWidgets[alert.material][0].set(alert.material.materialId)
            else:
                self.materialWidgets[alert.material][0].set(0)
            self.materialWidgets[alert.material][1].delete(0, tk.END)
            self.materialWidgets[alert.material][1].insert(0, Locale.stringFromNumber(alert.threshold, 2))

    # bound methods documentation is kinda lacking. I hacked around.
    def material_selectbox_event(self, _event=None):
        """
        Executed whenever a checkbox is selected.
        If enabled and the value is still empty, a default value will be added.
        """

        for material, widgets in self.materialWidgets.items():
            # enabled
            checkbox_val = widgets[0].get()
            entry_value = widgets[1].get()
            if checkbox_val > 0 and entry_value.strip() == "":
                widgets[1].delete(0, tk.END)
                widgets[1].insert(0, Locale.stringFromNumber(self.defaultThresholds.get(material, 0.0), 2))


    def create_widgets(self):
        """Creates different frames for each known `Rarity`."""

        self._create_rarity_frame(self, Rarities.VERY_COMMON, column=0, row=0)
        self._create_rarity_frame(self, Rarities.COMMON, column=1, row=0)
        self._create_rarity_frame(self, Rarities.RARE, column=0, row=1)
        self._create_rarity_frame(self, Rarities.VERY_RARE, column=1, row=1)
        self.grid()

    def get_material_filters(self):
        """
        Convert the settings made in the UI in a list of `MaterialAlert`s.
        :return: list of MaterialAlert`s
        """

        material_filters = []
        for material, widgets in self.materialWidgets.items():
            enabled = True if widgets[0].get() > 0 else False
            entry_value = widgets[1].get() if widgets[1].get() else '0.0'
            threshold = round(Locale.numberFromString(entry_value) * 100) / 100.0
            material_filters.append(MaterialAlert(material, threshold, enabled))
        return material_filters

    def _create_rarity_frame(self, parent, rarity, **gridopts):
        """
        Helper that fills up a frame based on `Rarity`.
        :param parent: Parent frame
        :param rarity: Rarity to filter on
        :param gridopts: Extra gridopts for the frame
        :return: A frame
        """

        wrap_frame = tk.Frame(parent)
        wrap_frame.configure(padx=5, pady=5)
        wrap_frame.grid()

        title_label = tk.Label(wrap_frame, text=rarity.description, background=rarity.labelColor)
        materials_frame = tk.LabelFrame(wrap_frame, labelwidget=title_label)
        materials_frame.configure(padx=5, pady=5)

        index = 0
        for material in Materials.by_rarity(rarity):
            check_var = tk.IntVar(value=0)
            checkbox = tk.Checkbutton(
                materials_frame,
                text=material.name,
                variable=check_var,
                onvalue=material.materialId,
                offvalue=0,
                command=self.material_selectbox_event
            )
            checkbox.grid(column=0, row=index, sticky=tk.W)

            greater = tk.Label(materials_frame, text=">=")
            greater.grid(column=1, row=index, sticky=tk.E)

            entry = tk.Entry(materials_frame)
            entry.configure(width=10, justify=tk.RIGHT)
            entry.grid(column=2, row=index, sticky=tk.E)
            index = index + 1
            self.materialWidgets[material] = (check_var, entry)

        materials_frame.grid_columnconfigure(2, weight=1)
        materials_frame.grid(sticky=tk.N+tk.E+tk.S+tk.W)
        gridopts['sticky'] = tk.N+tk.W+tk.E
        wrap_frame.grid(**gridopts)

        return materials_frame


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
        """
        (re-)Generate the frame for all the matches.
        """


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
                enabled = True
                threshold = round(Locale.numberFromString(threshold) * 100) / 100.0
                if threshold <= -100:
                    threshold = (threshold * -1) - 100
                    enabled = False

                alert = MaterialAlert(material, round(threshold, 2), enabled)
                alerts.append(alert)

        return alerts

    @classmethod
    def translate_to_settings(cls, alerts, clean=False):
        """
        Convert a list of MaterialAlerts into a string only list to store in settings.
        :param alerts: list of MaterialAlert objects.
        :param clean: Omit disabled filters in the output
        :return: list of string representations of MaterialAlerts.
        """

        result = []
        if alerts is None:
            return result

        for alert in alerts:
            if clean and alert.disabled:
                continue

            threshold = alert.threshold
            if not alert.enabled:
                threshold = (threshold * -1) - 100.0

            result.append('{}>={}'.format(alert.material.symbol, Locale.stringFromNumber(threshold, 2)))

        return result


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
