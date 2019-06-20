# Materializer plugin for [EDMC](https://github.com/Marginal/EDMarketConnector/wiki)

This plugin helps you finding materials while exploring new systems.
It allows you to configure a certain watchlist for materials (with a threshold).

Only planets with matching materials and that are landable will be shown.

## Default thresholds

A number of default thresholds have been provided and are based on the data I found here:

* [Reddit/Elite Dangerous: Highest element material percentages by planet](https://www.reddit.com/r/EliteDangerous/comments/61g64i/highest_element_material_percentages_by_planet/)
* [Google Docs: Element Occurence by Planet Type](https://tinyurl.com/mexgpnb)


## Development


1. Get a clone from EDMC:
    * Using git-bash: 
        ```bash
        user@example MINGW64 ~
        $ git clone https://github.com/Marginal/EDMarketConnector.git Sources/EDMarketConnector
        Cloning into 'Sources/EDMarketConnector'...
        ...
        ```
    * Using command prompt:
        ```Shell
        C:\Users\user>git clone https://github.com/Marginal/EDMarketConnector.git Sources\EDMarketConnector
        Cloning into 'Sources\EDMarketConnector'...
        ...
        ```

2. Clone this repo:
    * Using git-bash:
        ```bash
        user@example MINGW64 ~
        $ cd $LOCALAPPDATA/EDMarketConnector/plugins/
        user@example MINGW64 ~/AppData/Local/EDMarketConnector/plugins
        $ git clone https://github.com/BuitenDeZone/EDMaterializer.git Materializer
        Cloning into 'Materializer'
        ...
        ```
    * Using command prompt:
        ```Shell
        C:\Users\user>cd %LOCALAPPDATA%\EDMarketConnector\plugins
        C:\Users\user\AppData\Local\EDMarketConnector\plugins>git clone https://github.com/BuitenDeZone/EDMaterializer.git Materializer
        Cloning into 'Materializer'
        ```
    
2. Using PyCharm:
    1. Open the project
    2. Configure the python environment (virtualenv)

### Tests

* `test.py`: Some unit tests have been added in tests.py. Mainly to assist with development.
* `test_*_frame.py`: These are some helpers to speed up UI development. 

    They require access to EDMC modules. Make sure the EDMC sources are on the python path.

## Contributing

 1. **Fork** the repo on GitHub
 2. **Clone** the project to your own machine
 3. Create a new **Branch**
 3. **Commit** changes to your own branch
 4. **Push** your work back up to your fork
 5. Submit a **Pull request** so that we can review your changes

Notes: 
* Be sure to merge the latest from "upstream" before making a pull request.
* Style: Make sure to use `pylint` before creating a pull request as much as possible.

## License

[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)