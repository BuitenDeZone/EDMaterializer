"""Plugin to help with finding planets with the materials you need while exploring."""

import sys
import Tkinter as tk

# EDMC Components
from config import config
import myNotebook as nb

# Own materializer stuff
from material_api import FIELD_BODY_NAME, FIELD_EVENT, FIELD_LANDABLE, FIELD_MATERIALS, FIELD_SCAN_TYPE
from material_api import VALUE_EVENT_FSDJUMP, VALUE_EVENT_SCAN, VALUE_SCAN_TYPE_DETAILED
from material_api import Materials
from material_ui import MaterialFilterConfigFrame, MaterialFilterListConfigTranslator, MaterialFilterMatchesFrame
from version import VERSION

this = sys.modules[__name__]  # For holding module globals


# Based on https://tinyurl.com/mexgpnb
DEFAULT_THRESHOLDS = {
    Materials.ANTIMONY: 1.4,
    Materials.ARSENIC: 2.6,
    Materials.CADMIUM: 3.0,
    Materials.CARBON: 22.0,
    Materials.CHROMIUM: 16.4,
    Materials.GERMANIUM: 5.6,
    Materials.IRON: 38.1,
    Materials.LEAD: 0.0,
    Materials.MANGANESE: 15.2,
    Materials.MERCURY: 1.7,
    Materials.MOLYBDENUM: 2.6,
    Materials.NICKEL: 28.8,
    Materials.NIOBIUM: 2.6,
    Materials.PHOSPHORUS: 14.1,
    Materials.POLONIUM: 1.1,
    Materials.RUTHENIUM: 2.5,
    Materials.SELENIUM: 4.1,
    Materials.SULPHUR: 26.1,
    Materials.TECHNETIUM: 1.4,
    Materials.TELLURIUM: 1.5,
    Materials.TIN: 2.6,
    Materials.TUNGSTEN: 2.1,
    Materials.VANADIUM: 9.5,
    Materials.YTTRIUM: 2.3,
    Materials.ZINC: 10.3,
    Materials.ZIRCONIUM: 4.6,
}


def plugin_prefs(parent, _cmdr, _is_beta):
    """Return a Tk Frame for adding to the EDMC settings dialog."""

    this.prefsFrame = nb.Frame(parent)

    this.materialFiltersPreferences = create_material_filter_prefs(
        this.prefsFrame,
        DEFAULT_THRESHOLDS,
        this.materialFilters,
    )
    this.materialFiltersPreferences.grid(column=0, row=0, sticky=tk.N + tk.S + tk.W)

    this.optionsFrame = create_options_prefs(this.prefsFrame)
    this.optionsFrame.grid(column=1, row=0, sticky=tk.N + tk.E + tk.S + tk.W)

    return this.prefsFrame


def prefs_changed(_cmdr, _is_beta):
    """
    Update changed preferences.

    Called by EDMC when the settings/config should be updated.
    """

    this.materialFilters = this.materialFiltersPreferences.get_material_filters()
    config.set('material_filters', MaterialFilterListConfigTranslator.translate_to_settings(this.materialFilters))


def plugin_start(_plugin_dir):
    """Initialize plugin.

    Called by EDMC on plugin start.
    """

    this.currentSystem = None
    raw_material_filters = [x for x in config.get('material_filters') if x]
    # Load known filters
    this.materialFilters = MaterialFilterListConfigTranslator.translate_from_settings(raw_material_filters)
    print 'Plugin Materializer (version: {version}) started...'.format(version=VERSION)
    return 'Materializer'


def plugin_app(parent):
    """
    Initialize our frame to display our matches.

    We do not return it because that kinda messes with how EDMC handles
    frames from plugins. It is lazy loaded later on.
    """

    this.materialMatchesFrame = MaterialFilterMatchesFrame(parent)
    return this.materialMatchesFrame


def journal_entry(_cmdr, _is_beta, system, _station, entry, _state):
    """Handle the events."""

    if entry[FIELD_EVENT] == VALUE_EVENT_FSDJUMP:
        this.materialMatchesFrame.clear_matches()

    elif entry[FIELD_EVENT] == VALUE_EVENT_SCAN \
            and entry[FIELD_SCAN_TYPE] == VALUE_SCAN_TYPE_DETAILED \
            and FIELD_LANDABLE in entry \
            and entry[FIELD_LANDABLE] is True:

        update_matches_frame(
            this.materialMatchesFrame,
            system,
            str(entry[FIELD_BODY_NAME]),
            entry[FIELD_MATERIALS],
            this.materialFilters,
        )


def create_material_filter_prefs(parent, defaults, filters):
    """Create a new MaterialFilterConfigFrame."""

    return MaterialFilterConfigFrame(parent, defaults, filters)


def create_options_prefs(parent):
    """Create a new options frame.

    :param parent: Parent frame
    """

    wrap_frame = tk.Frame(parent)
    wrap_frame.configure(padx=5, pady=5)
    wrap_frame.grid(sticky=tk.N + tk.E + tk.W)

    frame = tk.LabelFrame(wrap_frame, text="General Options")
    frame.configure(padx=5, pady=5)

    lbl = tk.Label(
        frame, wrap=200, justify=tk.LEFT,
        text="You can reset to defaults by clearing an entry and (dis)/enable it (again).",
    )
    lbl.grid()
    frame.grid()
    return wrap_frame


def check_material_matches(materials, filters):
    """
    Check each filter against the provided materials and returns matches.

    :param materials: List of materials: array of [{"Name": <value>, "Percent": <value>}, ...]
    :param filters: List of `MaterialFilter`s
    :return: list of `MaterialMatch`es
    """

    return [m for m in [f.check_matches(materials) for f in filters] if m is not None]


def update_matches_frame(filter_match_frame, system, planet, materials, filters):
    """
    Update the result frame by getting the matches on a scan event.

    :param filter_match_frame: Frame with filter matches
    :param system: Current system name: Used to create the planet 'short' name
    :param planet: Name of the planet
    :param materials: List of found materials
    :param filters: Filters to check against
    """

    matches = check_material_matches(materials, filters)
    if matches:
        planet_name = planet.replace(system, '')
        filter_match_frame.add_matches(planet_name, matches)

