"""
Plugin to help with finding planets with the materials you need while exploring.
"""

import sys

# EDMC Components
from config import config

# Own materializer stuff
from material_api import FIELD_BODY_NAME, FIELD_EVENT, FIELD_LANDABLE, FIELD_MATERIALS, FIELD_SCAN_TYPE
from material_api import FIELD_STAR_SYSTEM, VALUE_EVENT_FSDJUMP, VALUE_EVENT_SCAN, VALUE_SCAN_TYPE_DETAILED
from material_api import MaterialMatch, Materials
from material_ui import MaterialAlertListSettingsFrame, MaterialAlertListSettings, MaterialAlertListFrame


VERSION = '0.1'
this = sys.modules[__name__]  # For holding module globals


def plugin_prefs(parent, _cmdr, _is_beta):
    """
    Return a TK Frame for adding to the ED:MC settings dialog.
    """

    this.materialAlertListSettingsEditor = MaterialAlertListSettingsFrame(parent, this.materialAlertFilters)
    return this.materialAlertListSettingsEditor


def prefs_changed(_cmdr, _is_beta):
    """
    Called when the preferences ED:MC dialog is closed: Save settings.
    """

    this.materialAlertFilters = this.materialAlertListSettingsEditor.materialAlertsList
    translated = MaterialAlertListSettings.translate_to_settings(this.materialAlertFilters)
    config.set('material_filters', translated)


def plugin_start(_plugin_dir):
    """
    Called on plugin start.
    """
    this.currentSystem = None
    # Load known filters
    this.materialAlertFilters = MaterialAlertListSettings.translate_from_settings(config.get('material_filters'))
    return 'Materializer'

def add_test_matches_1():
    """Add test matches."""

    this.materialAlertsFrame.add_matches("1", [
        MaterialMatch(Materials.ARSENIC, 2.3415),
        MaterialMatch(Materials.IRON, 20.33)])

def add_test_matches_2():
    this.materialAlertsFrame.add_matches("2 b", [
        MaterialMatch(Materials.ARSENIC, 1.5),
        MaterialMatch(Materials.TUNGSTEN, 0.4)])

def add_test_matches_3():
    this.materialAlertsFrame.add_matches("3", [
        MaterialMatch(Materials.ARSENIC, 1.5),
        MaterialMatch(Materials.TUNGSTEN, 0.4)])

def clear_test_matches():
    this.materialAlertsFrame.clear_matches()

def plugin_app(parent):
    """
    Initialize our frame to display our matches.
    We do not return it because that kinda messes with how EDMC handles
    frames from plugins. It is lazy loaded later on.
    """

    this.materialAlertsFrame = MaterialAlertListFrame(parent)
    # parent.after(1000, add_test_matches_1)
    # parent.after(3000, add_test_matches_2)
    # parent.after(5000, add_test_matches_3)
    # parent.after(8000, clear_test_matches)
    # parent.after(10000, add_test_matches_3)
    return this.materialAlertsFrame


def journal_entry(_cmdr, _is_beta, system, _station, entry, _state):
    """
    Handle the events.
    """

    if entry[FIELD_EVENT] == VALUE_EVENT_FSDJUMP:
        this.materialAlertsFrame.clear_matches()

    elif entry[FIELD_EVENT] == VALUE_EVENT_SCAN \
            and entry[FIELD_SCAN_TYPE] == VALUE_SCAN_TYPE_DETAILED \
            and FIELD_LANDABLE in entry \
            and entry[FIELD_LANDABLE] is True:

        materials = entry[FIELD_MATERIALS]
        matches = [m for m in [f.check_matches(materials) for f in this.materialAlertFilters] if m is not None]
        planetentry = str(entry[FIELD_BODY_NAME])
        planetname = planetentry.replace(system, '')
        if matches:
            this.materialAlertsFrame.add_matches(planetname, matches)
