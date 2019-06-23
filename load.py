"""Plugin to help with finding planets with the materials you need while exploring."""

import sys
import Tkinter as tk
from pprint import pformat

# EDMC Components
from config import config
import myNotebook as nb
from monitor import monitor
import plug

# Own materializer stuff
from edsm_queries import EDSM_QUERIES
from material_api import LOGGER, LOG_INFO, LOG_DEBUG
from material_api import FIELD_BODY_NAME, FIELD_EVENT, FIELD_LANDABLE, FIELD_MATERIALS, FIELD_SCAN_TYPE
from material_api import VALUE_EVENT_FSDJUMP, VALUE_EVENT_SCAN, VALUE_SCAN_TYPE_DETAILED
from material_api import Materials
from material_ui import MaterialFilterConfigFrame, MaterialFilterListConfigTranslator, MaterialFilterMatchesFrame
from version import VERSION


this = sys.modules[__name__]  # For holding module globals

# this.logLevel = LOG_DEBUG
# LOGGER.logLevel = LOG_DEBUG
this.logPrefix = "Materializer Plugin > "

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
    this.materialMatchesFrame.update_filters(this.materialFilters)
    config.set('material_filters', MaterialFilterListConfigTranslator.translate_to_settings(this.materialFilters))


def plugin_start(_plugin_dir):
    """Initialize plugin.

    Called by EDMC on plugin start.
    """

    #                ,---.o                             o
    # ,---.,---.,---.|__. .,---.    ,---.,---.,---.,---..,---.,---.
    # |    |   ||   ||    ||   |    |   |,---||    `---.||   ||   |
    # `---'`---'`   '`    ``---|    |---'`---^`    `---'``   '`---|
    #                      `---'    |                         `---'
    material_filters_config = config.get('material_filters')
    if material_filters_config is None:
        material_filters_config = []

    # Get from config and trim out empty values
    raw_material_filters = [x for x in material_filters_config if x]
    # Load known filters
    this.materialFilters = MaterialFilterListConfigTranslator.translate_from_settings(raw_material_filters)

    #                |
    # . . .,---.,---.|__/ ,---.,---.
    # | | ||   ||    |  \ |---'|
    # `-'-'`---'`    `   ``---'`
    this.lastEDSMScan = None
    this.edsmQueries = EDSM_QUERIES

    LOGGER.log(this, LOG_INFO, 'Plugin Materializer (version: {version}) enabled...'.format(version=VERSION))
    for f in this.materialFilters:
        LOGGER.debug(this, '  Filter used: {filter}'.format(filter=f.__str__()))

    return 'Materializer'


def plugin_stop():
    """Stop and cleanup all running threads."""

    this.edsmQueries.stop()


def plugin_app(parent):
    """
    Initialize our frame to display our matches.

    We do not return it because that kinda messes with how EDMC handles
    frames from plugins. It is lazy loaded later on.
    """

    parent.bind('<<EDSMCallback>>', _edsm_callback_received)
    this.edsmQueries.start(parent)
    this.materialMatchesFrame = MaterialFilterMatchesFrame(parent, this.materialFilters)
    return this.materialMatchesFrame


def journal_entry(_cmdr, _is_beta, system, _station, entry, _state):
    """Handle the events."""

    if entry[FIELD_EVENT] == VALUE_EVENT_FSDJUMP:
        this.materialMatchesFrame.jump_system(system)

    elif entry[FIELD_EVENT] == VALUE_EVENT_SCAN \
            and entry[FIELD_SCAN_TYPE] == VALUE_SCAN_TYPE_DETAILED \
            and FIELD_LANDABLE in entry \
            and entry[FIELD_LANDABLE] is True:

        this.materialMatchesFrame.process_filter_planet_materials(
            system,
            str(entry[FIELD_BODY_NAME]),
            entry[FIELD_MATERIALS],
            True,  # With priority. If we are scanning this system, we are on this system!
        )


# |         |
# |---.,---.|    ,---.,---.,---.,---.
# |   ||---'|    |   ||---'|    `---.
# `   '`---'`---'|---'`---'`    `---'
#                |

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


def _edsm_callback_received(_event=None):
    """Proxy callbacks to plugins that support them.

    You should filter the responses you need out yourself.
    You can pre-filter specific api's and endpoints by implementing
    specific callbacks for each:

        * edsm_querier_response_api_system_v1_bodies: will only receive api-system-v1 bodies responses.
        * edsm_querier_response_api_system_v1: will receive all api-system-v1 responses.
        * edsm_querier_response: will receive all responses.


    If any of these returns `True`, the remaining more generic methods will be skipped for your plugin.
    """

    LOGGER.debug(this, 'edsm callback received')
    while True:
        response = this.edsmQueries.get_response()
        if response is None:
            break

        # LOGGER.debug(this, 'response: {resp}'.format(resp=pformat(response)))
        (request, reply) = response
        (api, endpoint, _method, _request_params) = request

        api_callbacks = [
            'edsm_querier_response_{api}_{endpoint}'.format(
                api=api.replace('-', '_'),
                endpoint=endpoint,
            ),
            'edsm_querier_response_{api}'.format(api=api.replace('-', '_')),
            'edsm_querier_response',
        ]

        for plugin in plug.PLUGINS:
            for api_callback in api_callbacks:

                LOGGER.debug(this, "checking for function: '{func}' on {plugin}".format(
                    func=api_callback,
                    plugin=plugin.name,
                ))
                LOGGER.debug(this, "plugin: {pl}".format(pl=pformat(plugin)))
                if hasattr(plugin.module, api_callback):
                    response = plug.invoke(plugin.name, None, api_callback, request, reply)
                    LOGGER.debug(this, 'calling {func} on {plugin}: {response}'.format(
                        func=api_callback,
                        plugin=plugin,
                        response=str(response),
                    ))
                    if response is True:
                        break
